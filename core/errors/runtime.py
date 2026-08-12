"""Runtime error types for the DAIOPH system."""

from typing import Any, Dict, Optional

from core.errors.base import DAIOPHError


class RuntimeError(DAIOPHError):
    """Base runtime error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, code="RUNTIME_ERROR", details=details)


class ComponentNotFoundError(RuntimeError):
    """Raised when a component is not registered."""

    def __init__(self, component: str) -> None:
        """Initialize the error."""
        super().__init__(
            f"Component '{component}' not found",
            details={"component": component},
        )


class ComponentAlreadyRegisteredError(RuntimeError):
    """Raised when a component is registered twice."""

    def __init__(self, component: str) -> None:
        """Initialize the error."""
        super().__init__(
            f"Component '{component}' already registered",
            details={"component": component},
        )


class LifecycleError(RuntimeError):
    """Raised on invalid lifecycle transitions."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, details=details)


class EventLoopError(RuntimeError):
    """Raised when the event loop fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, details=details)


class ShutdownError(RuntimeError):
    """Raised when shutdown fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, details=details)