import json
import asyncio
import redis.asyncio as aioredis
import os
from services.connection_manager import manager

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# channel name — Celery publishes here, this listener subscribes
LEADERBOARD_CHANNEL = "leaderboard:updates"


async def listen_for_updates():
    """
    Long-running background task. Subscribes to Redis pub/sub channel
    and forwards messages to all connected WebSocket clients.

    This runs for the entire lifetime of the FastAPI server.
    """
    # separate Redis connection just for pub/sub
    # pub/sub connections can't be used for regular commands
    # so we create a dedicated one
    redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = redis.pubsub()

    await pubsub.subscribe(LEADERBOARD_CHANNEL)
    print(f"Subscribed to Redis channel: {LEADERBOARD_CHANNEL}")

    try:
        # this loop runs forever — each iteration waits for a message
        async for message in pubsub.listen():

            # pub/sub sends a "subscribe" confirmation message first
            # ignore it — only process actual data messages
            if message["type"] != "message":
                continue

            try:
                data = json.loads(message["data"])
                region = data.get("region")

                if region:
                    # forward the event to all clients watching this region
                    await manager.broadcast_to_region(region, data)
                    print(f"Broadcast to {region}: {data.get('event')}")

            except json.JSONDecodeError:
                print(f"Invalid JSON in pub/sub message: {message['data']}")

    except asyncio.CancelledError:
        # server is shutting down — clean up gracefully
        await pubsub.unsubscribe(LEADERBOARD_CHANNEL)
        await redis.aclose()
        print("Pub/sub listener shut down")