"""Ontology: class hierarchy with subclass closure."""

from __future__ import annotations

from typing import Dict, Iterable, List, Set

__all__ = ["Ontology"]


class Ontology:
    """A set of classes with ``subclass_of`` edges and closure queries."""

    def __init__(self) -> None:
        self._parents: Dict[str, List[str]] = {}
        self._classes: List[str] = []
        self._class_set: Set[str] = set()

    def add_class(self, name: str) -> None:
        """Register a class (no-op if present)."""
        if name not in self._class_set:
            self._class_set.add(name)
            self._classes.append(name)
            self._parents.setdefault(name, [])

    def add_subclass(self, child: str, parent: str) -> None:
        """Declare child is-a parent (both classes registered as needed)."""
        self.add_class(child)
        self.add_class(parent)
        parents = self._parents[child]
        if parent not in parents:
            parents.append(parent)

    def classes(self) -> List[str]:
        """All classes in insertion order."""
        return list(self._classes)

    def direct_parents(self, name: str) -> List[str]:
        """Immediate parents of *name*."""
        return list(self._parents.get(name, []))

    def ancestors(self, name: str) -> Set[str]:
        """All transitive parents of *name* (excluding name itself)."""
        seen: Set[str] = set()
        stack = list(self._parents.get(name, []))
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(self._parents.get(current, []))
        return seen

    def is_a(self, child: str, parent: str) -> bool:
        """True when child is parent or a transitive subclass."""
        if child == parent:
            return child in self._class_set
        return parent in self.ancestors(child)

    def descendants(self, parent: str) -> Set[str]:
        """All classes that are (transitively) subclasses of *parent*."""
        result: Set[str] = set()
        for name in self._classes:
            if name != parent and parent in self.ancestors(name):
                result.add(name)
        return result
