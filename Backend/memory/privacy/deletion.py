"""Memory deletion (right-to-be-forgotten)."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

__all__ = ["MemoryDeletion"]


class MemoryDeletion:
    """Deletes memory entries for a subject via an injectable store."""

    def __init__(self, delete_fn: Callable[[str], int]) -> None:
        self._delete_fn = delete_fn

    def delete_subject(self, subject: str) -> int:
        """Delete all memory for *subject*; returns count deleted."""
        return self._delete_fn(subject)
