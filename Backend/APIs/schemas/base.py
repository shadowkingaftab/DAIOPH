"""Minimal schema validation primitives for the API layer.

A :class:`Field` declares one expected property of a request payload;
:class:`Schema` validates a whole payload against its fields and returns
human-readable problems. Pure stdlib, framework-agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Type

__all__ = ["Field", "Schema", "ValidationError"]


class ValidationError(ValueError):
    """Raised by :meth:`Schema.validate_or_raise` on invalid payloads."""


@dataclass(frozen=True)
class Field:
    """One validated property of a payload.

    Attributes:
        name: Payload key.
        type: Expected Python type.
        required: Whether the key must be present.
        max_length: Maximum length for str values.
        choices: Allowed values, when given.
    """

    name: str
    type: Type = str
    required: bool = True
    max_length: Optional[int] = None
    choices: Optional[Tuple[Any, ...]] = None


@dataclass
class Schema:
    """A named collection of :class:`Field` rules."""

    name: str
    fields: List[Field] = field(default_factory=list)

    def validate(self, payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check *payload*; return ``(ok, problems)`` with clear messages."""
        problems: List[str] = []
        if not isinstance(payload, dict):
            return False, [f"{self.name}: payload must be a JSON object"]
        for spec in self.fields:
            if spec.name not in payload:
                if spec.required:
                    problems.append(f"{self.name}.{spec.name}: is required")
                continue
            value = payload[spec.name]
            if value is not None and not isinstance(value, spec.type):
                problems.append(
                    f"{self.name}.{spec.name}: expected "
                    f"{spec.type.__name__}, got {type(value).__name__}"
                )
                continue
            if isinstance(value, str):
                if spec.max_length is not None and len(value) > spec.max_length:
                    problems.append(
                        f"{self.name}.{spec.name}: length {len(value)} "
                        f"exceeds {spec.max_length}"
                    )
                if spec.choices is not None and value not in spec.choices:
                    problems.append(
                        f"{self.name}.{spec.name}: {value!r} not in "
                        f"{list(spec.choices)}"
                    )
        return (not problems, problems)

    def validate_or_raise(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and return the payload, or raise :class:`ValidationError`."""
        ok, problems = self.validate(payload)
        if not ok:
            raise ValidationError("; ".join(problems))
        return payload
