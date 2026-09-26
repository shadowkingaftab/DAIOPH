from __future__ import annotations

from typing import Any, Dict, List


class PeerManager:
    """Manages peer connections in the network."""

    def __init__(self) -> None:
        self.peers: Dict[str, Any] = {}

    def add_peer(self, peer_id: str, peer: Any) -> None:
        """Add a peer to be managed."""
        self.peers[peer_id] = peer

    def remove_peer(self, peer_id: str) -> None:
        """Remove a peer from management."""
        self.peers.pop(peer_id, None)

    def connect_all(self) -> int:
        """Connect to all managed peers.

        Returns:
            The number of successfully connected peers.
        """
        count = 0
        for peer in self.peers.values():
            peer.connect()
            count += 1
        return count

    def disconnect_all(self) -> None:
        """Disconnect from all managed peers."""
        for peer in self.peers.values():
            peer.disconnect()

    def get_peer(self, peer_id: str) -> Any:
        """Return a managed peer by ID."""
        return self.peers.get(peer_id)

    def get_connected_peers(self) -> List[str]:
        """Return IDs of connected peers."""
        result = []
        for peer_id, peer in self.peers.items():
            if getattr(peer, "connected", False):
                result.append(peer_id)
        return result

    def get_all_peers(self) -> Dict[str, Any]:
        """Return all managed peers."""
        return dict(self.peers)