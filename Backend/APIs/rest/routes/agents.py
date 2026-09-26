"""Agent management REST routes.

Handlers delegate to an injected agent runtime (see
``orchestration.agents.AgentRuntime``). The runtime is resolved lazily from
the dependency container so tests can inject fakes; unknown agent ids
produce explicit ``not_found`` responses, never fabricated results.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from APIs.rest.dependencies import DependencyContainer
from APIs.schemas.agents import AGENT_RUN_SCHEMA, AGENT_SPAWN_SCHEMA

__all__ = ["AgentsRoute"]

_ROLE_IMPORTS: Dict[str, str] = {
    "planner": "agents.planner.PlannerAgent",
    "executor": "agents.executor.ExecutorAgent",
    "coder": "agents.coder.CoderAgent",
    "analyst": "agents.analyst.AnalystAgent",
    "researcher": "agents.researcher.ResearcherAgent",
    "supervisor": "agents.supervisor.SupervisorAgent",
    "verifier": "agents.verifier.VerifierAgent",
}


class AgentsRoute:
    """Handlers for ``/agents`` endpoints."""

    def __init__(self, container: Optional[DependencyContainer] = None) -> None:
        self.container = container or DependencyContainer()

    def _runtime(self) -> Any:
        """Resolve the agent runtime; absent runtime is an explicit error."""
        runtime = self.container.try_resolve("agent_runtime")
        if runtime is None:
            raise RuntimeError(
                "no 'agent_runtime' dependency registered; wire "
                "orchestration.agents.AgentRuntime into the container"
            )
        return runtime

    def list_agents(self) -> Dict[str, Any]:
        """List registered agents with their snapshots."""
        runtime = self._runtime()
        return {"agents": runtime.status()["agents"], "count": len(runtime.registry)}

    def spawn_agent(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Spawn an agent from a validated ``agents.spawn`` payload."""
        try:
            data = AGENT_SPAWN_SCHEMA.validate_or_raise(payload)
        except ValueError as exc:
            return {"status": "invalid", "error": str(exc)}
        role_path = _ROLE_IMPORTS.get(data["role"])
        if role_path is None:
            return {"status": "invalid", "error": f"unknown role {data['role']!r}"}
        module_name, class_name = role_path.rsplit(".", 1)
        import importlib

        agent_cls = getattr(importlib.import_module(module_name), class_name)
        runtime = self._runtime()
        agent = runtime.spawn(agent_cls, agent_id=data["agent_id"])
        return {"status": "spawned", "agent_id": getattr(agent, "agent_id")}

    def run_agent(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run a registered agent on a validated ``agents.run`` payload."""
        try:
            data = AGENT_RUN_SCHEMA.validate_or_raise(payload)
        except ValueError as exc:
            return {"status": "invalid", "error": str(exc)}
        runtime = self._runtime()
        if data["agent_id"] not in runtime.registry.list_ids():
            return {"status": "not_found", "agent_id": data["agent_id"]}
        return runtime.run(data["agent_id"], data["task"])
