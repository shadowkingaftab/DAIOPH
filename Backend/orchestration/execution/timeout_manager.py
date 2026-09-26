"""Hard-timeout execution helpers.

Runs a callable in a worker thread and enforces a deadline. If the deadline
expires, the caller gets a :class:`TimeoutError` immediately; the worker
thread itself cannot be killed (a Python limitation) and is documented as
leaked-but-abandoned. Handlers should therefore be cooperative where
possible (see :mod:`orchestration.execution.cancellation`).
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Optional, Tuple

__all__ = ["run_with_timeout", "TimeoutManager"]

logger = logging.getLogger(__name__)

_SHARED_POOL = ThreadPoolExecutor(max_workers=8, thread_name_prefix="daioph-timeout")


def run_with_timeout(
    fn: Callable[..., Any],
    args: Tuple = (),
    kwargs: None | dict = None,
    timeout: float = 30.0,
) -> Any:
    """Call ``fn(*args, **kwargs)`` and return its result within *timeout*.

    Raises:
        ValueError: If *timeout* is not positive.
        TimeoutError: If *fn* did not finish in time. The worker thread is
            abandoned (it keeps running in the background); this is
            documented behaviour, not silent fake success.
    """
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    future = _SHARED_POOL.submit(fn, *args, **(kwargs or {}))
    try:
        return future.result(timeout=timeout)
    except TimeoutError:
        raise
    except Exception:
        future.cancel()
        raise


class TimeoutManager:
    """Configurable wrapper applying a default timeout to callables."""

    def __init__(self, default_timeout: float = 30.0) -> None:
        if default_timeout <= 0:
            raise ValueError("default_timeout must be positive")
        self.default_timeout = float(default_timeout)

    def run(
        self,
        fn: Callable[..., Any],
        args: Tuple = (),
        kwargs: None | dict = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Run *fn* under ``timeout or self.default_timeout`` seconds."""
        return run_with_timeout(
            fn, args=args, kwargs=kwargs, timeout=timeout or self.default_timeout
        )

    def wrap(self, fn: Callable[..., Any], timeout: Optional[float] = None):
        """Return a callable that applies the timeout around *fn*."""

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return self.run(fn, args=args, kwargs=kwargs, timeout=timeout)

        wrapped.__name__ = getattr(fn, "__name__", "wrapped")
        return wrapped
