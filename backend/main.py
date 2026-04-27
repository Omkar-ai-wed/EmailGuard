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

import os
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from limiter_config import limiter

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

class RequestIDFilter(logging.Filter):
    """Ensures request_id is always present in the log record to avoid KeyErrors."""
    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "System"
        return True

# Configure logging
handler = logging.StreamHandler()
handler.addFilter(RequestIDFilter())
handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | [%(request_id)s] %(name)s — %(message)s"))

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    handlers=[handler]
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
    logger.info("ML classifier ready")

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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Resource not found."})

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        import logging
        # Inject request_id into log context for this request
        logger_extra = logging.LoggerAdapter(
            logging.getLogger("emailguard.request"),
            {"request_id": request_id}
        )
        logger_extra.info("%s %s", request.method, request.url.path)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger_extra.info("%s %s → %d", request.method, request.url.path, response.status_code)
        return response

app.add_middleware(RequestIDMiddleware)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Open CORS so the local HTML dashboard files can call the API directly
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
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
    """Deep health check — verifies DB connectivity."""
    from database import SessionLocal
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error("Health check DB failure: %s", e)
        db_status = "unhealthy"
    finally:
        db.close()

    overall = "healthy" if db_status == "healthy" else "degraded"
    status_code = 200 if overall == "healthy" else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall,
            "database": db_status,
            "version": settings.APP_VERSION,
        },
    )
