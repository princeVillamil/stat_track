from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import leaderboard, players, heroes

app = FastAPI(
    title="Deadlock Leaderboard API",
    version="1.0.0",
    description="Real-time Deadlock leaderboard and player stats"
)

# CORS — allows your React frontend to call this API
# in production you'll replace "*" with your Vercel URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# register routers
app.include_router(leaderboard.router)
app.include_router(players.router)
app.include_router(heroes.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}



# from fastapi import FastAPI
# from services.deadlock_client import (
#     get_leaderboard,
#     get_player_mmr_history,
#     steam64_to_account_id
# )
# from services.leaderboard import (
#     get_enriched_leaderboard,
#     get_player_rank,
#     get_leaderboard_size
# )


# app = FastAPI(title="Deadlock Leaderboard", version="1.0.0")

# # test leaderboard
# @app.get("/test/leaderboard/{region}")
# async def test_leaderboard(region: str):
#     data = await get_leaderboard(region)
#     if not data:
#         return {"error": "not found"}
#     # return just first 3 entries so output is readable
#     return {"entries": data.get("entries", [])[:3]}

# # test mmr history — accepts steam64, converts automatically
# @app.get("/test/player/{steam64}/mmr")
# async def test_mmr(steam64: int):
#     account_id = steam64_to_account_id(steam64)
#     data = await get_player_mmr_history(account_id)
#     if not data:
#         return {"error": "not found"}
#     return data



# @app.get("/test/redis/leaderboard/{region}")
# async def test_redis_leaderboard(region: str, limit: int = 10):
#     entries = await get_enriched_leaderboard(region, limit=limit)
#     size = await get_leaderboard_size(region)
#     return {
#         "region":  region,
#         "total":   size,
#         "entries": entries
#     }

# @app.get("/test/redis/rank/{region}/{account_name}")
# async def test_redis_rank(region: str, account_name: str):
#     rank = await get_player_rank(region, account_name)
#     return {
#         "account_name": account_name,
#         "region":       region,
#         "rank":         rank
#     }