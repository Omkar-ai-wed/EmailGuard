"""Scanning Router — /api/v1/scan"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from services import scan_service
from middleware.auth_middleware import get_current_user
from models.user import User

router = APIRouter()


@router.post("/links/{email_id}")
def scan_email_links(
    email_id: int,
    urls: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Scan a list of URLs for phishing/suspicious patterns and link to an email."""
    results = scan_service.process_email_links(db, email_id, urls)
    return [
        {
            "url": lnk.url,
            "domain": lnk.domain,
            "is_suspicious": lnk.is_suspicious,
            "is_phishing_url": lnk.is_phishing_url,
            "scan_result": lnk.scan_result,
        }
        for lnk in results
    ]


@router.post("/attachments/{email_id}")
def scan_email_attachments(
    email_id: int,
    attachments: List[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Scan a list of attachments [{filename, file_type, file_size_bytes}] for an email."""
    results = scan_service.process_email_attachments(db, email_id, attachments)
    return [
        {
            "filename": att.filename,
            "file_type": att.file_type,
            "is_suspicious": att.is_suspicious,
            "scan_result": att.scan_result,
        }
        for att in results
    ]


@router.get("/{email_id}/results")
def get_scan_results(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all stored scan results (links + attachments) for an email."""
    results = scan_service.get_scan_results(db, email_id)
    return {
        "email_id": email_id,
        "links": [
            {"url": l.url, "domain": l.domain, "is_phishing_url": l.is_phishing_url, "scan_result": l.scan_result}
            for l in results["links"]
        ],
        "attachments": [
            {"filename": a.filename, "file_type": a.file_type, "is_suspicious": a.is_suspicious, "scan_result": a.scan_result}
            for a in results["attachments"]
        ],
    }
