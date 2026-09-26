"""Deduplicator - removes duplicate memories."""

from typing import Any, Dict, List, Optional


class Deduplicator:
    """Removes duplicate memories across stores."""

    def __init__(self) -> None:
        """Initialize the deduplicator."""
        self._seen: set = set()

    def is_duplicate(self, item: Dict[str, Any]) -> bool:
        """Check if an item is a duplicate.

        Args:
            item: Item to check.

        Returns:
            bool: True if duplicate.
        """
        key = str(sorted(item.items()))
        if key in self._seen:
            return True
        self._seen.add(key)
        return False

    def deduplicate(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates from a list.

        Args:
            items: Items to deduplicate.

        Returns:
            List[Dict[str, Any]]: Deduplicated items.
        """
        result = []
        for item in items:
            if not self.is_duplicate(item):
                result.append(item)
        return result

</final_file_content>
</write_to_file></tool_call>