"""
EmailGuard — Database Setup
SQLAlchemy engine, session factory, and Base class.
Connects to Supabase (PostgreSQL) via psycopg2 driver.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# PostgreSQL engine — pool_pre_ping detects dropped connections,
# pool_recycle helps with Supabase's connection pooler (pgBouncer).

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,       # Supabase pgBouncer drops idle conns after ~5 min
    pool_size=5,
    max_overflow=10,
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
