"""Email draft tool (in-memory; no SMTP)."""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List

from tools.registry.tool_schema import ToolSchema

__all__ = ["email_draft", "email_drafts"]

_drafts: List[Dict[str, Any]] = []
_lock = threading.Lock()


def email_draft(to: str, subject: str, body: str) -> str:
    """Store a draft; returns its id."""
    draft_id = f"draft-{int(time.time() * 1000)}"
    with _lock:
        _drafts.append({"id": draft_id, "to": to, "subject": subject,
                        "body": body, "at": time.time()})
    return draft_id


def email_drafts() -> List[Dict[str, Any]]:
    """Return all drafts."""
    with _lock:
        return list(_drafts)


email_draft_tool = ToolSchema(
    name="email_draft", description="Create an email draft (in-memory)",
    fn=email_draft, params={"to": str, "subject": str, "body": str})
email_drafts_tool = ToolSchema(name="email_drafts", description="List drafts",
                               fn=email_drafts)
