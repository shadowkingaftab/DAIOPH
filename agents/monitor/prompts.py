"""System prompt and prompt builder for the monitor role.

Mission: observe system resources, task execution, and agent health; raise
actionable alerts with concrete numbers instead of vague warnings.

The prompt layer is deliberately vendor-neutral: ``build_prompt`` renders a
plain-text prompt that any injected LLM callable can consume.
"""

from __future__ import annotations

from typing import Any, Dict

__all__ = ["ROLE", "SYSTEM_PROMPT", "build_prompt"]

ROLE = "monitor"

SYSTEM_PROMPT = """You are the monitor agent of the DAIOPH orchestration system.

Observe system resources, task execution, and agent health. Raise alerts
with concrete measurements (values, thresholds, timestamps) rather than
vague warnings. Never fabricate readings you were not given.
"""


def build_prompt(task: str, context: Dict[str, Any]) -> str:
    """Render the full monitoring prompt for *task* with optional *context*."""
    lines = [f"OBSERVATION REQUEST: {task}"]
    metrics = context.get("metrics")
    if metrics:
        lines.append("CURRENT METRICS:")
        for key, value in sorted(metrics.items()):
            lines.append(f"  - {key}: {value!r}")
    alerts = context.get("alerts")
    if alerts:
        lines.append("ACTIVE ALERTS:")
        for alert in alerts:
            lines.append(f"  - {alert!r}")
    lines.append("")
    lines.append("Assess health and recommend actions.")
    return "\n".join(lines)