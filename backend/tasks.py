import os
import asyncio
import redis as sync_redis
from celery import Celery
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert

# import your models and db session
from models import Player, LeaderboardSnapshot
from database import SessionLocal

# import your async API client
from services.deadlock_client import get_leaderboard, get_player_mmr_history
from services.leaderboard import bulk_update_leaderboard, store_leaderboard_metadata

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
        },
        "refresh-Europe-leaderboard": {
            "task": "tasks.refresh_leaderboard",
            "schedule": 300.0,
            "args": ["Europe"],
        },
        "refresh-Asia-leaderboard": {
            "task": "tasks.refresh_leaderboard",
            "schedule": 300.0,
            "args": ["Asia"],
        },
    },
)

# sync Redis client for Celery tasks
# Celery workers are synchronous — use the sync redis client here
# (your FastAPI routes use the async one in cache.py)
redis_client = sync_redis.from_url(
    os.getenv("REDIS_URL", "redis://redis:6379/0"),
    decode_responses=True
)


def run_async(coro):
    """
    Run an async function from sync Celery task.
    Celery workers are sync. Your API client is async.
    This bridges the gap.
    """
    return asyncio.get_event_loop().run_until_complete(coro)


@app.task(bind=True, max_retries=3)
def refresh_leaderboard(self, region: str):
    """
    Fetch leaderboard for a region and store results.
    Runs every 5 minutes per region via Beat scheduler.
    bind=True gives access to self for retry logic.
    """
    try:
        # fetch from API (async client, called from sync context)
        data = run_async(get_leaderboard(region))

        if not data or "entries" not in data:
            print(f"No data returned for region {region}")
            return

        entries = data["entries"]
        db = SessionLocal()
        # snapshot_at = datetime.utcnow()
        snapshot_at = datetime.now(timezone.utc)

        try:
            # Redis sorted set key for this region
            redis_key = f"leaderboard:{region}"

            # pipeline batches all Redis writes into one round trip
            # instead of 100 individual calls, send them all at once
            pipe = redis_client.pipeline()

            # for entry in entries:
            #     # account_id = entry.get("possible_account_ids", [None])[0] -- BROKEN: crashes if possible_account_ids = []
            #     account_ids = entry.get("possible_account_ids") or []
            #     account_id = account_ids[0] if account_ids else None
            #     if not account_id:
            #         continue

            #     # 1. upsert player
            #     # INSERT ... ON CONFLICT DO UPDATE
            #     # if player exists: update their name and last_seen
            #     # if player is new: insert them
            #     stmt = insert(Player).values(
            #         account_id=account_id,
            #         account_name=entry.get("account_name"),
            #         last_seen=snapshot_at,
            #     ).on_conflict_do_update(
            #         index_elements=["account_id"],
            #         set_={
            #             "account_name": entry.get("account_name"),
            #             "last_seen": snapshot_at,
            #         }
            #     )
            #     db.execute(stmt)

            for entry in entries:
                account_name  = entry.get("account_name")
                if not account_name:
                    continue

                possible_ids  = entry.get("possible_account_ids", [])
                account_id    = possible_ids[0] if len(possible_ids) == 1 else None
                badge_level   = entry.get("badge_level", 0)
                top_hero_ids  = ",".join(str(h) for h in entry.get("top_hero_ids", []))

                # upsert player
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

                # snapshot — account_name only, no account_id
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

                pipe.zadd(redis_key, {account_name: badge_level})
                # # 2. write snapshot row — rank history
                # snapshot = LeaderboardSnapshot(
                #     account_name=account_name,  # ← correct field
                #     region=region,
                #     rank=entry.get("rank"),
                #     badge_level=badge_level,
                #     ranked_rank=entry.get("ranked_rank"),
                #     ranked_subrank=entry.get("ranked_subrank"),
                #     top_hero_ids=top_hero_ids,
                #     snapshot_at=snapshot_at,
                # )
                # db.add(snapshot)

                # 3. add to Redis sorted set
                # score = badge_level so ZREVRANGE returns highest badge first
                # pipe.zadd(redis_key, {str(account_id): entry.get("badge_level", 0)})

            db.commit()

            # execute all Redis writes in one shot
            pipe.execute()

            # resolved = [
            #     {
            #         "account_name":   entry.get("account_name"),
            #         "badge_level":    entry.get("badge_level", 0),
            #         "ranked_rank":    entry.get("ranked_rank"),
            #         "ranked_subrank": entry.get("ranked_subrank"),
            #         "top_hero_ids":   entry.get("top_hero_ids", []),
            #         "rank":           entry.get("rank"),
            #     }
            #     for entry in entries
            #     if entry.get("account_name")
            # ]
            resolved = [
                {
                    "account_name": entry.get("account_name"),
                    "account_id":   entry.get("possible_account_ids", [None])[0] if len(entry.get("possible_account_ids", [])) == 1 else None,
                    "badge_level":  entry.get("badge_level", 0),
                    "ranked_rank":  entry.get("ranked_rank"),
                    "ranked_subrank": entry.get("ranked_subrank"),
                    "top_hero_ids": entry.get("top_hero_ids", []),
                    "rank":         entry.get("rank"),
                }
                for entry in entries
                if entry.get("account_name")
            ]
                        

            run_async(bulk_update_leaderboard(region, resolved))
            run_async(store_leaderboard_metadata(region, resolved))
            # set expiry on the sorted set — 10 min safety net
            redis_client.expire(f"leaderboard:{region}", 600)
            # redis_client.expire(redis_key, 600)

            print(f"Refreshed {region}: {len(resolved)} players in Postgres + Redis")
            print(f"Refreshed {region}: {len(entries)} players stored")

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    except Exception as exc:
        # retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@app.task(bind=True, max_retries=3)
def fetch_player_mmr_history(self, account_id: int):
    """
    Fetch and store MMR history for a single player.
    Called manually or triggered after leaderboard refresh.
    """
    from models import MmrHistory

    try:
        data = run_async(get_player_mmr_history(account_id))

        if not data:
            return

        db = SessionLocal()
        try:
            for entry in data:
                mmr_point = MmrHistory(
                    account_id=account_id,
                    mmr=entry.get("mmr"),
                    match_id=entry.get("match_id"),
                    # recorded_at=datetime.utcnow(),
                    recorded_at = datetime.now(timezone.utc),
                )
                db.add(mmr_point)

            db.commit()
            print(f"Stored MMR history for {account_id}")

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))