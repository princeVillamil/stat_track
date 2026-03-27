import os
import json
import redis.asyncio as redis

redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://redis:6379/0"),
    decode_responses=True
)

async def get_cached(key: str) -> dict | None:
    value = await redis_client.get(key)
    if value:
        return json.loads(value)
    return None

async def set_cached(key: str, data: dict, ttl: int = 300) -> None:
    await redis_client.set(key, json.dumps(data), ex=ttl)