"""GrokAdapter - adapts Grok API responses."""

from typing import Any, Dict, Optional


class GrokAdapter:
    """Adapts Grok API responses to internal format."""

    def adapt(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt a Grok API response.

        Args:
            response: Raw API response.

        Returns:
            Dict[str, Any]: Adapted response.
        """
        return {
            "text": response.get("response", ""),
            "model": response.get("model", "grok"),
            "usage": response.get("usage", {}),
        }

    def adapt_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt an internal request to Grok API format.

        Args:
            request: Internal request.

        Returns:
            Dict[str, Any]: Adapted request.
        """
        return {
            "messages": request.get("messages", []),
            "model": request.get("model", "grok"),
        }

</final_file_content>
</write_to_file></tool_call>