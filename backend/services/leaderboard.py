import json
from services.cache import redis_client

def _key(region: str) -> str:
    return f"leaderboard:{region}"

def _meta_key(region: str, account_name: str) -> str:
    return f"leaderboard:meta:{region}:{account_name}"

async def bulk_update_leaderboard(region: str, entries: list[dict]) -> None:
    if not entries:
        return
    # Use a composite score: BadgeLevel + (1 - Rank/10000)
    # This keeps BadgeLevel as the primary sort, but uses Rank to break ties
    # in the original order from the API.
    mapping = {
        entry["account_name"]: float(entry["badge_level"]) + (1.0 - (float(entry.get("rank", 10000)) / 10000.0))
        for entry in entries
        if entry.get("account_name")
    }
    key = _key(region)
    pipe = redis_client.pipeline()
    pipe.delete(key)
    pipe.zadd(key, mapping)
    await pipe.execute()

async def store_leaderboard_metadata(region: str, entries: list[dict]) -> None:
    if not entries:
        return
    pipe = redis_client.pipeline()
    for entry in entries:
        account_name = entry.get("account_name")
        if not account_name:
            continue
        meta = {
            "account_name":   account_name,
            "badge_level":    entry.get("badge_level", 0),
            "ranked_rank":    entry.get("ranked_rank"),
            "ranked_subrank": entry.get("ranked_subrank"),
            "top_hero_ids":   entry.get("top_hero_ids", []),
            "rank":           entry.get("rank"),
        }
        pipe.set(_meta_key(region, account_name), json.dumps(meta), ex=360)
    await pipe.execute()

async def get_top_players(region: str, limit: int = 50, offset: int = 0) -> list[dict]:
    results = await redis_client.zrevrange(
        _key(region), offset, offset + limit - 1, withscores=True
    )
    return [
        {
            "rank":         offset + i + 1,
            "account_name": account_name,
            "badge_level":  int(score),
        }
        for i, (account_name, score) in enumerate(results)
    ]

async def get_player_rank(region: str, account_name: str) -> int | None:
    rank = await redis_client.zrevrank(_key(region), account_name)
    return (rank + 1) if rank is not None else None

async def get_player_score(region: str, account_name: str) -> int | None:
    score = await redis_client.zscore(_key(region), account_name)
    return int(score) if score is not None else None

async def get_leaderboard_size(region: str) -> int:
    return await redis_client.zcard(_key(region))

async def get_enriched_leaderboard(
    region: str, limit: int = 50, offset: int = 0
) -> list[dict]:
    ranked = await get_top_players(region, limit, offset)
    if not ranked:
        return []
    pipe = redis_client.pipeline()
    for entry in ranked:
        pipe.get(_meta_key(region, entry["account_name"]))
    meta_results = await pipe.execute()
    enriched = []
    for entry, meta_raw in zip(ranked, meta_results):
        meta = json.loads(meta_raw) if meta_raw else {}
        enriched.append({
            "rank":           entry["rank"],
            "account_name":   entry["account_name"],
            "badge_level":    entry["badge_level"],
            "ranked_rank":    meta.get("ranked_rank"),
            "ranked_subrank": meta.get("ranked_subrank"),
            "top_hero_ids":   meta.get("top_hero_ids", []),
        })
    return enriched

