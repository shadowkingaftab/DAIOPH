"""Audit event model."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

__all__ = ["AuditEvent"]


@dataclass(frozen=True)
class AuditEvent:
    """One immutable audit record.

    Never stores secrets or sensitive content: callers must pass only
    non-sensitive metadata in ``details``.
    """

    action: str
    actor: str
    outcome: str  # "success" | "failure" | "denied"
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """JSON-friendly serialization."""
        return {
            "action": self.action,
            "actor": self.actor,
            "outcome": self.outcome,
            "timestamp": self.timestamp,
            "details": dict(self.details),
            "correlation_id": self.correlation_id,
        }
