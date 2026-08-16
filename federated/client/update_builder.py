from __future__ import annotations

from typing import Any, Dict


class UpdateBuilder:
    """Builds model updates to send to the federated server."""

    def __init__(self) -> None:
        self.current_update: Dict[str, Any] = {}

    def add_weight(self, name: str, value: Any) -> None:
        """Add a model weight to the update."""
        self.current_update[name] = value

    def add_metric(self, name: str, value: Any) -> None:
        """Add a training metric to the update."""
        if "metrics" not in self.current_update:
            self.current_update["metrics"] = {}
        self.current_update["metrics"][name] = value

    def build(self) -> Dict[str, Any]:
        """Build and return the final update payload."""
        update = dict(self.current_update)
        self.current_update = {}
        return update

    def clear(self) -> None:
        """Clear the current update."""
        self.current_update = {}