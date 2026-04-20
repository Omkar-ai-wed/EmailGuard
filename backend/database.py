"""
EmailGuard — Database Setup
SQLAlchemy engine, session factory, and Base class.
Using SQLite for ease of setup (no installation required).
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# SQLite needs check_same_thread=False for FastAPI's async nature
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG,  # Logs all SQL queries in debug mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All ORM models inherit from this Base
Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session, always closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
