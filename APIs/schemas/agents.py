"""Request schemas for the agents API surface."""

from __future__ import annotations

from APIs.schemas.base import Field, Schema

__all__ = ["AGENT_RUN_SCHEMA", "AGENT_SPAWN_SCHEMA"]

AGENT_RUN_SCHEMA = Schema(
    name="agents.run",
    fields=[
        Field(name="agent_id", type=str, required=True, max_length=128),
        Field(name="task", type=str, required=True, max_length=8000),
    ],
)

AGENT_SPAWN_SCHEMA = Schema(
    name="agents.spawn",
    fields=[
        Field(name="agent_id", type=str, required=True, max_length=128),
        Field(
            name="role",
            type=str,
            required=True,
            choices=(
                "planner", "executor", "coder", "analyst",
                "researcher", "supervisor", "verifier", "monitor",
            ),
        ),
    ],
)
