from fastapi import FastAPI
from services.deadlock_client import (
    get_leaderboard,
    get_player_mmr_history,
    steam64_to_account_id
)
app = FastAPI(title="Deadlock Leaderboard", version="1.0.0")

# test leaderboard
@app.get("/test/leaderboard/{region}")
async def test_leaderboard(region: str):
    data = await get_leaderboard(region)
    if not data:
        return {"error": "not found"}
    # return just first 3 entries so output is readable
    return {"entries": data.get("entries", [])[:3]}

# test mmr history — accepts steam64, converts automatically
@app.get("/test/player/{steam64}/mmr")
async def test_mmr(steam64: int):
    account_id = steam64_to_account_id(steam64)
    data = await get_player_mmr_history(account_id)
    if not data:
        return {"error": "not found"}
    return data