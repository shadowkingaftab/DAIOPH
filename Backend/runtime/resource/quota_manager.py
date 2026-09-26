"""Windowed per-key usage quotas."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, Dict

__all__ = ["QuotaExceeded", "QuotaManager", "QuotaStatus"]


class QuotaExceeded(RuntimeError):
    """The key consumed its allowance within the current window."""


@dataclass(frozen=True)
class QuotaStatus:
    """Remaining allowance for one key."""

    key: str
    limit: int
    used: int
    window_seconds: float

    @property
    def remaining(self) -> int:
        """Calls left in the current window."""
        return max(0, self.limit - self.used)


class QuotaManager:
    """Sliding-window counters enforcing per-key limits."""

    def __init__(self, limit: int, window_seconds: float = 60.0) -> None:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def _prune(self, key: str, now: float) -> None:
        cutoff = now - self.window_seconds
        events = self._events[key]
        while events and events[0] <= cutoff:
            events.popleft()

    def check(self, key: str) -> QuotaStatus:
        """Report remaining allowance without consuming any."""
        with self._lock:
            self._prune(key, time.time())
            return QuotaStatus(key=key, limit=self.limit,
                               used=len(self._events[key]),
                               window_seconds=self.window_seconds)

    def consume(self, key: str, amount: int = 1) -> QuotaStatus:
        """Consume *amount* units for *key*.

        Raises:
            QuotaExceeded: If consumption would exceed the window limit.
        """
        if amount < 1:
            raise ValueError("amount must be >= 1")
        with self._lock:
            now = time.time()
            self._prune(key, now)
            if len(self._events[key]) + amount > self.limit:
                raise QuotaExceeded(
                    f"quota exceeded for {key!r}: limit {self.limit}/"
                    f"{self.window_seconds}s"
                )
            for _ in range(amount):
                self._events[key].append(now)
            return QuotaStatus(key=key, limit=self.limit,
                               used=len(self._events[key]),
                               window_seconds=self.window_seconds)
