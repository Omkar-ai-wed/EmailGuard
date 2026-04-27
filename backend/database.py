"""
EmailGuard — Database Setup
SQLAlchemy engine, session factory, and Base class.
Connects to Supabase (PostgreSQL) via pg8000 driver.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# PostgreSQL engine — pool_pre_ping detects dropped connections,
# pool_recycle helps with Supabase's connection pooler (pgBouncer).

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,    # Checks connection health before using it
    pool_recycle=300,      # Closes connections older than 5 minutes to prevent staling
    pool_size=5,           # Reasonable default for small apps
    max_overflow=10,       # Allows temporary bursts
    echo=False,  # Never echo SQL in production; use application-level logging instead
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All ORM models inherit from this Base
Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session with proper rollback on error."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
