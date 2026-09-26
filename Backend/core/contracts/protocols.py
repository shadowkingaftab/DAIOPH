"""Protocol definitions for the DAIOPH system."""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class Component(Protocol):
    """Base protocol for all system components."""

    def start(self) -> None:
        """Start the component."""
        ...

    def stop(self) -> None:
        """Stop the component."""
        ...

    @property
    def is_running(self) -> bool:
        """Whether the component is running."""
        ...


@runtime_checkable
class Configurable(Protocol):
    """Protocol for components that accept configuration."""

    def configure(self, config: Dict[str, Any]) -> None:
        """Apply configuration.

        Args:
            config: Configuration dictionary.
        """
        ...


@runtime_checkable
class Runnable(Protocol):
    """Protocol for runnable tasks."""

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the task.

        Returns:
            Any: Task result.
        """
        ...


@runtime_checkable
class ModelProvider(Protocol):
    """Protocol for model providers."""

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate output from a prompt.

        Args:
            prompt: Input prompt.
            **kwargs: Provider-specific options.

        Returns:
            str: Generated output.
        """
        ...


@runtime_checkable
class MemoryStore(Protocol):
    """Protocol for memory stores."""

    def store(self, key: str, value: Any) -> None:
        """Store a value.

        Args:
            key: Storage key.
            value: Value to store.
        """
        ...

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value.

        Args:
            key: Storage key.

        Returns:
            Optional[Any]: Stored value or None.
        """
        ...