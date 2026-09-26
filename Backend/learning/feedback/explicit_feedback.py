"""ExplicitFeedback - handles user-provided feedback."""

from typing import Any, Dict, Optional


class ExplicitFeedback:
    """Handles explicitly provided user feedback."""

    def __init__(self) -> None:
        """Initialize explicit feedback handler."""
        self._feedback: Optional[Dict[str, Any]] = None

    def set_feedback(self, feedback: Dict[str, Any]) -> None:
        """Set explicit feedback.

        Args:
            feedback: User-provided feedback.
        """
        self._feedback = feedback

    def get_feedback(self) -> Optional[Dict[str, Any]]:
        """Get the stored feedback.

        Returns:
            Optional[Dict[str, Any]]: Stored feedback.
        """
        return self._feedback

    def clear(self) -> None:
        """Clear stored feedback."""
        self._feedback = None

</final_file_content>
</write_to_file>