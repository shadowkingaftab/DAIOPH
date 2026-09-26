"""gRPC server scaffold.

:class:`GrpcServer` reports honestly that serving requires ``grpcio``: the
dependency is guarded at import time and :meth:`serve` raises
:class:`GrpcNotAvailableError` unless the package (and generated stubs)
are present. No fake listening, no fake ports.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from APIs.grpc.services import GrpcNotAvailableError

__all__ = ["GrpcServer"]

logger = logging.getLogger(__name__)

try:  # guarded: grpcio is intentionally not a project dependency
    import grpc  # type: ignore[import-not-found]

    GRPC_AVAILABLE = True
except ImportError:  # pragma: no cover - depends on environment
    grpc = None  # type: ignore[assignment]
    GRPC_AVAILABLE = False


class GrpcServer:
    """Facade for a future grpc.io server."""

    def __init__(self, port: int = 50051, max_workers: int = 4) -> None:
        if port < 1 or port > 65535:
            raise ValueError("port must be within [1, 65535]")
        if max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        self.port = port
        self.max_workers = max_workers
        self._services: Dict[str, Any] = {}

    @property
    def available(self) -> bool:
        """True only when the grpcio package imports successfully."""
        return GRPC_AVAILABLE

    def register_service(self, name: str, service: Any) -> None:
        """Register a service implementation under *name*."""
        self._services[name] = service

    def serve(self, wait_forever: bool = True) -> Optional[Any]:
        """Start the gRPC server.

        Raises:
            GrpcNotAvailableError: When grpcio is not installed — the only
                honest behaviour for an unwired transport.
        """
        if not GRPC_AVAILABLE:
            raise GrpcNotAvailableError(
                "grpcio is not installed; the DAIOPH project does not "
                "bundle a gRPC transport. Install grpcio, generate stubs "
                "from protos, and extend GrpcServer to enable serving."
            )
        raise NotImplementedError(
            "grpcio detected but no generated service stubs are wired; "
            "extend GrpcServer with add_XServicer_to_server calls first"
        )
