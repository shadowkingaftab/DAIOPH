"""Concept drift detection over a rolling accuracy window."""

from __future__ import annotations

from collections import deque
from typing import Deque, List, Optional

__all__ = ["DriftDetector"]


class DriftDetector:
    """Flags drift when recent performance drops below a baseline margin.

    A long window tracks the stable baseline; a short window tracks
    recent behavior. Drift is signaled when the recent mean falls below
    ``baseline_mean - threshold``.
    """

    def __init__(
        self,
        window_size: int = 50,
        recent_size: int = 10,
        threshold: float = 0.1,
    ) -> None:
        if window_size < 2 or recent_size < 1:
            raise ValueError("window_size >= 2 and recent_size >= 1 required")
        if recent_size > window_size:
            raise ValueError("recent_size must not exceed window_size")
        if threshold < 0.0:
            raise ValueError("threshold must be >= 0")
        self._baseline: Deque[float] = deque(maxlen=window_size)
        self._recent: Deque[float] = deque(maxlen=recent_size)
        self._threshold = threshold

    def observe(self, value: float) -> bool:
        """Record a performance value; returns True when drift is detected."""
        self._baseline.append(value)
        self._recent.append(value)
        if len(self._recent) < self._recent.maxlen:
            return False
        if len(self._baseline) < 2:
            return False
        baseline_mean = sum(self._baseline) / len(self._baseline)
        recent_mean = sum(self._recent) / len(self._recent)
        return recent_mean < baseline_mean - self._threshold

    def baseline_mean(self) -> Optional[float]:
        """Mean of the baseline window, or None when empty."""
        if not self._baseline:
            return None
        return sum(self._baseline) / len(self._baseline)

    def recent_mean(self) -> Optional[float]:
        """Mean of the recent window, or None when empty."""
        if not self._recent:
            return None
        return sum(self._recent) / len(self._recent)

    def reset(self) -> None:
        """Clear both windows."""
        self._baseline.clear()
        self._recent.clear()

    def history(self) -> List[float]:
        """Baseline window contents (oldest first)."""
        return list(self._baseline)
