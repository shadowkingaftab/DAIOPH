"""Catastrophic forgetting detection from accuracy snapshots."""

from __future__ import annotations

from typing import Dict, List, Optional

__all__ = ["ForgettingDetector"]


class ForgettingDetector:
    """Compares per-task accuracy snapshots to detect regressions.

    Snapshots are recorded per task; ``forgetting`` is the drop from the
    best historical accuracy to the current one.
    """

    def __init__(self, threshold: float = 0.05) -> None:
        if threshold < 0.0:
            raise ValueError("threshold must be >= 0")
        self._threshold = threshold
        self._best: Dict[str, float] = {}
        self._current: Dict[str, float] = {}

    def record(self, task: str, accuracy: float) -> bool:
        """Record an accuracy for *task*; returns True when forgetting.

        Forgetting is signaled when the drop from the best recorded
        accuracy exceeds the threshold.
        """
        if not 0.0 <= accuracy <= 1.0:
            raise ValueError("accuracy must be within [0, 1]")
        self._current[task] = accuracy
        best = self._best.get(task)
        if best is None or accuracy > best:
            self._best[task] = accuracy
            return False
        return (best - accuracy) > self._threshold

    def forgetting(self, task: str) -> Optional[float]:
        """Current forgetting amount for *task* (best - current), or None."""
        if task not in self._best or task not in self._current:
            return None
        return self._best[task] - self._current[task]

    def is_forgetting(self, task: str) -> bool:
        """True when forgetting exceeds the threshold."""
        amount = self.forgetting(task)
        return amount is not None and amount > self._threshold

    def tasks(self) -> List[str]:
        """Tracked tasks in first-recorded order."""
        seen: List[str] = []
        for task in list(self._best) + list(self._current):
            if task not in seen:
                seen.append(task)
        return seen
