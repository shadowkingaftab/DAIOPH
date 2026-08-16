from __future__ import annotations

from typing import Any, Dict, List


class AutomationController:
    """Manages automation tasks and workflows."""

    def __init__(self) -> None:
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.executed: Dict[str, bool] = {}

    def create_task(self, task_id: str, actions: List[Dict[str, Any]]) -> bool:
        """Create an automation task."""
        if task_id in self.tasks:
            return False
        self.tasks[task_id] = {"actions": actions, "completed": False}
        self.executed[task_id] = False
        return True

    def execute_task(self, task_id: str) -> bool:
        """Execute an automation task."""
        if task_id not in self.tasks:
            return False
        self.executed[task_id] = True
        return True

    def stop_task(self, task_id: str) -> bool:
        """Stop an automation task."""
        if task_id not in self.tasks:
            return False
        self.executed[task_id] = False
        return True

    def is_completed(self, task_id: str) -> bool:
        """Check if a task is completed."""
        return self.executed.get(task_id, False)

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Return task information."""
        return self.tasks.get(task_id, {})