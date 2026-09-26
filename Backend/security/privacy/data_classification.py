"""Data classification levels."""

from __future__ import annotations

from enum import Enum

__all__ = ["DataClassification"]


class DataClassification(str, Enum):
    """Sensitivity levels for data handling."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
