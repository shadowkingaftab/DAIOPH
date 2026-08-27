"""Chaos runner: inject faults into a callable."""

from __future__ import annotations

from typing import Any, Callable, List, Optional

from resilience.chaos.fault_injection import inject_failure

__all__ = ["ChaosRunner"]


class ChaosRunner:
    """Runs a callable with a configurable fault-injection schedule."""

    def __init__(self, fail_every: Optional[int] = None) -> None:
        self.fail_every = fail_every
        self._calls = 0

    def run(self, fn: Callable[[], Any]) -> Any:
        """Run *fn*, injecting a fault every N calls when configured."""
        self._calls += 1
        if self.fail_every and self._calls % self.fail_every == 0:
            return inject_failure(fn, True)
        return fn()
