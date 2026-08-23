"""Composes a final user-facing answer from executed task results."""

from __future__ import annotations

from typing import Dict, List

from orchestration.execution.task_executor import TaskResult, TaskStatus
from orchestration.planning.execution_plan import ExecutionPlan

__all__ = ["AnswerComposer"]


class AnswerComposer:
    """Deterministic composition of outputs in topological task order."""

    def compose(self, goal: str, plan: ExecutionPlan,
                results: Dict[str, TaskResult]) -> str:
        """Build the final answer text.

        Successful outputs are joined in plan order; failures are listed
        explicitly so the user sees what could not be completed.
        """
        sections: List[str] = [f"Goal: {goal}", ""]
        delivered: List[str] = []
        unresolved: List[str] = []

        for task_id in plan.order:
            result = results.get(task_id)
            if result is None:
                unresolved.append(f"- {task_id}: no result recorded")
            elif result.status is TaskStatus.SUCCEEDED:
                delivered.append(f"[{task_id}] {_stringify(result.output)}")
            elif result.status is TaskStatus.SKIPPED:
                unresolved.append(f"- {task_id}: skipped ({result.error})")
            else:
                unresolved.append(f"- {task_id}: {result.status.value}"
                                  f" ({result.error})")

        if delivered:
            sections.append("Results:")
            sections.extend(delivered)
        if unresolved:
            sections.append("")
            sections.append("Unresolved:")
            sections.extend(unresolved)
        return "\n".join(sections).strip()


def _stringify(output: object) -> str:
    """Render an output value compactly for inclusion in the answer."""
    if isinstance(output, str):
        return output.strip()
    return repr(output)
