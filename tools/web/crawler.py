"""Crawler — requires an injected fetch callable (offline by default)."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from tools.registry.tool_schema import ToolSchema

__all__ = ["crawl", "crawler_tool"]

_fetch_page: Callable[[str], Dict[str, Any]] = None


def crawl(start_url: str, max_pages: int = 5) -> List[str]:
    """Breadth-first crawl via an injected fetch callable (offline)."""
    if _fetch_page is None:
        raise RuntimeError(
            "no crawler backend injected; set tools.web.crawler._fetch_page "
            "to a callable(url) -> dict for offline testing with mocks"
        )
    seen: List[str] = []
    queue = [start_url]
    while queue and len(seen) < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.append(url)
        page = _fetch_page(url)
        for link in page.get("links", []):
            if link not in seen and link not in queue:
                queue.append(link)
    return seen


crawler_tool = ToolSchema(
    name="crawler",
    description="Breadth-first crawl via injected backend (offline)",
    fn=crawl,
    params={"start_url": str, "max_pages": int},
    requires_network=True,
)
