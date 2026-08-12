"""Base error types for the DAIOPH system."""

from typing import Any, Dict, Optional


class DAIOPHError(Exception):
    """Base error class for all DAIOPH exceptions."""

    def __init__(
        self,
        message: str,
        code: str = "DAIOPH_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error message.
            code: Machine-readable error code.
            details: Additional structured error details.
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the error to a dict.

        Returns:
            Dict[str, Any]: Serialized error.
        """
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }


class ConfigurationError(DAIOPHError):
    """Raised when there is a configuration problem."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, code="CONFIGURATION_ERROR", details=details)


class InitializationError(DAIOPHError):
    """Raised when a component fails to initialize."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, code="INITIALIZATION_ERROR", details=details)


class UnsupportedOperationError(DAIOPHError):
    """Raised when an operation is not supported."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, code="UNSUPPORTED_OPERATION", details=details)


class NotImplementedFeatureError(DAIOPHError):
    """Raised when a feature is not yet implemented."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, code="NOT_IMPLEMENTED", details=details)