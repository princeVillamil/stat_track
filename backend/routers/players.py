from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal
from models import Player, LeaderboardSnapshot
from services.leaderboard import get_player_rank, get_player_score

router = APIRouter(prefix="/api/v1/players", tags=["players"])

class PlayerProfileResponse(BaseModel):
    account_name: str
    account_id:   Optional[int]
    ranks:        dict
    first_seen:   Optional[str]

@router.get("/{account_name}", response_model=PlayerProfileResponse)
async def get_player(account_name: str):
    db = SessionLocal()
    try:
        player = db.query(Player).filter(Player.account_name == account_name).first()
        if not player:
            raise HTTPException(status_code=404, detail=f"Player '{account_name}' not found.")

        regions = ["NAmerica", "Europe", "Asia", "SAmerica", "Oceania"]
        ranks = {}
        for region in regions:
            rank        = await get_player_rank(region, account_name)
            badge_level = await get_player_score(region, account_name)
            if rank is not None:
                ranks[region] = {"rank": rank, "badge_level": badge_level}

        return PlayerProfileResponse(
            account_name=player.account_name,
            account_id=player.account_id,
            ranks=ranks,
            first_seen=player.first_seen.isoformat() if player.first_seen else None,
        )
    finally:
        db.close()

@router.get("/{account_name}/history")
async def get_player_rank_history(account_name: str, region: str = "NAmerica"):
    db = SessionLocal()
    try:
        snapshots = db.query(LeaderboardSnapshot)\
            .filter(
                LeaderboardSnapshot.account_name == account_name,
                LeaderboardSnapshot.region == region
            )\
            .order_by(LeaderboardSnapshot.snapshot_at.asc())\
            .all()

        if not snapshots:
            raise HTTPException(status_code=404, detail=f"No history found for '{account_name}'")

        return {
            "account_name": account_name,
            "region": region,
            "history": [
                {
                    "rank":        s.rank,
                    "badge_level": s.badge_level,
                    "snapshot_at": s.snapshot_at.isoformat(),
                }
                for s in snapshots
            ]
        }
    finally:
        db.close()