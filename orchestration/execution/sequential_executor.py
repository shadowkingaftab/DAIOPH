"""Sequential (topological-order) plan executor.

Executes tasks one at a time following the plan's precomputed order.
Downstream tasks whose dependencies failed are marked SKIPPED rather than
attempted, and cooperative cancellation stops new work immediately.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

from orchestration.execution.cancellation import CancellationToken
from orchestration.execution.task_executor import (
    TaskExecutor,
    TaskHandler,
    TaskResult,
    TaskStatus,
)
from orchestration.planning.execution_plan import ExecutionPlan

__all__ = ["SequentialExecutor"]

logger = logging.getLogger(__name__)


class SequentialExecutor(TaskExecutor):
    """Runs every task in topological order, one at a time."""

    def __init__(
        self,
        token: Optional[CancellationToken] = None,
        on_task_done: Optional[Callable[[TaskResult], None]] = None,
    ) -> None:
        self._token = token
        self._on_task_done = on_task_done

    def execute(
        self,
        plan: ExecutionPlan,
        handler: TaskHandler,
    ) -> Dict[str, TaskResult]:
        """Execute *plan* sequentially with *handler*."""
        results: Dict[str, TaskResult] = {}
        outputs: Dict[str, Any] = {}
        for task_id in plan.order:
            node = plan.node(task_id)
            result = TaskResult(task_id=task_id)

            if self._token is not None and self._token.cancelled:
                result.status = TaskStatus.CANCELLED
                result.error = self._token.reason
                results[task_id] = result
                continue

            failed_deps = [
                d
                for d in node.depends_on
                if d in results and not results[d].ok
            ]
            if failed_deps:
                result.status = TaskStatus.SKIPPED
                result.error = f"upstream dependency failed: {failed_deps}"
                results[task_id] = result
                continue

            context = {d: outputs.get(d) for d in node.depends_on}
            result.mark_running()
            result.attempts = 1
            try:
                output = handler(task_id, node.description, context)
                outputs[task_id] = output
                result.mark_succeeded(output)
            except Exception as exc:  # noqa: BLE001 - isolated per task
                logger.warning("task %s failed: %s", task_id, exc)
                result.mark_failed(str(exc))
            results[task_id] = result
            if self._on_task_done is not None:
                self._on_task_done(result)
        return results
