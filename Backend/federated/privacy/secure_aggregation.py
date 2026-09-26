from __future__ import annotations

from typing import Any, Dict, List


class SecureAggregation:
    """Performs secure aggregation of client updates."""

    def __init__(self) -> None:
        self.masked_updates: List[Dict[str, Any]] = []

    def mask_update(
        self, update: Dict[str, Any], mask: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply a mask to a client update."""
        masked: Dict[str, Any] = {}
        for key, value in update.items():
            if isinstance(value, (int, float)) and key in mask:
                masked[key] = value + mask[key]
            else:
                masked[key] = value
        return masked

    def add_masked_update(self, masked: Dict[str, Any]) -> None:
        """Add a masked update to the aggregation pool."""
        self.masked_updates.append(masked)

    def unmask_and_aggregate(
        self, masks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Unmask updates and aggregate them."""
        if not self.masked_updates:
            return {}
        result: Dict[str, Any] = {}
        for update in self.masked_updates:
            for key, value in update.items():
                if key not in result:
                    result[key] = []
                result[key].append(value)
        aggregated: Dict[str, Any] = {}
        for key, values in result.items():
            if values and all(isinstance(v, (int, float)) for v in values):
                aggregated[key] = sum(values) / len(values)
            else:
                aggregated[key] = values[-1] if values else None
        return aggregated

    def clear(self) -> None:
        """Clear all masked updates."""
        self.masked_updates.clear()