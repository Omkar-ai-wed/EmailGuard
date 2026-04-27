"""
Keyword Service — matches email text against the keyword rules database
and returns a cumulative risk score contribution.
"""

import re
import logging
from sqlalchemy.orm import Session
from models.keyword import Keyword

logger = logging.getLogger(__name__)


import time
from threading import Lock

_keyword_cache: list | None = None
_keyword_cache_ts: float = 0.0
_keyword_cache_ttl: float = 60.0  # seconds
_keyword_cache_lock = Lock()

def get_all_keywords(db: Session, active_only: bool = True) -> list[Keyword]:
    """Return keywords, refreshing from DB at most every 60 seconds."""
    global _keyword_cache, _keyword_cache_ts
    now = time.monotonic()
    with _keyword_cache_lock:
        if _keyword_cache is None or (now - _keyword_cache_ts) > _keyword_cache_ttl:
            q = db.query(Keyword)
            if active_only:
                q = q.filter(Keyword.is_active == True)
            _keyword_cache = q.all()
            _keyword_cache_ts = now
    return _keyword_cache

def _invalidate_keyword_cache() -> None:
    global _keyword_cache
    with _keyword_cache_lock:
        _keyword_cache = None


def match_keywords(text: str, db: Session) -> dict:
    """
    Scan text against all active keywords.

    Returns:
        {
            "keyword_score": float,        # 0–100
            "matched_keywords": list[str], # which keywords fired
            "top_rule": str | None,        # highest-weight keyword
        }
    """
    keywords = get_all_keywords(db)
    text_lower = text.lower()

    matched = []
    matched_ids = []
    total_weight = 0.0
    top_rule = None
    top_weight = 0.0

    for kw in keywords:
        pattern = re.compile(r'\b' + re.escape(kw.keyword.lower()) + r'\b')
        if pattern.search(text_lower):
            matched.append(kw.keyword)
            matched_ids.append(kw.id)
            total_weight += kw.weight

            if kw.weight > top_weight:
                top_weight = kw.weight
                top_rule = kw.keyword

    keyword_score = min(total_weight * 10, 100.0)

    logger.debug("Keyword scan: matched=%s, score=%.1f", matched, keyword_score)
    return {
        "keyword_score": keyword_score,
        "matched_keywords": matched,
        "matched_ids": matched_ids,
        "top_rule": top_rule,
    }

def flush_keyword_hits(db: Session, keyword_ids: list[int]) -> None:
    """Atomically increment hit counts for matched keywords. Call after outer commit."""
    if not keyword_ids:
        return
    from models.keyword import Keyword
    db.query(Keyword).filter(Keyword.id.in_(keyword_ids)).update(
        {Keyword.hit_count: Keyword.hit_count + 1},
        synchronize_session=False,
    )
    # Caller is responsible for commit


# ── CRUD helpers ──────────────────────────────────────────────────────────────

def create_keyword(db: Session, keyword: str, weight: float, category_tag: str) -> Keyword:
    kw = Keyword(keyword=keyword.lower(), weight=weight, category_tag=category_tag)
    db.add(kw)
    db.commit()
    db.refresh(kw)
    _invalidate_keyword_cache()
    return kw


def update_keyword(db: Session, kw_id: int, **kwargs) -> Keyword | None:
    kw = db.query(Keyword).filter(Keyword.id == kw_id).first()
    if not kw:
        return None
    for field, value in kwargs.items():
        if value is not None:
            setattr(kw, field, value)
    db.commit()
    db.refresh(kw)
    _invalidate_keyword_cache()
    return kw


def delete_keyword(db: Session, kw_id: int) -> bool:
    kw = db.query(Keyword).filter(Keyword.id == kw_id).first()
    if not kw:
        return False
    db.delete(kw)
    db.commit()
    _invalidate_keyword_cache()
    return True


def get_keyword_frequency(db: Session, limit: int = 15) -> list[dict]:
    """Return top keywords by hit count."""
    rows = (
        db.query(Keyword)
        .filter(Keyword.hit_count > 0)
        .order_by(Keyword.hit_count.desc())
        .limit(limit)
        .all()
    )
    return [{"keyword": k.keyword, "hit_count": k.hit_count, "category_tag": k.category_tag} for k in rows]
