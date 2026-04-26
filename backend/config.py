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
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # ── Database ─────────────────────────────────────────
    # Supabase (PostgreSQL) via psycopg2 driver.
    # Format: postgresql+psycopg2://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres
    # Get your connection string from: Supabase Dashboard → Settings → Database → Connection String → URI
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost:5432/emailguard")

    # ── JWT Auth ─────────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "emailguard-super-secret-key-2024-change-in-prod")
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
