from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MemoryEntry:
    """A single memory entry stored by an agent.

    Attributes:
        key: Unique key identifying the memory entry.
        value: The stored value.
        timestamp: Optional timestamp of when the entry was created.
        metadata: Arbitrary metadata associated with the entry.
    """

    key: str
    value: Any
    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation of the entry."""
        return {
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class AgentMemory:
    """In-memory storage for agent state and knowledge.

    Provides a simple key-value store with history tracking.
    """

    def __init__(self) -> None:
        self._entries: Dict[str, MemoryEntry] = {}
        self._history: List[MemoryEntry] = []

    def store(self, key: str, value: Any, **metadata: Any) -> None:
        """Store a value under the given key.

        Args:
            key: The key to store the value under.
            value: The value to store.
            **metadata: Optional metadata to associate with the entry.
        """
        entry = MemoryEntry(key=key, value=value, metadata=metadata)
        self._entries[key] = entry
        self._history.append(entry)

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value by key.

        Args:
            key: The key to look up.

        Returns:
            The stored value, or None if the key is not present.
        """
        entry = self._entries.get(key)
        return entry.value if entry is not None else None

    def contains(self, key: str) -> bool:
        """Check if a key exists in memory."""
        return key in self._entries

    def remove(self, key: str) -> bool:
        """Remove a key from memory.

        Returns:
            True if the key was removed, False if it did not exist.
        """
        if key in self._entries:
            del self._entries[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all entries from memory."""
        self._entries.clear()
        self._history.clear()

    def keys(self) -> List[str]:
        """Return all keys currently in memory."""
        return list(self._entries.keys())

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return the history of stored entries.

        Args:
            limit: Optional maximum number of entries to return.

        Returns:
            List of serialized memory entries.
        """
        history = self._history if limit is None else self._history[-limit:]
        return [entry.to_dict() for entry in history]

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation of all memory."""
        return {
            key: entry.to_dict() for key, entry in self._entries.items()
        }