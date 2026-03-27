from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.connection_manager import manager
from services.leaderboard import get_enriched_leaderboard, get_leaderboard_size

router = APIRouter(tags=["websocket"])

VALID_REGIONS = ["NAmerica", "Europe", "Asia", "SAmerica", "Oceania"]


@router.websocket("/ws/leaderboard/{region}")
async def websocket_leaderboard(websocket: WebSocket, region: str):
    """
    WebSocket endpoint for live leaderboard updates.

    Connection lifecycle:
    1. Client connects
    2. Server sends current top 20 as initial snapshot
    3. Server pushes rank change events as they happen
    4. Client disconnects (or network drops)
    5. Server cleans up the connection

    Why top 20 snapshot on connect? Without it the client shows
    nothing until the next Celery run. The snapshot gives immediate
    useful data while waiting for the first live update.
    """
    if region not in VALID_REGIONS:
        await websocket.close(code=4004, reason=f"Invalid region: {region}")
        return

    # register connection
    await manager.connect(websocket, region)

    try:
        # send current leaderboard as initial snapshot
        entries = await get_enriched_leaderboard(region, limit=20)
        total   = await get_leaderboard_size(region)

        await websocket.send_json({
            "event":   "snapshot",
            "region":  region,
            "total":   total,
            "entries": entries
        })

        # keep connection alive — wait for client messages or disconnect
        # send periodic pings so the connection doesn't time out
        while True:
            try:
                # wait up to 30s for a message from client
                # if nothing arrives, send a ping to keep connection alive
                await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                # no message in 30s — send ping
                await websocket.send_json({"event": "ping"})

    except WebSocketDisconnect:
        # client disconnected cleanly
        manager.disconnect(websocket, region)

    except Exception as e:
        # unexpected error — clean up anyway
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, region)


# need asyncio in this file
import asyncio