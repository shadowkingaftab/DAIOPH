"""Fault injection helpers."""

from __future__ import annotations

from typing import Any, Callable, Optional

__all__ = ["inject_failure"]


def inject_failure(
    fn: Callable[[], Any],
    fail: bool,
    error: Optional[Exception] = None,
) -> Any:
    """Run *fn* normally, or raise *error* when *fail* is True."""
    if fail:
        raise error or RuntimeError("injected fault")
    return fn()
