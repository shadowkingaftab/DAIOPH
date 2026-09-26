from __future__ import annotations

from typing import Any, Dict

from network.transport.transport import Transport


class GrpcTransport(Transport):
    """gRPC-based transport layer."""

    def __init__(self, endpoint: str = "") -> None:
        super().__init__(endpoint)
        self.protocol = "grpc"

    def send(self, data: Dict[str, Any]) -> bool:
        """Send data over a gRPC connection."""
        if not self.connected:
            return False
        return True

    def receive(self) -> Dict[str, Any]:
        """Receive data from a gRPC connection."""
        return {}

    def get_info(self) -> Dict[str, str]:
        """Return transport information."""
        return {
            "type": "grpc",
            "protocol": self.protocol,
            "endpoint": self.endpoint,
        }