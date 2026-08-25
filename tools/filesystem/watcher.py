"""Thread-safe directory watcher (polling; no external deps)."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

from tools.registry.tool_schema import ToolSchema

__all__ = ["create_watcher", "fs_watch"]


def create_watcher(
    path: str,
    interval_seconds: float = 1.0,
    on_change: Optional[Callable[[List[str]], None]] = None,
) -> dict:
    """Poll *path* for new files; call *on_change* when the set changes.

    Returns a control dict with ``stop()`` to halt polling.
    """
    seen: Dict[str, float] = {}
    control = {"running": True}

    def _poll() -> None:
        base = Path(path)
        while control["running"]:
            current = {}
            if base.exists():
                for p in base.rglob("*"):
                    if p.is_file():
                        try:
                            current[str(p)] = p.stat().st_mtime
                        except OSError:
                            continue
            changes = [
                name for name, mtime in current.items()
                if seen.get(name) != mtime
            ]
            if changes and on_change is not None:
                on_change(changes)
            seen.clear()
            seen.update(current)
            time.sleep(interval_seconds)

    thread = threading.Thread(target=_poll, daemon=True)
    thread.start()

    def _stop() -> None:
        control["running"] = False

    control["stop"] = _stop
    return control


fs_watch = ToolSchema(
    name="fs_watch",
    description="Begin polling a directory for file changes",
    fn=create_watcher,
    params={"path": str, "interval_seconds": float},
)
