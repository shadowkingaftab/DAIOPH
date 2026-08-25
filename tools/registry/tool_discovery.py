"""Module-level tool discovery: import a module, find ToolSchema instances."""

from __future__ import annotations

import importlib
import inspect
from typing import List

from tools.registry.tool_registry import ToolRegistry
from tools.registry.tool_schema import ToolSchema

__all__ = ["discover_from_module", "discover_from_modules"]


def discover_from_module(module_name: str, registry: ToolRegistry) -> int:
    """Import *module_name* and register every ToolSchema it defines.

    Returns:
        Number of tools registered.
    """
    module = importlib.import_module(module_name)
    count = 0
    for _, obj in vars(module).items():
        if isinstance(obj, ToolSchema):
            registry.register(obj)
            count += 1
    return count


def discover_from_modules(module_names, registry: ToolRegistry) -> int:
    """Discover from *module_names*; a missing module is skipped, not fatal."""
    total = 0
    for name in module_names:
        try:
            total += discover_from_module(name, registry)
        except ImportError:
            continue
    return total
