"""Supervises multi-agent runs: dispatch, retry, and verdict aggregation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from orchestration.agents.agent_runtime import AgentRuntime

__all__ = ["AgentSupervisor", "SupervisionReport"]

logger = logging.getLogger(__name__)


@dataclass
class SupervisionReport:
    """Outcome of supervising one task across agents."""

    task: str
    results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    retries: Dict[str, int] = field(default_factory=dict)

    @property
    def succeeded(self) -> List[str]:
        """Agent ids whose run reported ok."""
        return [a for a, r in self.results.items() if r.get("ok")]

    @property
    def failed(self) -> List[str]:
        """Agent ids whose run reported failure."""
        return [a for a, r in self.results.items() if not r.get("ok")]

    @property
    def goal_met(self) -> bool:
        """True when at least one agent succeeded and none remain failed
        after retries."""
        return bool(self.succeeded) and not self.failed

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-friendly dictionary."""
        return {
            "task": self.task,
            "goal_met": self.goal_met,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "retries": dict(self.retries),
            "results": self.results,
        }


class AgentSupervisor:
    """Dispatches a task to agents and retries failures once by default."""

    def __init__(self, runtime: AgentRuntime, max_retries: int = 1) -> None:
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        self.runtime = runtime
        self.max_retries = max_retries

    def dispatch(
        self,
        task: str,
        agent_ids: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> SupervisionReport:
        """Send *task* to each listed agent, retrying failures.

        Args:
            task: The work item.
            agent_ids: Registered agent ids to involve.
            context: Shared context passed to every agent.

        Returns:
            A :class:`SupervisionReport` with per-agent outcomes.
        """
        report = SupervisionReport(task=task)
        for agent_id in agent_ids:
            attempts = 0
            while attempts <= self.max_retries:
                attempts += 1
                result = self.runtime.run(agent_id, task, context)
                if result.get("ok"):
                    break
                logger.warning(
                    "agent %s attempt %d failed: %s",
                    agent_id, attempts, result.get("error"),
                )
            report.results[agent_id] = result
            report.retries[agent_id] = attempts - 1
        logger.info(
            "supervision done: ok=%s failed=%s",
            report.succeeded, report.failed,
        )
        return report
