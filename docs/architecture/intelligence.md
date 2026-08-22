# Intelligence Architecture

## Overview

The intelligence subsystem provides the cognitive capabilities of DAIOPH: intent understanding, reasoning, cognition, and state management.

## Components

### Intent Engine (`intelligence/intent/`)
- **Intent Classifier**: Maps user input to registered intents
- **Intent Registry**: Catalog of available intents with schemas
- **Intent Schema**: Validation of intent parameters
- **Intent Embeddings**: Semantic similarity for fuzzy matching
- **Intent Learning**: Learns new intents from usage patterns

### Reasoning Engine (`intelligence/reasoning/`)
- **Planner**: Creates execution plans from goals
- **Task Decomposer**: Breaks complex tasks into subtasks (DAG)
- **Hypothesis Engine**: Generates candidate solutions
- **Verifier**: Validates outputs against constraints
- **Critic**: Scores and ranks alternatives
- **Uncertainty Reasoner**: Quantifies confidence in decisions
- **Reflection**: Post-hoc analysis of successes/failures

### Cognition (`intelligence/cognition/`)
- **Perception**: Raw input processing and feature extraction
- **Attention**: Focus allocation across competing inputs
- **Working Memory**: Active context maintenance
- **Episodic/Semantic/Procedural Reasoning**: Memory-informed inference
- **Metacognition**: Self-monitoring of cognitive processes

### State Management (`intelligence/state/`)
- **State Manager**: Central cognitive state store
- **State Transitions**: Validated state changes
- **Snapshots**: Point-in-time state capture
- **Recovery**: Restore from snapshots after failures

## Processing Pipeline

```
Input → Perception → Attention → Intent → Planning → Execution → Verification → Response
                ↓                                    ↓
          Working Memory                      Reflection/Learning
```

## Confidence & Uncertainty

Every decision carries:
- **Confidence score** (`intelligence/liquid/confidence.py`): 0.0–1.0
- **Uncertainty estimate** (`intelligence/liquid/uncertainty.py`): epistemic + aleatoric

Low-confidence decisions trigger clarification requests or fallback strategies.