"""Request schemas for the models API surface."""

from __future__ import annotations

from APIs.schemas.base import Field, Schema

__all__ = ["MODEL_LOAD_SCHEMA", "MODEL_INFER_SCHEMA"]

MODEL_LOAD_SCHEMA = Schema(
    name="models.load",
    fields=[
        Field(name="model_id", type=str, required=True, max_length=256),
        Field(
            name="quantization",
            type=str,
            required=False,
            choices=("q2_k", "q4_k_m", "q8_0", "none"),
        ),
    ],
)

MODEL_INFER_SCHEMA = Schema(
    name="models.infer",
    fields=[
        Field(name="model_id", type=str, required=True, max_length=256),
        Field(name="prompt", type=str, required=True, max_length=32000),
        Field(name="max_tokens", type=int, required=False),
    ],
)
