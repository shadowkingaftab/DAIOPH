from __future__ import annotations


class MultimodalFusionEvaluator:
    """Evaluates multimodal fusion performance."""

    def __init__(self) -> None:
        self.accuracy: float = 0.0
        self.latency: float = 0.0

    def set_metrics(self, accuracy: float, latency: float) -> None:
        """Set fusion metrics."""
        self.accuracy = accuracy
        self.latency = latency

    def get_metrics(self) -> dict[str, float]:
        """Return fusion metrics."""
        return {"accuracy": self.accuracy, "latency": self.latency}