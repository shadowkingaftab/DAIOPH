"""Checkpoint validation for liquid model state dicts."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

__all__ = ["validate_checkpoint", "ValidationError"]

REQUIRED_KEYS = ("taus", "weights", "biases", "dt", "state")


class ValidationError(ValueError):
    """Raised when a checkpoint fails structural validation."""


def validate_checkpoint(
    state: Dict[str, Any],
    required_keys: Sequence[str] = REQUIRED_KEYS,
) -> List[str]:
    """Validate a liquid state dict; returns a list of problems (empty=OK).

    Checks performed:
      * all required keys present
      * taus/weights/biases are equal-length lists of finite floats
      * every tau > 0
      * state is a list of finite floats matching the layer count
    """
    problems: List[str] = []
    for key in required_keys:
        if key not in state:
            problems.append(f"missing key: {key}")
    if problems:
        return problems

    taus = state["taus"]
    weights = state["weights"]
    biases = state["biases"]
    cell_state = state["state"]
    dt = state["dt"]

    for name, seq in (
        ("taus", taus),
        ("weights", weights),
        ("biases", biases),
        ("state", cell_state),
    ):
        if not isinstance(seq, list):
            problems.append(f"{name} must be a list")
            return problems
        if len(seq) != len(taus):
            problems.append(f"{name} length {len(seq)} != taus length {len(taus)}")
            return problems
        for i, value in enumerate(seq):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                problems.append(f"{name}[{i}] is not numeric")
                return problems
            if value != value or value in (float("inf"), float("-inf")):
                problems.append(f"{name}[{i}] is not finite")
                return problems

    for i, tau in enumerate(taus):
        if tau <= 0:
            problems.append(f"taus[{i}] must be > 0")
    if not isinstance(dt, (int, float)) or isinstance(dt, bool) or dt <= 0:
        problems.append("dt must be a positive number")
    elif dt > max(taus):
        problems.append("dt must not exceed the largest tau")
    return problems
