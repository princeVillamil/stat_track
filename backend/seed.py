import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Hero
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def seed_heroes():
    response = httpx.get("https://assets.deadlock-api.com/v2/heroes")
    heroes = response.json()

    # only seed heroes that are actually selectable
    selectable = [h for h in heroes if h.get("player_selectable")]

    with Session(engine) as session:
        for hero in selectable:
            existing = session.get(Hero, hero["id"])
            if not existing:
                session.add(Hero(
                    id=hero["id"],
                    name=hero["name"],
                    class_name=hero["class_name"],
                    hero_type=hero.get("hero_type"),
                    icon_url=hero.get("images", {}).get("icon_hero_card")
                ))
        session.commit()
        print(f"Seeded {len(selectable)} heroes")
if __name__ == "__main__":
    seed_heroes()