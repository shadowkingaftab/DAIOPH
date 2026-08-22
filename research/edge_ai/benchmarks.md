# Edge AI Benchmarks

## Benchmark Results

Results are collected via `benchmarks/devices/benchmark.py`. Each entry includes hardware specs, software versions, and methodology.

## Latency (First Token, ms)

| Device | Model | fp16 | int8 | int4 |
|--------|-------|------|------|------|
| Raspberry Pi 4 (4GB) | Qwen 0.5B | — | 2,400–4,000 | TBD |
| Jetson Nano | Qwen 0.5B | — | 1,000–2,000 | TBD |
| Intel NUC i7 | Qwen 1.5B | — | 500–1,000 | TBD |
| Desktop RTX 3060 | Llama 3B | 200–400 | 150–300 | TBD |

## Throughput (tokens/sec)

| Device | Model | int8 |
|--------|-------|------|
| Raspberry Pi 4 | Qwen 0.5B | 3–6 |
| Jetson Nano | Qwen 0.5B | 8–15 |
| Intel NUC i7 | Qwen 1.5B | 15–30 |
| RTX 3060 | Llama 3B | 40–80 |

## Memory Footprint (MB)

| Model | fp16 | int8 | int4 |
|-------|------|------|------|
| Qwen 0.5B | ~1,100 | ~600 | ~350 |
| Qwen 1.5B | ~3,200 | ~1,700 | ~950 |
| Llama 3B | ~6,500 | ~3,400 | ~1,900 |

## Energy per Interaction (Joules)

| Device | Simple Query | Complex Task |
|--------|-------------|--------------|
| Raspberry Pi 4 | 8–15 | 25–60 |
| Jetson Nano | 5–10 | 18–40 |

*Measured with power meter over 50-interaction average.*

## Thermal Behavior

| Device | Sustained Load Throttle Point | Recovery Time |
|--------|------------------------------|---------------|
| Raspberry Pi 4 | ~70°C after 10 min | 2–5 min |
| Jetson Nano | ~85°C after 15 min | 3–8 min |

## Methodology

- Warmup: 10 iterations discarded
- Measurement: 100 iterations, report p50/p95/p99
- Power: external power meter at wall (includes overhead)
- Software: pinned dependency versions recorded per run

## Reproducing

```bash
python benchmarks/devices/benchmark.py --device <profile> --iterations 100
python scripts/benchmarking/compare.py --baseline results/v1.json