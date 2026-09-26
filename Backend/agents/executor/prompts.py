"""System prompt and prompt builder for the executor role.

Mission: Carry out one assigned step by invoking the handler supplied in the run context; report structured outcomes.

The prompt layer is deliberately vendor-neutral: ``build_prompt`` renders a
plain-text prompt that any injected LLM callable can consume.
"""

from __future__ import annotations

from typing import Any, Dict

__all__ = ["ROLE", "SYSTEM_PROMPT", "build_prompt"]

ROLE = "executor"

SYSTEM_PROMPT = """You are the executor agent of the DAIOPH orchestration system.

Carry out one assigned step by invoking the handler supplied in the run context; report structured outcomes.

Execute the STEP exactly; do not invent extra work. Report the concrete result or the precise blocker.
"""


def build_prompt(task: str, context: Dict[str, Any]) -> str:
    """Render the full user prompt for *task* with optional *context*."""
    lines = [f"STEP: {task}"]
    if context:
        lines.append(f"INPUTS: {context!r}")
    lines.append("\nExecute the step and report the result.")
    return "\n".join(lines)
