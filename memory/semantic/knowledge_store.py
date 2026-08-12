"""KnowledgeStore - stores structured knowledge."""

from typing import Any, Dict, List, Optional


class KnowledgeStore:
    """Stores structured knowledge entries."""

    def __init__(self) -> None:
        """Initialize the knowledge store."""
        self._entries: Dict[str, Dict[str, Any]] = {}

    def add(self, key: str, entry: Dict[str, Any]) -> None:
        """Add a knowledge entry.

        Args:
            key: Entry key.
            entry: Entry data.
        """
        self._entries[key] = entry

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a knowledge entry.

        Args:
            key: Entry key.

        Returns:
            Optional[Dict[str, Any]]: Entry or None.
        """
        return self._entries.get(key)

    def query(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """Query entries by field.

        Args:
            field: Field name.
            value: Field value.

        Returns:
            List[Dict[str, Any]]: Matching entries.
        """
        return [e for e in self._entries.values() if e.get(field) == value]

</final_file_content>
</write_to_file></tool_call>