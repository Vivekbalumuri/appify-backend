from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

import os
# Robust Database Engine for High Concurrency (100k+ Users)
# Added pool_pre_ping to check for dropped connections (Network Unreachable fix)
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          
    max_overflow=20,       
    pool_timeout=30,       
    pool_recycle=1800,
    pool_pre_ping=True,    # 👈 Fixes dropped connections from Supabase
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
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