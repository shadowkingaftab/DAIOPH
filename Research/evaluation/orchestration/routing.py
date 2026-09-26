from __future__ import annotations


class RoutingEvaluator:
    """Evaluates routing performance."""

    def __init__(self) -> None:
        self.choices: int = 0
        self.correct: int = 0

    def record(self, correct: bool) -> None:
        """Record a routing decision."""
        self.choices += 1
        if correct:
            self.correct += 1

    def get_accuracy(self) -> float:
        """Return routing accuracy."""
        if self.choices == 0:
            return 0.0
        return (self.correct / self.choices) * 100