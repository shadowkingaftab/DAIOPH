"""Lineage tracking: transformation history of derived knowledge."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

__all__ = ["LineageTracker", "Transformation"]


@dataclass(frozen=True)
class Transformation:
    """One derivation step: inputs consumed, output produced."""

    output_id: str
    input_ids: tuple
    operation: str
    metadata: Dict[str, str] = field(default_factory=dict)


class LineageTracker:
    """Records how artifacts were derived and traces origins."""

    def __init__(self) -> None:
        self._steps: Dict[str, List[Transformation]] = {}

    def record(
        self,
        output_id: str,
        input_ids: List[str],
        operation: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Transformation:
        """Record that *output_id* was produced from *input_ids*."""
        step = Transformation(
            output_id=output_id,
            input_ids=tuple(input_ids),
            operation=operation,
            metadata=dict(metadata or {}),
        )
        self._steps.setdefault(output_id, []).append(step)
        return step

    def direct_inputs(self, artifact_id: str) -> List[str]:
        """Inputs of the most recent transformation of *artifact_id*."""
        steps = self._steps.get(artifact_id)
        return list(steps[-1].input_ids) if steps else []

    def origins(self, artifact_id: str, max_depth: int = 32) -> List[str]:
        """Root artifacts with no recorded transformation (BFS, bounded).

        Deterministic: inputs are visited in recorded order.
        """
        if max_depth < 1:
            raise ValueError("max_depth must be >= 1")
        roots: List[str] = []
        frontier = [artifact_id]
        depth = 0
        while frontier and depth < max_depth:
            nxt: List[str] = []
            for node in frontier:
                steps = self._steps.get(node)
                if not steps:
                    if node not in roots:
                        roots.append(node)
                    continue
                nxt.extend(steps[-1].input_ids)
            frontier = nxt
            depth += 1
        return roots

    def history(self, artifact_id: str) -> List[Transformation]:
        """All recorded transformations of *artifact_id* in order."""
        return list(self._steps.get(artifact_id, []))
