from __future__ import annotations

from typing import Any, Dict, List


class Aggregator:
    """Aggregates model updates from multiple clients."""

    def __init__(self) -> None:
        self.updates: List[Dict[str, Any]] = []

    def add_update(self, update: Dict[str, Any]) -> None:
        """Add a client update to the aggregation pool."""
        self.updates.append(update)

    def aggregate(self) -> Dict[str, Any]:
        """Aggregate all collected updates into a global model."""
        if not self.updates:
            return {}
        aggregated: Dict[str, Any] = {}
        for update in self.updates:
            for key, value in update.items():
                if key == "metrics":
                    continue
                if key not in aggregated:
                    aggregated[key] = []
                aggregated[key].append(value)
        result: Dict[str, Any] = {}
        for key, values in aggregated.items():
            if values and all(isinstance(v, (int, float)) for v in values):
                result[key] = sum(values) / len(values)
            else:
                result[key] = values[-1] if values else None
        return result

    def clear(self) -> None:
        """Clear all collected updates."""
        self.updates.clear()

    def get_update_count(self) -> int:
        """Return the number of collected updates."""
        return len(self.updates)