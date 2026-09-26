"""Facade composing memory, compute, power, and quota management."""

from __future__ import annotations

from typing import Any, Dict

from runtime.resource.compute_manager import ComputeManager
from runtime.resource.memory_manager import MemoryManager
from runtime.resource.power_manager import PowerManager, PowerStatus
from runtime.resource.quota_manager import QuotaManager

__all__ = ["ResourceManager"]


class ResourceManager:
    """Single entry point for resource governance."""

    def __init__(
        self,
        memory_budget_bytes: int = 1 << 30,
        compute_slots: int = 4,
        quota_limit: int = 100,
        quota_window_seconds: float = 60.0,
    ) -> None:
        self.memory = MemoryManager(memory_budget_bytes)
        self.compute = ComputeManager(compute_slots)
        self.power = PowerManager()
        self.quotas = QuotaManager(quota_limit, quota_window_seconds)

    def overview(self) -> Dict[str, Any]:
        """Combined status snapshot for dashboards."""
        memory = self.memory.status()
        power: PowerStatus = self.power.status()
        return {
            "memory": {
                "budget_bytes": memory.budget_bytes,
                "reserved_bytes": memory.reserved_bytes,
                "percent_used": memory.percent_used,
            },
            "compute_utilization": self.compute.utilization(),
            "power": {
                "plugged_in": power.plugged_in,
                "battery_percent": power.battery_percent,
                "source": power.source,
            },
            "recommended_power_mode": self.power.recommend_mode().value,
        }
