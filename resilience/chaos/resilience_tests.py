"""Resilience test helpers."""

from __future__ import annotations

from typing import Any, Callable, List

__all__ = ["assert_recovers"]


def assert_recovers(
    fn: Callable[[], Any],
    attempts: int = 3,
) -> List[Any]:
    """Call *fn* repeatedly; return results (failures are recorded)."""
    results: List[Any] = []
    for _ in range(attempts):
        try:
            results.append(fn())
        except Exception as exc:  # noqa: BLE001 - record, continue
            results.append(exc)
    return results
