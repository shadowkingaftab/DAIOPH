"""Default permission sets per tool category."""

from __future__ import annotations

from typing import FrozenSet

__all__ = ["DEFAULT_ALLOWED", "DESTRUCTIVE_CAPABILITIES"]

DEFAULT_ALLOWED = frozenset({
    # Filesystem reads
    "fs_read", "fs_search", "fs_metadata", "fs_watch",
    # System introspection
    "sys_info", "sys_env", "sys_env_read",
    # Developer reads
    "dev_analyzer", "dev_browse",
})


DESTRUCTIVE_CAPABILITIES: FrozenSet[str] = frozenset({
    "fs_write", "fs_delete", "fs_organize",
    "process_exec", "terminal", "code_runner", "code_apply",
    "email_send", "message_send", "calendar_write", "task_write",
})
