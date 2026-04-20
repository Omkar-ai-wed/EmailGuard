"""PerformanceMetric model — ML model accuracy snapshots over time."""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base


class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String(50), default="1.0.0")

    # Standard classification metrics
    accuracy = Column(Float, nullable=False)
    precision_score = Column(Float, nullable=False)
    recall_score = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    auc_roc = Column(Float, nullable=True)

    # Confusion matrix raw counts
    true_positives = Column(Integer, default=0)
    false_positives = Column(Integer, default=0)
    true_negatives = Column(Integer, default=0)
    false_negatives = Column(Integer, default=0)

    training_samples = Column(Integer, default=0)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
