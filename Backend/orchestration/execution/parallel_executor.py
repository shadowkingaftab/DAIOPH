"""Wave-parallel plan executor.

Executes the plan wave by wave (see
:meth:`orchestration.planning.dependency_resolver.execution_waves`). Tasks
inside a wave have no interdependencies and run concurrently in a thread
pool. A failed task causes its dependents to be SKIPPED in later waves;
cancellation between waves prevents new waves from starting.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional

from orchestration.execution.cancellation import CancellationToken
from orchestration.execution.task_executor import (
    TaskExecutor,
    TaskHandler,
    TaskResult,
    TaskStatus,
)
from orchestration.planning.execution_plan import ExecutionPlan

__all__ = ["ParallelExecutor"]

logger = logging.getLogger(__name__)


class ParallelExecutor(TaskExecutor):
    """Runs each execution wave concurrently with bounded workers."""

    def __init__(
        self,
        max_workers: int = 4,
        token: Optional[CancellationToken] = None,
        on_task_done: Optional[Callable[[TaskResult], None]] = None,
    ) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        self._max_workers = max_workers
        self._token = token
        self._on_task_done = on_task_done

    def execute(
        self,
        plan: ExecutionPlan,
        handler: TaskHandler,
    ) -> Dict[str, TaskResult]:
        """Execute *plan* wave-by-wave with *handler*."""
        results: Dict[str, TaskResult] = {}
        outputs: Dict[str, Any] = {}

        for wave_index, wave in enumerate(plan.waves):
            if self._token is not None and self._token.cancelled:
                for task_id in [t for w in plan.waves[wave_index:] for t in w]:
                    r = TaskResult(
                        task_id=task_id,
                        status=TaskStatus.CANCELLED,
                        error=self._token.reason,
                    )
                    results.setdefault(task_id, r)
                break

            runnable = []
            for task_id in wave:
                node = plan.node(task_id)
                failed = [
                    d for d in node.depends_on if d in results and not results[d].ok
                ]
                if failed:
                    results[task_id] = TaskResult(
                        task_id=task_id,
                        status=TaskStatus.SKIPPED,
                        error=f"upstream dependency failed: {failed}",
                    )
                else:
                    runnable.append(task_id)

            if runnable:
                with ThreadPoolExecutor(
                    max_workers=self._max_workers,
                    thread_name_prefix="daioph-wave",
                ) as pool:
                    futures = {}
                    for task_id in runnable:
                        node = plan.node(task_id)
                        context = {d: outputs.get(d) for d in node.depends_on}
                        result = TaskResult(task_id=task_id)
                        result.mark_running()
                        result.attempts = 1
                        results[task_id] = result
                        futures[pool.submit(handler, task_id, node.description, context)] = (
                            task_id
                        )
                    for future, task_id in futures.items():
                        result = results[task_id]
                        try:
                            output = future.result()
                            outputs[task_id] = output
                            result.mark_succeeded(output)
                        except Exception as exc:  # noqa: BLE001
                            logger.warning("task %s failed: %s", task_id, exc)
                            result.mark_failed(str(exc))
                        if self._on_task_done is not None:
                            self._on_task_done(result)

        # Guarantee a result entry for every task (defensive completeness).
        for node in plan.graph.tasks:
            results.setdefault(
                node.id,
                TaskResult(task_id=node.id, status=TaskStatus.SKIPPED,
                           error="not scheduled"),
            )
        return results
