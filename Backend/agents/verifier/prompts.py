"""System prompt and prompt builder for the verifier role.

Mission: Check an artifact against explicit acceptance criteria and emit a pass/fail verdict with per-criterion detail.

The prompt layer is deliberately vendor-neutral: ``build_prompt`` renders a
plain-text prompt that any injected LLM callable can consume.
"""

from __future__ import annotations

from typing import Any, Dict

__all__ = ["ROLE", "SYSTEM_PROMPT", "build_prompt"]

ROLE = "verifier"

SYSTEM_PROMPT = """You are the verifier agent of the DAIOPH orchestration system.

Check an artifact against explicit acceptance criteria and emit a pass/fail verdict with per-criterion detail.

Verify ARTIFACT against CRITERIA. Return verdict pass/fail with one line per criterion. Do not approve on missing evidence.
"""


def build_prompt(task: str, context: Dict[str, Any]) -> str:
    """Render the full user prompt for *task* with optional *context*."""
    lines = [f"ARTIFACT: {task}"]
    criteria = context.get("criteria")
    if criteria:
        lines.append("CRITERIA:")
        for c in criteria:
            lines.append(f"  - {c}")
    lines.append("\nVerify against every criterion.")
    return "\n".join(lines)
