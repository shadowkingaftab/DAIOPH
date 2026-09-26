"""ShortTermMemory - manages short-term memory storage."""

from typing import Any, Dict, List, Optional


class ShortTermMemory:
    """Manages short-term memory with limited capacity."""

    def __init__(self, capacity: int = 100) -> None:
        """Initialize short-term memory.

        Args:
            capacity: Maximum number of items.
        """
        self._capacity = capacity
        self._storage: List[Dict[str, Any]] = []

    def add(self, item: Dict[str, Any]) -> None:
        """Add an item to memory.

        Args:
            item: Memory item to add.
        """
        if len(self._storage) >= self._capacity:
            self._storage.pop(0)
        self._storage.append(item)

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all memory items.

        Returns:
            List[Dict[str, Any]]: All items.
        """
        return list(self._storage)

    def clear(self) -> None:
        """Clear all memory."""
        self._storage = []

</final_file_content>
</write_to_file></tool_call>