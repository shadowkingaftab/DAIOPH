# Agents Research

## Overview

Research on multi-agent collaboration patterns for DAIOPH: role specialization, communication topologies, and coordination efficiency.

## Research Questions

1. Which agent topology (hierarchical, flat, market-based) is most efficient for assistant tasks?
2. How much does verifier/critic separation improve output quality?
3. What is the minimum viable agent set for common task categories?
4. How do agents coordinate without excessive message overhead?

## Key Components Under Study

- `agents/base/agent.py` — base agent contract
- `agents/supervisor/` — orchestration topology
- `agents/verifier/` — output validation
- `agents/monitor/agent.py` — health tracking
- `execution/dag_generator.py` — plan-to-DAG mapping

## Related Documentation

- Architecture: `docs/architecture/agents.md`
- Architecture: `docs/architecture/orchestration.md`
- Experiments: [experiments.md](experiments.md)

## Getting Started

```bash
python experiments/agents/run_topology_comparison.py --topology hierarchical
```

## Contributing

Topology experiments should report both quality metrics and communication cost (messages, tokens).