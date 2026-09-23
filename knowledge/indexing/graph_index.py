"""Directed graph index with neighbor lookup and BFS shortest paths."""

from __future__ import annotations

from collections import deque
from typing import Dict, Hashable, List, Optional, Set, Tuple

__all__ = ["GraphIndex"]

Node = Hashable


class GraphIndex:
    """Directed multigraph over hashable nodes with deterministic order."""

    def __init__(self) -> None:
        self._edges: Dict[Node, List[Node]] = {}
        self._nodes: List[Node] = []
        self._node_set: Set[Node] = set()

    def add_node(self, node: Node) -> None:
        """Add an isolated node (no-op if present)."""
        if node not in self._node_set:
            self._node_set.add(node)
            self._nodes.append(node)
            self._edges.setdefault(node, [])

    def add_edge(self, src: Node, dst: Node) -> None:
        """Add a directed edge, creating nodes as needed."""
        self.add_node(src)
        self.add_node(dst)
        outs = self._edges[src]
        if dst not in outs:
            outs.append(dst)

    def has_edge(self, src: Node, dst: Node) -> bool:
        """True when a directed edge src -> dst exists."""
        return dst in self._edges.get(src, [])

    def neighbors(self, node: Node) -> List[Node]:
        """Out-neighbors in insertion order."""
        return list(self._edges.get(node, []))

    def nodes(self) -> List[Node]:
        """All nodes in insertion order."""
        return list(self._nodes)

    def shortest_path(self, src: Node, dst: Node) -> Optional[List[Node]]:
        """BFS shortest path from src to dst, or None if unreachable."""
        if src not in self._node_set or dst not in self._node_set:
            return None
        if src == dst:
            return [src]
        visited = {src}
        queue: deque = deque([(src, [src])])
        while queue:
            current, path = queue.popleft()
            for nxt in self._edges.get(current, []):
                if nxt in visited:
                    continue
                if nxt == dst:
                    return path + [nxt]
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))
        return None

    def reachable(self, src: Node) -> Set[Node]:
        """All nodes reachable from *src* (excluding src unless cyclic)."""
        if src not in self._node_set:
            return set()
        visited: Set[Node] = set()
        stack = [src]
        while stack:
            current = stack.pop()
            for nxt in self._edges.get(current, []):
                if nxt not in visited:
                    visited.add(nxt)
                    stack.append(nxt)
        return visited

    def __len__(self) -> int:
        return len(self._nodes)
