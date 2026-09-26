"""SemanticMemory - stores and retrieves semantic knowledge."""

from typing import Any, Dict, List, Optional


class SemanticMemory:
    """Stores and retrieves semantic knowledge."""

    def __init__(self) -> None:
        """Initialize semantic memory."""
        self._knowledge: Dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        """Store a knowledge item.

        Args:
            key: Knowledge key.
            value: Knowledge value.
        """
        self._knowledge[key] = value

    def retrieve(self, key: str, default: Any = None) -> Any:
        """Retrieve a knowledge item.

        Args:
            key: Knowledge key.
            default: Default if not found.

        Returns:
            Any: Knowledge value.
        """
        return self._knowledge.get(key, default)

    def search(self, pattern: str) -> List[Dict[str, Any]]:
        """Search knowledge by pattern.

        Args:
            pattern: Search pattern.

        Returns:
            List[Dict[str, Any]]: Matching items.
        """
        results = []
        for k, v in self._knowledge.items():
            if pattern.lower() in str(k).lower() or pattern.lower() in str(v).lower():
                results.append({"key": k, "value": v})
        return results

</final_file_content>
</write_to_file></tool_call>