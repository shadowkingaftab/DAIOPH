"""Thread-safe registry of agent instances.

:class:`AgentRegistry` maps agent ids to instances and supports lookup by
role. It is the shared directory used by the runtime and supervisor.
"""

from __future__ import annotations

import threading
from typing import Dict, List, Optional

__all__ = ["AgentRegistry"]


class AgentRegistry:
    """Register, look up, and list agents by id or role."""

    def __init__(self) -> None:
        self._agents: Dict[str, object] = {}
        self._lock = threading.Lock()

    def register(self, agent: object, agent_id: Optional[str] = None) -> str:
        """Register *agent* under *agent_id* (defaults to ``agent.agent_id``).

        Returns:
            The id the agent is registered under.

        Raises:
            ValueError: If the id is empty or already registered.
        """
        resolved = agent_id or getattr(agent, "agent_id", None)
        if not resolved:
            raise ValueError("agent_id could not be resolved")
        with self._lock:
            if resolved in self._agents:
                raise ValueError(f"agent id already registered: {resolved!r}")
            self._agents[resolved] = agent
        return resolved

    def get(self, agent_id: str) -> object:
        """Return the agent registered under *agent_id*.

        Raises:
            KeyError: If the id is unknown.
        """
        with self._lock:
            try:
                return self._agents[agent_id]
            except KeyError:
                raise KeyError(f"unknown agent id: {agent_id!r}") from None

    def remove(self, agent_id: str) -> None:
        """Unregister *agent_id* (no-op when absent)."""
        with self._lock:
            self._agents.pop(agent_id, None)

    def list_ids(self) -> List[str]:
        """All registered agent ids in registration order."""
        with self._lock:
            return list(self._agents.keys())

    def by_role(self, role: str) -> List[object]:
        """All agents whose ``ROLE`` attribute equals *role*."""
        with self._lock:
            return [
                a for a in self._agents.values()
                if getattr(a, "ROLE", None) == role
            ]

    def __len__(self) -> int:
        with self._lock:
            return len(self._agents)
