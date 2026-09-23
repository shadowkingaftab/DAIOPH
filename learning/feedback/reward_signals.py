"""Reward signal computation from ratings and outcomes."""

from __future__ import annotations

from typing import Dict, List, Sequence

__all__ = ["rating_to_reward", "discounted_rewards", "normalize_rewards"]

_RATING_MAP: Dict[str, float] = {
    "thumbs_up": 1.0,
    "thumbs_down": -1.0,
    "positive": 1.0,
    "negative": -1.0,
    "neutral": 0.0,
}


def rating_to_reward(rating: str) -> float:
    """Map a symbolic rating to a reward in [-1, 1].

    Numeric strings in [0, 1] map linearly to [-1, 1]; unknown symbols
    raise ValueError.
    """
    if rating in _RATING_MAP:
        return _RATING_MAP[rating]
    try:
        value = float(rating)
    except ValueError:
        raise ValueError(f"unknown rating: {rating!r}") from None
    if not 0.0 <= value <= 1.0:
        raise ValueError("numeric ratings must be within [0, 1]")
    return value * 2.0 - 1.0


def discounted_rewards(
    rewards: Sequence[float], gamma: float = 0.9
) -> List[float]:
    """Return-to-go with discount *gamma* (higher weight to earlier steps)."""
    if not 0.0 <= gamma <= 1.0:
        raise ValueError("gamma must be within [0, 1]")
    result = [0.0] * len(rewards)
    running = 0.0
    for i in range(len(rewards) - 1, -1, -1):
        running = rewards[i] + gamma * running
        result[i] = running
    return result


def normalize_rewards(rewards: Sequence[float]) -> List[float]:
    """Min-max scale rewards to [0, 1]; all-equal input maps to 0.5."""
    if not rewards:
        return []
    lo, hi = min(rewards), max(rewards)
    if hi == lo:
        return [0.5] * len(rewards)
    span = hi - lo
    return [(r - lo) / span for r in rewards]
