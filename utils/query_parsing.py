"""
Query parsing helpers shared across agents and entrypoints.

These are intentionally simple, rule-based extractors to keep the project
LLM-free and easy to reason about.
"""

from __future__ import annotations

import re
from typing import Optional


def extract_customer_id(query: str) -> Optional[int]:
    """Extract a customer ID from a query string."""
    query_lower = query.lower()

    # Look for patterns like "customer 123", "ID 123", "customer ID 123"
    patterns = [
        r"customer\s+id\s+(\d+)",
        r"customer\s+(\d+)",
        r"id\s+(\d+)",
        r"#(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            return int(match.group(1))

    return None


def extract_email(query: str) -> Optional[str]:
    """Extract the first email address from a query string."""
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", query)
    return match.group(0) if match else None

