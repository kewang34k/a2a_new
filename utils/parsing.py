"""Query parsing helpers used across the codebase."""

from __future__ import annotations

import re
from typing import Optional


_EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")

# Look for patterns like "customer 123", "ID 123", "customer ID 123", "#123"
_CUSTOMER_ID_PATTERNS = (
    re.compile(r"customer\s+id\s+(\d+)", re.IGNORECASE),
    re.compile(r"customer\s+(\d+)", re.IGNORECASE),
    re.compile(r"\bid\s+(\d+)\b", re.IGNORECASE),
    re.compile(r"#(\d+)", re.IGNORECASE),
)


def extract_customer_id(text: str) -> Optional[int]:
    """Extract a customer id from free text, if present."""
    for pattern in _CUSTOMER_ID_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    return None


def extract_email(text: str) -> Optional[str]:
    """Extract the first email address from free text, if present."""
    match = _EMAIL_RE.search(text)
    return match.group(0) if match else None

