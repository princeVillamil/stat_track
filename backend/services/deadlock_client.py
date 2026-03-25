# deadlock_client.py
import os
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from services.cache import get_cached, set_cached

BASE_URL = "https://api.deadlock-api.com"

VALID_REGIONS = ["NAmerica", "Europe", "Asia", "SAmerica", "Oceania"]

_client = httpx.AsyncClient(
    base_url=BASE_URL,
    timeout=10.0,
    headers={"User-Agent": "deadlock-leaderboard/1.0"},
    follow_redirects=True    # important — the API uses redirects
)

def steam64_to_account_id(steam64: int) -> int:
    """Convert SteamID64 to the account_id format the API expects."""
    return steam64 - 76561197960265728


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True
)
async def _get(endpoint: str, params: dict = None) -> dict:
    """Raw HTTP GET with retry. Private."""
    response = await _client.get(endpoint, params=params)
    response.raise_for_status()
    return response.json()


async def get_leaderboard(region: str = "NAmerica") -> dict | None:
    """
    Fetch leaderboard for a region.
    Regions: NAmerica, Europe, Asia, SAmerica, Oceania
    TTL: 5 minutes
    """
    if region not in VALID_REGIONS:
        raise ValueError(f"Invalid region '{region}'. Must be one of {VALID_REGIONS}")

    cache_key = f"api:leaderboard:{region}"

    cached = await get_cached(cache_key)
    if cached:
        return cached

    try:
        data = await _get(f"/v1/leaderboard/{region}")
        await set_cached(cache_key, data, ttl=300)
        return data
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def get_hero_leaderboard(region: str, hero_id: int) -> dict | None:
    """
    Fetch leaderboard for a specific hero in a region.
    TTL: 5 minutes
    """
    cache_key = f"api:leaderboard:{region}:hero:{hero_id}"

    cached = await get_cached(cache_key)
    if cached:
        return cached

    try:
        data = await _get(f"/v1/leaderboard/{region}/{hero_id}")
        await set_cached(cache_key, data, ttl=300)
        return data
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def get_player_mmr_history(account_id: int) -> dict | None:
    """
    Fetch MMR progression over time for a player.
    account_id must be SteamID3 — use steam64_to_account_id() to convert.
    TTL: 10 minutes
    """
    cache_key = f"api:mmr_history:{account_id}"

    cached = await get_cached(cache_key)
    if cached:
        return cached

    try:
        data = await _get(f"/v1/players/{account_id}/mmr-history")
        await set_cached(cache_key, data, ttl=600)
        return data
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def get_player_hero_stats(account_ids: list[int]) -> dict | None:
    """
    Fetch per-hero stats for up to 1000 players at once.
    account_ids must be SteamID3 format.
    TTL: 10 minutes
    """
    # sort so same set of ids always produces same cache key
    key_ids = ",".join(str(i) for i in sorted(account_ids))
    cache_key = f"api:hero_stats:{key_ids[:100]}"  # truncate key if many ids

    cached = await get_cached(cache_key)
    if cached:
        return cached

    try:
        data = await _get("/v1/players/hero-stats", params={"account_ids": account_ids})
        await set_cached(cache_key, data, ttl=600)
        return data
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def get_player_match_history(account_id: int) -> dict | None:
    """
    Fetch match history for a player.
    IMPORTANT: always use only_stored_history=true
    Without it: 3 requests/hour limit — will break fast
    With it: 100 req/s — safe to call normally
    TTL: 5 minutes
    """
    cache_key = f"api:match_history:{account_id}"

    cached = await get_cached(cache_key)
    if cached:
        return cached

    try:
        # only_stored_history=true is CRITICAL — without it you hit a 3 req/hour wall
        data = await _get(
            f"/v1/players/{account_id}/match-history",
            params={"only_stored_history": "true"}
        )
        await set_cached(cache_key, data, ttl=300)
        return data
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise