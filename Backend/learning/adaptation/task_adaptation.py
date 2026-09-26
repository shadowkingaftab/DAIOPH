"""TaskAdaptation - adapts tasks to current conditions."""

from typing import Any, Dict, Optional


class TaskAdaptation:
    """Adapts task execution based on current conditions."""

    def __init__(self) -> None:
        """Initialize task adaptation."""
        self._task_preferences: Dict[str, Any] = {}
        self._adaptation_history: List[Dict[str, Any]] = []
        self._limit = 50

    def adapt_task(self, task: Dict[str, Any], conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt a task to current conditions.

        Args:
            task: Task definition.
            conditions: Current adaptation conditions.

        Returns:
            Dict[str, Any]: Adapted task.
        """
        adapted = dict(task)
        # Apply condition-based modifications
        if conditions.get("resource_limit"):
            adapted["resource_limit"] = conditions["resource_limit"]
        if conditions.get("priority"):
            adapted["priority"] = conditions["priority"]
        self._adaptation_history.append({"task": task, "adapted": adapted, "conditions": conditions})
        if len(self._adaptation_history) > self._limit:
            self._adaptation_history = self._adaptation_history[-self._limit:]
        return adapted

    def get_adaptation_history(self) -> List[Dict[str, Any]]:
        """Get adaptation history.

        Returns:
            List[Dict[str, Any]]: Adaptation history.
        """
        return list(self._adaptation_history)

    def reset(self) -> None:
        """Reset task adaptation."""
        self._task_preferences = {}
        self._adaptation_history = []

</final_file_content>
</write_to_file>