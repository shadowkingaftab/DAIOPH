"""System prompt and prompt builder for the coder role.

Mission: Produce correct, minimal, well-documented code for the requested change, including how to test it.

The prompt layer is deliberately vendor-neutral: ``build_prompt`` renders a
plain-text prompt that any injected LLM callable can consume.
"""

from __future__ import annotations

from typing import Any, Dict

__all__ = ["ROLE", "SYSTEM_PROMPT", "build_prompt"]

ROLE = "coder"

SYSTEM_PROMPT = """You are the coder agent of the DAIOPH orchestration system.

Produce correct, minimal, well-documented code for the requested change, including how to test it.

Return a single fenced code block plus a short rationale and a test sketch. Never invent APIs that were not provided.
"""


def build_prompt(task: str, context: Dict[str, Any]) -> str:
    """Render the full user prompt for *task* with optional *context*."""
    lines = [f"TASK: {task}"]
    if context.get("language"):
        lines.append(f"LANGUAGE: {context['language']}")
    if context.get("existing_code"):
        lines.append("EXISTING CODE:\n" + str(context["existing_code"]))
    lines.append("\nWrite the code.")
    return "\n".join(lines)
