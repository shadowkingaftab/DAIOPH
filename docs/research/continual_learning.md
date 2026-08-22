# Research: Continual Learning

## Problem Statement

Models deployed in assistants face a **non-stationary distribution**: user preferences evolve, new topics emerge, and task patterns shift. Static models degrade; full retraining is expensive and loses personalization.

Continual learning aims to learn new information while retaining old capabilities — avoiding **catastrophic forgetting**.

## Approaches in DAIOPH

### 1. Experience Replay (`learning/continual/replay_buffer.py`)

Maintain a buffer of past examples; interleave with new data during training.

- **Buffer sizing**: Bounded by device memory (edge: ~1000 samples)
- **Selection strategy**: Reservoir sampling for uniform coverage
- **Prioritization**: High-importance memories replayed more often

Trade-off: replayed samples may be stale; privacy requires samples stay local.

### 2. Regularization-Based (EWC-style)

Penalize changes to parameters important for past tasks:

```
L_total = L_new + λ Σᵢ Fᵢ (θᵢ - θᵢ*)²
```

Where `F` is the Fisher information matrix (parameter importance).

- Implemented in `learning/continual/incremental_learning.py`
- Fisher estimates computed online from gradient statistics
- λ adapted by the liquid plasticity controller

### 3. Parameter-Efficient Fine-Tuning (LoRA/PEFT)

Instead of updating all weights:
- Freeze base model
- Train small adapter matrices
- Multiple adapters can represent different "skills"

Benefits for edge:
- Tiny update sizes (MBs vs GBs)
- Fast switching between specializations
- Easy rollback (drop adapter)

### 4. Federated Continual Learning

Combines continual learning with federation:
- Local continual adaptation on-device
- Federated aggregation of adapter updates
- DP noise protects individual adaptation patterns

## Forgetting Measurement

`evaluation/learning/forgetting.py` tracks:

```
Forgetting = max_performance_before - performance_after
```

Across a task suite, reported as average forgetting (BWT metric).

## Drift Detection

`evaluation/learning/drift.py` detects distribution shift:
- Input embedding drift (are queries changing?)
- Performance drift (is accuracy declining?)
- Triggers increased plasticity when drift detected

## Regression Safety

`learning/evolution/regression_guard.py`:
- Every update validated on held-out set
- Updates failing validation are rolled back
- Rollback history enables post-mortem analysis

## Open Challenges

1. **Buffer privacy**: Can replay buffers be made DP without destroying utility?
2. **Adapter proliferation**: Managing many adapters without interference
3. **Cross-task interference**: LoRA adapters trained on related tasks may conflict
4. **Evaluation**: No standard benchmark for assistant-style continual learning

## References

- Rolnick, D., et al. "Experience Replay for Continual Learning." NeurIPS 2019.
- Hu, E., et al. "LoRA: Low-Rank Adaptation of Large Language Models." 2021.
- De Lange, M., et al. "A Continual Learning Survey." TPAMI 2021.