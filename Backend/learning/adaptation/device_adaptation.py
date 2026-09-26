"""DeviceAdaptation - adapts to device capabilities and constraints."""

from typing import Any, Dict, Optional


class DeviceAdaptation:
    """Adapts system behavior based on device capabilities."""

    def __init__(self) -> None:
        """Initialize device adaptation."""
        self._capabilities: Dict[str, Any] = {}
        self._constraints: Dict[str, Any] = {}

    def set_capabilities(self, capabilities: Dict[str, Any]) -> None:
        """Set device capabilities.

        Args:
            capabilities: Device capability profile.
        """
        self._capabilities = capabilities

    def get_capability(self, name: str, default: Any = None) -> Any:
        """Get a device capability.

        Args:
            name: Capability name.
            default: Default if not found.

        Returns:
            Any: Capability value.
        """
        return self._capabilities.get(name, default)

    def set_constraint(self, name: str, value: Any) -> None:
        """Set a performance constraint.

        Args:
            name: Constraint name.
            value: Constraint value.
        """
        self._constraints[name] = value

    def get_constraint(self, name: str, default: Any = None) -> Any:
        """Get a performance constraint.

        Args:
            name: Constraint name.
            default: Default if not found.

        Returns:
            Any: Constraint value.
        """
        return self._constraints.get(name, default)

    def get_adaptation_profile(self) -> Dict[str, Any]:
        """Get the current adaptation profile.

        Returns:
            Dict[str, Any]: Adaptation profile.
        """
        return {
            "capabilities": dict(self._capabilities),
            "constraints": dict(self._constraints),
        }

    def reset(self) -> None:
        """Reset device adaptation."""
        self._capabilities = {}
        self._constraints = {}

</final_file_content>
</write_to_file>