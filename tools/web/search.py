"""Web search tool — requires an injected search callable (no network)."""

from __future__ import annotations

from typing import Any, Callable, List

from tools.registry.tool_schema import ToolSchema

__all__ = ["web_search", "web_search_fn", "web_search_tool"]

web_search_fn: Callable[[str, int], List[Any]] = None


def web_search(query: str, limit: int = 5) -> List[Any]:
    """Search via the injected callable; honest error when none wired."""
    if web_search_fn is None:
        raise RuntimeError(
            "no web search backend injected; set tools.web.search.web_search_fn "
            "to a callable(query, limit) -> list"
        )
    return web_search_fn(query, limit)


web_search_tool = ToolSchema(
    name="web_search",
    description="Web search via injected backend (no network by default)",
    fn=web_search,
    params={"query": str, "limit": int},
    requires_network=True,
)
