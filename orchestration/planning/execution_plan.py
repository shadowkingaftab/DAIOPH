"""Serializable execution plans built from task graphs.

An :class:`ExecutionPlan` is the immutable artifact handed from the planning
subsystem to the execution subsystem. It captures the task graph, a
precomputed topological order, and parallel execution waves, and can be
serialized to/from a plain dictionary (JSON-friendly) for logging, caching,
or transport over the API layer.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from orchestration.planning.dependency_resolver import execution_waves
from orchestration.planning.task_graph import TaskGraph, TaskNode

__all__ = ["ExecutionPlan"]


@dataclass
class ExecutionPlan:
    """An executable, serializable plan derived from a :class:`TaskGraph`.

    Attributes:
        plan_id: Unique identifier for this plan.
        goal: The user-facing goal the plan achieves.
        graph: The underlying task graph.
        order: Topological task order (precomputed at construction).
        waves: Parallel execution waves (precomputed at construction).
        created_at: Unix timestamp of plan creation.
        metadata: Arbitrary planner metadata (model, strategy, etc.).
    """

    plan_id: str
    goal: str
    graph: TaskGraph
    order: List[str] = field(default_factory=list)
    waves: List[List[str]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.plan_id:
            self.plan_id = uuid.uuid4().hex[:12]
        if not self.order:
            self.order = self.graph.topological_order()
        if not self.waves:
            self.waves = execution_waves(self.graph)

    # ── Queries ─────────────────────────────────────────────────────────────
    @property
    def task_count(self) -> int:
        """Number of tasks in the plan."""
        return len(self.graph)

    def node(self, task_id: str) -> TaskNode:
        """Return the :class:`TaskNode` for *task_id*."""
        return self.graph.get(task_id)

    # ── Serialization ───────────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-friendly dictionary."""
        return {
            "plan_id": self.plan_id,
            "goal": self.goal,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
            "tasks": [
                {
                    "id": n.id,
                    "description": n.description,
                    "depends_on": list(n.depends_on),
                    "route_hint": n.route_hint,
                    "metadata": dict(n.metadata),
                }
                for n in self.graph.tasks
            ],
            "order": list(self.order),
            "waves": [list(w) for w in self.waves],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionPlan":
        """Rebuild an :class:`ExecutionPlan` from :meth:`to_dict` output.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If task data is malformed.
        """
        graph = TaskGraph()
        for raw in data["tasks"]:
            graph.add_task(
                TaskNode(
                    id=raw["id"],
                    description=raw["description"],
                    depends_on=list(raw.get("depends_on", [])),
                    route_hint=raw.get("route_hint"),
                    metadata=dict(raw.get("metadata", {})),
                )
            )
        return cls(
            plan_id=data.get("plan_id") or uuid.uuid4().hex[:12],
            goal=data["goal"],
            graph=graph,
            order=list(data.get("order", [])),
            waves=[list(w) for w in data.get("waves", [])],
            created_at=float(data.get("created_at", time.time())),
            metadata=dict(data.get("metadata", {})),
        )

    def summary(self) -> str:
        """One-line human summary (for logs and dashboards)."""
        return (
            f"plan {self.plan_id}: {self.task_count} task(s), "
            f"{len(self.waves)} wave(s), goal={self.goal!r}"
        )


def new_plan(
    goal: str,
    graph: TaskGraph,
    metadata: Optional[Dict[str, Any]] = None,
) -> ExecutionPlan:
    """Convenience constructor generating a fresh plan id."""
    return ExecutionPlan(
        plan_id=uuid.uuid4().hex[:12],
        goal=goal,
        graph=graph,
        metadata=dict(metadata or {}),
    )