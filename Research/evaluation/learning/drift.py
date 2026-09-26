from __future__ import annotations


class DriftDetector:
    """Detects model drift over time."""

    def __init__(self) -> None:
        self.baseline: float = 0.0
        self.current: float = 0.0
        self.drift_detected: bool = False

    def set_values(self, baseline: float, current: float) -> None:
        """Set baseline and current values."""
        self.baseline = baseline
        self.current = current
        self.drift_detected = abs(self.current - self.baseline) > 0.1

    def has_drift(self) -> bool:
        """Return whether drift was detected."""
        return self.drift_detected

    def get_drift_magnitude(self) -> float:
        """Return the magnitude of drift."""
        return abs(self.current - self.baseline)