"""Contract-level error definitions for the DAIOPH system."""

from typing import Optional


class ContractError(Exception):
    """Base error for contract violations."""

    def __init__(self, message: str, code: str = "CONTRACT_ERROR", details: Optional[dict] = None) -> None:
        """Initialize the error.

        Args:
            message: Error message.
            code: Error code.
            details: Additional error details.
        """
        super().__init__(message)
        self.code = code
        self.details = details or {}


class ValidationError(ContractError):
    """Raised when a contract validation fails."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        """Initialize the error."""
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class SchemaError(ContractError):
    """Raised when a data schema is violated."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        """Initialize the error."""
        super().__init__(message, code="SCHEMA_ERROR", details=details)


class SerializationError(ContractError):
    """Raised when serialization/deserialization fails."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        """Initialize the error."""
        super().__init__(message, code="SERIALIZATION_ERROR", details=details)