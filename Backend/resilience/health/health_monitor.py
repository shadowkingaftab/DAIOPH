"""Health monitor aggregating dependency checks."""

from __future__ import annotations

from typing import List

from resilience.health.dependency_health import DependencyHealth
from resilience.health.health_check import HealthCheckResult

__all__ = ["HealthMonitor"]


class HealthMonitor:
    """Runs all registered dependency checks and aggregates results."""

    def __init__(self) -> None:
        self._checks: List[DependencyHealth] = []

    def register(self, check: DependencyHealth) -> None:
        """Register a dependency health check."""
        self._checks.append(check)

    def run_all(self) -> List[HealthCheckResult]:
        """Run every check; return results."""
        return [check.check() for check in self._checks]

    def is_healthy(self) -> bool:
        """True only when every check is healthy."""
        return all(r.healthy for r in self.run_all())
