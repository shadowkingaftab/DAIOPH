"""In-memory notification sink (no external services)."""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List

from tools.registry.tool_schema import ToolSchema

__all__ = ["notify", "notification_list"]

_notifications: List[Dict[str, Any]] = []
_lock = threading.Lock()


def notify(message: str, level: str = "info") -> str:
    """Record a notification; returns its id."""
    note_id = f"notif-{int(time.time() * 1000)}"
    with _lock:
        _notifications.append({"id": note_id, "message": message,
                               "level": level, "at": time.time()})
    return note_id


def notification_list(limit: int = 50) -> List[Dict[str, Any]]:
    """Return the most recent *limit* notifications."""
    with _lock:
        return list(_notifications[-limit:])


notify_tool = ToolSchema(name="notify", description="Record a notification",
                         fn=notify, params={"message": str, "level": str})
notification_list_tool = ToolSchema(
    name="notification_list", description="List recent notifications",
    fn=notification_list, params={"limit": int})
