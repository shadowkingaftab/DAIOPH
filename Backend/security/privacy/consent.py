"""Consent tracking (in-memory)."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List

__all__ = ["ConsentRecord", "ConsentManager"]


@dataclass(frozen=True)
class ConsentRecord:
    """One consent grant."""

    subject: str
    purpose: str
    granted_at: float = field(default_factory=time.time)
    revoked: bool = False


class ConsentManager:
    """Tracks consent per subject/purpose (deny by default)."""

    def __init__(self) -> None:
        self._records: Dict[str, ConsentRecord] = {}
        self._lock = threading.Lock()

    def grant(self, subject: str, purpose: str) -> None:
        """Record consent for *subject* on *purpose*."""
        with self._lock:
            self._records[f"{subject}:{purpose}"] = ConsentRecord(
                subject=subject, purpose=purpose
            )

    def revoke(self, subject: str, purpose: str) -> None:
        """Revoke consent (no-op when absent)."""
        with self._lock:
            key = f"{subject}:{purpose}"
            record = self._records.get(key)
            if record is not None:
                self._records[key] = ConsentRecord(
                    subject=subject, purpose=purpose,
                    granted_at=record.granted_at, revoked=True,
                )

    def has_consent(self, subject: str, purpose: str) -> bool:
        """True only when an un-revoked consent exists."""
        with self._lock:
            record = self._records.get(f"{subject}:{purpose}")
            return record is not None and not record.revoked
