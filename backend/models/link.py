"""Link model — URL scan results found inside an email."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), index=True, nullable=False)

    url = Column(String(2000))
    domain = Column(String(255), nullable=True)

    is_suspicious = Column(Boolean, default=False)
    is_phishing_url = Column(Boolean, default=False)
    redirect_count = Column(Integer, default=0)

    # safe | suspicious | malicious
    scan_result = Column(String(20), default="safe")
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())

    email = relationship("EmailRecord", back_populates="links")
