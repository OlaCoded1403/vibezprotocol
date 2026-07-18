# ================================================================
#  VIBEZ PROTOCOL — app/database.py
#  Database connection — SQLite locally, PostgreSQL on deploy
# ================================================================

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vibezprotocol.db")

# SQLite needs check_same_thread=False; PostgreSQL does not need it
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine       = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()


def init_db():
    """Creates all tables on startup if they don't exist."""
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yields a DB session per request, always closes after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
