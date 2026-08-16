from __future__ import annotations


class VisionEvaluator:
    """Evaluates vision model performance."""

    def __init__(self) -> None:
        self.accuracy: float = 0.0
        self.fps: float = 0.0

    def set_metrics(self, accuracy: float, fps: float) -> None:
        """Set vision metrics."""
        self.accuracy = accuracy
        self.fps = fps

    def get_metrics(self) -> dict[str, float]:
        """Return vision metrics."""
        return {"accuracy": self.accuracy, "fps": self.fps}