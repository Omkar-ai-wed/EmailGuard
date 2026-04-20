"""Emails Router — /api/v1/emails"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.email import EmailRecord
from schemas.email import EmailIngest, EmailStatusUpdate, EmailOut, EmailDetailOut, EmailListResponse
from services import classification_engine
from middleware.auth_middleware import get_current_user
from models.user import User

router = APIRouter()


@router.post("/ingest", response_model=EmailDetailOut, status_code=201)
def ingest_email(
    data: EmailIngest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ingest a new email — saves it, then runs the full classification pipeline.
    Classification happens in the background so the response is instant.
    """
    # Extract sender domain
    sender_domain = data.sender_email.split("@")[-1] if "@" in data.sender_email else "unknown"

    email = EmailRecord(
        message_id=str(uuid.uuid4()),
        sender_email=data.sender_email,
        sender_domain=sender_domain,
        recipient_email=data.recipient_email,
        subject=data.subject,
        body_text=data.body_text,
        body_html=data.body_html,
        received_at=data.received_at,
        ingested_by_user_id=current_user.id,
    )
    db.add(email)
    db.commit()
    db.refresh(email)

    # Run full classification pipeline immediately (for demo simplicity)
    classification_engine.run_classification_pipeline(
        db=db,
        email=email,
        extra_links=data.links,
        extra_attachments=data.attachments,
        user_id=current_user.id,
    )
    db.refresh(email)
    return email


@router.get("/", response_model=EmailListResponse)
def list_emails(
    category: Optional[str] = Query(None, description="wanted|unwanted|suspicious|phishing|pending"),
    status: Optional[str]   = Query(None, description="pending|classified|reviewed|blocked|safe"),
    sender_domain: Optional[str] = Query(None),
    min_risk: Optional[float]    = Query(None, ge=0, le=100),
    max_risk: Optional[float]    = Query(None, ge=0, le=100),
    search: Optional[str]        = Query(None, description="Search in subject/sender"),
    page: int                    = Query(1, ge=1),
    page_size: int               = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List emails with optional filtering and pagination."""
    q = db.query(EmailRecord)

    if category:
        q = q.filter(EmailRecord.category == category)
    if status:
        q = q.filter(EmailRecord.status == status)
    if sender_domain:
        q = q.filter(EmailRecord.sender_domain.ilike(f"%{sender_domain}%"))
    if min_risk is not None:
        q = q.filter(EmailRecord.risk_score >= min_risk)
    if max_risk is not None:
        q = q.filter(EmailRecord.risk_score <= max_risk)
    if search:
        q = q.filter(
            EmailRecord.subject.ilike(f"%{search}%") |
            EmailRecord.sender_email.ilike(f"%{search}%")
        )

    total = q.count()
    emails = q.order_by(EmailRecord.ingested_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return EmailListResponse(total=total, page=page, page_size=page_size, emails=emails)


@router.get("/search", response_model=EmailListResponse)
def search_emails(
    q: str = Query(..., min_length=2, description="Search term"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Full-text search across subject and sender email."""
    query = db.query(EmailRecord).filter(
        EmailRecord.subject.ilike(f"%{q}%") |
        EmailRecord.sender_email.ilike(f"%{q}%") |
        EmailRecord.body_text.ilike(f"%{q}%")
    )
    total = query.count()
    emails = query.order_by(EmailRecord.ingested_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return EmailListResponse(total=total, page=page, page_size=page_size, emails=emails)


@router.get("/{email_id}", response_model=EmailDetailOut)
def get_email(email_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get full details for a single email."""
    email = db.query(EmailRecord).filter(EmailRecord.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")
    return email


@router.patch("/{email_id}/status", response_model=EmailOut)
def update_email_status(
    email_id: int,
    data: EmailStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually update email status: safe | blocked | reported | reviewed."""
    allowed = {"safe", "blocked", "reported", "reviewed", "pending"}
    if data.status not in allowed:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {allowed}")

    email = db.query(EmailRecord).filter(EmailRecord.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")

    email.status = data.status
    db.commit()
    db.refresh(email)
    return email


@router.delete("/{email_id}", status_code=204)
def delete_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an email record (admin/analyst only)."""
    email = db.query(EmailRecord).filter(EmailRecord.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")
    db.delete(email)
    db.commit()
