"""Browser official plugin.

Registers the web tools into a :class:`ToolRegistry`. The plugin is
importable standalone; :func:`register` is the entry point used by the
plugin loader.
"""

from __future__ import annotations

from tools.registry.tool_registry import ToolRegistry
from tools.registry.tool_schema import ToolSchema

__all__ = ["PLUGIN_NAME", "register"]


PLUGIN_NAME = "browser"


def register(registry: ToolRegistry) -> int:
    """Register this plugin's tools into *registry*; returns count."""
    from tools.web.browser import browser_tool
    from tools.web.crawler import crawler_tool
    from tools.web.search import web_search_tool

    count = 0
    for schema in (browser_tool, crawler_tool, web_search_tool):
        registry.register(schema)
        count += 1
    return count
