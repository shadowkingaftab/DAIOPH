"""Cooperative cancellation for task execution.

:class:`CancellationToken` is a thread-safe, cooperative cancellation signal.
Executors check it between tasks (and handlers may check it inside long
work); cancelling never kills a running thread — it only prevents *new*
work from starting and lets cooperative handlers abort cleanly.

Example:
    >>> token = CancellationToken()
    >>> token.cancelled
    False
    >>> token.cancel("user requested stop")
    >>> token.cancelled
    True
    >>> token.reason
    'user requested stop'
"""

from __future__ import annotations

import threading
import time
from typing import List, Optional

__all__ = ["CancellationToken", "CancelledError"]


class CancelledError(RuntimeError):
    """Raised when work is attempted on a cancelled token."""


class CancellationToken:
    """Thread-safe cooperative cancellation signal.

    Attributes:
        cancelled: True once :meth:`cancel` has been called.
        reason: Human-readable reason supplied to :meth:`cancel`.
    """

    def __init__(self) -> None:
        self._event = threading.Event()
        self._reason: Optional[str] = None
        self._cancelled_at: Optional[float] = None
        self._callbacks: List = []
        self._lock = threading.Lock()

    @property
    def cancelled(self) -> bool:
        """True if cancellation has been requested."""
        return self._event.is_set()

    @property
    def reason(self) -> Optional[str]:
        """Reason passed to :meth:`cancel`, or None."""
        return self._reason

    @property
    def cancelled_at(self) -> Optional[float]:
        """Unix timestamp of cancellation, or None."""
        return self._cancelled_at

    def cancel(self, reason: str = "cancelled") -> None:
        """Request cancellation exactly once; later calls are no-ops.

        Args:
            reason: Why cancellation was requested (stored and logged).
        """
        with self._lock:
            if self._event.is_set():
                return
            self._reason = reason or "cancelled"
            self._cancelled_at = time.time()
            callbacks = list(self._callbacks)
            self._event.set()
        # Fire callbacks outside the lock so they may inspect the token.
        for callback in callbacks:
            try:
                callback(self)
            except Exception:  # noqa: BLE001 - callbacks must not break cancel
                pass

    def raise_if_cancelled(self) -> None:
        """Raise :class:`CancelledError` if the token is cancelled."""
        if self.cancelled:
            raise CancelledError(self._reason or "cancelled")

    def check(self) -> bool:
        """Convenience predicate for handler loops: ``while token.check():``"""
        return not self.cancelled

    def add_callback(self, callback) -> None:
        """Register *callback(token)* invoked once upon cancellation.

        If the token is already cancelled the callback fires immediately.
        """
        with self._lock:
            if self._event.is_set():
                fire_now = True
            else:
                self._callbacks.append(callback)
                fire_now = False
        if fire_now:
            try:
                callback(self)
            except Exception:  # noqa: BLE001
                pass

    def wait(self, timeout: Optional[float] = None) -> bool:
        """Block until cancelled (or *timeout* seconds elapse).

        Returns:
            True if the token became cancelled, False on timeout.
        """
        return self._event.wait(timeout)

    def __repr__(self) -> str:
        state = f"cancelled(reason={self._reason!r})" if self.cancelled else "active"
        return f"<CancellationToken {state}>"