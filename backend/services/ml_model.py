"""
ML Model Service — Simple Naive Bayes spam classifier.

For the college project we create a lightweight TF-IDF + Naive Bayes
model trained on a small set of hard-coded examples.  The model is
trained once at startup and cached in memory, so no .pkl files are needed.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

# ── Sample training data ──────────────────────────────────────────────────────
# 0 = wanted (ham), 1 = spam/unwanted
TRAINING_DATA = [
    # Spam samples
    ("Win a free iPhone! Click here now! Limited offer URGENT!", 1),
    ("Congratulations! You have been selected for a cash prize of $5000", 1),
    ("FREE WINNER! You won! Claim your reward immediately click now", 1),
    ("URGENT: Your account will be suspended. Verify your bank details NOW", 1),
    ("Make money fast! Work from home earn $500 per day guaranteed", 1),
    ("Hot singles in your area! Click here for exclusive offer", 1),
    ("You have won the lottery! Send your details to claim prize", 1),
    ("Act now! Limited time offer 100% FREE medication no prescription", 1),
    ("FINAL NOTICE: Your payment is overdue. Pay immediately or face action", 1),
    ("Get rich quick! Investment opportunity with 500% return guaranteed", 1),
    ("Phishing: Please update your PayPal account information immediately", 1),
    ("Your bank account has been compromised click here to secure it", 1),
    ("Dear customer your credit card has been suspended verify now", 1),
    ("Special promotion buy cheap pills online no doctor needed", 1),
    ("You are the lucky winner click to collect your $10000 prize", 1),

    # Ham / wanted samples
    ("Hi, just checking in about the project deadline next week", 0),
    ("Please find attached the meeting agenda for tomorrow's discussion", 0),
    ("Your order has been shipped and will arrive in 2-3 business days", 0),
    ("Thank you for your application. We will review and get back to you", 0),
    ("Reminder: Team standup at 10 AM tomorrow in conference room B", 0),
    ("The quarterly report is ready for your review, please check attached", 0),
    ("Your subscription has been renewed for another year. Thank you!", 0),
    ("Hi team, please review the pull request before end of day", 0),
    ("Weekly newsletter from your university alumni association", 0),
    ("Your appointment is confirmed for Thursday at 3 PM", 0),
    ("Invoice for consulting services rendered in March is attached", 0),
    ("The research paper draft is ready, please provide feedback", 0),
    ("Status update: all systems operational, no issues detected", 0),
    ("Thank you for attending our webinar. Recording link below", 0),
    ("Campus event: Annual tech fest this weekend, all welcome", 0),
]


from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.calibration import CalibratedClassifierCV
import threading

_pipeline: Pipeline | None = None
_pipeline_lock = threading.Lock()

def _build_pipeline() -> Pipeline:
    texts  = [d[0] for d in TRAINING_DATA]
    labels = [d[1] for d in TRAINING_DATA]
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)),
        ("clf",   CalibratedClassifierCV(MultinomialNB(alpha=0.1))),
    ])
    pipe.fit(texts, labels)
    return pipe

def get_classifier():
    global _pipeline
    if _pipeline is None:
        with _pipeline_lock:
            if _pipeline is None:
                _pipeline = _build_pipeline()
    return _pipeline

def predict_spam_probability(text: str) -> float:
    pipe = get_classifier()
    prob = pipe.predict_proba([text])[0]
    spam_idx = list(pipe.classes_).index(1)
    return float(prob[spam_idx])
