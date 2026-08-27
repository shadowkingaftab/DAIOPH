"""Circuit breaker (closed/open/half-open)."""

from __future__ import annotations

import time
from enum import Enum
from typing import Any, Callable, Optional

__all__ = ["CircuitState", "CircuitOpenError", "CircuitBreaker"]


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(RuntimeError):
    """Raised when the circuit is open and calls are rejected."""


class CircuitBreaker:
    """Trips open after *failure_threshold* consecutive failures."""

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 30.0,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = CircuitState.CLOSED
        self._failures = 0
        self._opened_at: Optional[float] = None
        self._lock = threading.Lock()

    def call(self, fn: Callable[[], Any]) -> Any:
        """Invoke *fn* if the circuit allows; else raise CircuitOpenError."""
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._opened_at is not None and                         time.time() - self._opened_at >= self.reset_timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitOpenError("circuit is open")
        try:
            result = fn()
        except Exception:
            with self._lock:
                self._failures += 1
                if self._failures >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    self._opened_at = time.time()
            raise
        with self._lock:
            self._failures = 0
            self.state = CircuitState.CLOSED
        return result
