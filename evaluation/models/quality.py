from __future__ import annotations


class ModelQuality:
    """Evaluates model quality metrics."""

    def __init__(self) -> None:
        self.accuracy: float = 0.0
        self.precision: float = 0.0
        self.recall: float = 0.0
        self.f1: float = 0.0

    def set_metrics(
        self, accuracy: float, precision: float, recall: float, f1: float
    ) -> None:
        """Set quality metrics."""
        self.accuracy = accuracy
        self.precision = precision
        self.recall = recall
        self.f1 = f1

    def get_all_metrics(self) -> dict[str, float]:
        """Return all quality metrics."""
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
        }