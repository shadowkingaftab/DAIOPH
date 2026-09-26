"""WorkingMemory - temporary storage for cognitive processing."""

from typing import Any, Dict, List, Optional


class WorkingMemory:
    """Temporary workspace for active cognitive processing."""

    def __init__(self, capacity: int = 7) -> None:
        """Initialize working memory.

        Args:
            capacity: Maximum number of items.
        """
        self._capacity = capacity
        self._storage: Dict[str, Any] = {}
        self._access_order: List[str] = []
        self._access_limit = capacity

    def store(self, key: str, value: Any) -> None:
        """Store a value in working memory.

        Args:
            key: Storage key.
            value: Value to store.
        """
        if key in self._storage:
            self._access_order.remove(key)
        elif len(self._storage) >= self._capacity:
            # Evict oldest
            oldest = self._access_order.pop(0)
            del self._storage[oldest]
        self._storage[key] = value
        self._access_order.append(key)

    def retrieve(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from working memory.

        Args:
            key: Storage key.
            default: Default if not found.

        Returns:
            Any: Stored value or default.
        """
        return self._storage.get(key, default)

    def clear(self) -> None:
        """Clear all working memory."""
        self._storage = {}
        self._access_order = []

    def get_all(self) -> Dict[str, Any]:
        """Get all stored items.

        Returns:
            Dict[str, Any]: All stored items.
        """
        return dict(self._storage)

    def get_recent(self, n: int = 1) -> List[Any]:
        """Get the n most recently accessed items.

        Args:
            n: Number of recent items.

        Returns:
            List[Any]: Recent items.
        """
        recent_keys = self._access_order[-n:] if n <= len(self._access_order) else self._access_order
        return [self._storage.get(k) for k in recent_keys if k in self._storage]

    def reset(self) -> None:
        """Reset working memory."""
        self._storage = {}
        self._access_order = []

</final_file_content>
</write_to_file>