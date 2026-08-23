"""WebSocket server facade over the connection manager.

:class:`WebSocketServer` routes incoming messages to registered handlers by
message ``type`` and manages connections. Actual socket serving requires a
WS runtime (ASGI/aiohttp) that this project does not bundle: :meth:`start`
accepts an injected *transport* callable — without one it raises an
explicit error instead of pretending to listen.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

from APIs.websocket.connection_manager import ConnectionManager

__all__ = ["WebSocketServer", "WebSocketTransportError"]

logger = logging.getLogger(__name__)

MessageHandler = Callable[[str, Dict[str, Any]], Optional[Dict[str, Any]]]


class WebSocketTransportError(RuntimeError):
    """No transport was injected; the server cannot accept connections."""


class WebSocketServer:
    """Message-type router plus connection lifecycle facade."""

    def __init__(
        self,
        manager: Optional[ConnectionManager] = None,
    ) -> None:
        self.manager = manager or ConnectionManager()
        self._handlers: Dict[str, MessageHandler] = {}
        self._transport: Optional[Callable[..., Any]] = None

    def register_handler(self, message_type: str, handler: MessageHandler) -> None:
        """Register *handler* for incoming messages of *message_type*."""
        self._handlers[message_type] = handler

    def attach_transport(self, transport: Callable[..., Any]) -> None:
        """Inject the platform transport that accepts real sockets.

        The callable receives this server and should run the accept loop
        (e.g. an ASGI application factory). Nothing is implied about the
        framework; the project ships none by default.
        """
        self._transport = transport

    def start(self) -> Any:
        """Start serving via the injected transport.

        Raises:
            WebSocketTransportError: If no transport was attached — an
                honest failure, never a silent no-op.
        """
        if self._transport is None:
            raise WebSocketTransportError(
                "no WebSocket transport attached; call attach_transport(...) "
                "with an ASGI/aiohttp accept-loop callable first"
            )
        logger.info("starting WebSocket server via injected transport")
        return self._transport(self)

    def handle_message(
        self, connection_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route one inbound message to its registered handler.

        Returns:
            The handler's reply wrapped as ``{"type": ..., "data": ...}``,
            or an explicit ``error`` message for unknown types/handlers.
        """
        if not isinstance(payload, dict) or "type" not in payload:
            return {"type": "error", "data": {"error": "message must be an "
                                              "object with a 'type' field"}}
        message_type = payload["type"]
        handler = self._handlers.get(message_type)
        if handler is None:
            return {
                "type": "error",
                "data": {"error": f"no handler for message type {message_type!r}"},
            }
        try:
            reply = handler(connection_id, payload.get("data", {}))
        except Exception as exc:  # noqa: BLE001 - isolate handler failure
            logger.warning("handler for %s failed: %s", message_type, exc)
            return {"type": "error", "data": {"error": str(exc)}}
        return {"type": f"{message_type}.reply", "data": reply}

    def connect(self, connection_id: str, connection: Any) -> None:
        """Register an inbound connection (delegates to the manager)."""
        self.manager.register(connection_id, connection)

    def disconnect(self, connection_id: str) -> None:
        """Drop a connection (delegates to the manager)."""
        self.manager.unregister(connection_id)
