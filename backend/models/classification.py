"""Classification model — audit log for every classification decision."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Classification(Base):
    __tablename__ = "classifications"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), index=True, nullable=False)

    # How the decision was made
    method = Column(String(20), nullable=False)  # rule_based | ml_model | manual

    # The output
    predicted_category = Column(String(20))      # wanted | unwanted | suspicious | phishing
    confidence_score = Column(Float, default=0.0)  # 0.0–1.0

    # Component scores from the pipeline
    rule_triggered = Column(String(255), nullable=True)   # name of rule that fired
    ml_score = Column(Float, nullable=True)               # raw ML probability
    keyword_score = Column(Float, nullable=True)          # keyword-based risk
    reputation_score = Column(Float, nullable=True)       # sender reputation contribution

    classified_at = Column(DateTime(timezone=True), server_default=func.now())
    classified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    email = relationship("EmailRecord", back_populates="classifications")
