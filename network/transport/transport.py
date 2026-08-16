from __future__ import annotations

from typing import Any, Dict


class Transport:
    """Base transport layer for network communication."""

    def __init__(self, endpoint: str = "") -> None:
        self.endpoint = endpoint
        self.connected: bool = False

    def connect(self) -> bool:
        """Establish a connection."""
        self.connected = True
        return True

    def disconnect(self) -> None:
        """Close the connection."""
        self.connected = False

    def send(self, data: Dict[str, Any]) -> bool:
        """Send data over the transport."""
        if not self.connected:
            return False
        return True

    def receive(self) -> Dict[str, Any]:
        """Receive data from the transport."""
        return {}

    def is_connected(self) -> bool:
        """Check if the transport is connected."""
        return self.connected