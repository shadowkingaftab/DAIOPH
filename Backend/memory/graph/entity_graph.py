"""EntityGraph - manages entity relationships."""

from typing import Any, Dict, List, Optional


class EntityGraph:
    """Manages entity relationships in a graph."""

    def __init__(self) -> None:
        """Initialize the entity graph."""
        self._entities: Dict[str, Dict[str, Any]] = {}
        self._relations: List[Dict[str, Any]] = []

    def add_entity(self, entity_id: str, data: Dict[str, Any]) -> None:
        """Add an entity.

        Args:
            entity_id: Entity identifier.
            data: Entity data.
        """
        self._entities[entity_id] = data

    def add_relation(self, source: str, target: str, relation_type: str) -> None:
        """Add a relation between entities.

        Args:
            source: Source entity ID.
            target: Target entity ID.
            relation_type: Relation type.
        """
        self._relations.append({"source": source, "target": target, "type": relation_type})

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity.

        Args:
            entity_id: Entity identifier.

        Returns:
            Optional[Dict[str, Any]]: Entity data or None.
        """
        return self._entities.get(entity_id)

    def get_relations(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get relations for an entity.

        Args:
            entity_id: Entity identifier.

        Returns:
            List[Dict[str, Any]]: Related entities.
        """
        return [r for r in self._relations if r["source"] == entity_id or r["target"] == entity_id]

</final_file_content>
</write_to_file></tool_call>