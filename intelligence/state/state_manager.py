"""StateManager - manages state transitions and versioning."""

from typing import Any, Dict, List, Optional


class StateManager:
    """Manages state transitions and version tracking."""

    def __init__(self) -> None:
        """Initialize state manager."""
        self._current_version: int = 0
        self._history: List[Dict[str, Any]] = []
        self._max_history = 50

    def transition(self, new_state: Dict[str, Any]) -> int:
        """Transition to a new state version.

        Args:
            new_state: New state contents.

        Returns:
            int: New version number.
        """
        self._current_version += 1
        record = {"version": self._current_version, "state": new_state, "timestamp": __import__("time").time()}
        self._history.append(record)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        return self._current_version

    def get_version(self) -> int:
        """Get current version.

        Returns:
            int: Current version.
        """
        return self._current_version

    def get_history(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get transition history.

        Args:
            n: Optional number of recent entries.

        Returns:
            List[Dict[str, Any]]: History entries.
        """
        if n:
            return self._history[-n:]
        return list(self._history)

    def get_state_at_version(self, version: int) -> Optional[Dict[str, Any]]:
        """Get state as it was at a specific version.

        Args:
            version: Version number.

        Returns:
            Optional[Dict[str, Any]]: State at that version.
        """
        for record in self._history:
            if record["version"] == version:
                return record["state"]
        return None

    def reset(self) -> None:
        """Reset state manager."""
        self._current_version = 0
        self._history = []

</final_file_content>
</write_to_file>