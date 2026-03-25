from fastapi import APIRouter, HTTPException
from schemas import HeroResponse
from database import SessionLocal
from models import Hero

router = APIRouter(prefix="/api/v1/heroes", tags=["heroes"])


@router.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

@router.get("/", response_model=list[HeroResponse])
async def get_all_heroes():
    """
    Get all playable heroes.
    This data changes rarely — cache it aggressively on the frontend.
    """
    db = SessionLocal()
    try:
        heroes = db.query(Hero).order_by(Hero.name).all()
        return [
            HeroResponse(
                id=h.id,
                name=h.name,
                class_name=h.class_name,
                hero_type=h.hero_type,
                icon_url=h.icon_url,
            )
            for h in heroes
        ]
    finally:
        db.close()


@router.get("/{hero_id}", response_model=HeroResponse)
async def get_hero(hero_id: int):
    """Get a single hero by ID."""
    db = SessionLocal()
    try:
        hero = db.query(Hero).filter(Hero.id == hero_id).first()
        if not hero:
            raise HTTPException(status_code=404, detail=f"Hero {hero_id} not found")
        return HeroResponse(
            id=hero.id,
            name=hero.name,
            class_name=hero.class_name,
            hero_type=hero.hero_type,
            icon_url=hero.icon_url,
        )
    finally:
        db.close()