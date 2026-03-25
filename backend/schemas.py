from pydantic import BaseModel, field_validator
from typing import Optional


class LeaderboardEntry(BaseModel):
    """One player's entry on the leaderboard."""
    rank:           int
    account_name:   str
    badge_level:    int
    ranked_rank:    Optional[int]   = None
    ranked_subrank: Optional[int]   = None
    top_hero_ids:   list[int]       = []


class LeaderboardResponse(BaseModel):
    """Full leaderboard response with pagination info."""
    region:   str
    total:    int
    limit:    int
    offset:   int
    entries:  list[LeaderboardEntry]


class PlayerRankResponse(BaseModel):
    """A player's rank in a specific region."""
    account_name: str
    region:       str
    rank:         Optional[int]   # None if player not on leaderboard
    badge_level:  Optional[int]


class HeroResponse(BaseModel):
    """A single hero."""
    id:         int
    name:       str
    class_name: str
    hero_type:  Optional[str]
    icon_url:   Optional[str]


class HealthResponse(BaseModel):
    """Health check response."""
    status:  str
    version: str