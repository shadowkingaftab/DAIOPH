"""gRPC service interfaces (scaffold).

gRPC is **not wired** in this project: ``grpcio`` is not a dependency and no
proto files are generated. These interfaces define the contract a future
implementation must satisfy; every method raises
:class:`GrpcNotAvailableError` until a real transport is added. This is a
deliberate honest stub, not fake functionality.
"""

from __future__ import annotations

from typing import Any, Dict

__all__ = ["GrpcNotAvailableError", "ChatService", "MemoryService"]


class GrpcNotAvailableError(ImportError):
    """gRPC transport is not installed/wired in this deployment."""


def _unavailable(service: str, method: str) -> GrpcNotAvailableError:
    return GrpcNotAvailableError(
        f"{service}.{method} requires the grpcio package and generated "
        "protos, which are not part of this project's dependencies. Add "
        "grpcio + generated stubs and override this service to enable it."
    )


class ChatService:
    """Contract for a future chat gRPC service."""

    def SendMessage(self, request: Dict[str, Any]) -> Dict[str, Any]:  # noqa: N802
        """Proxy a chat message; unavailable until grpcio is wired."""
        raise _unavailable("ChatService", "SendMessage")

    def StreamResponses(self, request: Dict[str, Any]) -> Dict[str, Any]:  # noqa: N802
        """Stream chat responses; unavailable until grpcio is wired."""
        raise _unavailable("ChatService", "StreamResponses")


class MemoryService:
    """Contract for a future memory gRPC service."""

    def QueryMemory(self, request: Dict[str, Any]) -> Dict[str, Any]:  # noqa: N802
        """Query memory stores; unavailable until grpcio is wired."""
        raise _unavailable("MemoryService", "QueryMemory")
