from __future__ import annotations


class SystemMonitor:
    """Monitors system health and performance."""

    def __init__(self) -> None:
        self.metrics: dict[str, float] = {
            "cpu": 0.0,
            "memory": 0.0,
            "temperature": 0.0,
        }

    def update_metrics(self, cpu: float, memory: float, temperature: float) -> None:
        """Update system metrics."""
        self.metrics["cpu"] = cpu
        self.metrics["memory"] = memory
        self.metrics["temperature"] = temperature

    def get_metrics(self) -> dict[str, float]:
        """Return current metrics."""
        return dict(self.metrics)

    def check_health(self) -> bool:
        """Check if system is healthy."""
        cpu = self.metrics.get("cpu", 0)
        memory = self.metrics.get("memory", 0)
        temperature = self.metrics.get("temperature", 0)
        return cpu < 80 and memory < 80 and temperature < 85