"""Command definitions for the DAIOPH system."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Command:
    """A command to be executed by the system."""

    name: str
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None


@dataclass
class CommandResult:
    """The result of executing a command."""

    command: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: float = 0.0


class CommandRegistry:
    """Registry for command handlers."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self._handlers: Dict[str, Any] = {}

    def register(self, name: str, handler: Any) -> None:
        """Register a command handler.

        Args:
            name: Command name.
            handler: Handler callable.
        """
        self._handlers[name] = handler

    def execute(self, command: Command) -> CommandResult:
        """Execute a command.

        Args:
            command: Command to execute.

        Returns:
            CommandResult: Command execution result.
        """
        import time

        handler = self._handlers.get(command.name)
        if not handler:
            return CommandResult(
                command=command.name,
                success=False,
                error=f"Unknown command: {command.name}",
            )

        start = time.time()
        try:
            data = handler(command.payload)
            return CommandResult(
                command=command.name,
                success=True,
                data=data,
                duration=time.time() - start,
            )
        except Exception as e:
            return CommandResult(
                command=command.name,
                success=False,
                error=str(e),
                duration=time.time() - start,
            )

    def has(self, name: str) -> bool:
        """Check if a command is registered.

        Args:
            name: Command name.

        Returns:
            bool: True if registered.
        """
        return name in self._handlers

    def list_commands(self) -> list:
        """List all registered command names.

        Returns:
            list: Registered command names.
        """
        return list(self._handlers.keys())