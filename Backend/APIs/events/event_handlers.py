"""Registry and dispatch for API-layer event handlers.

:class:`EventHandlerRegistry` maps event type names to handler callables.
Dispatch isolates handler failures: one broken handler logs and continues,
and the dispatch result reports per-handler outcomes honestly.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Callable, Dict, List

__all__ = ["EventHandlerRegistry"]

logger = logging.getLogger(__name__)

Handler = Callable[[Dict[str, Any]], Any]


class EventHandlerRegistry:
    """Register handlers per event type and dispatch events to them."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Handler]] = {}
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, handler: Handler) -> None:
        """Register *handler* for *event_type* (multiple allowed)."""
        with self._lock:
            self._handlers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: Handler) -> None:
        """Remove a previously registered handler (no-op when absent)."""
        with self._lock:
            handlers = self._handlers.get(event_type, [])
            if handler in handlers:
                handlers.remove(handler)

    def dispatch(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send *payload* to every handler of *event_type*.

        Returns:
            ``{"delivered": [...], "failed": {name: error}}`` — failures are
            isolated and reported, never silently swallowed.
        """
        with self._lock:
            handlers = list(self._handlers.get(event_type, []))
        delivered: List[str] = []
        failed: Dict[str, str] = {}
        for handler in handlers:
            name = getattr(handler, "__name__", repr(handler))
            try:
                handler(payload)
                delivered.append(name)
            except Exception as exc:  # noqa: BLE001 - isolate per handler
                logger.warning("handler %s failed on %s: %s", name, event_type, exc)
                failed[name] = str(exc)
        return {"delivered": delivered, "failed": failed}

    def event_types(self) -> List[str]:
        """All event types that currently have at least one handler."""
        with self._lock:
            return sorted(
                event_type
                for event_type, handlers in self._handlers.items()
                if handlers
            )
