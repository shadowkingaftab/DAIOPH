from __future__ import annotations

from typing import Any, Dict, Optional


class Peer:
    """Represents a network peer."""

    def __init__(self, peer_id: str, address: str = "") -> None:
        self.peer_id = peer_id
        self.address = address
        self.connected: bool = False
        self.last_seen: Optional[float] = None

    def connect(self) -> None:
        """Connect to the peer."""
        self.connected = True

    def disconnect(self) -> None:
        """Disconnect from the peer."""
        self.connected = False

    def send(self, message: Dict[str, Any]) -> bool:
        """Send a message to the peer."""
        if not self.connected:
            return False
        return True

    def get_info(self) -> Dict[str, Any]:
        """Return peer information."""
        return {
            "peer_id": self.peer_id,
            "address": self.address,
            "connected": self.connected,
            "last_seen": self.last_seen,
        }