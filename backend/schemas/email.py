"""Pydantic schemas for Email endpoints."""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Request Schemas ───────────────────────────────────────────────────────────

class EmailIngest(BaseModel):
    """Schema for submitting a new email for analysis."""
    sender_email: str
    recipient_email: Optional[str] = None
    subject: str
    body_text: str
    body_html: Optional[str] = None
    received_at: Optional[datetime] = None

    # Optionally provide pre-extracted metadata
    attachments: Optional[List[dict]] = []  # [{filename, file_type, file_size_bytes}]
    links: Optional[List[str]] = []         # List of URLs found in the email


class EmailStatusUpdate(BaseModel):
    """Manually update the status of an email."""
    # safe | blocked | reported | reviewed
    status: str
    notes: Optional[str] = None

    @classmethod
    def validate_status(cls, v):
        allowed = {"safe", "blocked", "reported", "reviewed", "pending"}
        if v not in allowed:
            raise ValueError(f"Status must be one of: {allowed}")
        return v


class EmailFilter(BaseModel):
    """Query parameters for filtering email list."""
    category: Optional[str] = None     # wanted | unwanted | suspicious | phishing
    status: Optional[str] = None       # pending | classified | reviewed …
    sender_domain: Optional[str] = None
    min_risk_score: Optional[float] = None
    max_risk_score: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None       # Full-text search across subject/sender


# ── Response Schemas ──────────────────────────────────────────────────────────

class AttachmentOut(BaseModel):
    id: int
    filename: str
    file_type: str
    is_suspicious: bool
    scan_result: str
    model_config = {"from_attributes": True}


class LinkOut(BaseModel):
    id: int
    url: str
    domain: Optional[str]
    is_suspicious: bool
    is_phishing_url: bool
    scan_result: str
    model_config = {"from_attributes": True}


class EmailOut(BaseModel):
    id: int
    message_id: str
    sender_email: str
    sender_domain: Optional[str]
    recipient_email: Optional[str]
    subject: str
    risk_score: float
    category: str
    status: str
    is_phishing: bool
    has_attachments: bool
    link_count: int
    ingested_at: datetime
    received_at: Optional[datetime]

    model_config = {"from_attributes": True}


class EmailDetailOut(EmailOut):
    """Full detail including body and related records."""
    body_text: str
    body_html: Optional[str]
    attachments: List[AttachmentOut] = []
    links: List[LinkOut] = []

    model_config = {"from_attributes": True}


class EmailListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    emails: List[EmailOut]
