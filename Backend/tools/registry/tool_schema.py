"""Tool metadata schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Optional

__all__ = ["ToolSchema", "ToolPermissionError"]


class ToolPermissionError(PermissionError):
    """Raised when a tool is not permitted or requires approval."""


@dataclass(frozen=True)
class ToolSchema:
    """Declarative metadata for one tool.

    Attributes:
        name: Unique tool name.
        description: Human-readable one-liner.
        fn: The callable implementing the tool.
        params: JSON-schema-ish param names -> types.
        destructive: Requires explicit approval before invocation.
        requires_network: Marks network-touching tools.
        hidden: Exclude from discovery lists.
    """

    name: str
    description: str
    fn: Callable[..., Any]
    params: Dict[str, type] = field(default_factory=dict)
    destructive: bool = False
    requires_network: bool = False
    hidden: bool = False

    def __post_init__(self) -> None:
        if not self.name or not isinstance(self.name, str):
            raise ValueError("name must be a non-empty string")
        if not callable(self.fn):
            raise TypeError("fn must be callable")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string")

    def validate_args(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate types of provided params; missing params are allowed.

        Tools declare their params with defaults, so presence is not
        enforced here — only that provided values match the declared type.
        """
        problems = []
        for key, expected in self.params.items():
            if key not in kwargs:
                continue
            value = kwargs[key]
            if value is not None and not isinstance(value, expected):
                problems.append(
                    f"parameter {key!r} expected {expected.__name__}, "
                    f"got {type(value).__name__}"
                )
        if problems:
            raise TypeError(f"{self.name}: " + "; ".join(problems))
        return {k: v for k, v in kwargs.items() if k in self.params}
