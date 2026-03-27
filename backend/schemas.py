from pydantic import BaseModel
from typing import Optional


class LeaderboardEntry(BaseModel):
    rank:           int
    account_name:   str
    badge_level:    int
    ranked_rank:    Optional[int]  = None
    ranked_subrank: Optional[int]  = None
    top_hero_ids:   list[int]      = []


class LeaderboardResponse(BaseModel):
    region:  str
    total:   int
    limit:   int
    offset:  int
    entries: list[LeaderboardEntry]


class PlayerRankResponse(BaseModel):
    account_name: str
    region:       str
    rank:         Optional[int]
    badge_level:  Optional[int]


class HeroResponse(BaseModel):
    id:         int
    name:       str
    class_name: str
    hero_type:  Optional[str]
    icon_url:   Optional[str]


class HealthResponse(BaseModel):
    status:  str
    version: str