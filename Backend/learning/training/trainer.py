"""Trainer - manages model training processes."""

from typing import Any, Dict, Optional


class Trainer:
    """Manages model training loops and lifecycle."""

    def __init__(self, model: Optional[Any] = None, max_epochs: int = 100) -> None:
        """Initialize the trainer.

        Args:
            model: Model to train.
            max_epochs: Maximum training epochs.
        """
        self._model = model
        self._max_epochs = max_epochs
        self._epoch = 0
        self._history: List[Dict[str, Any]] = []

    def train(self, data: Any, epochs: Optional[int] = None) -> Dict[str, Any]:
        """Run training for specified epochs.

        Args:
            data: Training data.
            epochs: Number of epochs (uses max if not specified).

        Returns:
            Dict[str, Any]: Training result.
        """
        epochs = epochs or self._max_epochs
        result = {"status": "started", "epochs": epochs}
        for epoch in range(self._epoch, self._epoch + epochs):
            self._epoch = epoch + 1
            # Simulate training step
            result[f"epoch_{epoch}"] = {"loss": 1.0 / (epoch + 1)}
        self._history.extend(result.items())
        return result

    def get_epoch(self) -> int:
        """Get current epoch.

        Returns:
            int: Current epoch.
        """
        return self._epoch

    def get_history(self) -> List[Dict[str, Any]]:
        """Get training history.

        Returns:
            List[Dict[str, Any]]: Training history.
        """
        return list(self._history)

    def reset(self) -> None:
        """Reset trainer."""
        self._epoch = 0
        self._history = []

</final_file_content>
</write_to_file>