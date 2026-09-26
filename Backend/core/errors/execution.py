"""Execution error types for the DAIOPH system."""

from typing import Any, Dict, Optional

from core.errors.base import DAIOPHError


class ExecutionError(DAIOPHError):
    """Base execution error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        super().__init__(message, code="EXECUTION_ERROR", details=details)


class TaskExecutionError(ExecutionError):
    """Raised when a task fails to execute."""

    def __init__(self, task_id: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the error."""
        message = f"Task '{task_id}' failed: {message}"
        super().__init__(message, details={"task_id": task_id, **(details or {})})


class TimeoutError(ExecutionError):
    """Raised when an execution times out."""

    def __init__(self, task_id: str, timeout: float) -> None:
        """Initialize the error."""
        super().__init__(
            f"Task '{task_id}' timed out after {timeout}s",
            details={"task_id": task_id, "timeout": timeout},
        )


class DependencyError(ExecutionError):
    """Raised when a task dependency is missing or failed."""

    def __init__(self, task_id: str, dependency: str) -> None:
        """Initialize the error."""
        super().__init__(
            f"Task '{task_id}' missing dependency '{dependency}'",
            details={"task_id": task_id, "dependency": dependency},
        )


class CancellationError(ExecutionError):
    """Raised when an execution is cancelled."""

    def __init__(self, task_id: str) -> None:
        """Initialize the error."""
        super().__init__(
            f"Task '{task_id}' was cancelled",
            details={"task_id": task_id},
        )