"""Worker-slot accounting for concurrent compute tasks."""

from __future__ import annotations

import threading
from typing import List, Optional

__all__ = ["NoSlotsAvailable", "ComputeManager"]


class NoSlotsAvailable(RuntimeError):
    """All worker slots are busy and the caller asked not to wait."""


class ComputeManager:
    """Bounded slot pool with FIFO waiting and explicit release."""

    def __init__(self, slots: int) -> None:
        if slots < 1:
            raise ValueError("slots must be >= 1")
        self.slots = slots
        self._busy: List[str] = []
        self._waiters: List[str] = []
        self._lock = threading.Lock()

    def acquire(self, owner: str, block: bool = True) -> bool:
        """Acquire a slot for *owner*.

        Returns:
            True when acquired. With ``block=False``, returns False instead
            of raising when the pool is full.
        """
        with self._lock:
            if owner in self._busy or owner in self._waiters:
                raise ValueError(f"owner already active: {owner!r}")
            if len(self._busy) < self.slots:
                self._busy.append(owner)
                return True
            if not block:
                return False
            self._waiters.append(owner)
        # Simple cooperative handoff loop (adequate for orchestration scale).
        while True:
            with self._lock:
                if self._waiters and self._waiters[0] == owner                         and len(self._busy) < self.slots:
                    self._waiters.remove(owner)
                    self._busy.append(owner)
                    return True
            threading.Event().wait(0.01)

    def release(self, owner: str) -> None:
        """Release *owner*'s slot (no-op when absent)."""
        with self._lock:
            if owner in self._busy:
                self._busy.remove(owner)

    def utilization(self) -> float:
        """Fraction of slots currently busy."""
        with self._lock:
            return round(len(self._busy) / self.slots, 3)
