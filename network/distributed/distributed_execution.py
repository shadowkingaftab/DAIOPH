from __future__ import annotations

from typing import Any, Dict


class DistributedExecutor:
    """Executes tasks across distributed nodes."""

    def __init__(self) -> None:
        self.tasks: Dict[str, Any] = {}
        self.results: Dict[str, Any] = {}

    def submit_task(self, task_id: str, task: Any) -> None:
        """Submit a task for distributed execution."""
        self.tasks[task_id] = task

    def execute(self, task_id: str) -> Any:
        """Execute a submitted task and store the result."""
        task = self.tasks.get(task_id)
        if task is None:
            return None
        result = task() if callable(task) else task
        self.results[task_id] = result
        return result

    def execute_all(self) -> Dict[str, Any]:
        """Execute all pending tasks."""
        for task_id in list(self.tasks.keys()):
            self.execute(task_id)
        return self.results

    def get_result(self, task_id: str) -> Any:
        """Return the result of a completed task."""
        return self.results.get(task_id)

    def get_all_results(self) -> Dict[str, Any]:
        """Return all task results."""
        return dict(self.results)