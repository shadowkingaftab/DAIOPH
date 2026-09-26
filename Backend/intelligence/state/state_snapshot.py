"""StateSnapshot - snapshots state at a point in time."""

from typing import Any, Dict, Optional, Tuple


class StateSnapshot:
    """Captures a snapshot of state at a point in time."""

    def __init__(self, state: Dict[str, Any], version: int, timestamp: Optional[float] = None) -> None:
        """Initialize state snapshot.

        Args:
            state: State dict to snapshot.
            version: Version number.
            timestamp: Optional timestamp.
        """
        self._state = state
        self._version = version
        self._timestamp = timestamp or __import__("time").time()

    def get_state(self) -> Dict[str, Any]:
        """Get the snapshotled state.

        Returns:
            Dict[str, Any]: State dict.
        """
        return dict(self._state)

    def get_version(self) -> int:
        """Get the snapshot version.

        Returns:
            int: Version number.
        """
        return self._version

    def get_timestamp(self) -> float:
        """Get the snapshot timestamp.

        Returns:
            float: Timestamp.
        """
        return self._timestamp

    def has_changed(self, other: "StateSnapshot") -> bool:
        """Check if this snapshot differs from another.

        Args:
            other: Other snapshot to compare.

        Returns:
            bool: True if different.
        """
        return self._state != other.get_state() or self._version != other.get_version()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize snapshot to dict.

        Returns:
            Dict[str, Any]: Serialized snapshot.
        """
        return {
            "state": self._state,
            "version": self._version,
            "timestamp": self._timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateSnapshot":
        """Create snapshot from dict.

        Args:
            data: Snapshot data.

        Returns:
            StateSnapshot: New snapshot.
        """
        return cls(
            state=data.get("state", {}),
            version=data.get("version", 0),
            timestamp=data.get("timestamp"),
        )

    def reset(self) -> None:
        """Reset snapshot."""
        self._state = {}
        self._version = 0
        self._timestamp = None

</final_file_content>
</write_to_file>