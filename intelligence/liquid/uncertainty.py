"""Uncertainty estimation for liquid intelligence."""

from typing import Any, Dict


class UncertaintyEstimator:
    """Estimates uncertainty in liquid intelligence decisions.

    Uncertainty is the complement of confidence and increases
    when the system encounters novel or conflicting inputs.
    """

    def __init__(self) -> None:
        """Initialize the uncertainty estimator."""
        self._recent: float = 0.3

    def estimate(self, state_snapshot: Dict[str, Any], input_data: Any) -> float:
        """Estimate uncertainty for a given state/input.

        Args:
            state_snapshot: Current state snapshot.
            input_data: Input data.

        Returns:
            float: Uncertainty in [0, 1].
        """
        # Uncertainty is complement of stability-adjusted baseline
        stability = state_snapshot.get("stability", 0.5)
        uncertainty = 1.0 - stability
        uncertainty = max(0.0, min(1.0, uncertainty))
        self._recent = uncertainty
        return uncertainty

    @property
    def recent(self) -> float:
        """Get the most recent uncertainty value.

        Returns:
            float: Recent uncertainty in [0, 1].
        """
        return self._recent

    def reset(self) -> None:
        """Reset the estimator."""
        self._recent = 0.3