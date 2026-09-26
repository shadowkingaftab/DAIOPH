"""Execution engine facade combining executors, timeouts, and reporting.

:class:`ExecutionEngine` is the one-stop entry point used by orchestrators:
choose sequential vs parallel execution, optionally enforce per-task
timeouts, and produce a consolidated report.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from orchestration.execution.cancellation import CancellationToken
from orchestration.execution.parallel_executor import ParallelExecutor
from orchestration.execution.sequential_executor import SequentialExecutor
from orchestration.execution.task_executor import (
    TaskExecutor,
    TaskHandler,
    TaskResult,
    TaskStatus,
)
from orchestration.planning.execution_plan import ExecutionPlan

__all__ = ["ExecutionEngine", "ExecutionReport"]

logger = logging.getLogger(__name__)


@dataclass
class ExecutionReport:
    """Aggregated outcome of executing a whole plan."""

    plan_id: str
    goal: str
    results: Dict[str, TaskResult] = field(default_factory=dict)

    @property
    def succeeded(self) -> int:
        """Count of succeeded tasks."""
        return self._count(TaskStatus.SUCCEEDED)

    @property
    def failed(self) -> int:
        """Count of failed tasks."""
        return self._count(TaskStatus.FAILED)

    @property
    def skipped(self) -> int:
        """Count of skipped tasks (upstream failure)."""
        return self._count(TaskStatus.SKIPPED)

    @property
    def cancelled(self) -> int:
        """Count of cancelled tasks."""
        return self._count(TaskStatus.CANCELLED)

    @property
    def total_duration(self) -> float:
        """Sum of individual task durations (not wall-clock)."""
        return sum(r.duration or 0.0 for r in self.results.values())

    @property
    def all_ok(self) -> bool:
        """True when every task succeeded."""
        return bool(self.results) and self.succeeded == len(self.results)

    def _count(self, status: TaskStatus) -> int:
        return sum(1 for r in self.results.values() if r.status is status)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-friendly dictionary."""
        return {
            "plan_id": self.plan_id,
            "goal": self.goal,
            "all_ok": self.all_ok,
            "counts": {
                "succeeded": self.succeeded,
                "failed": self.failed,
                "skipped": self.skipped,
                "cancelled": self.cancelled,
            },
            "total_duration": self.total_duration,
            "results": {tid: r.to_dict() for tid, r in self.results.items()},
        }


class ExecutionEngine:
    """Configurable facade over the executor implementations."""

    def __init__(
        self,
        parallel: bool = True,
        max_workers: int = 4,
        default_timeout: Optional[float] = None,
        token: Optional[CancellationToken] = None,
        on_task_done: Optional[Callable[[TaskResult], None]] = None,
    ) -> None:
        self._executor: TaskExecutor
        if parallel:
            self._executor = ParallelExecutor(
                max_workers=max_workers, token=token, on_task_done=on_task_done
            )
        else:
            self._executor = SequentialExecutor(token=token, on_task_done=on_task_done)
        self._timeout = default_timeout
        self._token = token

    def run(self, plan: ExecutionPlan, handler: TaskHandler) -> ExecutionReport:
        """Execute *plan* and return an :class:`ExecutionReport`.

        When a ``default_timeout`` was configured, each task runs under a
        hard deadline; expiry marks the task TIMEOUT (and FAILED-like for
        dependency purposes).
        """
        effective: TaskHandler = handler
        if self._timeout is not None:
            from orchestration.execution.timeout_manager import run_with_timeout

            def timed(task_id: str, description: str, context: Dict[str, Any]) -> Any:
                return run_with_timeout(
                    handler,
                    args=(task_id, description, context),
                    timeout=self._timeout,
                )

            effective = timed

        raw = self._executor.execute(plan, effective)
        if self._timeout is not None:
            for result in raw.values():
                if result.status is TaskStatus.RUNNING:
                    result.mark_timeout("deadline exceeded")
        report = ExecutionReport(
            plan_id=plan.plan_id, goal=plan.goal, results=raw
        )
        logger.info(
            "engine run %s: ok=%s succeeded=%d failed=%d skipped=%d",
            plan.plan_id,
            report.all_ok,
            report.succeeded,
            report.failed,
            report.skipped,
        )
        return report
