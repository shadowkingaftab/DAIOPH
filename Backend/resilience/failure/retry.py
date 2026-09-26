"""Retry with backoff (deterministic, injectable sleep)."""

from __future__ import annotations

import time
from typing import Any, Callable, Optional

__all__ = ["retry", "RetryExhausted"]


class RetryExhausted(RuntimeError):
    """Raised when all retry attempts fail."""


def retry(
    fn: Callable[[], Any],
    attempts: int = 3,
    base_delay: float = 0.1,
    backoff: float = 2.0,
    sleep: Optional[Callable[[float], None]] = None,
) -> Any:
    """Call *fn* up to *attempts* times with exponential backoff.

    *sleep* is injectable for deterministic tests (defaults to time.sleep).
    """
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    sleeper = sleep or time.sleep
    last_error: Optional[Exception] = None
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - retryable
            last_error = exc
            if attempt < attempts - 1:
                sleeper(base_delay * (backoff ** attempt))
    raise RetryExhausted(f"all {attempts} attempts failed: {last_error}")
