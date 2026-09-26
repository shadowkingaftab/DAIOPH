"""In-memory notes store (no persistence)."""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List

from tools.registry.tool_schema import ToolSchema

__all__ = ["NotesStore", "notes_store", "note_add", "note_list"]

_notes: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()


def note_add(title: str, body: str) -> str:
    """Store a note; returns its id."""
    note_id = f"note-{int(time.time() * 1000)}"
    with _lock:
        _notes[note_id] = {"title": title, "body": body, "created": time.time()}
    return note_id


def note_list() -> List[Dict[str, Any]]:
    """Return all notes (id, title, created)."""
    with _lock:
        return [
            {"id": nid, "title": meta["title"], "created": meta["created"]}
            for nid, meta in sorted(_notes.items())
        ]


class NotesStore:
    """Thread-safe in-memory notes store."""

    def add(self, title: str, body: str) -> str:
        return note_add(title, body)

    def list(self) -> List[Dict[str, Any]]:
        return note_list()


notes_store = NotesStore()

note_add_tool = ToolSchema(name="note_add", description="Add a note",
                           fn=note_add, params={"title": str, "body": str})
note_list_tool = ToolSchema(name="note_list", description="List notes",
                            fn=note_list)
