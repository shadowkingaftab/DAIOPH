"""Typed relations between entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

__all__ = ["Relation", "RelationStore"]


@dataclass(frozen=True)
class Relation:
    """A directed, typed relation: subject -predicate-> object."""

    subject: str
    predicate: str
    object: str


class RelationStore:
    """Store of relations with indexed lookups by subject and object."""

    def __init__(self) -> None:
        self._relations: List[Relation] = []
        self._by_subject: Dict[str, List[Relation]] = {}
        self._by_object: Dict[str, List[Relation]] = {}

    def add(self, relation: Relation) -> Relation:
        """Add a relation (duplicate triples are ignored)."""
        if relation not in self._relations:
            self._relations.append(relation)
            self._by_subject.setdefault(relation.subject, []).append(relation)
            self._by_object.setdefault(relation.object, []).append(relation)
        return relation

    def by_subject(
        self, subject: str, predicate: Optional[str] = None
    ) -> List[Relation]:
        """Relations with *subject*, optionally filtered by predicate."""
        rels = self._by_subject.get(subject, [])
        if predicate is None:
            return list(rels)
        return [r for r in rels if r.predicate == predicate]

    def by_object(
        self, obj: str, predicate: Optional[str] = None
    ) -> List[Relation]:
        """Relations with *object*, optionally filtered by predicate."""
        rels = self._by_object.get(obj, [])
        if predicate is None:
            return list(rels)
        return [r for r in rels if r.predicate == predicate]

    def all_relations(self) -> List[Relation]:
        """All relations in insertion order."""
        return list(self._relations)

    def objects_of(self, subject: str, predicate: str) -> List[str]:
        """Object ids for (subject, predicate) pairs."""
        return [r.object for r in self.by_subject(subject, predicate)]

    def subjects_of(self, obj: str, predicate: str) -> List[str]:
        """Subject ids for (predicate, object) pairs."""
        return [r.subject for r in self.by_object(obj, predicate)]

    def __len__(self) -> int:
        return len(self._relations)
