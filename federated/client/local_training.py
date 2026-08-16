from __future__ import annotations

from typing import Any, Dict, List


class LocalTrainer:
    """Trains a model locally on client data."""

    def __init__(self, learning_rate: float = 0.01) -> None:
        self.learning_rate = learning_rate
        self.epochs: int = 1
        self.training_history: List[Dict[str, Any]] = []

    def set_epochs(self, epochs: int) -> None:
        """Set the number of training epochs."""
        self.epochs = epochs

    def train(self, model: Any, data: Any) -> Dict[str, Any]:
        """Train the model on local data.

        Returns:
            A dictionary with training metrics.
        """
        result = {
            "epochs": self.epochs,
            "learning_rate": self.learning_rate,
            "samples": len(data) if hasattr(data, "__len__") else 0,
        }
        self.training_history.append(result)
        return result

    def get_history(self) -> List[Dict[str, Any]]:
        """Return the training history."""
        return list(self.training_history)