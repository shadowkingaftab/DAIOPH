from __future__ import annotations


class ModelEfficiency:
    """Evaluates model efficiency metrics."""

    def __init__(self) -> None:
        self.throughput: float = 0.0
        self.memory_usage: float = 0.0

    def set_metrics(self, throughput: float, memory_usage: float) -> None:
        """Set efficiency metrics."""
        self.throughput = throughput
        self.memory_usage = memory_usage

    def get_all_metrics(self) -> dict[str, float]:
        """Return all efficiency metrics."""
        return {
            "throughput": self.throughput,
            "memory_usage": self.memory_usage,
        }