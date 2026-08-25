"""Test runner helper (runs pytest in a subprocess; approval-gated)."""

from __future__ import annotations

import subprocess
from typing import Dict, Any

from tools.registry.tool_schema import ToolSchema

__all__ = ["run_tests", "dev_testing"]


def run_tests(path: str = "tests", timeout: float = 60.0) -> Dict[str, Any]:
    """Run pytest on *path*; returns exit code and captured output."""
    try:
        result = subprocess.run(  # noqa: S603 - fixed allowlisted argv
            ["python", "-m", "pytest", path, "-q"],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": result.returncode == 0, "exit_code": result.returncode,
            "output": result.stdout[-2000:]}


dev_testing = ToolSchema(
    name="dev_testing",
    description="Run pytest on a path (destructive; approval)",
    fn=run_tests,
    params={"path": str, "timeout": float},
    destructive=True,
)
