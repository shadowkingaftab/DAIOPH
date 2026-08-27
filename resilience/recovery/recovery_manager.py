"""Recovery manager: checkpoint + rollback + restore."""

from __future__ import annotations

from typing import Any, Dict, Optional

from resilience.recovery.checkpoint import CheckpointStore
from resilience.recovery.rollback import RollbackManager
from resilience.recovery.state_restore import StateRestore

__all__ = ["RecoveryManager"]


class RecoveryManager:
    """Coordinates checkpointing, rollback, and restore."""

    def __init__(self) -> None:
        self.checkpoints = CheckpointStore()
        self.rollback = RollbackManager()
        self.restore = StateRestore(self.checkpoints)

    def checkpoint(self, name: str, state: Dict[str, Any]) -> None:
        """Save a checkpoint."""
        self.checkpoints.save(name, state)

    def recover(self, name: str) -> Optional[Dict[str, Any]]:
        """Roll back then restore *name*'s state."""
        self.rollback.rollback()
        return self.restore.restore(name)
