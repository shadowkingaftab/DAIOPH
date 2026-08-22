# Agents Experiments

## Experiment Log

| ID | Date | Experiment | Status | Result |
|----|------|-----------|--------|--------|
| AG-001 | 2026-08 | Topology comparison | Planned | — |
| AG-002 | 2026-08 | Verifier impact on quality | Planned | — |
| AG-003 | 2026-08 | Minimum viable agent set | Planned | — |
| AG-004 | 2026-08 | Communication overhead analysis | Planned | — |

## AG-001: Topology Comparison

**Hypothesis**: Hierarchical (supervisor-mediated) topology outperforms flat peer-to-peer for complex tasks, but flat wins for simple ones.

**Topologies tested**:
1. **Hierarchical**: Supervisor routes all work
2. **Flat**: Agents negotiate directly
3. **Market-based**: Task auction with bids

**Setup**:
- 20-task benchmark suite spanning complexity levels
- Measure: task success rate, latency, total tokens consumed

**Protocol**:
```bash
python experiments/agents/run_topology_comparison.py --topology hierarchical
python experiments/agents/run_topology_comparison.py --topology flat
python experiments/agents/run_topology_comparison.py --topology market
```

**Results**: TBD

## AG-002: Verifier Impact on Quality

**Hypothesis**: Separate verifier agent improves output quality by 15–25% at the cost of ~30% more latency.

**Setup**:
- Run executor-only vs. executor+verifier pipelines
- Measure: correctness on verifiable tasks, hallucination rate, latency overhead

**Results**: TBD

## AG-003: Minimum Viable Agent Set

**Hypothesis**: A 3-agent set (planner, executor, verifier) covers ≥90% of common assistant tasks.

**Setup**:
- Ablate agent roles from the full set
- Measure: task coverage and success rate per configuration

**Results**: TBD

## AG-004: Communication Overhead Analysis

**Hypothesis**: Message overhead scales super-linearly in flat topologies beyond 5 agents.

**Setup**:
- Vary agent count: 2, 3, 5, 8
- Measure: messages per task, token overhead per task

**Results**: TBD

## Methodology Notes

- All topologies use identical underlying models for fairness
- Communication cost includes prompt construction tokens
- Success criteria are pre-defined per task; no post-hoc judgment