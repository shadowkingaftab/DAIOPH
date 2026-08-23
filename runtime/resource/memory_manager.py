"""Memory budget accounting for concurrent work."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Dict, Optional

__all__ = ["MemoryBudgetExceeded", "MemoryManager"]


class MemoryBudgetExceeded(RuntimeError):
    """Requested allocation would exceed the configured budget."""


@dataclass(frozen=True)
class BudgetStatus:
    """Current budget utilisation."""

    budget_bytes: int
    reserved_bytes: int

    @property
    def available_bytes(self) -> int:
        """Bytes still reservable."""
        return max(0, self.budget_bytes - self.reserved_bytes)

    @property
    def percent_used(self) -> float:
        """Budget utilisation percentage."""
        if self.budget_bytes <= 0:
            return 100.0
        return round(self.reserved_bytes / self.budget_bytes * 100.0, 1)


class MemoryManager:
    """Track reservations against a byte budget (advisory accounting)."""

    def __init__(self, budget_bytes: int) -> None:
        if budget_bytes <= 0:
            raise ValueError("budget_bytes must be positive")
        self.budget_bytes = budget_bytes
        self._reserved: Dict[str, int] = {}
        self._lock = threading.Lock()

    def reserve(self, owner: str, nbytes: int) -> None:
        """Reserve *nbytes* for *owner*.

        Raises:
            MemoryBudgetExceeded: If the reservation would overflow budget.
            ValueError: On non-positive sizes or duplicate owners.
        """
        if nbytes <= 0:
            raise ValueError("nbytes must be positive")
        with self._lock:
            if owner in self._reserved:
                raise ValueError(f"owner already holds a reservation: {owner!r}")
            projected = sum(self._reserved.values()) + nbytes
            if projected > self.budget_bytes:
                raise MemoryBudgetExceeded(
                    f"reservation of {nbytes} bytes for {owner!r} exceeds "
                    f"budget ({projected}/{self.budget_bytes})"
                )
            self._reserved[owner] = nbytes

    def release(self, owner: str) -> None:
        """Release *owner*'s reservation (no-op when absent)."""
        with self._lock:
            self._reserved.pop(owner, None)

    def status(self) -> BudgetStatus:
        """Current utilisation snapshot."""
        with self._lock:
            return BudgetStatus(
                budget_bytes=self.budget_bytes,
                reserved_bytes=sum(self._reserved.values()),
            )
