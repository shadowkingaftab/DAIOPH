"""Graceful degradation: fall back to a degraded result."""

from __future__ import annotations

from typing import Any, Callable, Optional

__all__ = ["degrade"]


def degrade(
    primary: Callable[[], Any],
    fallback: Callable[[], Any],
    on_error: Optional[Callable[[Exception], None]] = None,
) -> Any:
    """Run *primary*; on failure run *fallback* (never raises)."""
    try:
        return primary()
    except Exception as exc:  # noqa: BLE001 - degrade gracefully
        if on_error is not None:
            on_error(exc)
        return fallback()
