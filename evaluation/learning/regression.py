from __future__ import annotations


class RegressionGuard:
    """Guards against model regression."""

    def __init__(self) -> None:
        self.previous_metrics: float = 0.0
        self.current_metrics: float = 0.0
        self.regression_detected: bool = False

    def compare(self, previous: float, current: float) -> None:
        """Compare previous and current metrics."""
        self.previous_metrics = previous
        self.current_metrics = current
        self.regression_detected = current < previous

    def has_regression(self) -> bool:
        """Return whether regression was detected."""
        return self.regression_detected

    def get_regression_amount(self) -> float:
        """Return the amount of regression."""
        return self.previous_metrics - self.current_metrics