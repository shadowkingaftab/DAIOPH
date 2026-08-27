"""Memory retention policy."""

from __future__ import annotations

import time
from dataclasses import dataclass

__all__ = ["RetentionPolicy"]


@dataclass(frozen=True)
class RetentionPolicy:
    """Retention window for memory entries."""

    ttl_seconds: float

    def is_expired(self, created_at: float) -> bool:
        """True when *created_at* is older than the TTL."""
        return time.time() - created_at > self.ttl_seconds
