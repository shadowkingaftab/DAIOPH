# Research: Device Adaptation

## Problem Statement

AI assistants must run on wildly heterogeneous hardware: from a Raspberry Pi with 4GB RAM to a cloud GPU server. A single fixed configuration cannot serve this range — it either wastes resources on capable hardware or fails entirely on constrained devices.

**Device adaptation** is the automatic tailoring of models, strategies, and behavior to the specific device.

## Adaptation Dimensions

### 1. Model Selection (`hardware/model_scaler.py`)

Map device capabilities → appropriate model:

```
Device Profile
  ├── CPU cores, architecture (x86/ARM)
  ├── RAM total/available
  ├── GPU presence + VRAM
  ├── NPU availability
  └── Energy constraints (battery)
        ↓
   Model Tier Selection
```

Selection considers:
- **Memory footprint**: model + KV cache + activations must fit
- **Compute throughput**: tokens/sec targets per tier
- **Quantization**: int8/int4 on CPU; fp16 on GPU

### 2. Quantization Strategy (`models/optimization/quantization.py`)

| Device | Strategy |
|--------|----------|
| Edge CPU | int8 weight-only quantization |
| Mid-range | int8 activations + weights |
| GPU | fp16/bf16 native |
| NPU | Vendor-specific formats |

Dynamic quantization can adjust at runtime based on load.

### 3. Reasoning Depth Adaptation

Cognitive effort scales with available compute:
- **Constrained**: single-pass responses, no verification
- **Standard**: intent → plan → execute → verify
- **Capable**: hypothesis generation, critic ensembles, reflection loops

Implemented via `intelligence/liquid/adaptation.py` adjusting strategy parameters.

### 4. Batching & Concurrency (`models/optimization/batching.py`)

- Small devices: batch size 1, serialized requests
- Servers: dynamic batching, parallel inference streams

### 5. Energy-Aware Scheduling (`hardware/energy_manager.py`)

On battery-powered devices:
- Defer non-urgent learning tasks
- Reduce polling frequencies
- Throttle background consolidation

## Learning Device Preferences

`learning/adaptation/device_adaptation.py` learns:
- Which model tiers perform acceptably on this device
- Optimal context lengths before latency degrades
- Thermal patterns (when does throttling kick in?)

These learned profiles persist and improve over time.

## Benchmarking

Device benchmarks in `benchmarks/devices/` establish baselines:
- Latency percentiles per model/device combination
- Memory usage curves
- Energy consumption per interaction
- Throughput under concurrent load

Results feed back into the scaler's selection tables.

## Evaluation Metrics

From `evaluation/models/efficiency.py`:
- Tokens/sec/watt (energy efficiency)
- Quality-per-latency trade-off curves
- Adaptation convergence time after hardware change

## Open Challenges

1. **Cold start**: New/unusual devices lack benchmark data
2. **Thermal modeling**: Predicting sustained vs. burst performance
3. **Heterogeneous federation**: Aggregating across device classes fairly
4. **Quality guarantees**: Ensuring minimum quality floors on weak hardware

## References

- Dettmers, T., et al. "QLoRA: Efficient Finetuning of Quantized LLMs." 2023.
- Frantar, E., et al. "GPTQ: Accurate Post-Training Quantization." 2022.
- MLPerf Inference benchmarks.