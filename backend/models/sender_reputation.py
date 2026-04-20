"""SenderReputation model — trust/block status per domain."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class SenderReputation(Base):
    __tablename__ = "sender_reputation"

    id = Column(Integer, primary_key=True, index=True)
    sender_email = Column(String(255), nullable=True, index=True)
    sender_domain = Column(String(100), unique=True, index=True, nullable=False)

    # Score 0–10: 10 = fully trusted, 0 = known spam
    reputation_score = Column(Float, default=5.0)

    # trusted | blocked | monitoring
    category = Column(String(20), default="monitoring")

    is_blacklisted = Column(Boolean, default=False)
    total_emails_received = Column(Integer, default=0)
    spam_count = Column(Integer, default=0)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
