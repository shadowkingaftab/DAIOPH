"""Builds a complete hardware profile from the detection subsystems."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from runtime.hardware.accelerator import available_accelerators
from runtime.hardware.cpu import probe_cpu
from runtime.hardware.gpu import GPUDevice, detect_gpus
from runtime.hardware.hardware_detector import HardwareDetector
from runtime.hardware.memory import snapshot_memory
from runtime.hardware.storage import probe_storage

__all__ = ["HardwareProfile", "build_profile"]


@dataclass
class HardwareProfile:
    """Everything the adaptive layer knows about this machine."""

    platform: str
    architecture: str
    logical_cpus: int
    physical_cores: Any
    total_memory_gb: Any
    gpus: List[GPUDevice] = field(default_factory=list)
    accelerators: List[str] = field(default_factory=list)
    storage: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_gpu(self) -> bool:
        """True only when at least one GPU was actually detected."""
        return bool(self.gpus)

    def to_dict(self) -> Dict[str, Any]:
        """JSON-friendly representation."""
        return {
            "platform": self.platform,
            "architecture": self.architecture,
            "logical_cpus": self.logical_cpus,
            "physical_cores": self.physical_cores,
            "total_memory_gb": self.total_memory_gb,
            "has_gpu": self.has_gpu,
            "gpus": [
                {"vendor": g.vendor, "backend": g.backend, "name": g.name}
                for g in self.gpus
            ],
            "accelerators": list(self.accelerators),
            "storage": self.storage,
        }


def build_profile(storage_path: str = ".") -> HardwareProfile:
    """Assemble a full profile from every detection module."""
    info = HardwareDetector().detect()
    gpus = detect_gpus()
    memory = snapshot_memory()
    try:
        storage = probe_storage(storage_path)
        storage_view = {
            "path": storage.path,
            "total_gb": round(storage.total_bytes / 1024**3, 2),
            "percent_used": storage.percent_used,
        }
    except OSError:
        storage_view = {}
    return HardwareProfile(
        platform=f"{info.platform_name} {info.platform_release}",
        architecture=info.architecture,
        logical_cpus=info.logical_cpus,
        physical_cores=probe_cpu().physical_cores,
        total_memory_gb=(
            round(memory.total_bytes / 1024**3, 2)
            if memory.total_bytes else None
        ),
        gpus=gpus,
        accelerators=[a.backend for a in available_accelerators()],
        storage=storage_view,
    )
