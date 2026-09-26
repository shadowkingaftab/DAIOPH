# Hardware Architecture

## Overview

The hardware subsystem detects device capabilities and adapts system behavior to available compute, memory, and energy constraints.

## Components

### Hardware Detector (`Backend/hardware/hardware_detector.py`)
- Detects CPU cores, architecture, features
- Detects GPU availability (CUDA, Metal, ROCm)
- Detects NPU/accelerators where supported
- Reports total/available memory
- Caches results with configurable refresh interval

### CPU (`Backend/hardware/cpu.py`)
- Core count and thread management
- CPU feature detection (AVX2, NEON)
- Load monitoring
- Thread pool sizing for inference

### GPU (`Backend/hardware/gpu.py`)
- CUDA device enumeration
- VRAM capacity reporting
- Device selection strategy
- Fallback to CPU when unavailable

### Model Scaler (`Backend/hardware/model_scaler.py`)
Selects appropriate model sizes based on hardware:

| Hardware Tier | RAM | Recommended Models |
|---------------|-----|-------------------|
| Minimal | < 4GB | Qwen 0.5B int8 |
| Low | 4–8GB | Qwen 0.5B fp16 |
| Medium | 8–16GB | Qwen 1.5B / Llama 1B |
| High | 16GB+ | Llama 3B+ |
| GPU | VRAM ≥ 8GB | Larger models on GPU |

### Resource Monitor (`Backend/hardware/resource_monitor.py`)
- Real-time CPU/Backend/memory/GPU utilization
- Thermal state monitoring
- Alerts when resources are constrained

### Energy Manager (`Backend/hardware/energy_manager.py`)
- Battery level awareness
- Power saving mode triggers
- Defers heavy tasks when on battery
- Idle detection for background work scheduling

## Adaptation Flow

```
Detect Hardware → Build Profile → Select Models
       ↓                ↓              ↓
Resource Monitor → Constraints → Liquid Engine
       ↓
Energy Manager → Throttle/Defer Decisions
```

## Configuration

Hardware profiles are defined in `Operations/configs/hardware_profiles.yaml` and per-environment in `Operations/configs/edge/hardware.yaml`.

## Benchmarks

Performance baselines per device class are maintained in `Research/benchmarks/devices/` with latency, throughput, memory, and energy measurements.