from __future__ import annotations

from typing import Any, Dict


class Synchronizer:
    """Synchronizes state across distributed nodes."""

    def __init__(self) -> None:
        self.state: Dict[str, Any] = {}
        self.version: int = 0

    def update_state(self, key: str, value: Any) -> None:
        """Update a state key and increment the version."""
        self.state[key] = value
        self.version += 1

    def get_state(self, key: str) -> Any:
        """Return the value for a state key."""
        return self.state.get(key)

    def get_all_state(self) -> Dict[str, Any]:
        """Return the full state dictionary."""
        return dict(self.state)

    def get_version(self) -> int:
        """Return the current state version."""
        return self.version

    def merge(self, other: Dict[str, Any]) -> None:
        """Merge state from another node."""
        self.state.update(other)
        self.version += 1

    def reset(self) -> None:
        """Reset the synchronizer state."""
        self.state.clear()
        self.version = 0