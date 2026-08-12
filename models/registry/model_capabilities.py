"""ModelCapabilities - describes model capabilities."""

from typing import Any, Dict, List, Optional


class ModelCapabilities:
    """Describes the capabilities of a model."""

    def __init__(self) -> None:
        """Initialize model capabilities."""
        self._capabilities: Dict[str, Any] = {}

    def set(self, name: str, value: Any) -> None:
        """Set a capability.

        Args:
            name: Capability name.
            value: Capability value.
        """
        self._capabilities[name] = value

    def get(self, name: str, default: Any = None) -> Any:
        """Get a capability.

        Args:
            name: Capability name.
            default: Default if not found.

        Returns:
            Any: Capability value.
        """
        return self._capabilities.get(name, default)

    def supports(self, capability: str) -> bool:
        """Check if a capability is supported.

        Args:
            capability: Capability name.

        Returns:
            bool: True if supported.
        """
        return capability in self._capabilities

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict.

        Returns:
            Dict[str, Any]: Capabilities dict.
        """
        return dict(self._capabilities)

</final_file_content>
</write_to_file></tool_call>