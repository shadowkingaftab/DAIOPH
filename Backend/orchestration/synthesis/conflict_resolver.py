"""Resolves conflicting outputs when several tasks address the same question."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Hashable, List, Optional, Tuple

__all__ = ["ConflictResolver"]


class ConflictResolver:
    """Picks a winning value among candidates using a named strategy.

    Strategies:
        - ``"priority"``: first non-None candidate in priority order.
        - ``"majority"``: most frequent hashable value (ties → insertion order).
        - ``"first"`` / ``"last"``: positional selection among non-None values.
    """

    STRATEGIES = ("priority", "majority", "first", "last")

    def resolve(
        self,
        candidates: Dict[str, Any],
        strategy: str = "priority",
        priorities: Optional[List[str]] = None,
    ) -> Tuple[Optional[Any], str]:
        """Choose a winner from *candidates* (task_id → value).

        Returns:
            ``(winner_value_or_None, strategy_applied)``. Returns ``(None,
            strategy)`` when there are no non-None candidates — an honest
            "no consensus" outcome, never a fabricated answer.
        """
        if strategy not in self.STRATEGIES:
            raise ValueError(f"unknown strategy {strategy!r}")
        non_none = {k: v for k, v in candidates.items() if v is not None}
        if not non_none:
            return None, strategy

        if strategy == "priority":
            order = priorities or list(non_none.keys())
            for key in order:
                if key in non_none:
                    return non_none[key], strategy
            return next(iter(non_none.values())), strategy

        if strategy == "majority":
            try:
                counts: Counter = Counter(
                    v for v in non_none.values() if isinstance(v, Hashable)
                )
                if counts:
                    winner = counts.most_common(1)[0][0]
                    return winner, strategy
            except TypeError:  # pragma: no cover - unhashable majority
                pass
            return next(iter(non_none.values())), strategy

        values = list(non_none.values())
        if strategy == "last":
            return values[-1], strategy
        return values[0], strategy
