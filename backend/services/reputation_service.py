"""
Sender Reputation Service — looks up / updates domain trust scores.
"""

import logging
from sqlalchemy.orm import Session
from models.sender_reputation import SenderReputation

logger = logging.getLogger(__name__)

# Known safe domains — used as a seed whitelist
TRUSTED_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "edu.in", "ac.in", "university.edu", "college.edu",
    "amazon.com", "microsoft.com", "google.com", "apple.com",
    "github.com", "linkedin.com",
}

# Known spam/phishing domains
BLOCKED_DOMAINS = {
    "promo-scam.win", "free-prize.xyz", "winner-alert.net",
    "click-here-now.biz", "urgent-verify.org", "bank-update.info",
    "paypal-secure.biz", "account-suspended.net",
}


def get_or_create_reputation(db: Session, domain: str) -> SenderReputation:
    """Fetch reputation record for a domain, or auto-create one."""
    rep = db.query(SenderReputation).filter(SenderReputation.sender_domain == domain).first()
    if rep:
        return rep

    # Auto-classify based on known lists
    if domain in TRUSTED_DOMAINS:
        score, category, blacklisted = 9.0, "trusted", False
    elif domain in BLOCKED_DOMAINS:
        score, category, blacklisted = 1.0, "blocked", True
    else:
        score, category, blacklisted = 5.0, "monitoring", False

    rep = SenderReputation(
        sender_domain=domain,
        reputation_score=score,
        category=category,
        is_blacklisted=blacklisted,
    )
    db.add(rep)
    db.commit()
    db.refresh(rep)
    return rep


def get_reputation_score(db: Session, domain: str) -> float:
    """Return reputation score (0–10) for the given domain."""
    rep = get_or_create_reputation(db, domain)
    rep.total_emails_received = (rep.total_emails_received or 0) + 1
    db.commit()
    return rep.reputation_score


def reputation_risk_contribution(reputation_score: float) -> float:
    """
    Convert reputation score (0–10) into a risk contribution (0–100).
    A score of 0 (worst) → risk 100; score of 10 (best) → risk 0.
    """
    return (10.0 - reputation_score) * 10.0


def blacklist_domain(db: Session, domain: str) -> SenderReputation:
    rep = get_or_create_reputation(db, domain)
    rep.is_blacklisted = True
    rep.category = "blocked"
    rep.reputation_score = 0.0
    db.commit()
    db.refresh(rep)
    return rep


def list_reputations(db: Session, skip: int = 0, limit: int = 50) -> list[SenderReputation]:
    return db.query(SenderReputation).offset(skip).limit(limit).all()


def upsert_reputation(db: Session, domain: str, score: float, category: str, notes: str = None) -> SenderReputation:
    rep = get_or_create_reputation(db, domain)
    rep.reputation_score = score
    rep.category = category
    rep.is_blacklisted = category == "blocked"
    if notes:
        rep.notes = notes
    db.commit()
    db.refresh(rep)
    return rep
