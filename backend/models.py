from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

def utcnow():
    """Single helper so you never write datetime.now(timezone.utc) inline."""
    return datetime.now(timezone.utc)


class Hero(Base):
    __tablename__ = "heroes"

    id         = Column(Integer, primary_key=True)
    name       = Column(String, nullable=False)
    class_name = Column(String, unique=True, nullable=False)
    hero_type  = Column(String)
    icon_url   = Column(String)


class Player(Base):
    __tablename__ = "players"

    account_name = Column(String, primary_key=True)
    account_id   = Column(BigInteger, nullable=True, unique=True)
    first_seen   = Column(DateTime(timezone=True), default=utcnow)
    last_seen    = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class LeaderboardSnapshot(Base):
    __tablename__ = "leaderboard_snapshots"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    account_name   = Column(String, ForeignKey("players.account_name"), index=True)
    region         = Column(String, nullable=False)
    rank           = Column(Integer)
    badge_level    = Column(Integer)
    ranked_rank    = Column(Integer)
    ranked_subrank = Column(Integer)
    top_hero_ids   = Column(String)
    snapshot_at    = Column(DateTime(timezone=True), default=utcnow, index=True)


class PlayerHeroStats(Base):
    __tablename__ = "player_hero_stats"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    account_name   = Column(String, ForeignKey("players.account_name"), index=True)
    hero_id        = Column(Integer, ForeignKey("heroes.id"), index=True)
    matches_played = Column(Integer, default=0)
    wins           = Column(Integer, default=0)
    kills          = Column(Integer, default=0)
    deaths         = Column(Integer, default=0)
    assists        = Column(Integer, default=0)
    last_updated   = Column(DateTime(timezone=True), default=utcnow)


class MmrHistory(Base):
    __tablename__ = "mmr_history"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    account_name = Column(String, ForeignKey("players.account_name"), index=True)
    mmr          = Column(Integer)
    recorded_at  = Column(DateTime(timezone=True), default=utcnow, index=True)