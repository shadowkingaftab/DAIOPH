from __future__ import annotations


class SpeechEvaluator:
    """Evaluates speech model performance."""

    def __init__(self) -> None:
        self.accuracy: float = 0.0
        self.rttm: float = 0.0

    def set_metrics(self, accuracy: float, rttm: float) -> None:
        """Set speech metrics."""
        self.accuracy = accuracy
        self.rttm = rttm

    def get_metrics(self) -> dict[str, float]:
        """Return speech metrics."""
        return {"accuracy": self.accuracy, "rttm": self.rttm}