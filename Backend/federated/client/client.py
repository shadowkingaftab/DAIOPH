from __future__ import annotations

from typing import Any, Dict, Optional


class FederatedClient:
    """Represents a client participating in federated learning."""

    def __init__(self, client_id: str, endpoint: str = "") -> None:
        self.client_id = client_id
        self.endpoint = endpoint
        self.model_state: Optional[Dict[str, Any]] = None
        self.connected: bool = False
        self.rounds_participated: int = 0

    def connect(self) -> bool:
        """Establish a connection to the federated server."""
        self.connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from the federated server."""
        self.connected = False

    def receive_model(self, model_state: Dict[str, Any]) -> None:
        """Receive the global model state from the server."""
        self.model_state = model_state

    def participate_in_round(self) -> bool:
        """Mark participation in a training round."""
        if not self.connected:
            return False
        self.rounds_participated += 1
        return True

    def get_status(self) -> Dict[str, Any]:
        """Return the client status."""
        return {
            "client_id": self.client_id,
            "connected": self.connected,
            "rounds_participated": self.rounds_participated,
            "has_model": self.model_state is not None,
        }