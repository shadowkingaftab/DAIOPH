from __future__ import annotations


class IntentAccuracy:
    """Evaluates intent classification accuracy."""

    def __init__(self) -> None:
        self.correct: int = 0
        self.total: int = 0

    def record(self, predicted: str, actual: str) -> None:
        """Record a prediction result."""
        self.total += 1
        if predicted == actual:
            self.correct += 1

    def get_accuracy(self) -> float:
        """Return the accuracy percentage."""
        if self.total == 0:
            return 0.0
        return (self.correct / self.total) * 100

    def reset(self) -> None:
        """Reset the evaluator."""
        self.correct = 0
        self.total = 0