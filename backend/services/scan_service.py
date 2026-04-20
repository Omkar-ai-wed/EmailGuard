"""
Scan Service — analyse links and attachments found inside emails.
Simple heuristic-based scanner (no external APIs needed for demo).
"""

import re
import logging
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from models.attachment import Attachment
from models.link import Link

logger = logging.getLogger(__name__)

# File extensions that are considered dangerous
SUSPICIOUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".vbs", ".ps1", ".sh",
    ".zip", ".rar", ".7z", ".jar", ".js", ".scr",
    ".msi", ".dll", ".reg",
}

# URL patterns associated with phishing
PHISHING_URL_PATTERNS = [
    r"paypal.*\.(?!com)", r"bank.*\.(?!com)", r"secure.*login",
    r"account.*verify", r"update.*credential", r"click.*here.*now",
    r"free.*prize", r"winner.*claim", r"bit\.ly", r"tinyurl",
    r"\.xyz$", r"\.win$", r"\.biz$", r"\.info$",
]

SUSPICIOUS_DOMAINS = {
    "promo-scam.win", "free-prize.xyz", "winner-alert.net",
    "click-here-now.biz", "urgent-verify.org", "paypal-secure.biz",
}


def scan_url(url: str) -> dict:
    """
    Scan a single URL using heuristics.
    Returns: {is_suspicious, is_phishing_url, scan_result}
    """
    is_suspicious = False
    is_phishing = False

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().lstrip("www.")
    except Exception:
        domain = ""

    # Check against known bad domains
    if domain in SUSPICIOUS_DOMAINS:
        is_suspicious = True
        is_phishing = True

    # Pattern matching on full URL
    for pattern in PHISHING_URL_PATTERNS:
        if re.search(pattern, url.lower()):
            is_suspicious = True
            is_phishing = True
            break

    # No HTTPS is suspicious
    if url.startswith("http://"):
        is_suspicious = True

    result = "malicious" if is_phishing else ("suspicious" if is_suspicious else "safe")
    return {
        "domain": domain,
        "is_suspicious": is_suspicious,
        "is_phishing_url": is_phishing,
        "scan_result": result,
    }


def scan_attachment(filename: str, file_type: str = None) -> dict:
    """
    Scan an attachment by extension heuristics.
    Returns: {is_suspicious, scan_result}
    """
    ext = ""
    if "." in filename:
        ext = "." + filename.rsplit(".", 1)[-1].lower()
    elif file_type:
        ext = "." + file_type.lower()

    is_suspicious = ext in SUSPICIOUS_EXTENSIONS
    result = "suspicious" if is_suspicious else "safe"
    return {"is_suspicious": is_suspicious, "file_type": ext.lstrip("."), "scan_result": result}


def process_email_links(db: Session, email_id: int, urls: list[str]) -> list[Link]:
    """Scan all URLs in an email and persist results."""
    saved = []
    for url in urls:
        result = scan_url(url)
        link = Link(
            email_id=email_id,
            url=url,
            domain=result["domain"],
            is_suspicious=result["is_suspicious"],
            is_phishing_url=result["is_phishing_url"],
            scan_result=result["scan_result"],
        )
        db.add(link)
        saved.append(link)
    db.commit()
    return saved


def process_email_attachments(db: Session, email_id: int, attachments: list[dict]) -> list[Attachment]:
    """Scan all attachments in an email and persist results."""
    saved = []
    for att in attachments:
        result = scan_attachment(att.get("filename", ""), att.get("file_type", ""))
        attachment = Attachment(
            email_id=email_id,
            filename=att.get("filename", "unknown"),
            file_type=result["file_type"],
            file_size_bytes=att.get("file_size_bytes"),
            mime_type=att.get("mime_type"),
            is_suspicious=result["is_suspicious"],
            scan_result=result["scan_result"],
        )
        db.add(attachment)
        saved.append(attachment)
    db.commit()
    return saved


def get_scan_results(db: Session, email_id: int) -> dict:
    """Return all scan results for a given email."""
    links = db.query(Link).filter(Link.email_id == email_id).all()
    attachments = db.query(Attachment).filter(Attachment.email_id == email_id).all()
    return {"links": links, "attachments": attachments}
