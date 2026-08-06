# ================================================================
#  VIBEZ PROTOCOL — app/database.py
#  Database connection — SQLite locally, PostgreSQL on deploy
# ================================================================

import os
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vibezprotocol.db")

# Render/Heroku hand out "postgres://" URLs, which SQLAlchemy 2.x rejects.
# Normalise to the scheme it expects so the pasted URL just works.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

IS_SQLITE = DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    engine_kwargs = {"connect_args": {"check_same_thread": False}}
else:
    # Hosted Postgres drops idle connections (free tiers sleep, proxies time out).
    # pool_pre_ping discards dead connections instead of raising on first query;
    # pool_recycle retires them before the provider does.
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 5,
    }

engine       = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()


def init_db(retries: int = 4, delay: float = 2.0):
    """
    Creates all tables on startup if they don't exist.

    Retries first: a hosted database can be briefly unreachable at boot (DNS
    hiccup, provider waking from idle). Without this the exception propagates
    out of the startup lifespan and the process exits — which on a deploy means
    a failed release rather than an app that recovers a few seconds later.
    """
    from app import models  # noqa: F401

    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            # Loud enough to catch "still on SQLite in production" during a deploy.
            print(f"🗄️  Database: {'SQLite (local file)' if IS_SQLITE else 'PostgreSQL — ' + engine.url.host}")
            return
        except OperationalError as exc:
            reason = str(exc.orig).strip().splitlines()[0] if exc.orig else exc
            if attempt == retries:
                print(f"❌ Database unreachable after {retries} attempts: {reason}")
                print("   Starting anyway — the health check will respond and "
                      "connections retry per request. Data endpoints will fail until it returns.")
                return
            print(f"⚠️  Database unreachable (attempt {attempt}/{retries}): {reason}")
            print(f"   Retrying in {delay:.0f}s...")
            time.sleep(delay)
            delay *= 2


def get_db():
    """Yields a DB session per request, always closes after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
