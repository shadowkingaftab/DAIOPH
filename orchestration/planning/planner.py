"""Planner facade: goal → validated, wave-scheduled execution plan.

:class:`Planner` is the single entry point the rest of the system uses to
turn a natural-language goal into an :class:`ExecutionPlan`. It supports two
planning strategies:

- ``"llm"`` — delegate decomposition to an injected callable (the
  dependency-injection seam for any LLM backend). The callable receives the
  goal and must return a JSON list of task dicts.
- ``"single"`` — deterministic fallback producing a one-task plan (used when
  no LLM is configured; the plan is honest about being trivial).

No vendor SDKs are imported here; the LLM is always injected.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict, List, Optional

from orchestration.planning.dag_builder import DAGBuilder, DAGBuildError
from orchestration.planning.execution_plan import ExecutionPlan, new_plan

__all__ = ["Planner", "PlanningError"]

logger = logging.getLogger(__name__)

LLMDecomposer = Callable[[str], str]


class PlanningError(Exception):
    """Raised when a goal cannot be turned into a valid plan."""


class Planner:
    """Turns goals into validated :class:`ExecutionPlan` objects.

    Args:
        decomposer: Optional callable that maps a goal string to a JSON list
            of task specifications. When omitted, only the deterministic
            ``"single"`` strategy is available.
        sequential_fallback: Passed to :class:`DAGBuilder`; when True, tasks
            without explicit dependencies are chained in listed order.
    """

    def __init__(
        self,
        decomposer: Optional[LLMDecomposer] = None,
        sequential_fallback: bool = False,
    ) -> None:
        self._decomposer = decomposer
        self._builder = DAGBuilder(sequential_fallback=sequential_fallback)

    @property
    def llm_available(self) -> bool:
        """True when an LLM decomposer has been injected."""
        return self._decomposer is not None

    def plan(
        self,
        goal: str,
        strategy: str = "auto",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ExecutionPlan:
        """Produce an :class:`ExecutionPlan` for *goal*.

        Args:
            goal: The user-facing objective.
            strategy: ``"auto"`` (LLM when available, else single-task),
                ``"llm"``, or ``"single"``.
            metadata: Extra metadata stored on the plan.

        Raises:
            PlanningError: If the requested strategy is unavailable or the
                decomposer returns unusable output.
            ValueError: If *goal* is empty.
        """
        if not goal or not goal.strip():
            raise ValueError("goal must be a non-empty string")

        if strategy == "auto":
            strategy = "llm" if self._decomposer is not None else "single"

        if strategy == "single":
            graph = self._builder.build_linear([goal.strip()], goal=goal)
            plan = new_plan(goal=goal, graph=graph, metadata=metadata)
            plan.metadata["strategy"] = "single"
            logger.info("Planned (single): %s", plan.summary())
            return plan

        if strategy == "llm":
            if self._decomposer is None:
                raise PlanningError(
                    "Strategy 'llm' requested but no decomposer was injected; "
                    "pass a callable to Planner(decomposer=...) or use "
                    "strategy='single'."
                )
            raw = self._decomposer(goal)
            specs = self._parse_specs(raw)
            try:
                graph = self._builder.build(specs, goal=goal)
            except DAGBuildError as exc:
                raise PlanningError(f"Decomposer produced an invalid DAG: {exc}") from exc
            plan = new_plan(goal=goal, graph=graph, metadata=metadata)
            plan.metadata["strategy"] = "llm"
            logger.info("Planned (llm): %s", plan.summary())
            return plan

        raise PlanningError(f"Unknown strategy {strategy!r} (use auto/llm/single)")

    # ── Internals ───────────────────────────────────────────────────────────
    @staticmethod
    def _parse_specs(raw: str) -> List[Dict[str, Any]]:
        """Parse decomposer output into task spec dicts.

        Accepts a JSON array of objects, or a JSON object with a ``tasks``
        key. Raises :class:`PlanningError` with actionable messages otherwise.
        """
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise PlanningError(
                f"Decomposer output is not valid JSON: {exc}"
            ) from exc
        if isinstance(data, dict):
            data = data.get("tasks")
        if not isinstance(data, list) or not data:
            raise PlanningError(
                "Decomposer output must be a non-empty JSON array of task "
                "objects (or an object with a 'tasks' array)"
            )
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise PlanningError(f"Task #{i} is not a JSON object")
        return data