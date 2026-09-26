"""RemoteProviderRouter - routes requests to remote providers."""

from typing import Any, Dict, Optional


class RemoteProviderRouter:
    """Routes requests to appropriate remote providers."""

    def __init__(self) -> None:
        """Initialize the provider router."""
        self._routes: Dict[str, str] = {}
        self._providers: Dict[str, Any] = {}

    def add_route(self, model: str, provider_name: str) -> None:
        """Add a routing rule.

        Args:
            model: Model name.
            provider_name: Provider to route to.
        """
        self._routes[model] = provider_name

    def register_provider(self, name: str, provider: Any) -> None:
        """Register a provider.

        Args:
            name: Provider name.
            provider: Provider instance.
        """
        self._providers[name] = provider

    def route(self, model: str) -> Optional[Any]:
        """Route a model request to its provider.

        Args:
            model: Model name.

        Returns:
            Optional[Any]: Provider instance or None.
        """
        provider_name = self._routes.get(model)
        if provider_name:
            return self._providers.get(provider_name)
        return None

</final_file_content>
</write_to_file></tool_call>