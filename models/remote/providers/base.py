"""RemoteProviderBase - base class for remote model providers."""

from typing import Any, Dict, Optional


class RemoteProviderBase:
    """Base class for remote model providers."""

    def __init__(self, api_key: str = "", endpoint: str = "") -> None:
        """Initialize the remote provider.

        Args:
            api_key: API key for authentication.
            endpoint: API endpoint URL.
        """
        self._api_key = api_key
        self._endpoint = endpoint

    def request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the remote API.

        Args:
            payload: Request payload.

        Returns:
            Dict[str, Any]: Response data.
        """
        return {"status": "ok", "response": "placeholder"}

    def get_endpoint(self) -> str:
        """Get the API endpoint.

        Returns:
            str: Endpoint URL.
        """
        return self._endpoint

</final_file_content>
</write_to_file></tool_call>