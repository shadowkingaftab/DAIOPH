"""Confidence estimation for liquid intelligence."""

from typing import Any, Dict, Optional


class ConfidenceEstimator:
    """Estimates confidence in liquid intelligence decisions.

    Confidence reflects how strongly the system believes its
    output is correct, based on state consistency and input
    familiarity.
    """

    def __init__(self) -> None:
        """Initialize the confidence estimator."""
        self._baseline: float = 0.7
        self._recent: float = 0.7

    def estimate(self, state_snapshot: Dict[str, Any], input_data: Any) -> float:
        """Estimate confidence for a given state/input.

        Args:
            state_snapshot: Current state snapshot.
            input_data: Input data.

        Returns:
            float: Confidence in [0, 1].
        """
        # Start from baseline
        confidence = self._baseline

        # Stability boosts confidence
        stability = state_snapshot.get("stability", 0.5)
        confidence += (stability - 0.5) * 0.2

        # Clamp to [0, 1]
        confidence = max(0.0, min(1.0, confidence))
        self._recent = confidence
        return confidence

    @property
    def recent(self) -> float:
        """Get the most recent confidence value.

        Returns:
            float: Recent confidence in [0, 1].
        """
        return self._recent

    def reset(self) -> None:
        """Reset the estimator."""
        self._baseline = 0.7
        self._recent = 0.7