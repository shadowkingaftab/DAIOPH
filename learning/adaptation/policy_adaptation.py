"""Policy adaptation: exponential-moving-average parameter updates."""

from __future__ import annotations

from typing import Dict, List, Optional

__all__ = ["PolicyAdapter"]


class PolicyAdapter:
    """Adapts named policy parameters from scalar feedback via EMA.

    ``update(name, feedback)`` moves the parameter toward the feedback
    value with learning rate ``alpha``; parameters are clamped to
    ``[min_value, max_value]``.
    """

    def __init__(
        self,
        alpha: float = 0.2,
        min_value: float = 0.0,
        max_value: float = 1.0,
    ) -> None:
        if not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be within (0, 1]")
        if min_value >= max_value:
            raise ValueError("min_value must be < max_value")
        self._alpha = alpha
        self._min = min_value
        self._max = max_value
        self._params: Dict[str, float] = {}
        self._history: Dict[str, List[float]] = {}

    def set_initial(self, name: str, value: float) -> None:
        """Seed a parameter (clamped); overwrites any current value."""
        self._params[name] = self._clamp(value)

    def get(self, name: str) -> Optional[float]:
        """Current parameter value, or None when unset."""
        return self._params.get(name)

    def update(self, name: str, feedback: float) -> float:
        """EMA update toward *feedback*; returns the new value."""
        target = self._clamp(feedback)
        current = self._params.get(name)
        if current is None:
            new_value = target
        else:
            new_value = current + self._alpha * (target - current)
        new_value = self._clamp(new_value)
        self._params[name] = new_value
        self._history.setdefault(name, []).append(new_value)
        return new_value

    def history(self, name: str) -> List[float]:
        """Value history for *name* after each update."""
        return list(self._history.get(name, []))

    def parameters(self) -> Dict[str, float]:
        """Snapshot of all parameters."""
        return dict(self._params)

    def _clamp(self, value: float) -> float:
        return max(self._min, min(self._max, value))
