"""Ordered fallback across route handlers.

Given handlers registered per route ("edge", "cloud"), :class:`FallbackManager`
tries them in preference order until one succeeds. Failures are collected
honestly: if every route fails, :class:`FallbackExhausted` carries each
route's error rather than fabricating success.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Sequence, Tuple

from orchestration.execution.task_executor import TaskHandler

__all__ = ["FallbackManager", "FallbackExhausted"]

logger = logging.getLogger(__name__)


class FallbackExhausted(RuntimeError):
    """All configured routes failed; carries per-route error details."""

    def __init__(self, errors: Dict[str, str]) -> None:
        self.errors = dict(errors)
        detail = "; ".join(f"{k}: {v}" for k, v in errors.items())
        super().__init__(f"all routes failed [{detail}]")


class FallbackManager:
    """Tries route handlers in order until one succeeds."""

    def __init__(
        self,
        handlers: Dict[str, TaskHandler],
        preference: Sequence[str] = ("edge", "cloud"),
    ) -> None:
        unknown = set(preference) - set(handlers)
        if unknown:
            raise ValueError(f"preference lists unregistered routes: {sorted(unknown)}")
        self.handlers = dict(handlers)
        self.preference = list(preference)

    def run(
        self,
        task_id: str,
        description: str,
        context: Dict[str, Any],
        order: List[str] | None = None,
    ) -> Tuple[Any, str, int]:
        """Execute via the first succeeding handler.

        Returns:
            ``(output, route_used, attempts)``.

        Raises:
            FallbackExhausted: If every attempted route fails.
        """
        errors: Dict[str, str] = {}
        attempts = 0
        for route in (order or self.preference):
            handler = self.handlers.get(route)
            if handler is None:
                continue
            attempts += 1
            try:
                output = handler(task_id, description, context)
                logger.info("task %s succeeded via %s", task_id, route)
                return output, route, attempts
            except Exception as exc:  # noqa: BLE001 - collect and continue
                logger.warning("task %s failed via %s: %s", task_id, route, exc)
                errors[route] = str(exc)
        raise FallbackExhausted(errors)
