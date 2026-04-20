"""Pydantic schemas for Classification, Keywords, Reputation."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── Classification ────────────────────────────────────────────────────────────

class ClassificationResult(BaseModel):
    email_id: int
    predicted_category: str        # wanted | unwanted | suspicious | phishing
    confidence_score: float        # 0.0 – 1.0
    risk_score: float              # 0 – 100
    method: str                    # rule_based | ml_model | combined
    rule_triggered: Optional[str]
    keyword_score: Optional[float]
    reputation_score: Optional[float]
    ml_score: Optional[float]
    is_phishing: bool
    classified_at: datetime

    model_config = {"from_attributes": True}


# ── Keywords ──────────────────────────────────────────────────────────────────

class KeywordCreate(BaseModel):
    keyword: str
    weight: float = 1.0
    category_tag: str = "spam"   # spam | phishing | promo | suspicious


class KeywordUpdate(BaseModel):
    weight: Optional[float] = None
    category_tag: Optional[str] = None
    is_active: Optional[bool] = None


class KeywordOut(BaseModel):
    id: int
    keyword: str
    weight: float
    category_tag: str
    is_active: bool
    hit_count: int
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Sender Reputation ─────────────────────────────────────────────────────────

class ReputationCreate(BaseModel):
    sender_domain: str
    sender_email: Optional[str] = None
    reputation_score: float = 5.0  # 0–10
    category: str = "monitoring"   # trusted | blocked | monitoring
    notes: Optional[str] = None


class ReputationOut(BaseModel):
    id: int
    sender_domain: str
    sender_email: Optional[str]
    reputation_score: float
    category: str
    is_blacklisted: bool
    total_emails_received: int
    spam_count: int
    last_seen: datetime
    model_config = {"from_attributes": True}


# ── Alerts ────────────────────────────────────────────────────────────────────

class AlertOut(BaseModel):
    id: int
    email_id: Optional[int]
    alert_type: str
    severity: str
    title: str
    description: str
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime]
    model_config = {"from_attributes": True}


# ── Performance Metrics ───────────────────────────────────────────────────────

class MetricOut(BaseModel):
    id: int
    model_version: str
    accuracy: float
    precision_score: float
    recall_score: float
    f1_score: float
    auc_roc: Optional[float]
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    training_samples: int
    recorded_at: datetime
    model_config = {"from_attributes": True}
