"""Security error types for the DAIOPH system."""

from typing import Any, Dict, Optional

from core.errors.base import DAIOPHError


class SecurityError(DAIOPHError):
    """Base security error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, code="SECURITY_ERROR", details=details)


class AuthenticationError(SecurityError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        """Initialize the error."""
        super().__init__(message)


class AuthorizationError(SecurityError):
    """Raised when a user lacks permission."""

    def __init__(self, message: str = "Permission denied") -> None:
        """Initialize the error."""
        super().__init__(message)


class EncryptionError(SecurityError):
    """Raised when encryption/decryption fails."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        super().__init__(message)


class SandboxViolationError(SecurityError):
    """Raised when a sandbox/security boundary is violated."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        super().__init__(message)


class PromptInjectionError(SecurityError):
    """Raised when a prompt injection attack is detected."""

    def __init__(self, message: str = "Prompt injection detected") -> None:
        """Initialize the error."""
        super().__init__(message)


class DataPrivacyError(SecurityError):
    """Raised when a privacy policy is violated."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        super().__init__(message)