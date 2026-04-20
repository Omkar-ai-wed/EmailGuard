"""Keywords Router — /api/v1/keywords"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.classification import KeywordCreate, KeywordUpdate, KeywordOut
from services import keyword_service
from middleware.auth_middleware import get_current_user
from models.user import User

router = APIRouter()


@router.get("/", response_model=List[KeywordOut])
def list_keywords(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all keyword rules."""
    return keyword_service.get_all_keywords(db, active_only=active_only)


@router.post("/", response_model=KeywordOut, status_code=201)
def add_keyword(
    data: KeywordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new spam keyword rule."""
    return keyword_service.create_keyword(db, data.keyword, data.weight, data.category_tag)


@router.put("/{kw_id}", response_model=KeywordOut)
def update_keyword(
    kw_id: int,
    data: KeywordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update weight, category, or active status of a keyword."""
    kw = keyword_service.update_keyword(db, kw_id, **data.model_dump(exclude_none=True))
    if not kw:
        raise HTTPException(status_code=404, detail="Keyword not found.")
    return kw


@router.delete("/{kw_id}", status_code=204)
def delete_keyword(
    kw_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a keyword rule."""
    if not keyword_service.delete_keyword(db, kw_id):
        raise HTTPException(status_code=404, detail="Keyword not found.")


@router.get("/frequency", response_model=List[dict])
def keyword_frequency(
    limit: int = Query(15, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Top keywords by hit count."""
    return keyword_service.get_keyword_frequency(db, limit)
