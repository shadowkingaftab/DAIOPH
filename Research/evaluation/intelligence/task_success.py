from __future__ import annotations


class TaskSuccess:
    """Evaluates task success rates."""

    def __init__(self) -> None:
        self.successful: int = 0
        self.failed: int = 0
        self.total: int = 0

    def record(self, success: bool) -> None:
        """Record a task result."""
        self.total += 1
        if success:
            self.successful += 1
        else:
            self.failed += 1

    def get_success_rate(self) -> float:
        """Return the success rate percentage."""
        if self.total == 0:
            return 0.0
        return (self.successful / self.total) * 100

    def reset(self) -> None:
        """Reset the evaluator."""
        self.successful = 0
        self.failed = 0
        self.total = 0