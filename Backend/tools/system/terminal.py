"""Terminal execution — destructive; approval-gated."""

from __future__ import annotations

import subprocess
from typing import Tuple

from tools.registry.tool_schema import ToolSchema

__all__ = ["run_command", "terminal"]


def run_command(command: str, timeout: float = 10.0) -> Tuple[int, str]:
    """Run *command* via the shell; returns (exit_code, stdout)."""
    result = subprocess.run(  # noqa: S602 - destructive plugin, approval-gated
        command, capture_output=True, text=True, shell=True, timeout=timeout, check=False
    )
    return result.returncode, result.stdout.strip()


terminal = ToolSchema(
    name="terminal",
    description="Execute a shell command (destructive; requires approval)",
    fn=run_command,
    params={"command": str, "timeout": float},
    destructive=True,
)
