from __future__ import annotations

from typing import Any, Dict

from network.transport.transport import Transport


class WebSocketTransport(Transport):
    """WebSocket-based transport layer."""

    def __init__(self, endpoint: str = "", protocol: str = "ws") -> None:
        super().__init__(endpoint)
        self.protocol = protocol

    def send(self, data: Dict[str, Any]) -> bool:
        """Send data over a WebSocket connection."""
        if not self.connected:
            return False
        return True

    def receive(self) -> Dict[str, Any]:
        """Receive data from a WebSocket connection."""
        return {}

    def get_info(self) -> Dict[str, str]:
        """Return transport information."""
        return {
            "type": "websocket",
            "protocol": self.protocol,
            "endpoint": self.endpoint,
        }