"""Liquid network: a chain of cells with per-layer time constants."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from models.liquid.lnn.cells import LiquidCell

__all__ = ["LiquidNetwork"]


class LiquidNetwork:
    """Feedforward-in-time stack of liquid cells.

    Layer i receives the state of layer i-1 as its input; the first layer
    receives the external input. States are exposed for inspection and
    checkpointing.
    """

    def __init__(
        self,
        layer_taus: Sequence[float],
        weight: float = 1.0,
        bias: float = 0.0,
        dt: float = 0.1,
    ) -> None:
        if not layer_taus:
            raise ValueError("at least one layer is required")
        self.cells: List[LiquidCell] = [
            LiquidCell(weight=weight, bias=bias, tau=tau, dt=dt)
            for tau in layer_taus
        ]

    @property
    def num_layers(self) -> int:
        """Number of stacked cells."""
        return len(self.cells)

    def reset(self) -> None:
        """Reset every cell."""
        for cell in self.cells:
            cell.reset()

    def step(self, x: float) -> List[float]:
        """Advance one timestep; returns per-layer states."""
        states: List[float] = []
        signal = x
        for cell in self.cells:
            signal = cell.step(signal)
            states.append(signal)
        return states

    def forward(self, inputs: Sequence[float]) -> List[List[float]]:
        """Run a sequence; returns one state list per timestep."""
        self.reset()
        return [self.step(x) for x in inputs]

    def state_dict(self) -> Dict[str, Any]:
        """Serializable parameters and current state."""
        return {
            "taus": [c.tau for c in self.cells],
            "weights": [c.weight for c in self.cells],
            "biases": [c.bias for c in self.cells],
            "dt": self.cells[0].dt,
            "state": [c.state for c in self.cells],
        }

    def load_state_dict(self, state: Dict[str, Any]) -> None:
        """Restore parameters and state produced by ``state_dict``."""
        taus = state["taus"]
        if len(taus) != len(self.cells):
            raise ValueError("layer count mismatch")
        for cell, tau, weight, bias, cell_state in zip(
            self.cells, taus, state["weights"], state["biases"], state["state"]
        ):
            cell.tau = tau
            cell.weight = weight
            cell.bias = bias
            cell.state = cell_state
