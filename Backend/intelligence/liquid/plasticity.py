"""Plasticity tracking for liquid intelligence."""

from typing import Any, Dict, List, Optional


class PlasticityTracker:
    """Tracks the plasticity (adaptability) of the liquid system.

    Plasticity measures how readily the system can change in
    response to new inputs.
    """

    def __init__(self) -> None:
        """Initialize the plasticity tracker."""
        self._plasticity: float = 0.5  # Neutral starting point
        self._history: List[Dict[str, Any]] = []

    def update(self, change_rate: float) -> None:
        """Update the plasticity based on a change rate.

        Args:
            change_rate: Rate of change in [0, 1]-ish scale.
        """
        # Decay toward the observed change rate
        self._plasticity = self._plasticity * 0.8 + max(0.0, min(1.0, change_rate)) * 0.2
        self._history.append({"change_rate": change_rate, "plasticity": self._plasticity})

    @property
    def value(self) -> float:
        """Get the current plasticity value.

        Returns:
            float: Plasticity in [0, 1].
        """
        return self._plasticity

    def increase(self, amount: float = 0.1) -> None:
        """Increase plasticity.

        Args:
            amount: Amount to increase by.
        """
        self._plasticity = min(1.0, self._plasticity + amount)

    def decrease(self, amount: float = 0.1) -> None:
        """Decrease plasticity.

        Args:
            amount: Amount to decrease by.
        """
        self._plasticity = max(0.0, self._plasticity - amount)

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get plasticity history.

        Args:
            limit: Optional number of recent entries.

        Returns:
            List[Dict[str, Any]]: History entries.
        """
        if limit:
            return self._history[-limit:]
        return list(self._history)

    def reset(self) -> None:
        """Reset the tracker."""
        self._plasticity = 0.5
        self._history = []