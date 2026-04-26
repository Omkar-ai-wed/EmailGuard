"""
EmailGuard — FastAPI Application Entry Point
============================================
Run with:  python run.py
  or:      uvicorn main:app --reload --port 8000

Swagger UI: http://localhost:8000/docs
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import Base + all models so SQLAlchemy creates all tables on startup
from database import engine, Base
import models  # noqa: F401 — triggers all model imports

from routers import auth, emails, classification, keywords, reputation, scanning, alerts, analytics
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables + warm up ML model."""
    logger.info("Starting EmailGuard API…")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready (Supabase / PostgreSQL)")

    # Pre-load and train the ML classifier so first request is fast
    from services.ml_model import get_classifier
    clf = get_classifier()
    logger.info("ML classifier ready (vocab size: %d)", len(clf.vocab))

    yield  # ← app is running here

    logger.info("EmailGuard API shutting down.")


# ── App definition ────────────────────────────────────────────────────────────
app = FastAPI(
    lifespan=lifespan,
    title="EmailGuard API",
    description=(
        "## Unwanted / Irrelevant Email Detection System\n\n"
        "A REST API for classifying emails as **Wanted**, **Unwanted**, **Suspicious**, or **Phishing**.\n\n"
        "### Quick Start\n"
        "1. `POST /api/v1/auth/register` — create an account\n"
        "2. `POST /api/v1/auth/login` — get your JWT token\n"
        "3. Click **Authorize** above and paste the token\n"
        "4. `POST /api/v1/emails/ingest` — submit an email for analysis\n"
        "5. `GET /api/v1/analytics/overview` — view dashboard stats\n"
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Authentication",    "description": "Register, login, and manage user sessions"},
        {"name": "Emails",            "description": "Ingest, filter, search, and manage emails"},
        {"name": "Classification",    "description": "Run and retrieve email classification results"},
        {"name": "Keywords",          "description": "Manage spam keyword rules"},
        {"name": "Sender Reputation", "description": "Domain trust scoring and blacklisting"},
        {"name": "Scanning",          "description": "Link and attachment security scanning"},
        {"name": "Alerts",            "description": "View and resolve security alerts"},
        {"name": "Analytics",         "description": "Dashboard metrics, trends, and model performance"},
    ],
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Open CORS so the local HTML dashboard files can call the API directly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router,           prefix="/api/v1/auth",       tags=["Authentication"])
app.include_router(emails.router,         prefix="/api/v1/emails",     tags=["Emails"])
app.include_router(classification.router, prefix="/api/v1/classify",   tags=["Classification"])
app.include_router(keywords.router,       prefix="/api/v1/keywords",   tags=["Keywords"])
app.include_router(reputation.router,     prefix="/api/v1/reputation", tags=["Sender Reputation"])
app.include_router(scanning.router,       prefix="/api/v1/scan",       tags=["Scanning"])
app.include_router(alerts.router,         prefix="/api/v1/alerts",     tags=["Alerts"])
app.include_router(analytics.router,      prefix="/api/v1/analytics",  tags=["Analytics"])


# ── Health endpoints ──────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "service": "EmailGuard API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
