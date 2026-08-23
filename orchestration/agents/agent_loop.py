"""Bounded step loop for iterative agent behaviour.

:func:`run_agent_loop` repeatedly invokes a *step* callable until it reports
completion, the step budget is exhausted, or cancellation is requested.
Each iteration is recorded, giving callers a full trace for debugging and
telemetry. The loop contains no model calls itself — *step* is the seam.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from agents.base.policy import AgentPolicy
from orchestration.execution.cancellation import CancellationToken

__all__ = ["run_agent_loop", "StepRecord", "LoopResult"]

logger = logging.getLogger(__name__)

StepFn = Callable[[int, Dict[str, Any]], Dict[str, Any]]


@dataclass
class StepRecord:
    """Trace of one loop iteration."""

    index: int
    ok: bool
    output: Any = None
    error: Optional[str] = None
    duration: float = 0.0


@dataclass
class LoopResult:
    """Aggregate outcome of a loop run."""

    steps: List[StepRecord] = field(default_factory=list)
    completed: bool = False
    stopped_reason: str = ""

    @property
    def step_count(self) -> int:
        """Number of executed steps."""
        return len(self.steps)


def run_agent_loop(
    step: StepFn,
    policy: AgentPolicy,
    token: Optional[CancellationToken] = None,
    state: Optional[Dict[str, Any]] = None,
) -> LoopResult:
    """Run *step* repeatedly within the policy's step budget.

    The step callable receives ``(index, state)`` and returns a dict; a
    truthy ``"done"`` key ends the loop successfully. Exceptions in a step
    are recorded and end the loop (fail fast) — the error is surfaced, not
    swallowed.
    """
    result = LoopResult()
    shared: Dict[str, Any] = dict(state or {})
    for index in range(policy.max_steps):
        if token is not None and token.cancelled:
            result.stopped_reason = token.reason or "cancelled"
            return result
        started = time.time()
        try:
            output = step(index, shared)
            record = StepRecord(
                index=index,
                ok=True,
                output=output,
                duration=time.time() - started,
            )
            result.steps.append(record)
            if isinstance(output, dict) and output.get("done"):
                result.completed = True
                return result
        except Exception as exc:  # noqa: BLE001 - recorded, then stop
            logger.warning("agent loop step %d failed: %s", index, exc)
            result.steps.append(
                StepRecord(
                    index=index,
                    ok=False,
                    error=str(exc),
                    duration=time.time() - started,
                )
            )
            result.stopped_reason = f"step error: {exc}"
            return result
    result.stopped_reason = "step budget exhausted"
    return result
