"""In-process code runner — destructive; approval-gated."""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from typing import Any, Dict

from tools.registry.tool_schema import ToolSchema

__all__ = ["run_python", "code_runner"]


def run_python(source: str, timeout: float = 5.0) -> Dict[str, Any]:
    """Execute *source* in-process, capturing stdout (approval-gated)."""
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            exec(compile(source, "<tool>", "exec"), {"__name__": "__tool__"})
    except Exception as exc:  # noqa: BLE001 - report, never crash
        return {"ok": False, "error": str(exc), "stdout": buffer.getvalue()}
    return {"ok": True, "stdout": buffer.getvalue()}


code_runner = ToolSchema(
    name="code_runner",
    description="Execute Python source in-process (destructive; approval)",
    fn=run_python,
    params={"source": str, "timeout": float},
    destructive=True,
)
