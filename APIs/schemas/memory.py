"""Request schemas for the memory API surface."""

from __future__ import annotations

from APIs.schemas.base import Field, Schema

__all__ = ["MEMORY_STORE_SCHEMA", "MEMORY_QUERY_SCHEMA", "MEMORY_DELETE_SCHEMA"]

MEMORY_STORE_SCHEMA = Schema(
    name="memory.store",
    fields=[
        Field(name="session_id", type=str, required=True, max_length=128),
        Field(name="content", type=str, required=True, max_length=32000),
        Field(
            name="kind",
            type=str,
            required=False,
            choices=("episodic", "semantic", "preference"),
        ),
    ],
)

MEMORY_QUERY_SCHEMA = Schema(
    name="memory.query",
    fields=[
        Field(name="session_id", type=str, required=True, max_length=128),
        Field(name="query", type=str, required=True, max_length=2000),
        Field(name="limit", type=int, required=False),
    ],
)

MEMORY_DELETE_SCHEMA = Schema(
    name="memory.delete",
    fields=[Field(name="session_id", type=str, required=True, max_length=128)],
)
