from __future__ import annotations


class ModelLatency:
    """Evaluates model latency metrics."""

    def __init__(self) -> None:
        self.latencies: list[float] = []

    def record(self, latency: float) -> None:
        """Record a latency measurement."""
        self.latencies.append(latency)

    def get_average_latency(self) -> float:
        """Return the average latency."""
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    def get_max_latency(self) -> float:
        """Return the maximum latency."""
        if not self.latencies:
            return 0.0
        return max(self.latencies)