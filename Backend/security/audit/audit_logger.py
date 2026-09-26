"""Audit logger facade."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from security.audit.audit_event import AuditEvent

__all__ = ["AuditLogger"]

logger = logging.getLogger("daioph.audit")


class AuditLogger:
    """Writes audit events to a store and a structured log line."""

    def __init__(self, store=None) -> None:
        self._store = store

    def record(
        self,
        action: str,
        actor: str,
        outcome: str = "success",
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> AuditEvent:
        """Create, persist, and log an audit event."""
        event = AuditEvent(
            action=action, actor=actor, outcome=outcome,
            details=details or {}, correlation_id=correlation_id,
        )
        if self._store is not None:
            self._store.append(event)
        logger.info(
            "audit action=%s actor=%s outcome=%s",
            action, actor, outcome,
        )
        return event
