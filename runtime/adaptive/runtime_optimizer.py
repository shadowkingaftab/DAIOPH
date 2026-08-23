"""Turns hardware profiles and workload stats into concrete tuning advice."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from runtime.adaptive.capability_mapper import RecommendedSettings
from runtime.adaptive.workload_profiler import WorkloadProfiler
from runtime.hardware.hardware_detector import HardwareDetector

__all__ = ["OptimizationPlan", "optimize"]


@dataclass(frozen=True)
class OptimizationPlan:
    """Concrete, justified tuning knobs for the runtime."""

    threads: int
    context_tokens: int
    quantization: str
    batch_size: int
    notes: tuple


def optimize(
    profiler: Optional[WorkloadProfiler] = None,
    slow_threshold_ms: float = 500.0,
) -> OptimizationPlan:
    """Combine hardware mapping with observed workload latency.

    Slow observed workloads increase the suggested batch size; fast ones
    keep it small to bound latency. Everything traces back to measurements.
    """
    info = HardwareDetector().detect()
    from runtime.adaptive.capability_mapper import map_capabilities

    settings: RecommendedSettings = map_capabilities(info)
    notes = [f"hardware: {settings.rationale}"]
    batch_size = 128
    if profiler is not None:
        for key in profiler.keys():
            stats = profiler.stats(key)
            if stats is None:
                continue
            if stats.p95_ms > slow_threshold_ms:
                batch_size = min(512, batch_size * 2)
                notes.append(
                    f"{key}: p95 {stats.p95_ms:.0f}ms > "
                    f"{slow_threshold_ms:.0f}ms -> batch doubled"
                )
            else:
                notes.append(f"{key}: p95 {stats.p95_ms:.0f}ms within budget")
    return OptimizationPlan(
        threads=settings.inference_threads,
        context_tokens=settings.context_tokens,
        quantization=("q4_k_m" if settings.prefer_quantized else "q8_0"),
        batch_size=batch_size,
        notes=tuple(notes),
    )


def to_env(plan: OptimizationPlan) -> Dict[str, Any]:
    """Render the plan as docker-compose-compatible environment values."""
    return {
        "QWEN_THREADS": str(plan.threads),
        "QWEN_CTX": str(plan.context_tokens),
        "QWEN_QUANT": plan.quantization,
        "QWEN_BATCH": str(plan.batch_size),
    }
