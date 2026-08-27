"""Checkpoint store (in-memory)."""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional

__all__ = ["CheckpointStore"]


class CheckpointStore:
    """Stores named checkpoints with timestamps."""

    def __init__(self) -> None:
        self._checkpoints: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def save(self, name: str, state: Dict[str, Any]) -> None:
        """Save a checkpoint."""
        with self._lock:
            self._checkpoints[name] = {
                "data": dict(state), "saved_at": time.time(),
            }

    def load(self, name: str) -> Optional[Dict[str, Any]]:
        """Return a checkpoint's data, or None when absent."""
        with self._lock:
            cp = self._checkpoints.get(name)
            return dict(cp["data"]) if cp else None

    def list(self) -> List[str]:
        """Return checkpoint names."""
        with self._lock:
            return sorted(self._checkpoints.keys())
