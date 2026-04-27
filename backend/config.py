"""
EmailGuard — Application Configuration
Loads settings from environment variables or .env file.
Database: Supabase (PostgreSQL) via psycopg2 driver.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "EmailGuard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ── Database ─────────────────────────────────────────
    # Supabase (PostgreSQL) via pg8000 driver (pure Python, no compiler needed).
    # Format: postgresql+pg8000://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres
    # Get your connection string from: Supabase Dashboard → Settings → Database → Connection String → URI
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+pg8000://postgres:password@localhost:5432/emailguard")

    # ── JWT Auth ─────────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ── CORS ─────────────────────────────────────────────
    # Allow all origins so the local HTML dashboard files work
    ALLOWED_ORIGINS: list = ["*"]

    # ── Risk Score Thresholds ────────────────────────────
    RISK_LOW_THRESHOLD: float = 30.0      # below this → Wanted
    RISK_MEDIUM_THRESHOLD: float = 60.0   # 30–60 → Suspicious
    # above 60 → Unwanted/Spam; above 80 → Phishing


settings = Settings()

import sys

def _validate_settings(s: "Settings") -> None:
    if not s.SECRET_KEY:
        print("FATAL: SECRET_KEY environment variable is not set. Refusing to start.", file=sys.stderr)
        sys.exit(1)
    if len(s.SECRET_KEY) < 32:
        print("FATAL: SECRET_KEY must be at least 32 characters.", file=sys.stderr)
        sys.exit(1)
    if not s.DEBUG and s.DATABASE_URL.startswith("sqlite"):
        print("WARNING: Using SQLite in non-debug mode. Set DATABASE_URL to PostgreSQL.", file=sys.stderr)

_validate_settings(settings)
