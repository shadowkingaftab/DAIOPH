from __future__ import annotations


class UncertaintyEvaluator:
    """Evaluates uncertainty metrics."""

    def __init__(self) -> None:
        self.uncertainty_readings: list[float] = []

    def record(self, uncertainty: float) -> None:
        """Record an uncertainty reading."""
        self.uncertainty_readings.append(uncertainty)

    def get_average_uncertainty(self) -> float:
        """Return the average uncertainty."""
        if not self.uncertainty_readings:
            return 0.0
        return sum(self.uncertainty_readings) / len(self.uncertainty_readings)

    def get_max_uncertainty(self) -> float:
        """Return the maximum uncertainty reading."""
        if not self.uncertainty_readings:
            return 0.0
        return max(self.uncertainty_readings)

    def reset(self) -> None:
        """Reset the evaluator."""
        self.uncertainty_readings.clear()