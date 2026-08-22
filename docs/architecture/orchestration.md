# Orchestration Architecture

## Overview

Orchestration coordinates multi-step task execution across agents, models, and tools using DAG-based planning with fallback and recovery.

## Orchestrators

DAIOPH provides multiple orchestrator implementations:

| Orchestrator | Location | Use Case |
|--------------|----------|----------|
| Hybrid | `core/hybrid_orchestrator.py` | Default: local + remote mix |
| Revolutionary | `revolutionary_orchestrator/` | Experimental strategies |
| Smart | `smart_orchestrator/` | Heuristic-driven routing |
| Unified | `unified_orchestrator/` | Single entry point facade |

## Execution Pipeline (`execution/`)

### DAG Generator (`dag_generator.py`)
Converts plans into directed acyclic graphs:
- Nodes = tasks with dependencies
- Edges = data/control flow
- Validates acyclicity and completeness

### Task Scheduler (`task_scheduler.py`)
- Topological ordering of tasks
- Parallel execution of independent branches
- Resource-aware scheduling

### Fallback Manager (`fallback_manager.py`)
- Per-task fallback strategies
- Model fallback chains (local → alternative local → remote)
- Timeout handling with partial results

### Result Aggregator (`result_aggregator.py`)
- Merges outputs from parallel branches
- Resolves conflicts between results
- Produces unified final output

## Agent Coordination (`agents/`)

```
                    ┌────────────┐
                    │ Supervisor │
                    └─────┬──────┘
          ┌───────────┬───┴────┬───────────┐
     ┌────▼───┐  ┌────▼───┐ ┌──▼─────┐ ┌───▼─────┐
     │Planner │  │Executor│ │Monitor │ │Verifier │
     └────────┘  └────────┘ └────────┘ └─────────┘
          │           │         │           │
     ┌────▼───┐  ┌────▼───┐ ┌──▼─────┐ ┌───▼─────┐
     │Researcher│ │Coder  │ │Analyst │ │(results)│
     └────────┘  └────────┘ └────────┘ └─────────┘
```

- **Supervisor**: Routes work, resolves escalations
- **Planner**: Creates task plans
- **Executor**: Runs individual tasks
- **Monitor**: Tracks progress and health
- **Verifier**: Validates outputs
- **Researcher/Coder/Analyst**: Specialized workers

## Routing (`evaluation/orchestration/routing.py`)

Model routing strategies:
1. **Local-first**: Prefer on-device models
2. **Hardware-aware**: Route based on device capabilities
3. **Quality-first**: Use best available model
4. **Cost-aware**: Minimize API costs when online

## Recovery (`evaluation/orchestration/recovery.py`)

Failure recovery patterns:
- Retry with backoff for transient failures
- Checkpoint/resume for long-running pipelines
- Partial result salvage when branches fail