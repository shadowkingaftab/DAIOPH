"""In-memory calendar events (no persistence)."""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List

from tools.registry.tool_schema import ToolSchema

__all__ = ["event_add", "event_list"]

_events: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()


def event_add(title: str, when: str) -> str:
    """Add an event; returns its id."""
    event_id = f"evt-{int(time.time() * 1000)}"
    with _lock:
        _events[event_id] = {"title": title, "when": when,
                             "created": time.time()}
    return event_id


def event_list() -> List[Dict[str, Any]]:
    """Return all events."""
    with _lock:
        return [{"id": eid, **meta} for eid, meta in sorted(_events.items())]


event_add_tool = ToolSchema(name="event_add", description="Add a calendar event",
                            fn=event_add, params={"title": str, "when": str})
event_list_tool = ToolSchema(name="event_list", description="List events",
                             fn=event_list)
