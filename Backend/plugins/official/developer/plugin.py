"""Developer official plugin.

Registers the developer tools into a :class:`ToolRegistry`. The plugin is
importable standalone; :func:`register` is the entry point used by the
plugin loader.
"""

from __future__ import annotations

from tools.registry.tool_registry import ToolRegistry
from tools.registry.tool_schema import ToolSchema

__all__ = ["PLUGIN_NAME", "register"]


PLUGIN_NAME = "developer"


def register(registry: ToolRegistry) -> int:
    """Register this plugin's tools into *registry*; returns count."""
    from tools.developer.code_analyzer import dev_analyzer
    from tools.developer.code_runner import code_runner
    from tools.developer.debugger import dev_debugger
    from tools.developer.git import dev_git
    from tools.developer.project_manager import dev_project
    from tools.developer.testing import dev_testing

    count = 0
    for schema in (dev_analyzer, code_runner, dev_debugger, dev_git, dev_project, dev_testing):
        registry.register(schema)
        count += 1
    return count
