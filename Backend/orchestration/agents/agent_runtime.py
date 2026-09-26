"""Agent runtime: spawn agents, run them under policy, record history."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional, Type

from agents.base.policy import AgentPolicy
from orchestration.agents.agent_memory import AgentMemory
from orchestration.agents.agent_registry import AgentRegistry

__all__ = ["AgentRuntime"]

logger = logging.getLogger(__name__)


class AgentRuntime:
    """Owns the agent registry and memory; executes runs under policy.

    Args:
        timeout_seconds: Default wall-clock budget applied when an agent's
            policy does not specify one. Uses the cooperative timeout
            manager (documented thread-leak semantics on expiry).
    """

    def __init__(self, timeout_seconds: float = 60.0) -> None:
        self.registry = AgentRegistry()
        self.memory = AgentMemory()
        self.default_timeout = timeout_seconds

    def spawn(
        self,
        agent_cls: Type,
        agent_id: Optional[str] = None,
        policy: Optional[AgentPolicy] = None,
        **kwargs: Any,
    ) -> object:
        """Instantiate *agent_cls*, register it, and return the instance."""
        agent = agent_cls(agent_id=agent_id or agent_cls.__name__, **kwargs)
        if policy is not None:
            agent.policy = policy
        registered_id = self.registry.register(agent)
        self.memory.append(registered_id, {"event": "spawned"})
        logger.info("spawned agent %s (%s)", registered_id, agent_cls.__name__)
        return agent

    def run(
        self,
        agent_id: str,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run the registered agent on *task*, enforcing its time budget.

        Returns:
            The agent's result dictionary, augmented with ``agent_id``.
        """
        agent = self.registry.get(agent_id)
        policy: AgentPolicy = getattr(agent, "policy", AgentPolicy())
        timeout = policy.timeout_seconds or self.default_timeout
        self.memory.append(agent_id, {"event": "run_start", "task": task[:200]})
        try:
            from orchestration.execution.timeout_manager import run_with_timeout

            result = run_with_timeout(
                lambda: agent.run(task, context), timeout=timeout
            )
        except TimeoutError:
            result = {
                "ok": False,
                "error": f"agent {agent_id!r} exceeded {timeout}s budget",
            }
        except Exception as exc:  # noqa: BLE001 - surface as failure
            result = {"ok": False, "error": str(exc)}
        result["agent_id"] = agent_id
        self.memory.append(
            agent_id, {"event": "run_end", "ok": result.get("ok", False)}
        )
        return result

    def status(self) -> Dict[str, Any]:
        """Snapshot of registered agents and their run counts."""
        agents = {}
        for agent_id in self.registry.list_ids():
            agent = self.registry.get(agent_id)
            agents[agent_id] = (
                agent.snapshot() if hasattr(agent, "snapshot") else {"id": agent_id}
            )
        return {"agents": agents}
