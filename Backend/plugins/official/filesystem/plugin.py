"""Filesystem official plugin.

Registers the filesystem tools into a :class:`ToolRegistry`. The plugin is
importable standalone; :func:`register` is the entry point used by the
plugin loader.
"""

from __future__ import annotations

from tools.registry.tool_registry import ToolRegistry
from tools.registry.tool_schema import ToolSchema

__all__ = ["PLUGIN_NAME", "register"]


PLUGIN_NAME = "filesystem"


def register(registry: ToolRegistry) -> int:
    """Register this plugin's tools into *registry*; returns count."""
    from tools.filesystem.read import fs_read
    from tools.filesystem.write import fs_write
    from tools.filesystem.search import fs_search
    from tools.filesystem.metadata import fs_metadata
    from tools.filesystem.watcher import fs_watch
    from tools.filesystem.organize import fs_organize

    count = 0
    for schema in (fs_read, fs_write, fs_search, fs_metadata, fs_watch, fs_organize):
        registry.register(schema)
        count += 1
    return count
