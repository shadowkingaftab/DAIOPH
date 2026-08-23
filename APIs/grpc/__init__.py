"""gRPC API scaffold (grpcio is not a project dependency)."""

from APIs.grpc.server import GrpcServer
from APIs.grpc.services import GrpcNotAvailableError

__all__ = ["GrpcNotAvailableError", "GrpcServer"]
