"""Browser tool — requires an injected page callable (offline by default)."""

from __future__ import annotations

from typing import Any, Callable, Dict

from tools.registry.tool_schema import ToolSchema

__all__ = ["browse", "browser_tool"]

_page_fn: Callable[[str], Dict[str, Any]] = None


def browse(url: str) -> Dict[str, Any]:
    """Fetch a page via an injected callable (offline by default)."""
    if _page_fn is None:
        raise RuntimeError(
            "no browser backend injected; set tools.web.browser._page_fn "
            "to a callable(url) -> dict for offline testing with mocks"
        )
    return _page_fn(url)


browser_tool = ToolSchema(
    name="browser",
    description="Fetch a page via injected backend (offline by default)",
    fn=browse,
    params={"url": str},
    requires_network=True,
)
