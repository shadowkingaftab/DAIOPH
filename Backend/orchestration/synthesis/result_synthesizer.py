"""Synthesis facade: validate → resolve conflicts → compose the answer."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

from orchestration.execution.task_executor import TaskResult
from orchestration.planning.execution_plan import ExecutionPlan
from orchestration.synthesis.answer_composer import AnswerComposer
from orchestration.synthesis.conflict_resolver import ConflictResolver
from orchestration.synthesis.output_validator import OutputValidator

__all__ = ["ResultSynthesizer", "SynthesisReport"]

logger = logging.getLogger(__name__)


@dataclass
class SynthesisReport:
    """Outcome of synthesizing a plan's results."""

    answer: str
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        """One-line human summary."""
        return (
            f"synthesis: {self.succeeded} ok / {self.failed} failed / "
            f"{self.skipped} skipped, {len(self.warnings)} warning(s)"
        )


class ResultSynthesizer:
    """Turns raw task results into a validated final answer."""

    def __init__(
        self,
        validator: Any = None,
        resolver: Any = None,
        composer: Any = None,
    ) -> None:
        self.validator = validator or OutputValidator()
        self.resolver = resolver or ConflictResolver()
        self.composer = composer or AnswerComposer()

    def synthesize(
        self,
        goal: str,
        plan: ExecutionPlan,
        results: Dict[str, TaskResult],
    ) -> SynthesisReport:
        """Produce a :class:`SynthesisReport` for *results*."""
        warnings: List[str] = []
        invalid = self.validator.validate_results(results)
        for task_id, problems in invalid.items():
            warnings.append(f"{task_id}: " + "; ".join(problems))

        counts = {"succeeded": 0, "failed": 0, "skipped": 0}
        for result in results.values():
            key = result.status.name.lower()
            if key in counts:
                counts[key] += 1

        # Resolve duplicate-goal conflicts among leaf outputs deterministically.
        leaves = plan.graph.leaves()
        if len(leaves) > 1:
            candidates = {
                tid: results[tid].output
                for tid in leaves
                if tid in results and results[tid].ok
            }
            if len({repr(v) for v in candidates.values()}) > 1:
                winner, strategy = self.resolver.resolve(candidates, "priority")
                warnings.append(
                    f"conflicting leaf outputs resolved via {strategy!r}"
                )
                logger.info("conflict resolved via %s", strategy)

        answer = self.composer.compose(goal, plan, results)
        report = SynthesisReport(
            answer=answer,
            succeeded=counts["succeeded"],
            failed=counts["failed"],
            skipped=counts["skipped"],
            warnings=warnings,
        )
        logger.info(report.summary())
        return report
