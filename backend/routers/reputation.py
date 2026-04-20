"""Reputation Router — /api/v1/reputation"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.classification import ReputationCreate, ReputationOut
from services import reputation_service
from middleware.auth_middleware import get_current_user
from models.user import User

router = APIRouter()


@router.get("/", response_model=List[ReputationOut])
def list_reputations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all sender reputation records."""
    return reputation_service.list_reputations(db, skip, limit)


@router.get("/{domain}", response_model=ReputationOut)
def lookup_domain(
    domain: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Look up (or auto-create) a domain's reputation record."""
    return reputation_service.get_or_create_reputation(db, domain)


@router.post("/", response_model=ReputationOut, status_code=201)
def add_or_update_reputation(
    data: ReputationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually add or update a sender reputation record."""
    return reputation_service.upsert_reputation(
        db, data.sender_domain, data.reputation_score, data.category, data.notes
    )


@router.post("/blacklist/{domain}", response_model=ReputationOut)
def blacklist_domain(
    domain: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Blacklist a sender domain (sets score to 0, category to blocked)."""
    return reputation_service.blacklist_domain(db, domain)
