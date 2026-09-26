"""Request schemas for the chat API surface."""

from __future__ import annotations

from APIs.schemas.base import Field, Schema

__all__ = ["CHAT_SEND_SCHEMA", "CHAT_HISTORY_SCHEMA"]

CHAT_SEND_SCHEMA = Schema(
    name="chat.send",
    fields=[
        Field(name="message", type=str, required=True, max_length=8000),
        Field(name="session_id", type=str, required=True, max_length=128),
        Field(
            name="route",
            type=str,
            required=False,
            choices=("edge", "cloud", "hybrid", "auto"),
        ),
    ],
)

CHAT_HISTORY_SCHEMA = Schema(
    name="chat.history",
    fields=[
        Field(name="session_id", type=str, required=True, max_length=128),
        Field(name="limit", type=int, required=False),
    ],
)
