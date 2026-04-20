"""Attachment model — scan results for email attachments."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), index=True, nullable=False)

    filename = Column(String(255))
    file_type = Column(String(50))        # Extension: .exe, .pdf, .zip …
    file_size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)

    is_suspicious = Column(Boolean, default=False)

    # safe | suspicious | malicious
    scan_result = Column(String(20), default="safe")
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())

    email = relationship("EmailRecord", back_populates="attachments")
