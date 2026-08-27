"""Fallback chain (first success wins)."""

from __future__ import annotations

from typing import Any, Callable, List, Tuple

__all__ = ["FallbackExhausted", "fallback"]


class FallbackExhausted(RuntimeError):
    """Raised when every fallback fails."""


def fallback(handlers: List[Callable[[], Any]]) -> Tuple[Any, int]:
    """Try *handlers* in order; return (result, index) of first success.

    Raises:
        FallbackExhausted: When all handlers fail.
    """
    errors = []
    for index, handler in enumerate(handlers):
        try:
            return handler(), index
        except Exception as exc:  # noqa: BLE001 - try next
            errors.append(str(exc))
    raise FallbackExhausted(f"all fallbacks failed: {errors}")
