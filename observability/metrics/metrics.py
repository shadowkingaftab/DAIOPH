from __future__ import annotations


class MetricsCollector:
    """Collects and tracks metrics."""

    def __init__(self) -> None:
        self.metrics: Dict[str, Any] = {}

    def record(self, name: str, value: Any, labels: Dict[str, str] = {}) -> None:
        """Record a metric value."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({"value": value, "labels": labels})

    def get(self, name: str) -> Any:
        """Get a metric value."""
        return self.metrics.get(name, [])

    def get_all(self) -> Dict[str, Any]:
        """Return all metrics."""
        return dict(self.metrics)

    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()