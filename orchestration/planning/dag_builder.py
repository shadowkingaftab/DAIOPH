"""DAG construction from raw task specifications.

:class:`DAGBuilder` converts planner output — a list of task dictionaries or
:class:`~orchestration.planning.task_graph.TaskNode` objects — into a validated
:class:`~orchestration.planning.task_graph.TaskGraph`. It auto-generates ids
when omitted, rejects duplicate/unknown references with clear errors, and can
infer a linear chain when no dependencies are given but ``sequential=True``.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from orchestration.planning.task_graph import TaskGraph, TaskNode

__all__ = ["DAGBuilder", "DAGBuildError"]

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(text: str, fallback: str) -> str:
    """Turn *text* into a short id-safe slug, falling back to *fallback*."""
    slug = _SLUG_RE.sub("-", text.strip().lower()).strip("-")
    return slug[:40] or fallback


class DAGBuildError(Exception):
    """Raised when raw task specifications cannot be assembled into a DAG."""


class DAGBuilder:
    """Builds validated :class:`TaskGraph` objects from raw specifications.

    Example:
        >>> builder = DAGBuilder()
        >>> graph = builder.build([
        ...     {"id": "a", "description": "fetch"},
        ...     {"id": "b", "description": "analyze", "depends_on": ["a"]},
        ... ])
        >>> len(graph)
        2
    """

    def __init__(self, sequential_fallback: bool = False) -> None:
        """Create a builder.

        Args:
            sequential_fallback: When True, tasks without explicit
                dependencies are chained onto the previously added task
                (useful for planner output that lists steps in order).
        """
        self._sequential_fallback = sequential_fallback

    def build(
        self,
        specs: Sequence[Union[TaskNode, Dict[str, Any]]],
        goal: str = "",
    ) -> TaskGraph:
        """Assemble a :class:`TaskGraph` from *specs*.

        Each spec may be a :class:`TaskNode` or a dict with keys ``id``
        (optional — auto-generated from the description), ``description``
        (required), ``depends_on`` (optional), ``route_hint`` (optional),
        and ``metadata`` (optional).

        Raises:
            DAGBuildError: If specs are empty, malformed, or inconsistent.
        """
        if not specs:
            raise DAGBuildError("Cannot build a DAG from an empty task list")

        graph = TaskGraph()
        previous_id: Optional[str] = None
        for index, spec in enumerate(specs):
            node = self._normalize(spec, index)
            if self._sequential_fallback and previous_id is not None:
                if not node.depends_on:
                    node.depends_on = [previous_id]
            try:
                graph.add_task(node)
            except Exception as exc:  # noqa: BLE001 - re-raise with context
                raise DAGBuildError(
                    f"Task #{index} ({node.id!r}) rejected: {exc}"
                ) from exc
            previous_id = node.id
        if goal:
            for node in graph.tasks:
                node.metadata.setdefault("goal", goal)
        return graph

    def build_linear(self, descriptions: Iterable[str], goal: str = "") -> TaskGraph:
        """Build a simple sequential chain from *descriptions*."""
        specs: List[Dict[str, Any]] = []
        previous: Optional[str] = None
        for i, text in enumerate(descriptions):
            tid = f"step_{i}"
            spec: Dict[str, Any] = {"id": tid, "description": text}
            if previous is not None:
                spec["depends_on"] = [previous]
            specs.append(spec)
            previous = tid
        return self.build(specs, goal=goal)

    # ── Internals ───────────────────────────────────────────────────────────
    @staticmethod
    def _normalize(spec: Union[TaskNode, Dict[str, Any]], index: int) -> TaskNode:
        """Coerce *spec* into a :class:`TaskNode`, generating ids as needed."""
        if isinstance(spec, TaskNode):
            return spec
        if not isinstance(spec, dict):
            raise DAGBuildError(
                f"Task spec must be a dict or TaskNode, got {type(spec).__name__}"
            )
        description = spec.get("description")
        if not description or not isinstance(description, str):
            raise DAGBuildError(f"Task #{index} is missing a string 'description'")
        task_id = spec.get("id") or _slugify(description, f"task_{index}")
        depends_on = spec.get("depends_on") or []
        if not isinstance(depends_on, (list, tuple)):
            raise DAGBuildError(f"Task #{index}: 'depends_on' must be a list")
        route_hint = spec.get("route_hint")
        if route_hint is not None and route_hint not in ("edge", "cloud", "hybrid"):
            raise DAGBuildError(
                f"Task #{index}: invalid route_hint {route_hint!r} "
                "(expected 'edge', 'cloud', or 'hybrid')"
            )
        return TaskNode(
            id=str(task_id),
            description=description,
            depends_on=[str(d) for d in depends_on],
            route_hint=route_hint,
            metadata=dict(spec.get("metadata", {})),
        )