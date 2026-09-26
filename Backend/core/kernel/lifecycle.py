"""Lifecycle management for the DAIOPH kernel."""

from enum import Enum
from typing import Any, Callable, Dict, Optional


class ComponentState(Enum):
    """Lifecycle states for a component."""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class LifecycleManager:
    """Tracks and manages the lifecycle of kernel components."""

    def __init__(self) -> None:
        """Initialize the lifecycle manager."""
        self._states: Dict[str, ComponentState] = {}
        self._hooks: Dict[str, Dict[str, Callable]] = {}

    def register(self, name: str, hooks: Optional[Dict[str, Callable]] = None) -> None:
        """Register a component with lifecycle hooks.

        Args:
            name: Component name.
            hooks: Optional dict of lifecycle hook callables
                   (init, start, stop, destroy).
        """
        self._states[name] = ComponentState.UNINITIALIZED
        self._hooks[name] = hooks or {}

    def transition(self, name: str, state: ComponentState) -> None:
        """Transition a component to a new state.

        Args:
            name: Component name.
            state: Target state.
        """
        self._states[name] = state
        hook = self._hooks.get(name, {}).get(state.value)
        if hook:
            try:
                hook()
            except Exception as e:  # pragma: no cover
                print(f"[Lifecycle] Hook error for {name}: {e}")

    def get_state(self, name: str) -> ComponentState:
        """Get a component's current state.

        Args:
            name: Component name.

        Returns:
            ComponentState: Current state.
        """
        return self._states.get(name, ComponentState.UNINITIALIZED)

    def initialize(self, name: str) -> None:
        """Initialize a component."""
        self.transition(name, ComponentState.INITIALIZING)
        self.transition(name, ComponentState.READY)

    def start(self, name: str) -> None:
        """Start a component."""
        self.transition(name, ComponentState.STARTING)
        self.transition(name, ComponentState.RUNNING)

    def stop(self, name: str) -> None:
        """Stop a component."""
        self.transition(name, ComponentState.STOPPING)
        self.transition(name, ComponentState.STOPPED)

    def fail(self, name: str) -> None:
        """Mark a component as failed."""
        self.transition(name, ComponentState.ERROR)

    def all_ready(self) -> bool:
        """Check if all registered components are ready/running.

        Returns:
            bool: True if all components are in a healthy state.
        """
        return all(
            s in (ComponentState.READY, ComponentState.RUNNING)
            for s in self._states.values()
        )

    def get_status(self) -> Dict[str, str]:
        """Get the status of all components.

        Returns:
            Dict[str, str]: Component name to state mapping.
        """
        return {name: state.value for name, state in self._states.items()}