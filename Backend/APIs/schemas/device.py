"""Request schemas for the device API surface."""

from __future__ import annotations

from APIs.schemas.base import Field, Schema

__all__ = ["DEVICE_REGISTER_SCHEMA", "DEVICE_TELEMETRY_SCHEMA"]

DEVICE_REGISTER_SCHEMA = Schema(
    name="device.register",
    fields=[
        Field(name="device_id", type=str, required=True, max_length=128),
        Field(
            name="platform",
            type=str,
            required=True,
            choices=("windows", "linux", "macos", "android", "ios"),
        ),
        Field(name="model_name", type=str, required=False, max_length=256),
    ],
)

DEVICE_TELEMETRY_SCHEMA = Schema(
    name="device.telemetry",
    fields=[
        Field(name="device_id", type=str, required=True, max_length=128),
        Field(name="cpu_percent", type=(int, float), required=False),
        Field(name="memory_percent", type=(int, float), required=False),
    ],
)
