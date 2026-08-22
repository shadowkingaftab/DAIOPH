# ADR-003: DAG-Based Orchestration with Fallback Chains

## Status

Accepted

## Context

Complex user requests require multiple steps: research, planning, execution, verification. These steps may involve different models (local/remote), tools, and agents. We needed orchestration that:

1. Handles dependencies between steps correctly
2. Executes independent steps in parallel
3. Recovers from partial failures without losing completed work
4. Falls back across models when one is unavailable
5. Works identically on edge (in-process) and cloud (distributed)

Alternatives considered:
- **Sequential pipeline**: Simple but no parallelism; a single failure loses everything
- **Free-form agent loops**: Flexible but unpredictable latency and cost; hard to verify
- **Workflow engines (Temporal, Airflow)**: Heavy external dependencies; overkill for edge

## Decision

Implement **DAG-based orchestration** (`execution/`) with:

1. **Plan → DAG compilation** (`dag_generator.py`): plans become validated directed acyclic graphs
2. **Topological scheduling** (`task_scheduler.py`): independent branches run in parallel
3. **Per-node fallback chains** (`fallback_manager.py`):

```
Primary model → Alt local → Quantized → Remote API → Cached response
```

4. **Result aggregation** (`result_aggregator.py`): merges branch outputs, resolves conflicts
5. **Checkpointing**: long DAGs persist progress; resume after interruption
6. **Agent roles** (`agents/`): supervisor/planner/executor/monitor/verifier map onto DAG stages

## Failure Semantics

| Node failure | Behavior |
|--------------|----------|
| Transient | Retry with exponential backoff (max 5) |
| Model unavailable | Walk fallback chain |
| Branch failed | Salvage sibling branches; aggregate partial results |
| Critical node failed | Fail fast; return partial + explanation |

## Consequences

### Positive
- Predictable structure enables verification and cost estimation before execution
- Parallelism where possible; correctness guaranteed by DAG validation
- Partial failure tolerance maximizes value from expensive pipelines
- Same code path works in-process (edge) and distributed (cloud)

### Negative
- Some tasks don't decompose cleanly into DAGs (conversational back-and-forth)
- Checkpoint storage adds I/O overhead
- DAG validation must be strict to avoid runtime surprises

### Neutral
- Free-form agent loops remain available for exploratory tasks via the reasoning engine; the DAG path is used when a plan exists