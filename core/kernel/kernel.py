"""Core kernel - the central orchestrator for the DAIOPH runtime."""

import time
from typing import Any, Dict, List, Optional


class Kernel:
    """Central kernel that coordinates all system components.

    The kernel manages the lifecycle of all subsystems (models, memory,
    orchestration, hardware) and provides a unified runtime interface.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the kernel.

        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        self._components: Dict[str, Any] = {}
        self._started = False
        self._start_time: Optional[float] = None

    def register(self, name: str, component: Any) -> None:
        """Register a component with the kernel.

        Args:
            name: Component name.
            component: Component instance.
        """
        self._components[name] = component

    def get(self, name: str) -> Optional[Any]:
        """Get a registered component.

        Args:
            name: Component name.

        Returns:
            Optional[Any]: The component, or None if not registered.
        """
        return self._components.get(name)

    def start(self) -> None:
        """Start the kernel and all registered components."""
        if self._started:
            return
        self._start_time = time.time()
        self._started = True
        print(f"[Kernel] Started with {len(self._components)} components")

    def stop(self) -> None:
        """Stop the kernel and all registered components."""
        if not self._started:
            return
        self._started = False
        print("[Kernel] Stopped")

    @property
    def uptime(self) -> float:
        """Get kernel uptime in seconds."""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    @property
    def is_running(self) -> bool:
        """Whether the kernel is running."""
        return self._started

    def components(self) -> Dict[str, Any]:
        """Get all registered components.

        Returns:
            Dict[str, Any]: Registered components.
        """
        return dict(self._components)