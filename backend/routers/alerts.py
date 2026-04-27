"""Alerts Router — /api/v1/alerts"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.alert import Alert
from models.email import EmailRecord
from schemas.classification import AlertOut
from middleware.auth_middleware import get_current_user
from models.user import User

router = APIRouter()


@router.get("/", response_model=List[AlertOut])
def list_alerts(
    severity: Optional[str] = Query(None, description="low|medium|high|critical"),
    resolved: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List security alerts with optional filters."""
    q = db.query(Alert).join(EmailRecord).filter(EmailRecord.ingested_by_user_id == current_user.id)
    if severity:
        q = q.filter(Alert.severity == severity)
    if resolved is not None:
        q = q.filter(Alert.is_resolved == resolved)
    return q.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single alert by ID."""
    alert = db.query(Alert).join(EmailRecord).filter(
        Alert.id == alert_id,
        EmailRecord.ingested_by_user_id == current_user.id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return alert


@router.patch("/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an alert as resolved."""
    alert = db.query(Alert).join(EmailRecord).filter(
        Alert.id == alert_id,
        EmailRecord.ingested_by_user_id == current_user.id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = current_user.id
    db.commit()
    db.refresh(alert)
    return alert
