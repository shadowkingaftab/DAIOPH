"""RelationStore - stores graph relations."""

from typing import Any, Dict, List, Optional


class RelationStore:
    """Stores graph relations between entities."""

    def __init__(self) -> None:
        """Initialize the relation store."""
        self._relations: List[Dict[str, Any]] = []

    def add(self, source: str, target: str, relation_type: str, weight: float = 1.0) -> None:
        """Add a relation.

        Args:
            source: Source entity.
            target: Target entity.
            relation_type: Relation type.
            weight: Relation weight.
        """
        self._relations.append({"source": source, "target": target, "type": relation_type, "weight": weight})

    def get(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get a relation.

        Args:
            source: Source entity.
            target: Target entity.

        Returns:
            Optional[Dict[str, Any]]: Relation or None.
        """
        for r in self._relations:
            if r["source"] == source and r["target"] == target:
                return r
        return None

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all relations.

        Returns:
            List[Dict[str, Any]]: All relations.
        """
        return list(self._relations)

</final_file_content>
</write_to_file></tool_call>