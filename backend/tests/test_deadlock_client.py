import pytest
import httpx
import pytest_asyncio
from unittest.mock import AsyncMock, patch

# you'll need to add pytest-asyncio to requirements.txt
# pip install pytest-asyncio

@pytest.mark.asyncio
async def test_get_player_cache_miss_then_hit():
    """First call hits API, second call returns from cache."""
    fake_player = {"account_id": 12345, "name": "TestPlayer"}

    with patch("services.deadlock_client._get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = fake_player

        from services.deadlock_client import get_player
        from services.cache import redis_client

        # clear cache first
        await redis_client.delete("api:player:12345")

        # first call — should hit API
        result1 = await get_player(12345)
        assert result1 == fake_player
        assert mock_get.call_count == 1

        # second call — should return from cache, not call API again
        result2 = await get_player(12345)
        assert result2 == fake_player
        assert mock_get.call_count == 1   # still 1 — no new API call

@pytest.mark.asyncio
async def test_get_player_returns_none_on_404():
    """404 from API returns None, does not raise."""
    mock_response = httpx.Response(404)

    # mock both the HTTP call AND the cache layer
    # this test is about 404 handling, not Redis
    with patch("services.deadlock_client._get", new_callable=AsyncMock) as mock_get, \
        patch("services.deadlock_client.get_cached", new_callable=AsyncMock) as mock_cache:

        mock_cache.return_value = None   # simulate cache miss
        mock_get.side_effect = httpx.HTTPStatusError(
            "not found", request=httpx.Request("GET", "http://test"), response=mock_response
        )

        from services.deadlock_client import get_player
        result = await get_player(99999999)
        assert result is None