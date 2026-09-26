"""Environment variable read tool."""

from __future__ import annotations

import os
from typing import Dict, List

from tools.registry.tool_schema import ToolSchema

__all__ = ["read_env", "get_env_keys", "sys_env", "sys_env_read"]


def read_env(key: str, default: str = "") -> str:
    """Return *key* from the environment, or *default*."""
    return os.environ.get(key, default)


def get_env_keys() -> List[str]:
    """Return sorted environment variable names."""
    return sorted(os.environ.keys())


sys_env = ToolSchema(name="sys_env", description="List environment keys",
                     fn=get_env_keys)

sys_env_read = ToolSchema(name="sys_env_read", description="Read an env var",
                          fn=read_env, params={"key": str})
