from __future__ import annotations


class ImprovementTracker:
    """Tracks model improvement over time."""

    def __init__(self) -> None:
        self.before: float = 0.0
        self.after: float = 0.0
        self.improved: bool = False

    def set_results(self, before: float, after: float) -> None:
        """Set before and after metrics."""
        self.before = before
        self.after = after
        self.improved = after > before

    def has_improved(self) -> bool:
        """Return whether improvement was detected."""
        return self.improved

    def get_improvement_amount(self) -> float:
        """Return the amount of improvement."""
        return self.after - self.before