"""Selects an execution route for a single task."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from orchestration.hybrid.route_policy import Route, RoutePolicy

__all__ = ["RouteSelector", "RouteDecision"]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RouteDecision:
    """Outcome of routing one task.

    Attributes:
        route: Chosen :class:`Route`.
        reason: Human-readable justification (logged/shown in dashboards).
    """

    route: Route
    reason: str


class RouteSelector:
    """Chooses edge vs cloud per task using a :class:`RoutePolicy`.

    Args:
        policy: Routing preferences.
        cloud_available: Runtime availability of the cloud provider
            (e.g. API key present). Never assumed True implicitly.
    """

    def __init__(self, policy: RoutePolicy, cloud_available: bool = False) -> None:
        self.policy = policy
        self.cloud_available = cloud_available

    def select(
        self,
        description: str,
        complexity: float = 0.0,
        hint: Optional[str] = None,
    ) -> RouteDecision:
        """Pick a route for one task.

        Args:
            description: Task description (used for logging context).
            complexity: Estimated complexity in [0, 1]; higher favours cloud.
            hint: Planner-provided preference ("edge"/"cloud"/"hybrid").

        Returns:
            A :class:`RouteDecision`; never raises for ordinary inputs.
        """
        if hint == "cloud" and self._cloud_ok():
            return RouteDecision(Route.CLOUD, "planner hint: cloud")
        if hint == "edge":
            return RouteDecision(Route.EDGE, "planner hint: edge")
        if hint == "hybrid" and self._cloud_ok():
            return RouteDecision(Route.HYBRID, "planner hint: hybrid")

        if self._cloud_ok() and complexity >= self.policy.complexity_threshold:
            return RouteDecision(
                Route.CLOUD,
                f"complexity {complexity:.2f} >= threshold "
                f"{self.policy.complexity_threshold:.2f}",
            )
        if self._cloud_ok() and not self.policy.prefer_edge:
            return RouteDecision(Route.HYBRID, "policy prefers cloud when tied")
        return RouteDecision(Route.EDGE, "default: edge-first")

    def _cloud_ok(self) -> bool:
        """Cloud usable only when both configured and available."""
        return self.policy.allow_cloud and self.cloud_available
