from __future__ import annotations

from typing import Any, Dict, List


class FederatedServer:
    """Coordinates federated learning across multiple clients."""

    def __init__(self, server_id: str = "server") -> None:
        self.server_id = server_id
        self.clients: Dict[str, Any] = {}
        self.global_model: Dict[str, Any] = {}
        self.round: int = 0
        self.running: bool = False

    def start(self) -> None:
        """Start the federated server."""
        self.running = True

    def stop(self) -> None:
        """Stop the federated server."""
        self.running = False

    def register_client(self, client_id: str, client: Any) -> None:
        """Register a client with the server."""
        self.clients[client_id] = client

    def unregister_client(self, client_id: str) -> None:
        """Remove a client from the server."""
        self.clients.pop(client_id, None)

    def set_global_model(self, model: Dict[str, Any]) -> None:
        """Set the global model state."""
        self.global_model = model

    def get_global_model(self) -> Dict[str, Any]:
        """Return the current global model."""
        return self.global_model

    def next_round(self) -> int:
        """Advance to the next training round."""
        self.round += 1
        return self.round

    def get_client_ids(self) -> List[str]:
        """Return the list of registered client IDs."""
        return list(self.clients.keys())

    def get_status(self) -> Dict[str, Any]:
        """Return the server status."""
        return {
            "server_id": self.server_id,
            "running": self.running,
            "round": self.round,
            "client_count": len(self.clients),
            "has_model": bool(self.global_model),
        }