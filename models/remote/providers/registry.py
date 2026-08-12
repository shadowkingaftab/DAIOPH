"""RemoteProviderRegistry - registry for remote providers."""

from typing import Any, Dict, Optional


class RemoteProviderRegistry:
    """Registry for remote model providers."""

    def __init__(self) -> None:
        """Initialize the provider registry."""
        self._providers: Dict[str, Any] = {}

    def register(self, name: str, provider: Any) -> None:
        """Register a provider.

        Args:
            name: Provider name.
            provider: Provider instance.
        """
        self._providers[name] = provider

    def get(self, name: str) -> Optional[Any]:
        """Get a provider by name.

        Args:
            name: Provider name.

        Returns:
            Optional[Any]: Provider instance or None.
        """
        return self._providers.get(name)

    def list_providers(self) -> List[str]:
        """List all provider names.

        Returns:
            List[str]: Provider names.
        """
        return list(self._providers.keys())

</final_file_content>
</write_to_file></tool_call>