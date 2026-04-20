"""Analytics Router — /api/v1/analytics"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from services import analytics_service, keyword_service
from schemas.classification import MetricOut
from middleware.auth_middleware import get_current_user
from models.user import User

router = APIRouter()


@router.get("/overview")
def dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Summary stats for the main dashboard: totals, accuracy, FP/FN rates."""
    return analytics_service.get_overview_stats(db)


@router.get("/trend")
def spam_trend(
    days: int = Query(7, ge=1, le=30, description="Number of days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Daily spam vs wanted email counts for the last N days."""
    return analytics_service.get_spam_trend(db, days)


@router.get("/risk-distribution")
def risk_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Count of emails in each risk bucket: low / medium / high / critical."""
    return analytics_service.get_risk_distribution(db)


@router.get("/top-keywords")
def top_keywords(
    limit: int = Query(15, ge=5, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Top spam keywords by hit frequency."""
    return keyword_service.get_keyword_frequency(db, limit)


@router.get("/performance", response_model=List[MetricOut])
def model_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """ML model performance metrics history."""
    return analytics_service.get_all_metrics(db)
