"""Gradient-free optimizer: seeded hill climbing over parameters."""

from __future__ import annotations

import random
from typing import Callable, Dict, List, Tuple

__all__ = ["HillClimbOptimizer"]

Objective = Callable[[Dict[str, float]], float]


class HillClimbOptimizer:
    """Deterministic random-restart-free hill climbing.

    Uses a local ``random.Random(seed)`` so runs are reproducible without
    touching global RNG state. The objective is maximized.
    """

    def __init__(
        self,
        param_bounds: Dict[str, Tuple[float, float]],
        step_size: float = 0.1,
        seed: int = 0,
    ) -> None:
        if not param_bounds:
            raise ValueError("at least one parameter is required")
        if step_size <= 0.0:
            raise ValueError("step_size must be > 0")
        for name, (lo, hi) in param_bounds.items():
            if lo >= hi:
                raise ValueError(f"invalid bounds for {name!r}: {lo} >= {hi}")
        self._bounds = dict(param_bounds)
        self._step = step_size
        self._rng = random.Random(seed)

    def optimize(
        self,
        objective: Objective,
        iterations: int = 100,
        initial: Dict[str, float] | None = None,
    ) -> Tuple[Dict[str, float], float]:
        """Maximize *objective*; returns (best_params, best_score)."""
        if iterations < 1:
            raise ValueError("iterations must be >= 1")
        if initial is None:
            current = {
                name: self._rng.uniform(lo, hi)
                for name, (lo, hi) in self._bounds.items()
            }
        else:
            current = {
                name: self._clamp(name, initial.get(name, (lo + hi) / 2.0))
                for name, (lo, hi) in self._bounds.items()
            }
        best_params = dict(current)
        best_score = objective(current)
        for _ in range(iterations):
            candidate = {
                name: self._clamp(
                    name, value + self._rng.uniform(-self._step, self._step)
                )
                for name, value in current.items()
            }
            score = objective(candidate)
            if score > best_score:
                best_score = score
                best_params = dict(candidate)
                current = candidate
        return best_params, best_score

    def _clamp(self, name: str, value: float) -> float:
        lo, hi = self._bounds[name]
        return max(lo, min(hi, value))

    def history_note(self) -> str:
        """Human-readable description of the search configuration."""
        names = ", ".join(sorted(self._bounds))
        return f"hill climbing over [{names}] with step {self._step}"
