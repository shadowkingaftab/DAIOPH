from __future__ import annotations


class DAGEvaluator:
    """Evaluates DAG execution performance."""

    def __init__(self) -> None:
        self.executions: int = 0
        self.successes: int = 0

    def record(self, success: bool) -> None:
        """Record a DAG execution result."""
        self.executions += 1
        if success:
            self.successes += 1

    def get_success_rate(self) -> float:
        """Return DAG success rate."""
        if self.executions == 0:
            return 0.0
        return (self.successes / self.executions) * 100