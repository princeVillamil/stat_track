import json
from services.cache import redis_client


def _key(region: str) -> str:
    return f"leaderboard:{region}"

def _meta_key(region: str, account_name: str) -> str:
    return f"leaderboard:meta:{region}:{account_name}"


async def bulk_update_leaderboard(region: str, entries: list[dict]) -> None:
    """Write all player scores to sorted set. member=account_name, score=badge_level."""
    if not entries:
        return

    mapping = {
        entry["account_name"]: entry["badge_level"]
        for entry in entries
        if entry.get("account_name")
    }

    await redis_client.zadd(_key(region), mapping)


async def store_leaderboard_metadata(region: str, entries: list[dict]) -> None:
    """Store display data per player. Pipeline = one round trip for all entries."""
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


async def get_top_players(
    region: str,
    limit: int = 50,
    offset: int = 0
) -> list[dict]:
    """Get top N players by badge level. Returns account_name not account_id."""
    results = await redis_client.zrevrange(
        _key(region),
        offset,
        offset + limit - 1,
        withscores=True
    )

    return [
        {
            "rank":         offset + i + 1,
            "account_name": account_name,    # ← string, never cast to int
            "badge_level":  int(score),
        }
        for i, (account_name, score) in enumerate(results)
    ]


async def get_player_rank(region: str, account_name: str) -> int | None:
    """Get 1-indexed rank for a player. None if not on leaderboard."""
    rank = await redis_client.zrevrank(_key(region), account_name)
    return (rank + 1) if rank is not None else None


async def get_player_score(region: str, account_name: str) -> int | None:
    """Get badge level for a player."""
    score = await redis_client.zscore(_key(region), account_name)
    print("SCORE: ",score)
    return int(score) if score is not None else None


async def get_leaderboard_size(region: str) -> int:
    """Total players in a region's sorted set."""
    return await redis_client.zcard(_key(region))


async def get_enriched_leaderboard(
    region: str,
    limit: int = 50,
    offset: int = 0
) -> list[dict]:
    """
    Get ranked players with full display data.
    Step 1: sorted set → ordered account_names + scores
    Step 2: pipeline → fetch all metadata in one round trip
    Step 3: merge and return
    """
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