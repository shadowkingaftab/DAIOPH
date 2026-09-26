"""System prompt and prompt builder for the researcher role.

Mission: Gather and cite sources for a question using the injected search callable; distinguish verified facts from speculation.

The prompt layer is deliberately vendor-neutral: ``build_prompt`` renders a
plain-text prompt that any injected LLM callable can consume.
"""

from __future__ import annotations

from typing import Any, Dict

__all__ = ["ROLE", "SYSTEM_PROMPT", "build_prompt"]

ROLE = "researcher"

SYSTEM_PROMPT = """You are the researcher agent of the DAIOPH orchestration system.

Gather and cite sources for a question using the injected search callable; distinguish verified facts from speculation.

Answer with findings, each tied to a source identifier from the provided corpus. Mark anything uncertain explicitly.
"""


def build_prompt(task: str, context: Dict[str, Any]) -> str:
    """Render the full user prompt for *task* with optional *context*."""
    lines = [f"QUESTION: {task}"]
    corpus = context.get("corpus")
    if corpus:
        lines.append("CORPUS:")
        for i, doc in enumerate(corpus):
            lines.append(f"  [{i}] {doc!r}")
    lines.append("\nResearch using only the corpus above.")
    return "\n".join(lines)
