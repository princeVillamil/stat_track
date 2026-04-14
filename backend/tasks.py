import os
import asyncio
import redis as sync_redis
from celery import Celery
import json
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert
from models import Player, LeaderboardSnapshot, MmrHistory, PlayerHeroStats
from database import SessionLocal
from services.deadlock_client import get_leaderboard, get_player_mmr_history
from services.leaderboard import bulk_update_leaderboard, store_leaderboard_metadata
from services.response_cache import invalidate_cache_prefix

app = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
)

app.conf.update(
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "refresh-NAmerica-leaderboard": {
            "task": "tasks.refresh_leaderboard",
            "schedule": 300.0,
            "args": ["NAmerica"],
            # fires at 0:00, 5:00, 10:00...
        },
        "refresh-Europe-leaderboard": {
            "task": "tasks.refresh_leaderboard",
            "schedule": 300.0,
            "args": ["Europe"],
            # offset by 100 seconds
            "options": {"countdown": 100},
        },
        "refresh-Asia-leaderboard": {
            "task": "tasks.refresh_leaderboard",
            "schedule": 300.0,
            "args": ["Asia"],
            # offset by 200 seconds
            "options": {"countdown": 200},
        },
        "refresh-SAmerica-leaderboard": {
            "task": "tasks.refresh_leaderboard",
            "schedule": 300.0,
            "args": ["SAmerica"],
            "options": {"countdown": 300},
        },
        "refresh-Oceania-leaderboard": {
            "task": "tasks.refresh_leaderboard",
            "schedule": 300.0,
            "args": ["Oceania"],
            "options": {"countdown": 400},
        },
    },
)

redis_client = sync_redis.from_url(
    os.getenv("REDIS_URL", "redis://redis:6379/0"),
    decode_responses=True
)

def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@app.task(bind=True, max_retries=3)
def refresh_leaderboard(self, region: str):
    try:
        data = run_async(get_leaderboard(region))

        if not data or "entries" not in data:
            print(f"No data returned for region {region}")
            return

        entries = sorted(
            data["entries"],
            key=lambda e: e.get("rank", 0)
        )

        db = SessionLocal()
        snapshot_at = datetime.now(timezone.utc)

        try:
            pipe = redis_client.pipeline()
            resolved = []

            for entry in entries:
                account_name = entry.get("account_name")
                if not account_name:
                    continue

                possible_ids = entry.get("possible_account_ids", [])

                # should pick deterministic account_id (never skip for uniqueness logic)
                account_id = possible_ids[0] if possible_ids else None

                badge_level = entry.get("badge_level", 0)
                top_hero_ids = ",".join(
                    str(h) for h in entry.get("top_hero_ids", [])
                )

                # Stable Upsert Logic
                try:
                    stmt = insert(Player).values(
                        account_name=account_name,
                        account_id=account_id,
                        last_seen=snapshot_at,
                    ).on_conflict_do_update(
                        index_elements=["account_name"],
                        set_={
                            "account_id": account_id,
                            "last_seen": snapshot_at,
                        }
                    )
                    db.execute(stmt)
                    db.flush()
                except Exception as e:
                    db.rollback()
                    # Check if it's a unique constraint violation on account_id
                    # This happens when a player changes their name (e.g., Bob -> Dave, but ID is same)
                    if account_id and ("account_id" in str(e).lower()):
                        print(f"DEBUG: Identity conflict for {account_id} ({account_name}). Attempting rename.")
                        existing_by_id = db.query(Player).filter(Player.account_id == account_id).first()
                        if existing_by_id:
                            # We found the player by ID. Now we need to rename them to the new name.
                            conflict_player = db.query(Player).filter(Player.account_name == account_name).first()
                            if conflict_player:
                                print(f"DEBUG: Name conflict for {account_name}. Deleting redundant player.")
                                db.query(LeaderboardSnapshot).filter(LeaderboardSnapshot.account_name == account_name).update({"account_name": existing_by_id.account_name})
                                db.query(MmrHistory).filter(MmrHistory.account_name == account_name).update({"account_name": existing_by_id.account_name})
                                db.query(PlayerHeroStats).filter(PlayerHeroStats.account_name == account_name).update({"account_name": existing_by_id.account_name})
                                db.delete(conflict_player)
                                db.flush()

                            existing_by_id.account_name = account_name
                            existing_by_id.last_seen = snapshot_at
                            db.flush()
                            print(f"DEBUG: Renamed player to {account_name}")
                    else:
                        print(f"ERROR: Unexpected exception for {account_name}: {e}")
                        raise e

                # =========================
                # Snapshot insert (history)
                # =========================
                db.add(LeaderboardSnapshot(
                    account_name=account_name,
                    region=region,
                    rank=entry.get("rank"),
                    badge_level=badge_level,
                    ranked_rank=entry.get("ranked_rank"),
                    ranked_subrank=entry.get("ranked_subrank"),
                    top_hero_ids=top_hero_ids,
                    snapshot_at=snapshot_at,
                ))

                resolved.append({
                    "account_name": account_name,
                    "account_id": account_id,
                    "badge_level": badge_level,
                    "ranked_rank": entry.get("ranked_rank"),
                    "ranked_subrank": entry.get("ranked_subrank"),
                    "top_hero_ids": entry.get("top_hero_ids", []),
                    "rank": entry.get("rank"),
                })

            db.commit()
            pipe.execute()

            # Redis + leaderboard update
            run_async(bulk_update_leaderboard(region, resolved))
            run_async(store_leaderboard_metadata(region, resolved))

            redis_client.expire(f"leaderboard:{region}", 600)

            # Cache invalidation
            run_async(invalidate_cache_prefix("cache:leaderboard"))
            run_async(invalidate_cache_prefix("cache:player_rank"))

            # WebSocket notif
            redis_client.publish(
                "leaderboard:updates",
                json.dumps({
                    "event": "leaderboard_updated",
                    "region": region,
                    "updated": len(resolved),
                })
            )

            print(f"Refreshed {region}: {len(resolved)} players stored")
            print(f"Published update event for {region}")

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=60 * (2 ** self.request.retries)
        )

@app.task(bind=True, max_retries=3)
def fetch_player_mmr_history(self, account_id: int):
    try:
        data = run_async(get_player_mmr_history(account_id))
        if not data:
            return

        db = SessionLocal()
        try:
            for entry in data:
                db.add(MmrHistory(
                    account_id=account_id,
                    mmr=entry.get("mmr"),
                    recorded_at=datetime.now(timezone.utc),
                ))
            db.commit()
            print(f"Stored MMR history for {account_id}")
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))