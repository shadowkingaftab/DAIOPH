"""Stability tracking for liquid intelligence."""

from typing import Any, Dict, List, Optional


class StabilityTracker:
    """Tracks the stability of the liquid intelligence system.

    Stability measures the system's resistance to disruptive
    change — the complement of plasticity.
    """

    def __init__(self) -> None:
        """Initialize the stability tracker."""
        self._stability: float = 0.5
        self._history: List[Dict[str, Any]] = []

    def update(self, stability_feedback: float) -> None:
        """Update stability based on feedback.

        Args:
            stability_feedback: Stability feedback in [0, 1].
        """
        self._stability = self._stability * 0.8 + max(0.0, min(1.0, stability_feedback)) * 0.2
        self._history.append({"feedback": stability_feedback, "stability": self._stability})

    @property
    def value(self) -> float:
        """Get the current stability value.

        Returns:
            float: Stability in [0, 1].
        """
        return self._stability

    def increase(self, amount: float = 0.1) -> None:
        """Increase stability.

        Args:
            amount: Amount to increase by.
        """
        self._stability = min(1.0, self._stability + amount)

    def decrease(self, amount: float = 0.1) -> None:
        """Decrease stability.

        Args:
            amount: Amount to decrease by.
        """
        self._stability = max(0.0, self._stability - amount)

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get stability history.

        Args:
            limit: Optional number of recent entries.

        Returns:
            List[Dict[str, Any]]: History entries.
        """
        if limit:
            return self._history[-limit:]
        return list(self._history)

    def reset(self) -> None:
        """Reset the tracker."""
        self._stability = 0.5
        self._history = []