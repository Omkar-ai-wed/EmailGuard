"""EmailRecord model — stores a single processed email."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class EmailRecord(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    # Identifiers
    message_id = Column(String(255), unique=True, index=True)
    sender_email = Column(String(255), index=True, nullable=False)
    sender_domain = Column(String(100), index=True)
    recipient_email = Column(String(255))

    # Content
    subject = Column(String(500))
    body_text = Column(Text)
    body_html = Column(Text, nullable=True)

    # Timestamps
    received_at = Column(DateTime(timezone=True), nullable=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

    # Analysis metadata
    has_attachments = Column(Boolean, default=False)
    link_count = Column(Integer, default=0)

    # Risk score 0–100 (higher = more dangerous)
    risk_score = Column(Float, default=0.0)

    # wanted | unwanted | suspicious | phishing | pending
    category = Column(String(20), default="pending", index=True)

    # pending | classified | reviewed | blocked | safe | reported
    status = Column(String(20), default="pending", index=True)

    is_phishing = Column(Boolean, default=False)
    ingested_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    classifications = relationship("Classification", back_populates="email", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="email", cascade="all, delete-orphan")
    links = relationship("Link", back_populates="email", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="email")
