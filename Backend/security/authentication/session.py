"""Session manager (in-memory, thread-safe)."""

from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

__all__ = ["Session", "SessionManager"]


@dataclass
class Session:
    """One authenticated session."""

    session_id: str
    subject: str
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    data: Dict[str, Any] = field(default_factory=dict)

    @property
    def expired(self) -> bool:
        """True when past expiry."""
        return time.time() > self.expires_at


class SessionManager:
    """Creates, validates, and destroys sessions."""

    def __init__(self, ttl_seconds: float = 3600.0) -> None:
        self.ttl_seconds = ttl_seconds
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()

    def create(self, subject: str) -> Session:
        """Create a new session for *subject*."""
        session = Session(
            session_id=secrets.token_hex(16),
            subject=subject,
            expires_at=time.time() + self.ttl_seconds,
        )
        with self._lock:
            self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> Optional[Session]:
        """Return a valid session, or None when unknown/expired."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None or session.expired:
                return None
            return session

    def destroy(self, session_id: str) -> None:
        """Remove a session (no-op when absent)."""
        with self._lock:
            self._sessions.pop(session_id, None)

    def active_count(self) -> int:
        """Number of non-expired sessions."""
        with self._lock:
            now = time.time()
            return sum(1 for s in self._sessions.values() if s.expires_at > now)
