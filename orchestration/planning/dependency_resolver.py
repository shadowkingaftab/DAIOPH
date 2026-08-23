"""Dependency resolution for task graphs.

Provides topological scheduling helpers on top of
:class:`orchestration.planning.task_graph.TaskGraph`:

- :func:`resolve_order` — a deterministic topological order.
- :func:`execution_waves` — groups of tasks that can run in parallel.
- :func:`validate` — structural validation with human-readable errors.

All functions are pure: they never mutate the input graph.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from orchestration.planning.task_graph import (
    CycleError,
    TaskGraph,
    UnknownTaskError,
)

__all__ = ["resolve_order", "execution_waves", "validate", "critical_path_length"]


def resolve_order(graph: TaskGraph) -> List[str]:
    """Return a deterministic topological order of *graph*.

    Ties are broken by insertion order so repeated calls return identical
    results (important for reproducible plans and tests).

    Raises:
        CycleError: If the graph contains a cycle.
    """
    return graph.topological_order()


def execution_waves(graph: TaskGraph) -> List[List[str]]:
    """Group tasks into parallel execution waves.

    Wave 0 contains all roots; wave *k* contains every task whose
    dependencies all appear in earlier waves. Tasks within a wave have no
    interdependencies and may run concurrently.

    Raises:
        CycleError: If the graph contains a cycle.
    """
    waves: List[List[str]] = []
    scheduled: set = set()
    remaining = {node.id for node in graph.tasks}
    while remaining:
        wave = [
            tid
            for tid in graph.ready_tasks(scheduled)
            if tid in remaining
        ]
        if not wave:
            raise CycleError("No progress possible; graph contains a cycle")
        # Preserve insertion order for determinism.
        wave = [tid for tid in (n.id for n in graph.tasks) if tid in set(wave)]
        waves.append(wave)
        scheduled.update(wave)
        remaining -= set(wave)
    return waves


def validate(graph: TaskGraph) -> Tuple[bool, List[str]]:
    """Validate *graph* structure.

    Returns:
        A ``(ok, errors)`` tuple. ``ok`` is True when the graph is a valid,
        acyclic DAG with well-formed dependency references.
    """
    errors: List[str] = []
    ids = {node.id for node in graph.tasks}
    for node in graph.tasks:
        for dep in node.depends_on:
            if dep not in ids:
                errors.append(f"Task {node.id!r} depends on unknown task {dep!r}")
            elif dep == node.id:
                errors.append(f"Task {node.id!r} depends on itself")
    try:
        graph.topological_order()
    except CycleError as exc:
        errors.append(str(exc))
    except UnknownTaskError as exc:  # pragma: no cover - defensive
        errors.append(str(exc))
    return (not errors, errors)


def critical_path_length(graph: TaskGraph, cost: Dict[str, float]) -> float:
    """Length of the critical path given per-task *cost* (e.g. seconds).

    Useful for estimating the minimum wall-clock time of a parallel
    execution. Tasks missing from *cost* are treated as cost ``0.0``.
    """
    order = resolve_order(graph)
    finish: Dict[str, float] = {}
    for tid in order:
        node = graph.get(tid)
        start = max((finish.get(d, 0.0) for d in node.depends_on), default=0.0)
        finish[tid] = start + float(cost.get(tid, 0.0))
    return max(finish.values(), default=0.0)


def wave_summary(graph: TaskGraph) -> Sequence[str]:
    """Human-readable one-line summary per execution wave (for logs/UI)."""
    return [
        f"wave {i}: {len(wave)} task(s): {', '.join(wave)}"
        for i, wave in enumerate(execution_waves(graph))
    ]