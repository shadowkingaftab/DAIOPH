"""Lightweight ontology reasoning: transitivity and path queries."""

from __future__ import annotations

from typing import Dict, List, Optional

from knowledge.ontology.relations import Relation, RelationStore

__all__ = ["infer_transitive", "explain_relation"]


def infer_transitive(
    store: RelationStore, predicate: str, max_depth: int = 8
) -> Dict[str, List[str]]:
    """Infer transitive closure of *predicate* over the relation store.

    For example, with predicate ``"part_of"`` the result maps each subject
    to every object reachable through one or more ``part_of`` hops.
    """
    if max_depth < 1:
        raise ValueError("max_depth must be >= 1")
    closure: Dict[str, List[str]] = {}
    # Build adjacency once for determinism and speed.
    adjacency: Dict[str, List[str]] = {}
    for rel in store.all_relations():
        if rel.predicate == predicate:
            adjacency.setdefault(rel.subject, []).append(rel.object)

    def walk(start: str) -> List[str]:
        seen: List[str] = []
        frontier = [start]
        for _ in range(max_depth):
            nxt: List[str] = []
            for node in frontier:
                for target in adjacency.get(node, []):
                    if target == start or target in seen:
                        continue
                    seen.append(target)
                    nxt.append(target)
            if not nxt:
                break
            frontier = nxt
        return seen

    for subject in sorted(adjacency):
        closure[subject] = walk(subject)
    return closure


def explain_relation(
    store: RelationStore, subject: str, obj: str, predicate: str
) -> Optional[List[Relation]]:
    """Return a hop-by-hop relation chain subject -> ... -> obj, or None.

    Breadth-first over *predicate* edges; the first found chain is
    returned (deterministic given insertion order).
    """
    if subject == obj:
        return []
    frontier: List[List[Relation]] = [
        [r] for r in store.by_subject(subject, predicate)
    ]
    visited = {subject}
    while frontier:
        chain = frontier.pop(0)
        tail = chain[-1].object
        if tail == obj:
            return chain
        if tail in visited:
            continue
        visited.add(tail)
        for rel in store.by_subject(tail, predicate):
            frontier.append(chain + [rel])
    return None
