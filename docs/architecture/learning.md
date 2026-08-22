# Learning Architecture

## Overview

The learning subsystem enables DAIOPH to improve continuously from interactions, feedback, and environmental changes without catastrophic forgetting.

## Components

### Continual Learning (`learning/continual/`)
- **Continual Engine**: Orchestrates ongoing learning
- **Replay Buffer**: Stores samples to prevent forgetting
- **Incremental Learning**: Online model updates

Techniques supported:
- Experience replay
- Elastic Weight Consolidation (EWC)
- Gradient episodic memory (GEM)

### Adaptation (`learning/adaptation/`)
- **User Adaptation**: Personalizes to individual users
- **Device Adaptation**: Optimizes for hardware capabilities
- **Task Adaptation**: Specializes for recurring task types
- **Strategy Adaptation**: Adjusts high-level approaches

### Feedback (`learning/feedback/`)
- **Feedback Engine**: Central feedback processing
- **Explicit Feedback**: Ratings, corrections, preferences
- **Implicit Feedback**: Usage patterns, abandonment, retries

### Training (`learning/training/`)
- **Trainer**: Local fine-tuning pipelines
- Supports LoRA/PEFT for efficient adaptation

### Evolution (`learning/evolution/`)
- **Evolution Engine**: Long-term capability improvement
- **Strategy Evolution**: Evolves decision strategies
- **Capability Evolution**: Grows new capabilities
- **Architecture Search**: NAS for model selection
- **Regression Guard**: Prevents performance regressions

## Learning Loop

```
Interaction → Feedback Capture → Signal Processing
      ↑                                ↓
Model Update ← Training ← Replay Buffer
      ↓
Regression Check → Deploy or Rollback
```

## Safety Mechanisms

1. **Regression Guard**: Every update is validated against a held-out set
2. **Rollback**: Failed updates are automatically reverted
3. **Rate Limiting**: Learning updates are throttled on constrained hardware
4. **Privacy**: Training data never leaves the device (unless federated)

## Integration with Liquid Intelligence

The learning subsystem provides signals to the liquid engine:
- Task success rates → adaptation triggers
- User satisfaction → plasticity adjustments
- Hardware metrics → training throttling