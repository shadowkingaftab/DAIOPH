"""Per-agent short-term memory with a bounded event log."""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional

__all__ = ["AgentMemory"]


class AgentMemory:
    """Namespaced key/value store plus a bounded event log per agent.

    All operations are thread-safe. The event log keeps the most recent
    ``log_size`` entries (oldest are dropped), so long runs cannot grow
    memory without bound.
    """

    def __init__(self, log_size: int = 200) -> None:
        if log_size < 1:
            raise ValueError("log_size must be >= 1")
        self._kv: Dict[str, Dict[str, Any]] = {}
        self._logs: Dict[str, Deque[Dict[str, Any]]] = {}
        self._log_size = log_size
        self._lock = threading.Lock()

    def remember(self, agent_id: str, key: str, value: Any) -> None:
        """Store *value* under *key* in *agent_id*'s namespace."""
        with self._lock:
            self._kv.setdefault(agent_id, {})[key] = value

    def recall(self, agent_id: str, key: str, default: Any = None) -> Any:
        """Retrieve *key* for *agent_id*, or *default* when absent."""
        with self._lock:
            return self._kv.get(agent_id, {}).get(key, default)

    def forget(self, agent_id: str, key: str) -> None:
        """Remove *key* from *agent_id*'s namespace (no-op when absent)."""
        with self._lock:
            self._kv.get(agent_id, {}).pop(key, None)

    def append(self, agent_id: str, event: Dict[str, Any]) -> None:
        """Append *event* to *agent_id*'s bounded log with a timestamp."""
        entry = {"at": time.time(), **event}
        with self._lock:
            log = self._logs.setdefault(
                agent_id, deque(maxlen=self._log_size)
            )
            log.append(entry)

    def history(self, agent_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return the agent's log, newest last; optionally only last *limit*."""
        with self._lock:
            entries = list(self._logs.get(agent_id, ()))
        return entries[-limit:] if limit else entries

    def clear(self, agent_id: Optional[str] = None) -> None:
        """Clear one agent's memory, or everything when *agent_id* is None."""
        with self._lock:
            if agent_id is None:
                self._kv.clear()
                self._logs.clear()
            else:
                self._kv.pop(agent_id, None)
                self._logs.pop(agent_id, None)
