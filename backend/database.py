import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    os.getenv("DATABASE_URL"),
    pool_pre_ping=True,      # test connection before using it — handles dropped connections
    pool_size=5,             # keep 5 connections open in the pool
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    """Get a database session. Always use as a context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()