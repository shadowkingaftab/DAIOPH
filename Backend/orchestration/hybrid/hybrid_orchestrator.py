"""Hybrid orchestrator facade: plan → route → execute → synthesize.

:class:`HybridOrchestrator` wires the planning, routing, execution, and
synthesis subsystems into a single ``run(goal, ...)`` call. Route handlers
are injected per route; nothing here talks to a model vendor directly.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from orchestration.execution.cancellation import CancellationToken
from orchestration.execution.execution_engine import ExecutionEngine
from orchestration.execution.task_executor import TaskHandler
from orchestration.hybrid.fallback_manager import FallbackManager
from orchestration.hybrid.route_engine import RouteEngine
from orchestration.hybrid.route_policy import RoutePolicy
from orchestration.hybrid.route_selector import RouteSelector
from orchestration.planning.planner import Planner
from orchestration.synthesis.result_synthesizer import ResultSynthesizer

__all__ = ["HybridOrchestrator"]

logger = logging.getLogger(__name__)


class HybridOrchestrator:
    """End-to-end hybrid orchestration over injected components.

    Args:
        planner: Goal → plan (defaults to a deterministic single-task planner).
        selector: Route selector (edge-first, cloud only when available).
        engine: Executor (parallel waves by default).
        synthesizer: Result → final answer composer.
        token: Cooperative cancellation token shared with the executor.
    """

    def __init__(
        self,
        planner: Optional[Planner] = None,
        selector: Optional[RouteSelector] = None,
        engine: Optional[ExecutionEngine] = None,
        synthesizer: Optional[ResultSynthesizer] = None,
        token: Optional[CancellationToken] = None,
    ) -> None:
        self.planner = planner or Planner()
        self.selector = selector or RouteSelector(RoutePolicy())
        self.engine = engine or ExecutionEngine(parallel=True, token=token)
        self.synthesizer = synthesizer or ResultSynthesizer()
        self.routes = RouteEngine(self.selector)

    def run(
        self,
        goal: str,
        handlers: Dict[str, TaskHandler],
        strategy: str = "auto",
    ) -> Dict[str, Any]:
        """Plan, route, execute, and synthesize *goal*.

        Args:
            goal: Natural-language objective.
            handlers: Mapping route name ("edge"/"cloud") → handler.
            strategy: Planning strategy passed through to the planner.

        Returns:
            Report dictionary with plan summary, route distribution,
            per-task results, and the synthesized answer.
        """
        plan = self.planner.plan(goal, strategy=strategy)
        decisions = self.routes.route_plan(plan)

        fallback = FallbackManager(handlers)

        def dispatch(task_id: str, description: str, context: Dict[str, Any]) -> Any:
            decision = decisions[task_id]
            preferred = (
                [decision.route.value]
                if decision.route.value in handlers
                else list(handlers.keys())
            )
            output, route_used, attempts = fallback.run(
                task_id, description, context, order=preferred
            )
            self.routes.record(type(decision.route)(route_used))
            meta = plan.node(task_id).metadata
            meta["route_used"] = route_used
            meta["attempts"] = attempts
            return output

        report = self.engine.run(plan, dispatch)
        synthesis = self.synthesizer.synthesize(goal, plan, report.results)
        payload = report.to_dict()
        payload["routes"] = self.routes.distribution
        payload["answer"] = synthesis.answer
        payload["warnings"] = synthesis.warnings
        logger.info("hybrid run complete: %s", synthesis.summary())
        return payload
