"""In-memory audit store (bounded)."""

from __future__ import annotations

import threading
from collections import deque
from typing import Deque, List

from security.audit.audit_event import AuditEvent

__all__ = ["AuditStore"]


class AuditStore:
    """Thread-safe bounded audit event store."""

    def __init__(self, max_events: int = 1000) -> None:
        if max_events < 1:
            raise ValueError("max_events must be >= 1")
        self._events: Deque[AuditEvent] = deque(maxlen=max_events)
        self._lock = threading.Lock()

    def append(self, event: AuditEvent) -> None:
        """Append an event (oldest dropped when full)."""
        with self._lock:
            self._events.append(event)

    def list(self, limit: int = 100) -> List[AuditEvent]:
        """Return the most recent *limit* events."""
        with self._lock:
            return list(self._events)[-limit:]

    def count(self) -> int:
        """Number of stored events."""
        with self._lock:
            return len(self._events)
