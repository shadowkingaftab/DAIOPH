"""Health check result model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

__all__ = ["HealthStatus", "HealthCheckResult"]


class HealthStatus(str):
    """Health status values."""

    OK = "ok"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True)
class HealthCheckResult:
    """Outcome of one health check."""

    name: str
    status: str
    detail: Optional[str] = None

    @property
    def healthy(self) -> bool:
        """True when status is ok or degraded."""
        return self.status in {HealthStatus.OK, HealthStatus.DEGRADED}
