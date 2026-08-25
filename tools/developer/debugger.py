"""Debugger helper: traceback formatting and expression eval."""

from __future__ import annotations

import traceback
from typing import Any, Dict

from tools.registry.tool_schema import ToolSchema

__all__ = ["format_traceback", "dev_debugger"]


def format_traceback(exc: BaseException) -> str:
    """Return a compact traceback string for *exc*."""
    return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))


dev_debugger = ToolSchema(
    name="dev_debugger",
    description="Format an exception into a traceback string",
    fn=format_traceback,
    params={"exc": BaseException},
)
