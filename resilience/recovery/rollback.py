"""Rollback manager (undo stack)."""

from __future__ import annotations

from typing import Any, Callable, List

__all__ = ["RollbackManager"]


class RollbackManager:
    """Executes registered undo callbacks in reverse order."""

    def __init__(self) -> None:
        self._undo: List[Callable[[], None]] = []

    def register(self, undo: Callable[[], None]) -> None:
        """Register an undo callback."""
        self._undo.append(undo)

    def rollback(self) -> int:
        """Run all undo callbacks in reverse; returns count executed."""
        count = 0
        for undo in reversed(self._undo):
            undo()
            count += 1
        self._undo.clear()
        return count
