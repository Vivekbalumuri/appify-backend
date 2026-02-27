from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

# Robust Database Engine for High Concurrency (100k+ Users)
engine = create_engine(
    DATABASE_URL,
    pool_size=50,          # Keep 50 connections open at all times
    max_overflow=50,       # Allow an extra 50 connections if traffic spikes
    pool_timeout=45,       # Seconds to wait for an available connection before failing
    pool_recycle=1800      # Reconnect after 30 minutes to drop stale connections
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()