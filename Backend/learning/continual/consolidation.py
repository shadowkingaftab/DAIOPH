"""Knowledge consolidation: merge new facts with importance weighting."""

from __future__ import annotations

from typing import Dict, List, Optional

__all__ = ["Consolidator"]


class Consolidator:
    """Merges incoming facts into a consolidated knowledge dict.

    Each fact carries an importance in [0, 1]. When a fact already exists,
    the higher importance wins and the value is overwritten; the winner
    count is tracked so callers can inspect merge behavior.
    """

    def __init__(self, decay: float = 0.0) -> None:
        if not 0.0 <= decay <= 1.0:
            raise ValueError("decay must be within [0, 1]")
        self._decay = decay
        self._facts: Dict[str, str] = {}
        self._importance: Dict[str, float] = {}
        self._updates: Dict[str, int] = {}

    def consolidate(
        self, key: str, value: str, importance: float = 0.5
    ) -> bool:
        """Merge one fact; returns True when the stored value changed."""
        if not 0.0 <= importance <= 1.0:
            raise ValueError("importance must be within [0, 1]")
        current_importance = self._importance.get(key)
        if current_importance is None or importance >= current_importance:
            changed = self._facts.get(key) != value
            self._facts[key] = value
            self._importance[key] = max(importance, current_importance or 0.0)
            self._updates[key] = self._updates.get(key, 0) + 1
            return changed
        return False

    def get(self, key: str) -> Optional[str]:
        """Consolidated value for *key*, or None."""
        return self._facts.get(key)

    def importance(self, key: str) -> Optional[float]:
        """Stored importance for *key*, or None."""
        return self._importance.get(key)

    def forget(self, key: str) -> bool:
        """Drop a fact; returns True when something was removed."""
        if key not in self._facts:
            return False
        del self._facts[key]
        self._importance.pop(key, None)
        self._updates.pop(key, None)
        return True

    def keys(self) -> List[str]:
        """Consolidated keys in insertion order."""
        return list(self._facts)

    def __len__(self) -> int:
        return len(self._facts)
