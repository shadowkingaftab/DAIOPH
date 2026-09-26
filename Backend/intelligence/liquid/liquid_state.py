"""Liquid state - represents the current state of the liquid intelligence system."""

import time
from typing import Any, Dict, List, Optional


class LiquidState:
    """Tracks the dynamic state of the liquid intelligence system.

    The state evolves over time through updates, incorporating
    stability and plasticity measures that characterize the
    liquid dynamics.
    """

    def __init__(self) -> None:
        """Initialize the liquid state."""
        self._values: Dict[str, Any] = {}
        self._history: List[Dict[str, Any]] = []
        self._stability: float = 1.0
        self._last_update: Optional[float] = None
        self._history_limit: int = 1000

    def update(self, input_data: Any) -> None:
        """Update the state with new input.

        Args:
            input_data: New input data.
        """
        now = time.time()
        previous = self.get_snapshot()

        if isinstance(input_data, dict):
            self._values.update(input_data)
        else:
            self._values["last_input"] = input_data

        self._last_update = now

        # Track history
        self._history.append({
            "timestamp": now,
            "previous": previous,
            "current": self.get_snapshot(),
        })
        if len(self._history) > self._history_limit:
            self._history = self._history[-self._history_limit:]

    def get_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of the current state.

        Returns:
            Dict[str, Any]: State snapshot.
        """
        return {
            "values": dict(self._values),
            "stability": self._stability,
            "last_update": self._last_update,
            "history_size": len(self._history),
        }

    def set_value(self, key: str, value: Any) -> None:
        """Set a state value.

        Args:
            key: State key.
            value: State value.
        """
        self._values[key] = value

    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a state value.

        Args:
            key: State key.
            default: Default if not found.

        Returns:
            Any: State value or default.
        """
        return self._values.get(key, default)

    @property
    def stability(self) -> float:
        """Get the current stability measure.

        Returns:
            float: Stability in [0, 1].
        """
        return self._stability

    def set_stability(self, value: float) -> None:
        """Set the stability measure.

        Args:
            value: Stability value in [0, 1].
        """
        self._stability = max(0.0, min(1.0, value))

    def reset(self) -> None:
        """Reset the state."""
        self._values = {}
        self._history = []
        self._stability = 1.0
        self._last_update = None