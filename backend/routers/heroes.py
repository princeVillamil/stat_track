from fastapi import APIRouter, HTTPException
from schemas import HeroResponse
from database import SessionLocal
from models import Hero
from services.response_cache import cache_response

router = APIRouter(prefix="/api/v1/heroes", tags=["heroes"])


@router.get("/", response_model=list[HeroResponse])
@cache_response(ttl=3600, prefix="cache:heroes")   # 1 hour TTL
async def get_all_heroes():
    db = SessionLocal()
    try:
        heroes = db.query(Hero).order_by(Hero.name).all()
        return [
            HeroResponse(
                id=h.id, name=h.name, class_name=h.class_name,
                hero_type=h.hero_type, icon_url=h.icon_url
            )
            for h in heroes
        ]
    finally:
        db.close()


@router.get("/{hero_id}", response_model=HeroResponse)
@cache_response(ttl=3600, prefix="cache:heroes")
async def get_hero(hero_id: int):
    db = SessionLocal()
    try:
        hero = db.query(Hero).filter(Hero.id == hero_id).first()
        if not hero:
            raise HTTPException(status_code=404, detail=f"Hero {hero_id} not found")
        return HeroResponse(
            id=hero.id, name=hero.name, class_name=hero.class_name,
            hero_type=hero.hero_type, icon_url=hero.icon_url
        )
    finally:
        db.close()