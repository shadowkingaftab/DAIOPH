"""Memory error types for the DAIOPH system."""

from typing import Any, Dict, Optional

from core.errors.base import DAIOPHError


class MemoryError(DAIOPHError):
    """Base memory error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, code="MEMORY_ERROR", details=details)


class MemoryFullError(MemoryError):
    """Raised when memory storage is full."""

    def __init__(self, memory_type: str, limit: int) -> None:
        """Initialize the error."""
        super().__init__(
            f"{memory_type} memory is full (limit: {limit})",
            details={"memory_type": memory_type, "limit": limit},
        )


class MemoryNotFoundError(MemoryError):
    """Raised when a memory entry is not found."""

    def __init__(self, key: str) -> None:
        """Initialize the error."""
        super().__init__(
            f"Memory entry '{key}' not found",
            details={"key": key},
        )


class MemorySerializationError(MemoryError):
    """Raised when memory content fails to serialize/deserialize."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        super().__init__(message)


class MemoryConsolidationError(MemoryError):
    """Raised when memory consolidation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, details=details)