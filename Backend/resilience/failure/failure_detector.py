"""Failure detector (consecutive-failure based)."""

from __future__ import annotations

import threading
from typing import Optional

__all__ = ["FailureDetector"]


class FailureDetector:
    """Tracks consecutive failures and reports suspected failures."""

    def __init__(self, threshold: int = 3) -> None:
        if threshold < 1:
            raise ValueError("threshold must be >= 1")
        self.threshold = threshold
        self._failures = 0
        self._lock = threading.Lock()

    def record_success(self) -> None:
        """Reset the failure counter."""
        with self._lock:
            self._failures = 0

    def record_failure(self) -> bool:
        """Increment failures; True when the threshold is reached."""
        with self._lock:
            self._failures += 1
            return self._failures >= self.threshold

    def is_suspected(self) -> bool:
        """True when the failure threshold has been reached."""
        with self._lock:
            return self._failures >= self.threshold
