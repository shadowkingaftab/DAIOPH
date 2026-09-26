"""Applies the route selector across a whole plan and tracks statistics."""

from __future__ import annotations

import logging
from collections import Counter
from typing import Dict

from orchestration.hybrid.route_policy import Route
from orchestration.hybrid.route_selector import RouteDecision, RouteSelector
from orchestration.planning.execution_plan import ExecutionPlan

__all__ = ["RouteEngine"]

logger = logging.getLogger(__name__)


class RouteEngine:
    """Routes every task of a plan and records distribution statistics."""

    def __init__(self, selector: RouteSelector) -> None:
        self.selector = selector
        self._counts: Counter = Counter()

    def route_plan(self, plan: ExecutionPlan) -> Dict[str, RouteDecision]:
        """Return a decision per task id in *plan*."""
        decisions: Dict[str, RouteDecision] = {}
        for node in plan.graph.tasks:
            complexity = float(node.metadata.get("complexity", 0.0))
            decision = self.selector.select(
                description=node.description,
                complexity=complexity,
                hint=node.route_hint,
            )
            decisions[node.id] = decision
            self._counts[decision.route.value] += 1
        logger.info("routed plan %s: %s", plan.plan_id, dict(self._counts))
        return decisions

    def record(self, route: Route) -> None:
        """Manually record one executed route (e.g. after fallback)."""
        self._counts[route.value] += 1

    @property
    def distribution(self) -> Dict[str, int]:
        """Copy of route-name → count statistics."""
        return dict(self._counts)

    def reset_stats(self) -> None:
        """Clear accumulated statistics."""
        self._counts.clear()
