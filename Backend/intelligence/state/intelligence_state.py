"""IntelligenceState - central state container for intelligence subsystem."""

from typing import Any, Dict, List, Optional


class IntelligenceState:
    """Central state container aggregating all intelligence components."""

    def __init__(self) -> None:
        """Initialize intelligence state."""
        self._state: Dict[str, Any] = {}
        self._version: int = 0
        self._observers: List[str] = []

    def update(self, key: str, value: Any) -> None:
        """Update a state value.

        Args:
            key: State key.
            value: Value to set.
        """
        self._state[key] = value
        self._version += 1

    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value.

        Args:
            key: State key.
            default: Default if not found.

        Returns:
            Any: State value or default.
        """
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a state value.

        Args:
            key: State key.
            value: Value to set.
        """
        self._state[key] = value

    def get_all(self) -> Dict[str, Any]:
        """Get all state.

        Returns:
            Dict[str, Any]: Full state dict.
        """
        return dict(self._state)

    def get_version(self) -> int:
        """Get current state version.

        Returns:
            int: Version number.
        """
        return self._version

    def add_observer(self, observer_id: str) -> None:
        """Add an observer.

        Args:
            observer_id: Observer identifier.
        """
        self._observers.append(observer_id)

    def remove_observer(self, observer_id: str) -> None:
        """Remove an observer.

        Args:
            observer_id: Observer identifier.
        """
        self._observers = [o for o in self._observers if o != observer_id]

    def get_observers(self) -> List[str]:
        """Get observer list.

        Returns:
            List[str]: Observer identifiers.
        """
        return list(self._observers)

    def reset(self) -> None:
        """Reset intelligence state."""
        self._state = {}
        self._version = 0
        self._observers = []

</final_file_content>
</write_to_file>