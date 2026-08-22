# Liquid Intelligence Experiments

## Experiment Log

| ID | Date | Experiment | Status | Result |
|----|------|-----------|--------|--------|
| LI-001 | 2026-08 | Plasticity schedule comparison | Planned | — |
| LI-002 | 2026-08 | Stability anchor ablation | Planned | — |
| LI-003 | 2026-08 | Confidence calibration | Planned | — |
| LI-004 | 2026-08 | Hardware-aware adaptation | Planned | — |

## LI-001: Plasticity Schedule Comparison

**Hypothesis**: Decaying plasticity schedules outperform constant rates for long-running assistants.

**Setup**:
- Simulated 10,000 interactions with drifting user preferences
- Compare: constant, exponential decay, cosine decay, adaptive (confidence-gated)
- Metrics: adaptation speed, final accuracy, forgetting rate

**Protocol**:
```bash
python experiments/liquid/run_adaptation_study.py --schedule constant
python experiments/liquid/run_adaptation_study.py --schedule exp_decay
python experiments/liquid/run_adaptation_study.py --schedule cosine
python experiments/liquid/run_adaptation_study.py --schedule adaptive
```

**Expected outcome**: Adaptive schedules converge fastest while maintaining stability.

**Results**: TBD

## LI-002: Stability Anchor Ablation

**Hypothesis**: Anchoring core behaviors (safety, formatting) prevents harmful drift without blocking useful adaptation.

**Setup**:
- Vary the set of anchored capabilities
- Measure: drift on anchored vs. free capabilities
- Detect: any harmful adaptation that anchors would have prevented

**Results**: TBD

## LI-003: Confidence Calibration

**Hypothesis**: Confidence scores can be calibrated to within ±5% of actual accuracy using temperature scaling on interaction outcomes.

**Setup**:
- Collect (predicted confidence, actual correctness) pairs over 1,000 interactions
- Fit calibration curve; measure ECE (Expected Calibration Error)

**Results**: TBD

## LI-004: Hardware-Aware Adaptation

**Hypothesis**: Strategy-level adaptation (reasoning depth) recovers most quality lost from model downsizing on constrained hardware.

**Setup**:
- Run identical task suite on 3 hardware tiers
- Compare: fixed strategy vs. adapted strategy at each tier
- Metrics: quality score, latency, energy

**Results**: TBD

## Methodology Notes

- All experiments use seeded randomness for reproducibility
- Baselines are always the current production configuration
- Results are committed alongside the experiment code