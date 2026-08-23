"""Task executor contract and result model.

Defines the vocabulary shared by every executor implementation:

- :class:`TaskResult` — the outcome of executing one task (status, output,
  timing, route used, error details).
- :class:`TaskExecutor` — the abstract interface executors implement.

Executors receive an :class:`~orchestration.planning.execution_plan.ExecutionPlan`
plus a *handler* callable that performs the actual work for one task. The
handler is the dependency-injection seam: production wires it to model
providers/tools; tests wire it to fakes. Executors themselves never call
LLMs or network services directly.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional

from orchestration.planning.execution_plan import ExecutionPlan

__all__ = ["TaskStatus", "TaskResult", "TaskExecutor", "TaskHandler"]

#: A handler executes one task description with upstream results available.
#: It receives (task_id, description, context) and returns any JSON-able value.
TaskHandler = Callable[[str, str, Dict[str, Any]], Any]


class TaskStatus(str, Enum):
    """Lifecycle status of a single task execution."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class TaskResult:
    """Outcome of executing one task.

    Attributes:
        task_id: Id of the executed task.
        status: Final :class:`TaskStatus`.
        output: Handler return value on success (JSON-able).
        error: Error message on failure.
        route: Route used ("edge"/"cloud"/"hybrid") when routing applied.
        started_at / finished_at: Unix timestamps.
        attempts: Number of attempts made (>= 1).
        metadata: Executor-provided extras (retries, wave index, ...).
    """

    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    output: Any = None
    error: Optional[str] = None
    route: Optional[str] = None
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    attempts: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """Wall-clock duration in seconds, or None if not finished."""
        if self.started_at is None or self.finished_at is None:
            return None
        return self.finished_at - self.started_at

    @property
    def ok(self) -> bool:
        """True when the task succeeded."""
        return self.status is TaskStatus.SUCCEEDED

    def mark_running(self) -> None:
        """Transition to RUNNING and stamp the start time."""
        self.status = TaskStatus.RUNNING
        self.started_at = time.time()

    def mark_succeeded(self, output: Any) -> None:
        """Transition to SUCCEEDED with *output*."""
        self.status = TaskStatus.SUCCEEDED
        self.output = output
        self.finished_at = time.time()

    def mark_failed(self, error: str) -> None:
        """Transition to FAILED with an error message."""
        self.status = TaskStatus.FAILED
        self.error = error
        self.finished_at = time.time()

    def mark_timeout(self, error: str) -> None:
        """Transition to TIMEOUT with an error message."""
        self.status = TaskStatus.TIMEOUT
        self.error = error
        self.finished_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-friendly dictionary."""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "route": self.route,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration": self.duration,
            "attempts": self.attempts,
            "metadata": dict(self.metadata),
        }


class TaskExecutor(ABC):
    """Abstract interface for plan executors.

    Implementations decide *how* tasks run (sequentially, in parallel waves,
    with timeouts/cancellation), but always delegate *what* runs to the
    injected :data:`TaskHandler`.
    """

    @abstractmethod
    def execute(
        self,
        plan: ExecutionPlan,
        handler: TaskHandler,
    ) -> Dict[str, TaskResult]:
        """Execute every task in *plan* using *handler*.

        Returns:
            Mapping of task id → :class:`TaskResult` covering all tasks.
        """
        raise NotImplementedError