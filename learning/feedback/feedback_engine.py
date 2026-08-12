"""FeedbackEngine - manages feedback loops for learning."""

from typing import Any, Dict, List, Optional


class FeedbackEngine:
    """Manages feedback loops for learning systems."""

    def __init__(self) -> None:
        """Initialize feedback engine."""
        self._feedback_history: List[Dict[str, Any]] = []
        self._active_loops: Dict[str, Any] = {}
        self._limit = 100

    def record_feedback(self, feedback: Dict[str, Any]) -> None:
        """Record feedback entry.

        Args:
            feedback: Feedback data.
        """
        self._feedback_history.append(feedback)
        if len(self._feedback_history) > self._limit:
            self._feedback_history = self._feedback_history[-self._limit:]

    def start_loop(self, loop_id: str, config: Dict[str, Any]) -> None:
        """Start a feedback loop.

        Args:
            loop_id: Identifier for the loop.
            config: Loop configuration.
        """
        self._active_loops[loop_id] = config

    def end_loop(self, loop_id: str) -> None:
        """End a feedback loop.

        Args:
            loop_id: Identifier for the loop.
        """
        self._active_loops.pop(loop_id, None)

    def get_feedback(self, loop_id: Optional[str] = None) -> Any:
        """Get feedback data.

        Args:
            loop_id: Optional loop identifier.

        Returns:
            Any: Feedback data.
        """
        if loop_id:
            return self._active_loops.get(loop_id)
        return self._feedback_history

    def get_stats(self) -> Dict[str, Any]:
        """Get feedback statistics.

        Returns:
            Dict[str, Any]: Statistics.
        """
        return {
            "total_feedback": len(self._feedback_history),
            "active_loops": len(self._active_loops),
        }

    def reset(self) -> None:
        """Reset feedback engine."""
        self._feedback_history = []
        self._active_loops = {}

</final_file_content>
</write_to_file>