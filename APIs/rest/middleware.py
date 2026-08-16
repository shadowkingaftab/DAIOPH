from __future__ import annotations

from typing import Any, Dict


class Middleware:
    """Base middleware class for REST API."""

    def __init__(self, name: str = "") -> None:
        self.name = name

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request."""
        return request

    def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process a response."""
        return response