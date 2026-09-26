"""In-memory task list (no persistence)."""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List

from tools.registry.tool_schema import ToolSchema

__all__ = ["task_add", "task_list", "task_complete"]

_tasks: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()


def task_add(title: str, priority: str = "medium") -> str:
    """Add a task; returns its id."""
    task_id = f"task-{int(time.time() * 1000)}"
    with _lock:
        _tasks[task_id] = {"title": title, "priority": priority,
                           "done": False, "created": time.time()}
    return task_id


def task_list() -> List[Dict[str, Any]]:
    """Return all tasks."""
    with _lock:
        return [{"id": tid, **meta} for tid, meta in sorted(_tasks.items())]


def task_complete(task_id: str) -> bool:
    """Mark *task_id* done; False when unknown."""
    with _lock:
        task = _tasks.get(task_id)
        if task is None:
            return False
        task["done"] = True
        return True


task_add_tool = ToolSchema(name="task_add", description="Add a task",
                           fn=task_add, params={"title": str, "priority": str})
task_list_tool = ToolSchema(name="task_list", description="List tasks",
                            fn=task_list)
task_complete_tool = ToolSchema(name="task_complete", description="Complete a task",
                                fn=task_complete, params={"task_id": str})
