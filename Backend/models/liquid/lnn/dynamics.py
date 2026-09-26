"""Dynamics helpers: simulation and time-constant sweeps."""

from __future__ import annotations

from typing import Callable, List, Sequence, Tuple

from models.liquid.lnn.cells import LiquidCell

__all__ = ["simulate", "sweep_tau", "steady_state"]


def simulate(cell: LiquidCell, inputs: Sequence[float]) -> List[float]:
    """Run *cell* over *inputs* and return the state trajectory."""
    return cell.run(inputs)


def sweep_tau(
    taus: Sequence[float],
    inputs: Sequence[float],
    weight: float = 1.0,
    bias: float = 0.0,
    dt: float = 0.1,
) -> List[Tuple[float, float]]:
    """Final state for each candidate tau (deterministic order).

    Returns (tau, final_state) pairs; useful for picking a time constant
    that settles quickly or retains memory, depending on the task.
    """
    results: List[Tuple[float, float]] = []
    for tau in taus:
        cell = LiquidCell(weight=weight, bias=bias, tau=tau, dt=dt)
        trajectory = cell.run(inputs)
        results.append((tau, trajectory[-1] if trajectory else 0.0))
    return results


def steady_state(cell: LiquidCell, x: float, steps: int = 200) -> float:
    """Drive the cell with constant input until it settles.

    Returns the state after *steps* iterations; with dt <= tau the update
    is a contraction, so this converges to the fixed point.
    """
    if steps < 1:
        raise ValueError("steps must be >= 1")
    cell.reset()
    state = 0.0
    for _ in range(steps):
        state = cell.step(x)
    return state
