"""Result definitions for the DAIOPH system."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Result:
    """A generic execution result."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, data: Any = None, **metadata: Any) -> "Result":
        """Create a success result.

        Args:
            data: Result data.
            **metadata: Additional metadata.

        Returns:
            Result: Success result.
        """
        return cls(success=True, data=data, metadata=metadata)

    @classmethod
    def fail(cls, error: str, **metadata: Any) -> "Result":
        """Create a failure result.

        Args:
            error: Error message.
            **metadata: Additional metadata.

        Returns:
            Result: Failure result.
        """
        return cls(success=False, error=error, metadata=metadata)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict.

        Returns:
            Dict[str, Any]: Serialized result.
        """
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "duration": self.duration,
            "metadata": self.metadata,
        }