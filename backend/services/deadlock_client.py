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
    follow_redirects=True
)

def steam64_to_account_id(steam64: int) -> int:
    return steam64 - 76561197960265728

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True
)
async def _get(endpoint: str, params: dict = None) -> dict:
    response = await _client.get(endpoint, params=params)
    response.raise_for_status()
    return response.json()

async def get_leaderboard(region: str = "NAmerica") -> dict | None:
    if region not in VALID_REGIONS:
        raise ValueError(f"Invalid region '{region}'.")
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

async def get_player_mmr_history(account_id: int) -> dict | None:
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
    key_ids = ",".join(str(i) for i in sorted(account_ids))
    cache_key = f"api:hero_stats:{key_ids[:100]}"
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
    cache_key = f"api:match_history:{account_id}"
    cached = await get_cached(cache_key)
    if cached:
        return cached
    try:
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