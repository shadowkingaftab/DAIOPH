"""HypothesisEngine - generates and tracks hypotheses."""

from typing import Any, Dict, List, Optional


class HypothesisEngine:
    """Generates and manages hypotheses during reasoning."""

    def __init__(self) -> None:
        """Initialize the hypothesis engine."""
        self._hypotheses: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1

    def generate(self, tasks: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate hypotheses based on tasks and context.

        Args:
            tasks: List of tasks to generate hypotheses for.
            context: Optional context.

        Returns:
            List[Dict[str, Any]]: Generated hypotheses.
        """
        hypotheses = []
        for task in tasks:
            hypothesis = {
                "id": f"hyp_{self._next_id}",
                "task_id": task.get("id"),
                "description": f"Hypothesis for: {task.get('description', '')}",
                "status": "pending",
                "evidence": [],
            }
            self._hypotheses[hypothesis["id"]] = hypothesis
            self._next_id += 1
            hypotheses.append(hypothesis)
        return hypotheses

    def update(self, hypothesis_id: str, evidence: Any, status: str = "pending") -> None:
        """Update a hypothesis with new evidence.

        Args:
            hypothesis_id: Hypothesis identifier.
            evidence: New evidence.
            status: New status.
        """
        if hypothesis_id in self._hypotheses:
            self._hypotheses[hypothesis_id]["evidence"].append(evidence)
            self._hypotheses[hypothesis_id]["status"] = status

    def get(self, hypothesis_id: str) -> Optional[Dict[str, Any]]:
        """Get a hypothesis.

        Args:
            hypothesis_id: Hypothesis identifier.

        Returns:
            Optional[Dict[str, Any]]: Hypothesis or None.
        """
        return self._hypotheses.get(hypothesis_id)

    def list_hypotheses(self) -> List[Dict[str, Any]]:
        """List all hypotheses.

        Returns:
            List[Dict[str, Any]]: All hypotheses.
        """
        return list(self._hypotheses.values())

    def reset(self) -> None:
        """Reset the hypothesis engine."""
        self._hypotheses = {}
        self._next_id = 1