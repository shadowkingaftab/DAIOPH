"""ModelHealth - tracks model health metrics."""

from typing import Any, Dict, Optional


class ModelHealth:
    """Tracks health metrics for a model."""

    def __init__(self, model_name: str) -> None:
        """Initialize model health tracking.

        Args:
            model_name: Name of the model.
        """
        self._model_name = model_name
        self._metrics: Dict[str, Any] = {}
        self._healthy: bool = True

    def update_metric(self, name: str, value: Any) -> None:
        """Update a health metric.

        Args:
            name: Metric name.
            value: Metric value.
        """
        self._metrics[name] = value

    def get_metric(self, name: str, default: Any = None) -> Any:
        """Get a health metric.

        Args:
            name: Metric name.
            default: Default if not found.

        Returns:
            Any: Metric value.
        """
        return self._metrics.get(name, default)

    def set_healthy(self, healthy: bool) -> None:
        """Set health status.

        Args:
            healthy: Health status.
        """
        self._healthy = healthy

    def is_healthy(self) -> bool:
        """Check if model is healthy.

        Returns:
            bool: True if healthy.
        """
        return self._healthy

    def get_status(self) -> Dict[str, Any]:
        """Get full health status.

        Returns:
            Dict[str, Any]: Health status.
        """
        return {
            "model": self._model_name,
            "healthy": self._healthy,
            "metrics": dict(self._metrics),
        }

</final_file_content>
</write_to_file></tool_call>