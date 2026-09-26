"""Prompt-injection detection (heuristic, deterministic)."""

from __future__ import annotations

from typing import List, Tuple

__all__ = ["detect_prompt_injection"]

_SIGNALS = (
    "ignore previous instructions",
    "ignore all previous",
    "disregard your instructions",
    "you are now",
    "act as if",
    "system prompt",
    "reveal your system",
    "forget your rules",
)


def detect_prompt_injection(text: str) -> Tuple[bool, List[str]]:
    """Return ``(flagged, matched_signals)`` for *text*.

    Case-insensitive substring matching against known injection signals.
    Deterministic and offline; not a substitute for a real model guard.
    """
    lowered = text.lower()
    matched = [s for s in _SIGNALS if s in lowered]
    return (bool(matched), matched)
