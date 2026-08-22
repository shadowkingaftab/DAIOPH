# Research: Liquid Intelligence

## Motivation

Traditional AI assistants are static: their behavior is fixed at deployment. Real assistants need to adapt continuously — to users, devices, and tasks — without retraining from scratch or losing existing capabilities.

Liquid intelligence draws inspiration from **Liquid Neural Networks** (Hasani et al.), whose time-continuous, adaptive dynamics enable robust behavior in changing environments.

## Core Ideas

### 1. Continuous Adaptation
Rather than discrete "training phases," the system adapts continuously:
- Every interaction produces a learning signal
- Adaptations are small, frequent, and reversible
- The system is never "done" learning

### 2. Plasticity-Stability Balance
A fundamental tension in continual learning:
- **Too plastic**: catastrophic forgetting, instability
- **Too stable**: cannot adapt to new patterns

Our approach modulates plasticity per-capability based on:
- Signal reliability (confidence of feedback)
- Change magnitude (how different is new data?)
- Stability anchors (core behaviors that must not drift)

### 3. Hardware-Aware Cognition
Cognition itself adapts to hardware constraints:
- On low-power devices: simpler reasoning chains, smaller models
- On capable hardware: deeper deliberation, ensemble verification
- Adaptation happens at the *strategy* level, not just model selection

## Architecture Mapping

| Research Concept | Implementation |
|------------------|----------------|
| Adaptive dynamics | `intelligence/liquid/liquid_engine.py` |
| State fluidity | `intelligence/liquid/liquid_state.py` |
| Learning rate modulation | `intelligence/liquid/plasticity.py` |
| Forgetting prevention | `intelligence/liquid/stability.py` |
| Calibrated confidence | `intelligence/liquid/confidence.py` |
| Uncertainty decomposition | `intelligence/liquid/uncertainty.py` |

## Open Questions

1. **Optimal plasticity schedules**: How should learning rates decay over a system's lifetime?
2. **Stability anchor selection**: Which behaviors are truly core vs. adaptable?
3. **Cross-device transfer**: How do adaptations generalize across hardware profiles?
4. **Federated liquid learning**: Can adaptation strategies themselves be federated?

## Evaluation

Metrics tracked in `evaluation/intelligence/` and `evaluation/learning/`:
- Adaptation speed (interactions to converge on user preference)
- Stability (performance variance over time)
- Forgetting rate (old task performance after new learning)
- Calibration (confidence vs. actual accuracy)

## References

- Hasani, R., et al. "Liquid Time-constant Networks." AAAI 2021.
- Kirkpatrick, J., et al. "Overcoming Catastrophic Forgetting" (EWC). 2017.
- Zenke, F., et al. "Continual Learning Through Synaptic Intelligence." 2017.