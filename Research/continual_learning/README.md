# Continual Learning Research

## Overview

Research on enabling DAIOPH to learn continuously from interactions without catastrophic forgetting.

## Research Questions

1. Which anti-forgetting technique works best for assistant workloads (replay, EWC, LoRA adapters)?
2. How large must replay buffers be on memory-constrained devices?
3. Can adapter proliferation be managed automatically?
4. How does federated aggregation interact with local continual adaptation?

## Key Components Under Study

- `Backend/learning/continual/replay_buffer.py` — experience replay
- `Backend/learning/continual/incremental_learning.py` — online updates
- `Backend/learning/Research/training/trainer.py` — LoRA/PEFT pipelines
- `Backend/learning/evolution/regression_guard.py` — update safety
- `Research/evaluation/Backend/learning/forgetting.py` — forgetting metrics

## Related Documentation

- Architecture: `Documentation/docs/architecture/learning.md`
- Research overview: `Documentation/docs/Research/research/continual_learning.md`
- Experiments: [experiments.md](experiments.md)

## Getting Started

```bash
python Research/experiments/continual_Backend/learning/run_forgetting_study.py
```

## Contributing

Document all experiment results in `experiments.md` with reproducible protocols.