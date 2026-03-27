import json
import hashlib
from functools import wraps
from services.cache import redis_client


def cache_response(ttl: int = 30, prefix: str = "cache"):
    """
    Decorator that caches the return value of an async route handler.

    Usage:
        @router.get("/{region}")
        @cache_response(ttl=30, prefix="leaderboard")
        async def get_leaderboard(region: str, limit: int = 50):
            ...

    Cache key: cache:{prefix}:{hash of all arguments}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # build a stable cache key from the function arguments
            # kwargs contains route params + query params
            key_data = f"{func.__name__}:{json.dumps(kwargs, sort_keys=True)}"
            key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]
            cache_key = f"{prefix}:{key_hash}"

            # check cache first
            cached = await redis_client.get(cache_key)
            if cached:
                # return raw JSON string — FastAPI accepts this via Response
                from fastapi.responses import JSONResponse
                import json as _json
                return JSONResponse(
                    content=_json.loads(cached),
                    headers={"X-Cache": "HIT"}
                )

            # cache miss — call the actual route handler
            result = await func(*args, **kwargs)

            # serialize and store
            # result is a Pydantic model — convert to dict first
            if hasattr(result, "model_dump"):
                serializable = result.model_dump()
            elif isinstance(result, dict):
                serializable = result
            else:
                serializable = result

            await redis_client.set(
                cache_key,
                json.dumps(serializable),
                ex=ttl
            )

            # attach cache miss header to response
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content=serializable,
                headers={"X-Cache": "MISS"}
            )

        # store cache key prefix on the function so invalidation can find it
        wrapper._cache_prefix = prefix
        return wrapper
    return decorator


async def invalidate_cache_prefix(prefix: str) -> int:
    """
    Delete all cache keys matching a prefix.
    Uses SCAN — never KEYS — to avoid blocking Redis.
    Returns count of deleted keys.
    """
    deleted = 0
    cursor = 0

    while True:
        cursor, keys = await redis_client.scan(
            cursor=cursor,
            match=f"{prefix}:*",
            count=100       # scan 100 keys per iteration
        )

        if keys:
            await redis_client.delete(*keys)
            deleted += len(keys)

        if cursor == 0:
            break           # scan complete — cursor returns to 0 when done

    return deleted