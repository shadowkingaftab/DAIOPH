"""OpenAIClient - client for OpenAI API."""

from typing import Any, Dict, Optional


class OpenAIClient:
    """Client for interacting with OpenAI API."""

    def __init__(self, api_key: str = "", endpoint: str = "https://api.openai.com") -> None:
        """Initialize the OpenAI client.

        Args:
            api_key: API key for authentication.
            endpoint: API endpoint URL.
        """
        self._api_key = api_key
        self._endpoint = endpoint

    def chat(self, messages: list, **kwargs: Any) -> Dict[str, Any]:
        """Send a chat request.

        Args:
            messages: List of message dicts.
            **kwargs: Additional arguments.

        Returns:
            Dict[str, Any]: Chat response.
        """
        return {"response": "openai_chat_response", "model": "gpt"}

    def get_endpoint(self) -> str:
        """Get the API endpoint.

        Returns:
            str: Endpoint URL.
        """
        return self._endpoint

</final_file_content>
</write_to_file></tool_call>