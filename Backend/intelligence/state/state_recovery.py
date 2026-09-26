"""StateRecovery - recovers state from snapshots and history."""

from typing import Any, Dict, List, Optional


class StateRecovery:
    """Recovers state from snapshots and transition history."""

    def __init__(self, state_manager: Any, snapshot_manager: Any) -> None:
        """Initialize state recovery.

        Args:
            state_manager: State manager instance.
            snapshot_manager: Snapshot manager instance.
        """
        self._state_manager = state_manager
        self._snapshot_manager = snapshot_manager

    def recover_latest(self) -> Optional[Dict[str, Any]]:
        """Recover the latest state.

        Returns:
            Optional[Dict[str, Any]]: Recovered state.
        """
        # Get latest snapshot
        latest = self._snapshot_manager.get_latest()
        if latest:
            return latest.get_state()
        # Fall back to state manager version
        return self._state_manager.get_state_at_version(
            self._state_manager.get_version()
        )

    def recover_at_version(self, version: int) -> Optional[Dict[str, Any]]:
        """Recover state at a specific version.

        Args:
            version: Version number.

        Returns:
            Optional[Dict[str, Any]]: Recovered state.
        """
        return self._state_manager.get_state_at_version(version)

    def recover_from_history(self, n: int = 1) -> List[Dict[str, Any]]:
        """Recover the last n states from history.

        Args:
            n: Number of states to recover.

        Returns:
            List[Dict[str, Any]]: Recovered states.
        """
        history = self._state_manager.get_history(n)
        return [record["state"] for record in history]

    def reset(self) -> None:
        """Reset state recovery."""
        pass

</final_file_content>
</write_to_file>