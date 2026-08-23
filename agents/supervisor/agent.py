"""supervisor role agent.

:class:`SupervisorAgent` extends :class:`agents.base.agent.BaseAgent`. Behaviour:

- With an injected ``llm`` callable, sends the rendered prompt and returns
  the model output wrapped in a result dictionary.
- Without an LLM, runs a documented deterministic local behaviour
  (see `_local_fallback`) or raises :class:`AgentCapabilityError` when the role
  fundamentally requires a model. It never fabricates success.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, Optional

from agents.base.agent import BaseAgent
from agents.base.policy import AgentPolicy
from agents.supervisor.prompts import ROLE, build_prompt

__all__ = ["SupervisorAgent", "AgentCapabilityError"]

logger = logging.getLogger(__name__)

LLMCallable = Callable[[str], str]


class AgentCapabilityError(RuntimeError):
    """The requested capability needs an LLM/handler that was not injected."""


def _split_steps(text: str) -> list:
    """Split a goal into heuristic steps on newlines/semicolons/periods."""
    import re

    parts = [p for p in re.split(r"[\n;]|(?<=\.)\s+", text) if p.strip()]
    return parts or [text]


class SupervisorAgent(BaseAgent):
    """Agent responsible for: Aggregate worker results into a run verdict: success ratio, failed tasks, and whether the overall goal is met."""

    ROLE = ROLE

    def __init__(
        self,
        agent_id: str = "supervisor",
        llm: Optional[LLMCallable] = None,
        policy: Optional[AgentPolicy] = None,
    ) -> None:
        super().__init__(agent_id)
        self.llm = llm
        self.policy = policy or AgentPolicy()
        self._running = False
        self.history: list = []

    # ── Lifecycle (BaseAgent contract) ────────────────────────────────────
    def start(self) -> None:
        """Mark the agent ready to accept work."""
        self._running = True
        self._state["started_at"] = time.time()

    def stop(self) -> None:
        """Stop accepting new work."""
        self._running = False

    def reset(self) -> None:
        """Clear history and transient state."""
        self.history.clear()
        self._state.clear()
        self._running = False

    # ── Work ──────────────────────────────────────────────────────────────
    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process *task*, returning a structured result dictionary.

        Raises:
            AgentCapabilityError: When no LLM is injected and the role has
                no local implementation for this input.
        """
        if not task or not task.strip():
            raise ValueError("task must be a non-empty string")
        ctx = dict(context or {})
        started = time.time()

        if self.llm is not None:
            prompt = build_prompt(task, ctx)
            try:
                raw = self.llm(prompt)
            except Exception as exc:  # noqa: BLE001 - surface as failure
                logger.error("%s llm call failed: %s", self.agent_id, exc)
                return {
                    "ok": False,
                    "error": f"llm failure: {exc}",
                    "role": ROLE,
                    "duration": time.time() - started,
                }
            record = {
                "ok": True,
                "role": ROLE,
                "output": raw,
                "source": "llm",
                "duration": time.time() - started,
            }
            self.history.append({"task": task, **record})
            return record

        result = self._local_fallback(task, ctx)
        record = {**result, "ok": True, "role": ROLE,
                  "duration": time.time() - started}
        self.history.append({"task": task, **record})
        return record

    def _local_fallback(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic local behaviour used when no LLM is injected."""
        results = context.get("results") or {}
        total = len(results)
        ok = sum(1 for v in results.values()
                 if isinstance(v, dict) and v.get("ok"))
        failed = [k for k, v in results.items()
                  if isinstance(v, dict) and not v.get("ok")]
        return {
            "goal_met": total > 0 and not failed,
            "succeeded": ok,
            "failed_tasks": failed,
            "total": total,
            "source": "local_heuristic",
        }

    def snapshot(self) -> Dict[str, Any]:
        """Return a JSON-friendly view of the agent state."""
        return {
            "agent_id": self.agent_id,
            "role": ROLE,
            "running": self._running,
            "llm_injected": self.llm is not None,
            "runs": len(self.history),
        }
