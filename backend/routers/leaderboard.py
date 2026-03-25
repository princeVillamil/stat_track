from fastapi import APIRouter, HTTPException, Query
from schemas import LeaderboardResponse, LeaderboardEntry, PlayerRankResponse
from services.leaderboard import (
    get_enriched_leaderboard,
    get_player_rank,
    get_leaderboard_size,
    get_player_score,
)

router = APIRouter(prefix="/api/v1/leaderboard", tags=["leaderboard"])

VALID_REGIONS = ["NAmerica", "Europe", "Asia", "SAmerica", "Oceania"]


def validate_region(region: str) -> str:
    """Raise 404 if region string is not valid."""
    if region not in VALID_REGIONS:
        raise HTTPException(
            status_code=404,
            detail=f"Region '{region}' not found. Valid regions: {VALID_REGIONS}"
        )
    return region

@router.get("/health}")
async def health():
    return {"status": "ok", "version": "1.0.0"}
    
@router.get("/{region}", response_model=LeaderboardResponse)
async def get_leaderboard(
    region: str,
    limit:  int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0,  ge=0, le=10000),
):
    """
    Get the leaderboard for a region.

    - **region**: NAmerica | Europe | Asia | SAmerica | Oceania
    - **limit**: number of players to return (1-100, default 50)
    - **offset**: pagination offset (default 0)
    """
    validate_region(region)

    entries = await get_enriched_leaderboard(region, limit=limit, offset=offset)
    total   = await get_leaderboard_size(region)

    if not entries and total == 0:
        raise HTTPException(
            status_code=503,
            detail="Leaderboard data not yet available. Check back in a few minutes."
        )

    return LeaderboardResponse(
        region=region,
        total=total,
        limit=limit,
        offset=offset,
        entries=[
            LeaderboardEntry(
                rank=e["rank"],
                account_name=e["account_name"],
                badge_level=e["badge_level"],
                ranked_rank=e.get("ranked_rank"),
                ranked_subrank=e.get("ranked_subrank"),
                top_hero_ids=e.get("top_hero_ids", []),
            )
            for e in entries
        ]
    )


@router.get("/{region}/player/{account_name}", response_model=PlayerRankResponse)
async def get_player_leaderboard_rank(region: str, account_name: str):
    """
    Get a specific player's rank in a region.
    Returns rank=null if the player is not on the leaderboard.
    """
    validate_region(region)

    rank        = await get_player_rank(region, account_name)
    badge_level = await get_player_score(region, account_name)
    print("Rank",rank)
    print("Rank",badge_level)

    return PlayerRankResponse(
        account_name=account_name,
        region=region,
        rank=rank,
        badge_level=badge_level,
    )