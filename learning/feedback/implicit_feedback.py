"""ImplicitFeedback - handles indirect feedback signals."""

from typing import Any, Dict, Optional


class ImplicitFeedback:
    """Handles implicit feedback signals from user behavior."""

    def __init__(self) -> None:
        """Initialize implicit feedback handler."""
        self._signals: Dict[str, Any] = {}
        self._weight: float = 0.5

    def record_signal(self, signal_name: str, value: Any) -> None:
        """Record an implicit feedback signal.

        Args:
            signal_name: Name of the signal.
            value: Signal value.
        """
        self._signals[signal_name] = value

    def get_signal(self, signal_name: str, default: Any = None) -> Any:
        """Get an implicit feedback signal.

        Args:
            signal_name: Name of the signal.
            default: Default if not found.

        Returns:
            Any: Signal value.
        """
        return self._signals.get(signal_name, default)

    def set_weight(self, weight: float) -> None:
        """Set the weight for implicit feedback.

        Args:
            weight: Weight in [0, 1].
        """
        self._weight = max(0.0, min(1.0, weight))

    def get_weight(self) -> float:
        """Get the current weight.

        Returns:
            float: Current weight.
        """
        return self._weight

</final_file_content>
</write_to_file>