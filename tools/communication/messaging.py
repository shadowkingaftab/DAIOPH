"""In-memory message log (no network)."""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List

from tools.registry.tool_schema import ToolSchema

__all__ = ["send_message", "message_log"]

_messages: List[Dict[str, Any]] = []
_lock = threading.Lock()


def send_message(channel: str, text: str) -> str:
    """Record a message; returns its id."""
    msg_id = f"msg-{int(time.time() * 1000)}"
    with _lock:
        _messages.append({"id": msg_id, "channel": channel, "text": text,
                          "at": time.time()})
    return msg_id


def message_log(limit: int = 50) -> List[Dict[str, Any]]:
    """Return the most recent *limit* messages."""
    with _lock:
        return list(_messages[-limit:])


send_message_tool = ToolSchema(
    name="message_send", description="Record a message (in-memory)",
    fn=send_message, params={"channel": str, "text": str})
message_log_tool = ToolSchema(name="message_log", description="List messages",
                              fn=message_log, params={"limit": int})
