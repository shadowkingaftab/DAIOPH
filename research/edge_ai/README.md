# Edge AI Research

## Overview

Research on running capable AI on resource-constrained hardware: quantization, model scaling, energy efficiency, and hardware-aware inference.

## Research Questions

1. What quality is recoverable through strategy adaptation when models are downsized?
2. Which quantization schemes offer the best quality/latency trade-off per device class?
3. How much energy does an average interaction consume on edge devices?
4. Can thermal throttling be predicted and mitigated?

## Key Components Under Study

- `hardware/model_scaler.py` — device-to-model mapping
- `hardware/energy_manager.py` — power-aware scheduling
- `models/optimization/quantization.py` — int8/int4 schemes
- `models/optimization/compilation.py` — runtime optimization
- `benchmarks/devices/` — device baselines

## Related Documentation

- Architecture: `docs/architecture/hardware.md`
- Research overview: `docs/research/device_adaptation.md`
- Benchmarks: [benchmarks.md](benchmarks.md)

## Getting Started

```bash
python benchmarks/devices/benchmark.py --device raspberry_pi_4
```

## Contributing

Benchmark results should include full hardware specs, software versions, and measurement methodology.