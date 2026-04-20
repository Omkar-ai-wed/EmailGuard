"""
Seed Data Script — populates the database with realistic sample data
suitable for a college case study demonstration.

Run with:  python seed_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
import models  # noqa: registers all ORM models

from models.user import User
from models.keyword import Keyword
from models.sender_reputation import SenderReputation
from models.performance_metric import PerformanceMetric
from models.email import EmailRecord
from models.classification import Classification
from models.alert import Alert
from services.auth_service import hash_password
from services.classification_engine import run_classification_pipeline

import uuid
from datetime import datetime, timedelta
import random

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def seed_users():
    print("→ Seeding users…")
    users = [
        {"username": "admin",   "email": "admin@emailguard.local",   "password": "admin123",   "role": "admin"},
        {"username": "analyst", "email": "analyst@emailguard.local",  "password": "analyst123", "role": "analyst"},
        {"username": "viewer",  "email": "viewer@emailguard.local",   "password": "viewer123",  "role": "viewer"},
    ]
    for u in users:
        if not db.query(User).filter(User.username == u["username"]).first():
            db.add(User(
                username=u["username"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
            ))
    db.commit()
    print("  ✓ 3 users created (admin / analyst / viewer)")


def seed_keywords():
    print("→ Seeding keywords…")
    keywords = [
        ("free", 8.0, "spam"),        ("winner", 9.0, "spam"),
        ("urgent", 7.0, "spam"),       ("click here", 8.5, "spam"),
        ("prize", 8.0, "spam"),        ("limited time", 7.0, "spam"),
        ("act now", 7.5, "spam"),      ("exclusive offer", 6.5, "spam"),
        ("congratulations", 7.0, "spam"), ("you have been selected", 9.0, "spam"),
        ("claim your reward", 9.0, "spam"), ("100% free", 9.5, "spam"),
        ("bank details", 9.5, "phishing"), ("verify now", 8.0, "phishing"),
        ("account suspended", 9.0, "phishing"), ("update your password", 8.0, "phishing"),
        ("confirm your identity", 7.5, "phishing"), ("paypal", 5.0, "phishing"),
        ("make money fast", 9.0, "spam"), ("work from home", 5.0, "promo"),
        ("unsubscribe", 2.0, "promo"),  ("newsletter", 1.0, "promo"),
    ]
    for kw, weight, tag in keywords:
        if not db.query(Keyword).filter(Keyword.keyword == kw).first():
            db.add(Keyword(keyword=kw, weight=weight, category_tag=tag))
    db.commit()
    print(f"  ✓ {len(keywords)} keywords seeded")


def seed_reputation():
    print("→ Seeding sender reputation…")
    domains = [
        ("amazon.com",       9.8, "trusted",    False),
        ("gmail.com",        9.5, "trusted",    False),
        ("microsoft.com",    9.7, "trusted",    False),
        ("university.edu",   9.5, "trusted",    False),
        ("github.com",       9.6, "trusted",    False),
        ("linkedin.com",     9.2, "trusted",    False),
        ("promo-scam.win",   0.5, "blocked",    True),
        ("free-prize.xyz",   0.2, "blocked",    True),
        ("winner-alert.net", 0.3, "blocked",    True),
        ("urgent-verify.org",0.4, "blocked",    True),
        ("marketing-co.biz", 3.5, "monitoring", False),
        ("newsletter-hub.io",4.0, "monitoring", False),
    ]
    for domain, score, cat, blacklisted in domains:
        if not db.query(SenderReputation).filter(SenderReputation.sender_domain == domain).first():
            db.add(SenderReputation(
                sender_domain=domain,
                reputation_score=score,
                category=cat,
                is_blacklisted=blacklisted,
                total_emails_received=random.randint(10, 500),
                spam_count=random.randint(0, 50) if cat != "trusted" else 0,
            ))
    db.commit()
    print(f"  ✓ {len(domains)} domain reputations seeded")


def seed_performance_metrics():
    print("→ Seeding performance metrics…")
    if db.query(PerformanceMetric).count() == 0:
        db.add(PerformanceMetric(
            model_version="1.0.0",
            accuracy=0.974,
            precision_score=0.968,
            recall_score=0.981,
            f1_score=0.974,
            auc_roc=0.991,
            true_positives=8147,
            false_positives=174,
            true_negatives=16380,
            false_negatives=146,
            training_samples=50000,
        ))
        db.commit()
        print("  ✓ Performance metrics snapshot added")


def seed_sample_emails():
    print("→ Seeding sample emails (this may take a moment)…")
    if db.query(EmailRecord).count() > 0:
        print("  ⚠ Emails already exist, skipping")
        return

    admin_user = db.query(User).filter(User.username == "admin").first()

    samples = [
        # (sender, subject, body, received_days_ago)
        ("noreply@amazon.com",        "Your order has been shipped!",
         "Hi, your order #AM-2847 has been shipped and will arrive in 2 business days.", 1),
        ("winner@promo-scam.win",     "CONGRATULATIONS! You have WON $10,000!!!",
         "FREE WINNER! You have been selected! CLICK HERE NOW to claim your cash prize! Limited time offer! ACT NOW!", 1),
        ("newsletter@university.edu", "Weekly Campus Newsletter — April 2024",
         "Dear student, please find this week's campus events and announcements below.", 2),
        ("support@urgent-verify.org", "URGENT: Your bank account has been suspended",
         "VERIFY your bank details NOW or your account will be permanently blocked. Click here to update.", 2),
        ("hr@company.com",            "Interview Confirmation — Thursday 3 PM",
         "Dear candidate, we are pleased to confirm your interview for the Software Engineer role.", 3),
        ("noreply@paypal-secure.biz", "Update your PayPal account immediately",
         "Your PayPal account requires verification. Provide your bank details to avoid suspension.", 3),
        ("reports@github.com",        "New pull request review requested",
         "A pull request has been opened on EmailGuard/backend and your review is requested.", 4),
        ("promo@free-prize.xyz",      "You are the LUCKY WINNER! Claim $5000 prize",
         "Congratulations! 100% FREE prize awaiting. You have been selected for our exclusive offer.", 4),
        ("prof.sharma@university.edu","Assignment Deadline Reminder — Unit 3",
         "This is a reminder that your Unit 3 case study submission is due next Friday.", 5),
        ("deals@marketing-co.biz",    "Exclusive offer just for you — 50% off everything",
         "Limited time offer! Exclusive members-only discount. Act now before it expires!", 5),
        ("no-reply@linkedin.com",     "You have 3 new connection requests",
         "John Smith, Priya Patel and 1 other sent you connection requests on LinkedIn.", 6),
        ("info@startup-verify.io",    "Action Required: Verify your email address",
         "Please verify your email address to complete your account setup at StartupVerify.", 6),
        ("noreply@microsoft.com",     "Your Microsoft 365 subscription renews soon",
         "Your subscription will automatically renew on May 1st. No action required.", 7),
        ("cash@make-money-fast.xyz",  "Make money FAST! Work from home $500 per day GUARANTEED",
         "GET RICH QUICK! Guaranteed income from home. No experience needed. Click here now!", 7),
    ]

    for sender, subject, body, days_ago in samples:
        email = EmailRecord(
            message_id=str(uuid.uuid4()),
            sender_email=sender,
            sender_domain=sender.split("@")[-1],
            recipient_email="student@university.edu",
            subject=subject,
            body_text=body,
            received_at=datetime.utcnow() - timedelta(days=days_ago),
            ingested_by_user_id=admin_user.id if admin_user else None,
        )
        db.add(email)
        db.commit()
        db.refresh(email)

        # Run the classification pipeline on each seeded email
        run_classification_pipeline(db, email, user_id=admin_user.id if admin_user else None)

    print(f"  ✓ {len(samples)} sample emails seeded and classified")


def seed_alerts():
    """Add a few manual alerts for the demo dashboard."""
    print("→ Seeding additional alerts…")
    existing = db.query(Alert).count()
    if existing < 3:
        db.add(Alert(
            alert_type="spam_surge",
            severity="medium",
            title="Spam Volume Spike Detected",
            description="Spam emails from .xyz domains increased by 45% in the last hour.",
            is_resolved=False,
        ))
        db.add(Alert(
            alert_type="new_sender",
            severity="low",
            title="New Unknown Sender Flagged",
            description="Bulk emails from a previously unseen domain 'marketing-co.biz' have been flagged for review.",
            is_resolved=False,
        ))
        db.commit()
        print("  ✓ Additional alerts added")


if __name__ == "__main__":
    print("\n🌱 EmailGuard Seed Script")
    print("=" * 40)
    seed_users()
    seed_keywords()
    seed_reputation()
    seed_performance_metrics()
    seed_sample_emails()
    seed_alerts()
    db.close()
    print("\n✅ Database seeded successfully!")
    print("\n📌 Login credentials:")
    print("  admin   / admin123   (full access)")
    print("  analyst / analyst123 (classify & view)")
    print("  viewer  / viewer123  (read-only)")
    print("\n🚀 Start the server: python run.py")
    print("📖 Open Swagger UI:  http://localhost:8000/docs\n")
