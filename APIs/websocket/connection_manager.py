"""Thread-safe registry of live WebSocket-style connections.

A *connection* is any object exposing ``send(payload_dict)`` and an id —
the manager is transport-agnostic so ASGI, aiohttp, or test fakes all work.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, List, Optional

__all__ = ["ConnectionManager"]

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Track connections, send targeted messages, and broadcast."""

    def __init__(self) -> None:
        self._connections: Dict[str, Any] = {}
        self._meta: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def register(self, connection_id: str, connection: Any) -> None:
        """Register *connection* under *connection_id*."""
        with self._lock:
            if connection_id in self._connections:
                raise ValueError(f"connection id already registered: {connection_id!r}")
            self._connections[connection_id] = connection
            self._meta[connection_id] = {"connected_at": time.time()}

    def unregister(self, connection_id: str) -> None:
        """Drop *connection_id* (no-op when absent)."""
        with self._lock:
            self._connections.pop(connection_id, None)
            self._meta.pop(connection_id, None)

    def is_connected(self, connection_id: str) -> bool:
        """True when *connection_id* is currently registered."""
        with self._lock:
            return connection_id in self._connections

    def count(self) -> int:
        """Number of live connections."""
        with self._lock:
            return len(self._connections)

    def send_to(self, connection_id: str, payload: Dict[str, Any]) -> bool:
        """Send *payload* to one connection.

        Returns:
            True on success; False when the connection is gone or the send
            failed (the failure is logged, not raised).
        """
        with self._lock:
            connection = self._connections.get(connection_id)
        if connection is None:
            return False
        try:
            connection.send(payload)
            return True
        except Exception as exc:  # noqa: BLE001 - dead connection
            logger.warning("send to %s failed: %s", connection_id, exc)
            self.unregister(connection_id)
            return False

    def broadcast(self, payload: Dict[str, Any]) -> Dict[str, int]:
        """Send *payload* to every connection.

        Returns:
            ``{"sent": n, "failed": m}`` summary counts.
        """
        with self._lock:
            ids = list(self._connections.keys())
        sent = failed = 0
        for connection_id in ids:
            if self.send_to(connection_id, payload):
                sent += 1
            else:
                failed += 1
        return {"sent": sent, "failed": failed}

    def metadata(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Connection metadata (connected_at), or None when unknown."""
        with self._lock:
            meta = self._meta.get(connection_id)
            return dict(meta) if meta else None
