"""System prompt and prompt builder for the planner role.

Mission: Decompose a goal into an ordered list of concrete, executable steps with explicit dependencies.

The prompt layer is deliberately vendor-neutral: ``build_prompt`` renders a
plain-text prompt that any injected LLM callable can consume.
"""

from __future__ import annotations

from typing import Any, Dict

__all__ = ["ROLE", "SYSTEM_PROMPT", "build_prompt"]

ROLE = "planner"

SYSTEM_PROMPT = """You are the planner agent of the DAIOPH orchestration system.

Decompose a goal into an ordered list of concrete, executable steps with explicit dependencies.

Return STRICT JSON: {"steps": [{"id": str, "description": str,\n"depends_on": [str]}]}. Keep steps small and testable.
"""


def build_prompt(task: str, context: Dict[str, Any]) -> str:
    """Render the full user prompt for *task* with optional *context*."""
    lines = [f"GOAL: {task}"]
    if context:
        lines.append("CONTEXT:")
        for key, value in sorted(context.items()):
            lines.append(f"  - {key}: {value!r}")
    lines.append("\nDecompose the goal into steps.")
    return "\n".join(lines)
