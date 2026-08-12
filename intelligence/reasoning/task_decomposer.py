"""TaskDecomposer - breaks complex tasks into sub-tasks."""

from typing import Any, Dict, List, Optional


class TaskDecomposer:
    """Decomposes complex tasks into manageable sub-tasks."""

    def decompose(self, task: Any, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Decompose a task into sub-tasks.

        Args:
            task: The task to decompose.
            context: Optional contextual information.

        Returns:
            List[Dict[str, Any]]: Sub-task list.
        """
        if isinstance(task, str):
            task = {"description": task}
        if isinstance(task, dict):
            description = task.get("description", str(task))
        else:
            description = str(task)

        # Standard decomposition pattern
        subtasks = [
            {"id": 1, "name": f"Initialize: {description}", "type": "setup"},
            {"id": 2, "name": f"Execute: {description}", "type": "execution"},
            {"id": 3, "name": f"Validate: {description}", "type": "validation"},
            {"id": 4, "name": f"Finalize: {description}", "type": "wrapup"},
        ]

        return subtasks

    def simplify(self, subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simplify a subtask list by merging related tasks.

        Args:
            subtasks: List of subtasks to simplify.

        Returns:
            List[Dict[str, Any]]: Simplified subtask list.
        """
        simplified: List[Dict[str, Any]] = []
        for subtask in subtasks:
            name = subtask.get("name", "")
            # Merge if similar type
            if simplified and simplified[-1].get("type") == subtask.get("type"):
                simplified[-1]["name"] = f"{simplified[-1]['name']} & {subtask['name']}"
            else:
                simplified.append(subtask)
        return simplified

    def reset(self) -> None:
        """Reset the decomposer."""
        pass