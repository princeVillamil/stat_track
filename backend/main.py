from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import leaderboard, players, heroes, websocket
from services.pubsub_listener import listen_for_updates
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on startup and shutdown.
    asynccontextmanager splits it: code before yield = startup, after = shutdown.
    """
    # startup — launch the pub/sub listener as a background task
    task = asyncio.create_task(listen_for_updates())
    print("Pub/sub listener started")

    yield  # server is running — handle requests

    # shutdown — cancel the background task cleanly
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    print("Pub/sub listener stopped")


app = FastAPI(
    title="Deadlock Leaderboard API",
    version="1.0.0",
    description="Real-time Deadlock leaderboard and player stats",
    lifespan=lifespan    # register the lifespan handler
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(leaderboard.router)
app.include_router(players.router)
app.include_router(heroes.router)
app.include_router(websocket.router)

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}