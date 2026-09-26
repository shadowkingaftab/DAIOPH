from __future__ import annotations

from typing import Any, Dict, List


class RESTApp:
    """REST API application framework."""

    def __init__(self, title: str = "DAIOPH API", version: str = "1.0.0") -> None:
        self.title = title
        self.version = version
        self.routes: Dict[str, Dict[str, Any]] = {}
        self.middleware: List[Any] = []

    def add_route(self, path: str, method: str, handler: Any) -> None:
        """Add a route to the application."""
        if path not in self.routes:
            self.routes[path] = {}
        self.routes[path][method] = handler

    def add_middleware(self, middleware: Any) -> None:
        """Add middleware to the application."""
        self.middleware.append(middleware)

    def get_routes(self) -> Dict[str, Dict[str, Any]]:
        """Return all registered routes."""
        return dict(self.routes)

    def get_info(self) -> Dict[str, str]:
        """Return application information."""
        return {"title": self.title, "version": self.version}