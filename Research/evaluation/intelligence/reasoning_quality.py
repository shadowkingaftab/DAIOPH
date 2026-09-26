from __future__ import annotations


class ReasoningQuality:
    """Evaluates reasoning quality metrics."""

    def __init__(self) -> None:
        self.valid: int = 0
        self.invalid: int = 0
        self.total: int = 0

    def record(self, valid: bool) -> None:
        """Record a reasoning result."""
        self.total += 1
        if valid:
            self.valid += 1
        else:
            self.invalid += 1

    def get_quality_ratio(self) -> float:
        """Return the valid reasoning ratio."""
        if self.total == 0:
            return 0.0
        return (self.valid / self.total) * 100

    def reset(self) -> None:
        """Reset the evaluator."""
        self.valid = 0
        self.invalid = 0
        self.total = 0