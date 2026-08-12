"""Capability definitions for the DAIOPH system."""

from dataclasses import dataclass, field
from typing import Any, Dict, Set


@dataclass
class Capability:
    """A capability descriptor for a system component."""

    name: str
    version: str = "1.0"
    parameters: Dict[str, Any] = field(default_factory=dict)


class CapabilityRegistry:
    """Registry mapping components to their capabilities."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self._capabilities: Dict[str, Set[str]] = {}

    def register(self, component: str, capabilities: Set[str]) -> None:
        """Register capabilities for a component.

        Args:
            component: Component name.
            capabilities: Set of capability names.
        """
        self._capabilities[component] = capabilities

    def has(self, component: str, capability: str) -> bool:
        """Check if a component has a capability.

        Args:
            component: Component name.
            capability: Capability name.

        Returns:
            bool: True if the component has the capability.
        """
        return capability in self._capabilities.get(component, set())

    def get(self, component: str) -> Set[str]:
        """Get all capabilities of a component.

        Args:
            component: Component name.

        Returns:
            Set[str]: Capability names.
        """
        return set(self._capabilities.get(component, set()))

    def all(self) -> Dict[str, Set[str]]:
        """Get all component capabilities.

        Returns:
            Dict[str, Set[str]]: Component to capabilities mapping.
        """
        return {k: set(v) for k, v in self._capabilities.items()}