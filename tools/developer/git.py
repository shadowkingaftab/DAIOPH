"""Git status tool (read-only; no network)."""

from __future__ import annotations

import subprocess
from typing import List

from tools.registry.tool_schema import ToolSchema

__all__ = ["git_status", "dev_git"]


def git_status(repo: str = ".") -> List[str]:
    """Return ``git status --short`` lines for *repo* (empty on failure)."""
    try:
        result = subprocess.run(  # noqa: S603 - fixed allowlisted argv
            ["git", "-C", repo, "status", "--short"],
            capture_output=True, text=True, timeout=10.0, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    return [ln for ln in result.stdout.splitlines() if ln.strip()]


dev_git = ToolSchema(
    name="dev_git",
    description="Read-only git status for a repository",
    fn=git_status,
    params={"repo": str},
)
