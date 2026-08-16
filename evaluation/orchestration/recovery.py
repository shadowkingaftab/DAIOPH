from __future__ import annotations


class RecoveryEvaluator:
    """Evaluates recovery performance."""

    def __init__(self) -> None:
        self.recoveries: int = 0
        self.failures: int = 0

    def record(self, success: bool) -> None:
        """Record a recovery event."""
        if success:
            self.recoveries += 1
        else:
            self.failures += 1

    def get_recovery_rate(self) -> float:
        """Return recovery rate."""
        total = self.recoveries + self.failures
        if total == 0:
            return 0.0
        return (self.recoveries / total) * 100