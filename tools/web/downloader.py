"""HTTP downloader (injected fetch backend; no network by default)."""

from __future__ import annotations

from typing import Any, Callable, Dict

from tools.registry.tool_schema import ToolSchema

__all__ = ["http_get", "web_download", "http_get_tool"]

_fetch_fn: Callable[[str], Dict[str, Any]] = None


def http_get(url: str) -> Dict[str, Any]:
    """Fetch *url* via an injected fetch callable (offline by default)."""
    if _fetch_fn is None:
        raise RuntimeError(
            "no HTTP backend injected; set tools.web.downloader._fetch_fn "
            "to a callable(url) -> dict for offline testing with mocks"
        )
    return _fetch_fn(url)


http_get_tool = ToolSchema(
    name="web_download",
    description="HTTP GET via injected backend (offline by default)",
    fn=http_get,
    params={"url": str},
    requires_network=True,
)

web_download = http_get
