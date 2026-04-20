"""
Classification Engine — the core pipeline that decides if an email
is Wanted, Unwanted, Suspicious, or Phishing.

Pipeline (in order):
  1. Keyword scoring  (rule-based, uses DB keyword table)
  2. Sender reputation check
  3. Link/attachment scan summary
  4. ML model score
  5. Weighted combination → final risk score (0–100)
  6. Category decision based on thresholds
  7. Persist Classification record and optionally create Alert
"""

import logging
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from models.email import EmailRecord
from models.classification import Classification
from models.alert import Alert
from services import keyword_service, reputation_service, scan_service, ml_model
from config import settings

logger = logging.getLogger(__name__)

# ── Weights for each signal (must sum to 1.0) ────────────────────────────────
WEIGHT_KEYWORDS    = 0.30
WEIGHT_REPUTATION  = 0.25
WEIGHT_SCAN        = 0.15
WEIGHT_ML          = 0.30


def _extract_urls_from_text(text: str) -> list[str]:
    """Quick regex to pull URLs out of plain text."""
    import re
    return re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)


def calculate_risk_score(
    keyword_score: float,
    reputation_score: float,
    scan_score: float,
    ml_score: float,
) -> float:
    """
    Weighted average of all pipeline signals → 0–100 risk score.
    Higher score = more risky.
    """
    risk = (
        WEIGHT_KEYWORDS   * keyword_score   +
        WEIGHT_REPUTATION * reputation_score +
        WEIGHT_SCAN       * scan_score       +
        WEIGHT_ML         * (ml_score * 100)
    )
    return round(min(max(risk, 0.0), 100.0), 2)


def decide_category(risk_score: float, is_phishing_link: bool = False) -> str:
    """Convert a risk score into a human-readable category."""
    if is_phishing_link or risk_score >= 80:
        return "phishing"
    elif risk_score >= settings.RISK_MEDIUM_THRESHOLD:
        return "unwanted"
    elif risk_score >= settings.RISK_LOW_THRESHOLD:
        return "suspicious"
    else:
        return "wanted"


def run_classification_pipeline(
    db: Session,
    email: EmailRecord,
    extra_links: list[str] = None,
    extra_attachments: list[dict] = None,
    user_id: int = None,
) -> Classification:
    """
    Full classification pipeline for one email.
    Returns a Classification record (already saved to DB).
    """
    full_text = f"{email.subject or ''} {email.body_text or ''}"

    # ── Step 1: Keyword Matching ──────────────────────────────────────────────
    kw_result = keyword_service.match_keywords(full_text, db)
    keyword_score = kw_result["keyword_score"]
    top_rule = kw_result["top_rule"]

    # ── Step 2: Sender Reputation ─────────────────────────────────────────────
    domain = email.sender_domain or (email.sender_email.split("@")[-1] if "@" in (email.sender_email or "") else "unknown")
    rep_score_raw = reputation_service.get_reputation_score(db, domain)
    reputation_risk = reputation_service.reputation_risk_contribution(rep_score_raw)

    # ── Step 3: Link / Attachment Scan ────────────────────────────────────────
    # Collect URLs from body text + any explicitly provided
    body_urls = _extract_urls_from_text(full_text)
    all_urls = list(set(body_urls + (extra_links or [])))

    link_records = scan_service.process_email_links(db, email.id, all_urls)
    att_records = scan_service.process_email_attachments(db, email.id, extra_attachments or [])

    has_phishing_link = any(lnk.is_phishing_url for lnk in link_records)
    has_malicious_att = any(att.scan_result == "suspicious" for att in att_records)

    # Scan score: 0 (all clear) → 100 (all malicious)
    suspicious_links = sum(1 for l in link_records if l.is_suspicious)
    total_links = len(link_records) or 1
    scan_score = min((suspicious_links / total_links) * 100 + (50 if has_malicious_att else 0), 100.0)

    # ── Step 4: ML Model ──────────────────────────────────────────────────────
    ml_spam_prob = ml_model.predict_spam_probability(full_text)

    # ── Step 5: Combined Risk Score ───────────────────────────────────────────
    risk_score = calculate_risk_score(keyword_score, reputation_risk, scan_score, ml_spam_prob)

    # Bump risk if phishing link detected
    if has_phishing_link:
        risk_score = max(risk_score, 85.0)

    # ── Step 6: Category Decision ─────────────────────────────────────────────
    category = decide_category(risk_score, has_phishing_link)
    confidence = round(abs(risk_score - 50) / 50, 2)  # Higher confidence the more extreme the score

    # ── Step 7: Update EmailRecord ────────────────────────────────────────────
    email.risk_score = risk_score
    email.category = category
    email.status = "classified"
    email.is_phishing = has_phishing_link
    email.has_attachments = len(att_records) > 0
    email.link_count = len(link_records)
    db.commit()

    # ── Step 8: Persist Classification ───────────────────────────────────────
    clf = Classification(
        email_id=email.id,
        method="combined",
        predicted_category=category,
        confidence_score=confidence,
        rule_triggered=top_rule,
        keyword_score=keyword_score,
        reputation_score=reputation_risk,
        ml_score=ml_spam_prob,
        classified_by=user_id,
    )
    db.add(clf)
    db.commit()
    db.refresh(clf)

    # ── Step 9: Auto-generate Alert for high-risk emails ─────────────────────
    if category in ("phishing", "unwanted") or risk_score >= 75:
        severity = "critical" if category == "phishing" else "high"
        alert = Alert(
            email_id=email.id,
            alert_type="phishing" if has_phishing_link else "spam_surge",
            severity=severity,
            title=f"{severity.title()} Risk Email Detected",
            description=(
                f"Email from {email.sender_email} with subject '{email.subject}' "
                f"was classified as {category.upper()} with risk score {risk_score:.1f}/100."
            ),
        )
        db.add(alert)
        db.commit()

    logger.info(
        "Classified email %d → %s (risk=%.1f, kw=%.1f, rep=%.1f, ml=%.2f)",
        email.id, category, risk_score, keyword_score, reputation_risk, ml_spam_prob,
    )
    return clf
