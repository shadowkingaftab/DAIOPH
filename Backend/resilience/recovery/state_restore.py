"""State restore from checkpoints."""

from __future__ import annotations

from typing import Any, Dict, Optional

from resilience.recovery.checkpoint import CheckpointStore

__all__ = ["StateRestore"]


class StateRestore:
    """Restores state from a checkpoint store."""

    def __init__(self, store: CheckpointStore) -> None:
        self._store = store

    def restore(self, name: str) -> Optional[Dict[str, Any]]:
        """Return the checkpoint's state, or None when absent."""
        return self._store.load(name)
