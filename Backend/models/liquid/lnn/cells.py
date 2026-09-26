"""Liquid cell: deterministic leaky-integrator time-constant unit."""

from __future__ import annotations

import math
from typing import List, Sequence

__all__ = ["LiquidCell"]


class LiquidCell:
    """Single-input liquid time-constant cell.

    Discrete-time update (Euler integration of a first-order ODE):

        h[t+1] = (1 - dt/tau) * h[t] + (dt/tau) * tanh(w * x[t] + b)

    All arithmetic is plain Python floats, so results are deterministic
    across platforms and require no ML framework.
    """

    def __init__(
        self,
        weight: float = 1.0,
        bias: float = 0.0,
        tau: float = 1.0,
        dt: float = 0.1,
    ) -> None:
        if tau <= 0.0:
            raise ValueError("tau must be > 0")
        if dt <= 0.0:
            raise ValueError("dt must be > 0")
        if dt > tau:
            raise ValueError("dt must not exceed tau (stability)")
        self.weight = weight
        self.bias = bias
        self.tau = tau
        self.dt = dt
        self.state = 0.0

    @property
    def decay(self) -> float:
        """Per-step retention factor ``1 - dt/tau``."""
        return 1.0 - self.dt / self.tau

    def reset(self) -> None:
        """Zero the hidden state."""
        self.state = 0.0

    def step(self, x: float) -> float:
        """Advance one timestep with input *x*; returns the new state."""
        drive = math.tanh(self.weight * x + self.bias)
        self.state = self.decay * self.state + (self.dt / self.tau) * drive
        return self.state

    def run(self, inputs: Sequence[float]) -> List[float]:
        """Run over an input sequence, returning all states."""
        self.reset()
        return [self.step(x) for x in inputs]
