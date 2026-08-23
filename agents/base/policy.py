"""Execution policies constraining agent behaviour.

An :class:`AgentPolicy` is a small, serializable declaration of what an
agent may do and how long it may run. Policies are enforced by callers
(runtime, supervisors), not by the policy object itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["AgentPolicy"]


@dataclass
class AgentPolicy:
    """Bounds and permissions for one agent.

    Attributes:
        max_steps: Maximum reasoning/tool steps per run (>= 1).
        timeout_seconds: Soft wall-clock budget per run (None = unbounded,
            which callers should treat as "use the runtime default").
        allowed_tools: Tool names the agent may request; empty means none.
        require_approval: Tool names that additionally need explicit
            human/runtime approval before invocation.
        max_retries: Retry budget for failed steps (>= 0).
    """

    max_steps: int = 8
    timeout_seconds: float | None = None
    allowed_tools: frozenset = field(default_factory=frozenset)
    require_approval: frozenset = field(default_factory=frozenset)
    max_retries: int = 1

    def __post_init__(self) -> None:
        if self.max_steps < 1:
            raise ValueError("max_steps must be >= 1")
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive when given")
        unknown = set(self.require_approval) - set(self.allowed_tools)
        if unknown:
            raise ValueError(
                f"require_approval lists tools not in allowed_tools: {sorted(unknown)}"
            )

    def may_use(self, tool: str) -> bool:
        """True when *tool* is permitted (approval still checked by caller)."""
        return tool in self.allowed_tools

    def needs_approval(self, tool: str) -> bool:
        """True when *tool* additionally requires explicit approval."""
        return tool in self.require_approval
