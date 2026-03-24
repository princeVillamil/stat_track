import os
import json
import redis.asyncio as redis

# create one shared connection pool — not a new connection per request
redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://redis:6379/0"),
    decode_responses=True      # return strings instead of bytes
)

async def get_cached(key: str) -> dict | None:
    """Return cached value if it exists, None if not."""
    value = await redis_client.get(key)
    if value:
        return json.loads(value)
    return None

async def set_cached(key: str, data: dict, ttl: int = 300) -> None:
    """Store value in Redis with expiry. Default 5 minutes."""
    await redis_client.set(key, json.dumps(data), ex=ttl)