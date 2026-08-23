"""Permissioned tool access for agents.

A :class:`ToolBinding` pairs a callable with metadata; an
:class:`AgentToolbelt` exposes only the tools an :class:`AgentPolicy`
allows, enforcing an approval callback for sensitive tools. Deny-by-default.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from agents.base.policy import AgentPolicy

__all__ = ["ToolBinding", "AgentToolbelt", "ToolPermissionError"]

logger = logging.getLogger(__name__)


class ToolPermissionError(PermissionError):
    """Raised when a tool is not permitted or lacks required approval."""


@dataclass
class ToolBinding:
    """A callable tool with metadata.

    Attributes:
        name: Unique tool name.
        fn: The callable implementing the tool.
        description: Short human-readable description.
        requires_approval: Whether invocation needs explicit approval.
    """

    name: str
    fn: Callable[..., Any]
    description: str = ""
    requires_approval: bool = False


class AgentToolbelt:
    """Exposes policy-permitted tools to an agent.

    Args:
        policy: The owning agent's policy (source of allowed tools).
        approval_callback: Optional callable ``(tool_name, kwargs) -> bool``
            consulted for tools flagged as requiring approval. When None,
            approval-requiring tools are always denied (safe default).
    """

    def __init__(
        self,
        policy: AgentPolicy,
        approval_callback: Optional[Callable[[str, Dict[str, Any]], bool]] = None,
    ) -> None:
        self.policy = policy
        self.approval_callback = approval_callback
        self._tools: Dict[str, ToolBinding] = {}

    def register(self, binding: ToolBinding) -> None:
        """Register *binding*; later registrations replace earlier ones."""
        self._tools[binding.name] = binding

    def available(self) -> Dict[str, str]:
        """Names and descriptions of tools the policy permits."""
        return {
            name: b.description
            for name, b in self._tools.items()
            if self.policy.may_use(name)
        }

    def invoke(self, name: str, **kwargs: Any) -> Any:
        """Invoke tool *name* after permission and approval checks.

        Raises:
            KeyError: If the tool is unknown.
            ToolPermissionError: If the policy forbids it or approval is
                required but not granted.
        """
        binding = self._tools.get(name)
        if binding is None:
            raise KeyError(f"unknown tool: {name!r}")
        if not self.policy.may_use(name):
            raise ToolPermissionError(
                f"tool {name!r} is not in the agent policy's allowed_tools"
            )
        if binding.requires_approval or self.policy.needs_approval(name):
            if self.approval_callback is None or not self.approval_callback(
                name, kwargs
            ):
                raise ToolPermissionError(
                    f"tool {name!r} requires approval and none was granted"
                )
        logger.info("invoking tool %s", name)
        return binding.fn(**kwargs)
