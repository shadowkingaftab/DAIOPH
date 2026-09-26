"""Entities and an entity store."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

__all__ = ["Entity", "EntityStore"]


@dataclass(frozen=True)
class Entity:
    """A named entity with an ontology type and free-form attributes."""

    entity_id: str
    name: str
    entity_type: str
    attributes: Dict[str, str] = field(default_factory=dict)


class EntityStore:
    """Insertion-ordered store of entities keyed by id."""

    def __init__(self) -> None:
        self._entities: Dict[str, Entity] = {}

    def add(self, entity: Entity) -> Entity:
        """Add an entity; raises ValueError on duplicate id."""
        if entity.entity_id in self._entities:
            raise ValueError(f"duplicate entity id: {entity.entity_id!r}")
        self._entities[entity.entity_id] = entity
        return entity

    def get(self, entity_id: str) -> Optional[Entity]:
        """Fetch an entity by id, or None."""
        return self._entities.get(entity_id)

    def require(self, entity_id: str) -> Entity:
        """Fetch an entity or raise KeyError."""
        try:
            return self._entities[entity_id]
        except KeyError:
            raise KeyError(f"unknown entity: {entity_id!r}") from None

    def by_type(self, entity_type: str) -> List[Entity]:
        """All entities of *entity_type* in insertion order."""
        return [
            e for e in self._entities.values() if e.entity_type == entity_type
        ]

    def find_by_name(self, name: str) -> List[Entity]:
        """Case-insensitive name lookup."""
        lowered = name.lower()
        return [e for e in self._entities.values() if e.name.lower() == lowered]

    def __len__(self) -> int:
        return len(self._entities)
