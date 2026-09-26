from __future__ import annotations

import math
import random
from typing import Any, Dict


class DifferentialPrivacy:
    """Adds differential privacy noise to model updates."""

    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5) -> None:
        self.epsilon = epsilon
        self.delta = delta

    def add_noise(self, value: float) -> float:
        """Add Laplace noise to a value."""
        scale = 1.0 / self.epsilon
        u = random.random() - 0.5
        noise = -scale * math.copysign(1.0, u) * math.log(1.0 - 2.0 * abs(u))
        return value + noise

    def apply_to_update(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """Apply differential privacy to a model update."""
        noisy: Dict[str, Any] = {}
        for key, value in update.items():
            if isinstance(value, (int, float)):
                noisy[key] = self.add_noise(float(value))
            else:
                noisy[key] = value
        return noisy

    def get_privacy_budget(self) -> Dict[str, Any]:
        """Return the current privacy budget."""
        return {
            "epsilon": self.epsilon,
            "delta": self.delta,
        }