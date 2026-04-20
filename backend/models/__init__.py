# Re-export all models so SQLAlchemy can find them for table creation
from models.user import User
from models.email import EmailRecord
from models.classification import Classification
from models.keyword import Keyword
from models.sender_reputation import SenderReputation
from models.attachment import Attachment
from models.link import Link
from models.alert import Alert
from models.performance_metric import PerformanceMetric

__all__ = [
    "User", "EmailRecord", "Classification", "Keyword",
    "SenderReputation", "Attachment", "Link", "Alert", "PerformanceMetric",
]
