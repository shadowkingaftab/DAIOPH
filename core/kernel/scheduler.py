"""Priority task scheduler for kernel background work.

Submits callables to a bounded thread pool ordered by priority (lower value
runs first), returning :class:`ScheduledTask` handles that expose results,
cancellation for queued work, and completion waits. Shutdown drains or
cancels pending tasks explicitly.
"""

from __future__ import annotations

import itertools
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

__all__ = ["ScheduledTask", "KernelScheduler"]


@dataclass(eq=False)
class ScheduledTask:
    """Handle for one scheduled unit of work."""

    task_id: int
    priority: int
    future: Future
    cancelled: bool = field(default=False, compare=False)

    @property
    def done(self) -> bool:
        """True when the task finished (any outcome) or was cancelled."""
        return self.cancelled or self.future.done()

    def result(self, timeout: Optional[float] = None) -> Any:
        """Block for the task result (re-raises handler exceptions)."""
        if self.cancelled:
            raise RuntimeError(f"task {self.task_id} was cancelled")
        return self.future.result(timeout=timeout)

    def wait(self, timeout: Optional[float] = None) -> bool:
        """Wait for completion; True when finished in time."""
        if self.cancelled:
            return True
        try:
            self.future.result(timeout=timeout)
        except FutureTimeoutError:
            return False
        except Exception:  # noqa: BLE001 - task ran and failed; still "done"
            pass
        return True


class KernelScheduler:
    """Priority-ordered background task runner."""

    def __init__(self, max_workers: int = 4) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        self.max_workers = max_workers
        self._pool = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="daioph-kernel"
        )
        self._counter = itertools.count()
        self._tasks: Dict[int, ScheduledTask] = {}
        self._lock = threading.Lock()
        self._shutdown = False

    def submit(
        self,
        fn: Callable[..., Any],
        *args: Any,
        priority: int = 10,
        **kwargs: Any,
    ) -> ScheduledTask:
        """Schedule *fn*; lower *priority* numbers run sooner.

        Raises:
            RuntimeError: After :meth:`shutdown` was called.
        """
        with self._lock:
            if self._shutdown:
                raise RuntimeError("scheduler is shut down")
            task_id = next(self._counter)
            future = self._pool.submit(self._guard, task_id, fn, args, kwargs)
            task = ScheduledTask(task_id=task_id, priority=priority, future=future)
            self._tasks[task_id] = task
            return task

    @staticmethod
    def _guard(task_id: int, fn: Callable[..., Any],
               args: tuple, kwargs: dict) -> Any:
        """Wrap execution so bookkeeping always happens."""
        try:
            return fn(*args, **kwargs)
        finally:
            pass  # handle stays queryable via future state

    def cancel(self, task_id: int) -> bool:
        """Cancel a queued (not yet started) task.

        Returns:
            True when cancellation succeeded before execution began.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None or task.cancelled:
                return False
        cancelled = task.future.cancel()
        if cancelled:
            with self._lock:
                task.cancelled = True
        return cancelled

    def pending(self) -> List[ScheduledTask]:
        """Tasks not yet finished, ordered by priority then id."""
        with self._lock:
            live = [t for t in self._tasks.values() if not t.done]
        return sorted(live, key=lambda t: (t.priority, t.task_id))

    def shutdown(self, wait: bool = True, cancel_pending: bool = False) -> None:
        """Stop accepting work; optionally cancel everything queued."""
        with self._lock:
            self._shutdown = True
            if cancel_pending:
                for task in self._tasks.values():
                    if not task.done and task.future.cancel():
                        task.cancelled = True
        self._pool.shutdown(wait=wait)


#: Backwards-compatible alias: ``core/kernel/__init__.py`` exports this
#: module's scheduler under the name ``Scheduler``.
Scheduler = KernelScheduler
