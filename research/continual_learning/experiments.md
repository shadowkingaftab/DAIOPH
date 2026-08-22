# Continual Learning Experiments

## Experiment Log

| ID | Date | Experiment | Status | Result |
|----|------|-----------|--------|--------|
| CL-001 | 2026-08 | Anti-forgetting technique comparison | Planned | — |
| CL-002 | 2026-08 | Replay buffer sizing on edge | Planned | — |
| CL-003 | 2026-08 | Adapter interference study | Planned | — |
| CL-004 | 2026-08 | Federated continual learning | Planned | — |

## CL-001: Anti-Forgetting Technique Comparison

**Hypothesis**: LoRA adapters with replay outperform pure EWC for assistant workloads.

**Setup**:
- Task sequence: intent classification → preference learning → skill acquisition
- Techniques: fine-tune only (baseline), EWC, replay, LoRA+replay
- Metrics: BWT (backward transfer), FWT (forward transfer), average accuracy

**Protocol**:
```bash
python experiments/continual_learning/run_forgetting_study.py --method finetune
python experiments/continual_learning/run_forgetting_study.py --method ewc
python experiments/continual_learning/run_forgetting_study.py --method replay
python experiments/continual_learning/run_forgetting_study.py --method lora_replay
```

**Results**: TBD

## CL-002: Replay Buffer Sizing on Edge

**Hypothesis**: 500–1000 samples suffice for stable replay on 4GB devices.

**Setup**:
- Vary buffer size: 100, 250, 500, 1000, 2000
- Measure: forgetting rate vs. memory footprint
- Device: Raspberry Pi 4 profile

**Results**: TBD

## CL-003: Adapter Interference Study

**Hypothesis**: Adapters trained on related tasks interfere less than unrelated tasks.

**Setup**:
- Train adapters on task pairs with varying similarity
- Measure: cross-adapter performance degradation
- Test: adapter merging vs. switching strategies

**Results**: TBD

## CL-004: Federated Continual Learning

**Hypothesis**: Federated aggregation of adapter updates improves global performance without increasing local forgetting.

**Setup**:
- 10 simulated clients with non-IID data
- Compare: local-only vs. federated adapter updates
- Metrics: global accuracy, local forgetting, communication cost

**Results**: TBD

## Methodology Notes

- Task sequences are fixed and versioned for comparability
- Forgetting measured with the standard BWT metric
- All runs use 3 seeds; report mean ± std