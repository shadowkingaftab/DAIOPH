from __future__ import annotations

from typing import Any, Dict, List


class PeerRegistry:
    """Registry for tracking known network peers."""

    def __init__(self) -> None:
        self.peers: Dict[str, Any] = {}

    def register(self, peer_id: str, info: Any) -> None:
        """Register a peer with its information."""
        self.peers[peer_id] = info

    def unregister(self, peer_id: str) -> None:
        """Remove a peer from the registry."""
        self.peers.pop(peer_id, None)

    def get_peer(self, peer_id: str) -> Any:
        """Return information about a peer."""
        return self.peers.get(peer_id)

    def has_peer(self, peer_id: str) -> bool:
        """Check if a peer is registered."""
        return peer_id in self.peers

    def get_all_peers(self) -> Dict[str, Any]:
        """Return all registered peers."""
        return dict(self.peers)

    def get_peer_ids(self) -> List[str]:
        """Return all registered peer IDs."""
        return list(self.peers.keys())