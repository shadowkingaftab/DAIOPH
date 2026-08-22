# Liquid Intelligence Research

## Overview

This directory contains research on DAIOPH's liquid intelligence: continuously adapting cognitive behavior inspired by Liquid Neural Networks.

## Research Questions

1. How should plasticity be modulated over a system's lifetime?
2. Which behaviors should be stability anchors vs. adaptable?
3. Can adaptation strategies themselves be learned?
4. How does adaptation interact with hardware constraints?

## Key Components Under Study

- `intelligence/liquid/liquid_engine.py` — central adaptive orchestrator
- `intelligence/liquid/plasticity.py` — learning rate modulation
- `intelligence/liquid/stability.py` — forgetting prevention
- `intelligence/liquid/confidence.py` — calibrated confidence
- `intelligence/liquid/uncertainty.py` — epistemic/aleatoric decomposition

## Related Documentation

- Architecture: `docs/architecture/liquid.md`
- Research overview: `docs/research/liquid_intelligence.md`
- Experiments: [experiments.md](experiments.md)

## Getting Started

Run experiments from `experiments/liquid/`:

```bash
python experiments/liquid/run_adaptation_study.py
```

## Contributing

New findings should update both `experiments.md` (results) and `docs/research/liquid_intelligence.md` (theory).