"""Model error types for the DAIOPH system."""

from typing import Any, Dict, Optional

from core.errors.base import DAIOPHError


class ModelError(DAIOPHError):
    """Base model error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, code="MODEL_ERROR", details=details)


class ModelLoadError(ModelError):
    """Raised when a model fails to load."""

    def __init__(self, model_id: str, message: str) -> None:
        """Initialize the error."""
        super().__init__(
            f"Failed to load model '{model_id}': {message}",
            details={"model_id": model_id},
        )


class ModelNotFoundError(ModelError):
    """Raised when a model is not found."""

    def __init__(self, model_id: str) -> None:
        """Initialize the error."""
        super().__init__(
            f"Model '{model_id}' not found",
            details={"model_id": model_id},
        )


class ModelUnavailableError(ModelError):
    """Raised when a model is unavailable (e.g., API down)."""

    def __init__(self, model_id: str, message: str = "") -> None:
        """Initialize the error."""
        suffix = f": {message}" if message else ""
        super().__init__(
            f"Model '{model_id}' unavailable{suffix}",
            details={"model_id": model_id},
        )


class ModelGenerationError(ModelError):
    """Raised when model inference/generation fails."""

    def __init__(self, model_id: str, message: str) -> None:
        """Initialize the error."""
        super().__init__(
            f"Model '{model_id}' generation failed: {message}",
            details={"model_id": model_id},
        )


class OOMError(ModelError):
    """Raised when a model runs out of memory."""

    def __init__(self, model_id: str) -> None:
        """Initialize the error."""
        super().__init__(
            f"Model '{model_id}' out of memory",
            details={"model_id": model_id},
        )