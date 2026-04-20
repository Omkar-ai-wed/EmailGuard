"""Classification Router — /api/v1/classify"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.email import EmailRecord
from models.classification import Classification
from schemas.classification import ClassificationResult
from services import classification_engine
from middleware.auth_middleware import get_current_user
from models.user import User

router = APIRouter()


@router.post("/{email_id}", response_model=ClassificationResult)
def classify_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger (or re-run) classification for an existing email.
    Returns the classification result.
    """
    email = db.query(EmailRecord).filter(EmailRecord.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")

    clf = classification_engine.run_classification_pipeline(db, email, user_id=current_user.id)
    db.refresh(email)

    return ClassificationResult(
        email_id=email.id,
        predicted_category=clf.predicted_category,
        confidence_score=clf.confidence_score,
        risk_score=email.risk_score,
        method=clf.method,
        rule_triggered=clf.rule_triggered,
        keyword_score=clf.keyword_score,
        reputation_score=clf.reputation_score,
        ml_score=clf.ml_score,
        is_phishing=email.is_phishing,
        classified_at=clf.classified_at,
    )


@router.get("/{email_id}", response_model=ClassificationResult)
def get_classification(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the most recent classification result for an email."""
    email = db.query(EmailRecord).filter(EmailRecord.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")

    clf = (
        db.query(Classification)
        .filter(Classification.email_id == email_id)
        .order_by(Classification.classified_at.desc())
        .first()
    )
    if not clf:
        raise HTTPException(status_code=404, detail="No classification found for this email. Run POST /classify/{id} first.")

    return ClassificationResult(
        email_id=email.id,
        predicted_category=clf.predicted_category,
        confidence_score=clf.confidence_score,
        risk_score=email.risk_score,
        method=clf.method,
        rule_triggered=clf.rule_triggered,
        keyword_score=clf.keyword_score,
        reputation_score=clf.reputation_score,
        ml_score=clf.ml_score,
        is_phishing=email.is_phishing,
        classified_at=clf.classified_at,
    )


@router.get("/history/all")
def classification_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return recent classification history log."""
    records = (
        db.query(Classification)
        .order_by(Classification.classified_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": c.id,
            "email_id": c.email_id,
            "method": c.method,
            "predicted_category": c.predicted_category,
            "confidence_score": c.confidence_score,
            "keyword_score": c.keyword_score,
            "ml_score": c.ml_score,
            "classified_at": c.classified_at,
        }
        for c in records
    ]
