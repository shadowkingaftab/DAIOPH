"""Provenance sources."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

__all__ = ["Source"]


@dataclass(frozen=True)
class Source:
    """Where a piece of knowledge came from.

    Attributes:
        source_id: Stable identifier.
        uri: Locator (URL, path, or other scheme).
        retrieved_at: Unix timestamp of retrieval (0 if unknown).
        trust: Trust score in [0, 1]; 0.5 by default.
        metadata: Arbitrary extra provenance data.
    """

    source_id: str
    uri: str
    retrieved_at: int = 0
    trust: float = 0.5
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.trust <= 1.0:
            raise ValueError("trust must be within [0, 1]")
