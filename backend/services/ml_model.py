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


class SpamClassifier:
    """
    Simple TF-IDF-inspired Naive Bayes classifier.
    Built from scratch without sklearn so the project has zero heavy deps
    beyond the standard library + numpy.
    """

    def __init__(self):
        self.vocab: dict[str, int] = {}
        self.spam_word_counts: np.ndarray | None = None
        self.ham_word_counts: np.ndarray | None = None
        self.spam_total: int = 0
        self.ham_total: int = 0
        self.spam_prior: float = 0.5
        self.ham_prior: float = 0.5
        self._trained = False

    # ── Tokenisation ──────────────────────────────────────────────────────────

    def _tokenize(self, text: str) -> list[str]:
        """Lower-case, split on non-alpha chars, remove short tokens."""
        import re
        tokens = re.findall(r"[a-zA-Z]{3,}", text.lower())
        return tokens

    def _build_vocab(self, corpus: list[str]) -> None:
        idx = 0
        for text in corpus:
            for token in self._tokenize(text):
                if token not in self.vocab:
                    self.vocab[token] = idx
                    idx += 1

    # ── Training ──────────────────────────────────────────────────────────────

    def train(self, data: list[tuple[str, int]]) -> None:
        texts = [d[0] for d in data]
        labels = [d[1] for d in data]

        self._build_vocab(texts)
        V = len(self.vocab)

        spam_docs = [t for t, l in zip(texts, labels) if l == 1]
        ham_docs = [t for t, l in zip(texts, labels) if l == 0]

        # Laplace smoothed word counts (alpha = 1)
        self.spam_word_counts = np.ones(V)
        self.ham_word_counts = np.ones(V)

        for doc in spam_docs:
            for token in self._tokenize(doc):
                if token in self.vocab:
                    self.spam_word_counts[self.vocab[token]] += 1

        for doc in ham_docs:
            for token in self._tokenize(doc):
                if token in self.vocab:
                    self.ham_word_counts[self.vocab[token]] += 1

        self.spam_total = self.spam_word_counts.sum()
        self.ham_total = self.ham_word_counts.sum()

        total = len(labels)
        self.spam_prior = sum(labels) / total
        self.ham_prior = 1 - self.spam_prior
        self._trained = True
        logger.info("SpamClassifier trained on %d samples, vocab size %d", len(data), V)

    # ── Prediction ────────────────────────────────────────────────────────────

    def predict_proba(self, text: str) -> float:
        """Return probability that the text is spam (0.0 – 1.0)."""
        if not self._trained:
            return 0.5

        import math

        tokens = self._tokenize(text)
        log_spam = math.log(self.spam_prior)
        log_ham = math.log(self.ham_prior)
        V = len(self.vocab)

        for token in tokens:
            if token in self.vocab:
                idx = self.vocab[token]
                log_spam += math.log(self.spam_word_counts[idx] / self.spam_total)
                log_ham += math.log(self.ham_word_counts[idx] / self.ham_total)

        # Convert log-probabilities to a normalised probability score
        # Using the log-sum-exp trick for numerical stability
        max_log = max(log_spam, log_ham)
        denom = max_log + math.log(
            math.exp(log_spam - max_log) + math.exp(log_ham - max_log)
        )
        return math.exp(log_spam - denom)  # P(spam | text)

    def predict(self, text: str) -> int:
        """Return 1 for spam, 0 for ham."""
        return 1 if self.predict_proba(text) >= 0.5 else 0


# ── Singleton instance ────────────────────────────────────────────────────────

_classifier: SpamClassifier | None = None


def get_classifier() -> SpamClassifier:
    """Return a trained classifier, training it on first call."""
    global _classifier
    if _classifier is None:
        _classifier = SpamClassifier()
        _classifier.train(TRAINING_DATA)
    return _classifier


def predict_spam_probability(text: str) -> float:
    """Public helper: returns spam probability for given text (0.0–1.0)."""
    clf = get_classifier()
    return clf.predict_proba(text)
