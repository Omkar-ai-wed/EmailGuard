"""Alert model — security alerts triggered by email analysis."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=True, index=True)

    # phishing | malware | spam_surge | new_sender | suspicious_link | high_risk
    alert_type = Column(String(50), nullable=False)

    # low | medium | high | critical
    severity = Column(String(20), default="medium", nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    email = relationship("EmailRecord", back_populates="alerts")
