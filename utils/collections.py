"""Collection helpers shared across modules."""

from __future__ import annotations

from typing import Iterable, List, TypeVar


T = TypeVar("T")


def dedupe_preserve_order(items: Iterable[T]) -> List[T]:
    """Return a list with duplicates removed, preserving first-seen order."""
    seen: set[T] = set()
    out: List[T] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out

