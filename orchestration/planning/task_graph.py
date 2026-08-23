"""Task graph: a validated directed acyclic graph of orchestration tasks.

This module defines the core domain model used by the planning and execution
subsystems. A :class:`TaskGraph` stores :class:`TaskNode` objects and directed
dependency edges, and enforces acyclicity on every insertion so downstream
executors can always obtain a valid topological order.

Example:
    >>> graph = TaskGraph()
    >>> graph.add_task(TaskNode(id="a", description="fetch data"))
    >>> graph.add_task(TaskNode(id="b", description="analyze", depends_on=["a"]))
    >>> graph.topological_order()
    ['a', 'b']
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

__all__ = ["TaskNode", "TaskGraph", "TaskGraphError", "CycleError", "UnknownTaskError"]


class TaskGraphError(Exception):
    """Base error for task graph operations."""


class CycleError(TaskGraphError):
    """Raised when adding a dependency would create a cycle."""


class UnknownTaskError(TaskGraphError):
    """Raised when referencing a task id that is not in the graph."""


@dataclass
class TaskNode:
    """A single unit of work inside a :class:`TaskGraph`.

    Attributes:
        id: Unique identifier within the graph.
        description: Human-readable description of the work.
        depends_on: Ids of tasks that must complete before this one.
        route_hint: Optional routing preference ("edge", "cloud", "hybrid",
            or None to let the route engine decide).
        metadata: Arbitrary planner-provided metadata.
    """

    id: str
    description: str
    depends_on: List[str] = field(default_factory=list)
    route_hint: Optional[str] = None
    metadata: Dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id or not isinstance(self.id, str):
            raise ValueError("TaskNode.id must be a non-empty string")
        if not self.description or not isinstance(self.description, str):
            raise ValueError("TaskNode.description must be a non-empty string")
        if self.depends_on is None:
            self.depends_on = []
        if self.metadata is None:
            self.metadata = {}


class TaskGraph:
    """A directed acyclic graph of :class:`TaskNode` objects.

    The graph validates on mutation: duplicate ids, unknown dependencies, and
    cycles are rejected immediately, so any successfully built graph is always
    executable in topological order.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, TaskNode] = {}

    def add_task(self, node: TaskNode) -> TaskNode:
        """Add *node* to the graph, validating dependencies and acyclicity.

        Raises:
            ValueError: If a task with the same id already exists.
            UnknownTaskError: If a dependency id is not in the graph.
            CycleError: If the new edges would create a cycle.
        """
        if node.id in self._nodes:
            raise ValueError(f"Duplicate task id: {node.id!r}")
        missing = [dep for dep in node.depends_on if dep not in self._nodes]
        if missing:
            raise UnknownTaskError(
                f"Task {node.id!r} depends on unknown task(s): {missing}"
            )
        self._nodes[node.id] = node
        try:
            self._assert_acyclic_from(node.id)
        except CycleError:
            del self._nodes[node.id]
            raise
        return node

    def remove_task(self, task_id: str) -> TaskNode:
        """Remove *task_id* and any edges pointing at it.

        Raises:
            UnknownTaskError: If the id is not in the graph.
        """
        node = self._nodes.pop(task_id, None)
        if node is None:
            raise UnknownTaskError(f"Unknown task id: {task_id!r}")
        for other in self._nodes.values():
            other.depends_on = [d for d in other.depends_on if d != task_id]
        return node

    def get(self, task_id: str) -> TaskNode:
        """Return the node with *task_id*.

        Raises:
            UnknownTaskError: If the id is not in the graph.
        """
        try:
            return self._nodes[task_id]
        except KeyError:
            raise UnknownTaskError(f"Unknown task id: {task_id!r}") from None

    def __contains__(self, task_id: object) -> bool:
        return task_id in self._nodes

    def __len__(self) -> int:
        return len(self._nodes)

    @property
    def tasks(self) -> List[TaskNode]:
        """All nodes in insertion order."""
        return list(self._nodes.values())

    def dependents_of(self, task_id: str) -> List[str]:
        """Ids of tasks that directly depend on *task_id*."""
        self.get(task_id)
        return [n.id for n in self._nodes.values() if task_id in n.depends_on]

    def roots(self) -> List[str]:
        """Ids of tasks with no dependencies (entry points)."""
        return [n.id for n in self._nodes.values() if not n.depends_on]

    def leaves(self) -> List[str]:
        """Ids of tasks that nothing depends on (exit points)."""
        depended: set = set()
        for node in self._nodes.values():
            depended.update(node.depends_on)
        return [n.id for n in self._nodes.values() if n.id not in depended]

    def topological_order(self) -> List[str]:
        """Return a valid topological order (Kahn's algorithm).

        Raises:
            CycleError: If the graph contains a cycle (defensive check).
        """
        indegree = {tid: 0 for tid in self._nodes}
        for node in self._nodes.values():
            for _dep in node.depends_on:
                indegree[node.id] += 1
        queue: List[str] = [tid for tid, deg in indegree.items() if deg == 0]
        order: List[str] = []
        while queue:
            current = queue.pop(0)
            order.append(current)
            for node in self._nodes.values():
                if current in node.depends_on:
                    indegree[node.id] -= 1
                    if indegree[node.id] == 0:
                        queue.append(node.id)
        if len(order) != len(self._nodes):
            raise CycleError("Graph contains a cycle")
        return order

    def ready_tasks(self, completed: Iterable[str]) -> List[str]:
        """Tasks whose dependencies are all in *completed* and not yet done."""
        done = set(completed)
        return [
            n.id
            for n in self._nodes.values()
            if n.id not in done and all(d in done for d in n.depends_on)
        ]

    def _assert_acyclic_from(self, start_id: str) -> None:
        """Depth-first cycle check reachable from *start_id*."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {tid: WHITE for tid in self._nodes}

        def visit(tid: str) -> None:
            color[tid] = GRAY
            for dep in self._nodes[tid].depends_on:
                state = color.get(dep, WHITE)
                if state == GRAY:
                    raise CycleError(
                        f"Adding task {start_id!r} would create a cycle via {dep!r}"
                    )
                if state == WHITE:
                    visit(dep)
            color[tid] = BLACK

        visit(start_id)