"""System prompt and prompt builder for the analyst role.

Mission: Summarize structured data: record counts, field coverage, and simple distributions; flag anomalies worth human attention.

The prompt layer is deliberately vendor-neutral: ``build_prompt`` renders a
plain-text prompt that any injected LLM callable can consume.
"""

from __future__ import annotations

from typing import Any, Dict

__all__ = ["ROLE", "SYSTEM_PROMPT", "build_prompt"]

ROLE = "analyst"

SYSTEM_PROMPT = """You are the analyst agent of the DAIOPH orchestration system.

Summarize structured data: record counts, field coverage, and simple distributions; flag anomalies worth human attention.

Given DATA, produce: overview, notable patterns, anomalies, and recommended next actions. Cite concrete numbers.
"""


def build_prompt(task: str, context: Dict[str, Any]) -> str:
    """Render the full user prompt for *task* with optional *context*."""
    lines = [f"QUESTION: {task}"]
    if context.get("data") is not None:
        lines.append(f"DATA: {context['data']!r}")
    lines.append("\nAnalyse the data.")
    return "\n".join(lines)
