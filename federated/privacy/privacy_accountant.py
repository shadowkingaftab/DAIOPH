from __future__ import annotations

from typing import Any, Dict, List


class PrivacyAccountant:
    """Tracks privacy budget consumption across training rounds."""

    def __init__(self) -> None:
        self.epsilon_spent: float = 0.0
        self.delta_spent: float = 0.0
        self.rounds: List[Dict[str, Any]] = []

    def record_round(self, epsilon: float, delta: float) -> None:
        """Record privacy consumption for a training round."""
        self.epsilon_spent += epsilon
        self.delta_spent += delta
        self.rounds.append(
            {"epsilon": epsilon, "delta": delta}
        )

    def get_total_spent(self) -> Dict[str, float]:
        """Return the total privacy budget spent."""
        return {
            "epsilon": self.epsilon_spent,
            "delta": self.delta_spent,
        }

    def get_remaining(self, budget: Dict[str, float]) -> Dict[str, float]:
        """Return the remaining privacy budget."""
        return {
            "epsilon": budget.get("epsilon", 0.0) - self.epsilon_spent,
            "delta": budget.get("delta", 0.0) - self.delta_spent,
        }

    def reset(self) -> None:
        """Reset the privacy accountant."""
        self.epsilon_spent = 0.0
        self.delta_spent = 0.0
        self.rounds.clear()