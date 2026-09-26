"""System prompt and prompt builder for the supervisor role.

Mission: Aggregate worker results into a run verdict: success ratio, failed tasks, and whether the overall goal is met.

The prompt layer is deliberately vendor-neutral: ``build_prompt`` renders a
plain-text prompt that any injected LLM callable can consume.
"""

from __future__ import annotations

from typing import Any, Dict

__all__ = ["ROLE", "SYSTEM_PROMPT", "build_prompt"]

ROLE = "supervisor"

SYSTEM_PROMPT = """You are the supervisor agent of the DAIOPH orchestration system.

Aggregate worker results into a run verdict: success ratio, failed tasks, and whether the overall goal is met.

Given RESULTS, decide: goal_met (bool), blockers, and next actions. Be conservative: any critical failure blocks the goal.
"""


def build_prompt(task: str, context: Dict[str, Any]) -> str:
    """Render the full user prompt for *task* with optional *context*."""
    lines = [f"GOAL: {task}"]
    results = context.get("results")
    if results:
        lines.append(f"RESULTS: {results!r}")
    lines.append("\nAssess the run.")
    return "\n".join(lines)
