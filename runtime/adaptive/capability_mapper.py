"""Maps detected hardware to recommended runtime settings.

Pure functions over a :class:`HardwareInfo` snapshot: no detection happens
here, so mapping logic is trivially testable with synthetic profiles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from runtime.hardware.hardware_detector import HardwareInfo

__all__ = ["RecommendedSettings", "map_capabilities"]


@dataclass(frozen=True)
class RecommendedSettings:
    """Conservative runtime settings derived from measured hardware."""

    inference_threads: int
    context_tokens: int
    prefer_quantized: bool
    rationale: str


def map_capabilities(info: HardwareInfo) -> RecommendedSettings:
    """Derive settings from *info* using conservative edge-device heuristics."""
    cpus = max(1, info.logical_cpus)
    threads = max(1, min(cpus - 1, 8))
    memory_gb = (
        info.total_memory_bytes / 1024**3 if info.total_memory_bytes else None
    )
    if memory_gb is None:
        ctx, quant = 2048, True
        rationale = "memory unknown; conservative defaults applied"
    elif memory_gb >= 16:
        ctx, quant = 4096, False
        rationale = f"ample memory ({memory_gb:.1f} GB)"
    elif memory_gb >= 8:
        ctx, quant = 2048, True
        rationale = f"moderate memory ({memory_gb:.1f} GB)"
    else:
        ctx, quant = 1024, True
        rationale = f"constrained memory ({memory_gb:.1f} GB)"
    return RecommendedSettings(
        inference_threads=threads,
        context_tokens=ctx,
        prefer_quantized=quant,
        rationale=rationale,
    )


def to_runtime_env(settings: RecommendedSettings) -> Dict[str, Any]:
    """Render settings as docker-compose-compatible env vars."""
    return {
        "QWEN_THREADS": str(settings.inference_threads),
        "QWEN_CTX": str(settings.context_tokens),
        "QWEN_QUANT": "q4_k_m" if settings.prefer_quantized else "q8_0",
    }
