"""Health and readiness REST routes.

Liveness answers "is the process up"; readiness additionally runs injected
check callables and reports each one's outcome honestly — a failing check
makes readiness report ``503``-style ``not_ready`` status, never a fake OK.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

__all__ = ["HealthRoute"]


class HealthRoute:
    """Handlers for ``/health/live`` and ``/health/ready``."""

    def __init__(
        self,
        version: str = "0.1.0",
        started_at: Optional[float] = None,
        readiness_checks: Optional[Dict[str, Callable[[], bool]]] = None,
    ) -> None:
        self.version = version
        self.started_at = started_at if started_at is not None else time.time()
        self.readiness_checks: Dict[str, Callable[[], bool]] = dict(
            readiness_checks or {}
        )

    def add_readiness_check(self, name: str, check: Callable[[], bool]) -> None:
        """Register a named readiness *check* returning True when healthy."""
        self.readiness_checks[name] = check

    def liveness(self) -> Dict[str, Any]:
        """Process is running; always reports alive with uptime."""
        return {
            "status": "alive",
            "version": self.version,
            "uptime_seconds": round(time.time() - self.started_at, 3),
        }

    def readiness(self) -> Dict[str, Any]:
        """Run every readiness check; report per-check outcomes."""
        results: Dict[str, str] = {}
        for name, check in sorted(self.readiness_checks.items()):
            try:
                results[name] = "ok" if check() else "failing"
            except Exception as exc:  # noqa: BLE001 - report, never crash
                results[name] = f"error: {exc}"
        failed = [name for name, state in results.items() if state != "ok"]
        return {
            "status": "ready" if not failed else "not_ready",
            "version": self.version,
            "checks": results,
            "failed": failed,
        }
