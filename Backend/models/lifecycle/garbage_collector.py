"""GarbageCollector - manages model memory cleanup."""

from typing import Any, Dict, List, Optional


class GarbageCollector:
    """Manages garbage collection for loaded models."""

    def __init__(self, threshold: float = 0.8) -> None:
        """Initialize the garbage collector.

        Args:
            threshold: Memory usage threshold (0-1).
        """
        self._threshold = threshold
        self._tracked: Dict[str, Any] = {}

    def track(self, model_id: str, model: Any) -> None:
        """Track a model for garbage collection.

        Args:
            model_id: Model identifier.
            model: Model instance.
        """
        self._tracked[model_id] = model

    def collect(self, memory_usage: float) -> List[str]:
        """Collect garbage if memory usage exceeds threshold.

        Args:
            memory_usage: Current memory usage ratio.

        Returns:
            List[str]: IDs of collected models.
        """
        collected = []
        if memory_usage > self._threshold:
            for model_id in list(self._tracked.keys()):
                self._tracked.pop(model_id, None)
                collected.append(model_id)
        return collected

    def get_tracked(self) -> List[str]:
        """Get tracked model IDs.

        Returns:
            List[str]: Tracked model IDs.
        """
        return list(self._tracked.keys())

    def reset(self) -> None:
        """Reset the garbage collector."""
        self._tracked = {}