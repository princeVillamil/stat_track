import os
import asyncio
import redis as sync_redis
from celery import Celery
import json
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert
from models import Player, LeaderboardSnapshot
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

        # ✅ FIX 1: sort entries BEFORE DB operations
        entries = sorted(
            data["entries"],
            key=lambda e: e.get("account_name", "")
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
                account_id = possible_ids[0] if len(possible_ids) == 1 else None
                badge_level = entry.get("badge_level", 0)
                top_hero_ids = ",".join(str(h) for h in entry.get("top_hero_ids", []))

                stmt = insert(Player).values(
                    account_name=account_name,
                    account_id=account_id,
                    last_seen=snapshot_at,
                ).on_conflict_do_update(
                    index_elements=["account_name"],
                    set_={
                        "last_seen": snapshot_at,
                        "account_id": account_id,
                    }
                )
                db.execute(stmt)

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
                    "badge_level": badge_level,
                    "ranked_rank": entry.get("ranked_rank"),
                    "ranked_subrank": entry.get("ranked_subrank"),
                    "top_hero_ids": entry.get("top_hero_ids", []),
                    "rank": entry.get("rank"),
                })

            db.commit()
            pipe.execute()

            run_async(bulk_update_leaderboard(region, resolved))
            run_async(store_leaderboard_metadata(region, resolved))
            redis_client.expire(f"leaderboard:{region}", 600)

            # Cache invalidation
            run_async(invalidate_cache_prefix("cache:leaderboard"))
            run_async(invalidate_cache_prefix("cache:player_rank"))

            # Notify WebSocket clients
            redis_client.publish(
                "leaderboard:updates",
                json.dumps({
                    "event": "leaderboard_updated",
                    "region": region,
                    "updated": len(resolved),
                })
            )

            print(f"Published update event for {region}")
            print(f"Refreshed {region}: {len(resolved)} players stored")

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@app.task(bind=True, max_retries=3)
def fetch_player_mmr_history(self, account_id: int):
    from models import MmrHistory
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