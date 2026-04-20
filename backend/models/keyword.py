"""Keyword model — spam/phishing keyword rules with weights."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(100), unique=True, index=True, nullable=False)

    # Weight 0–10: how strongly this keyword indicates spam
    weight = Column(Float, default=1.0, nullable=False)

    # spam | phishing | promo | suspicious
    category_tag = Column(String(20), default="spam")

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # How many times this keyword has been matched
    hit_count = Column(Integer, default=0)
