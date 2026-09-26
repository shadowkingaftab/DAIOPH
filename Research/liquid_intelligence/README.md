# Liquid Intelligence Research

## Overview

This directory contains research on DAIOPH's liquid intelligence: continuously adapting cognitive behavior inspired by Liquid Neural Networks.

## Research Questions

1. How should plasticity be modulated over a system's lifetime?
2. Which behaviors should be stability anchors vs. adaptable?
3. Can adaptation strategies themselves be learned?
4. How does adaptation interact with hardware constraints?

## Key Components Under Study

- `Backend/intelligence/liquid/liquid_engine.py` — central adaptive orchestrator
- `Backend/intelligence/liquid/plasticity.py` — learning rate modulation
- `Backend/intelligence/liquid/stability.py` — forgetting prevention
- `Backend/intelligence/liquid/confidence.py` — calibrated confidence
- `Backend/intelligence/liquid/uncertainty.py` — epistemic/aleatoric decomposition

## Related Documentation

- Architecture: `Documentation/docs/architecture/liquid.md`
- Research overview: `Documentation/docs/Research/research/liquid_intelligence.md`
- Experiments: [experiments.md](experiments.md)

## Getting Started

Run experiments from `Research/experiments/liquid/`:

```bash
python Research/experiments/liquid/run_adaptation_study.py
```

## Contributing

New findings should update both `experiments.md` (results) and `Documentation/docs/Research/research/liquid_intelligence.md` (theory).