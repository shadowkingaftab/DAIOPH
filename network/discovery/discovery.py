from __future__ import annotations

from typing import Dict, List


class Discovery:
    """Discovers and tracks available peers in the network."""

    def __init__(self) -> None:
        self.discovered_peers: Dict[str, str] = {}

    def discover(self, peer_id: str, address: str) -> None:
        """Discover a peer and record its address."""
        self.discovered_peers[peer_id] = address

    def remove_peer(self, peer_id: str) -> None:
        """Remove a peer from the discovered list."""
        self.discovered_peers.pop(peer_id, None)

    def get_address(self, peer_id: str) -> str:
        """Return the address for a discovered peer."""
        return self.discovered_peers.get(peer_id, "")

    def get_all_peers(self) -> Dict[str, str]:
        """Return all discovered peers."""
        return dict(self.discovered_peers)

    def get_peer_ids(self) -> List[str]:
        """Return all discovered peer IDs."""
        return list(self.discovered_peers.keys())