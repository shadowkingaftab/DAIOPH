"""Dependency health check."""

from __future__ import annotations

from typing import Callable, Optional

from resilience.health.health_check import HealthCheckResult, HealthStatus

__all__ = ["DependencyHealth"]


class DependencyHealth:
    """Runs an injected probe callable and reports its health."""

    def __init__(self, name: str, probe: Callable[[], bool]) -> None:
        self.name = name
        self._probe = probe

    def check(self) -> HealthCheckResult:
        """Run the probe; report ok or unhealthy (never raises)."""
        try:
            ok = bool(self._probe())
        except Exception as exc:  # noqa: BLE001 - report, never crash
            return HealthCheckResult(
                self.name, HealthStatus.UNHEALTHY, str(exc)
            )
        return HealthCheckResult(
            self.name, HealthStatus.OK if ok else HealthStatus.UNHEALTHY
        )
