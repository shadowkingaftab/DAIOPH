"""Route policy vocabulary for hybrid edge/cloud orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = ["Route", "RoutePolicy"]


class Route(str, Enum):
    """Where a task may execute."""

    EDGE = "edge"
    CLOUD = "cloud"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class RoutePolicy:
    """Declarative routing preferences.

    Attributes:
        allow_cloud: Master switch; when False nothing routes to cloud.
        prefer_edge: When True, ties between edge and cloud resolve to edge.
        complexity_threshold: Complexity score (0..1) above which cloud is
            considered for a task.
        hybrid_on_fallback: When True, a cloud failure may retry on edge
            (and vice versa) instead of failing outright.
    """

    allow_cloud: bool = True
    prefer_edge: bool = True
    complexity_threshold: float = 0.6
    hybrid_on_fallback: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.complexity_threshold <= 1.0:
            raise ValueError("complexity_threshold must be within [0, 1]")
