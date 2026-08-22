# Distributed AI Research

## Overview

Research on distributing DAIOPH across multiple devices and nodes: peer discovery, distributed memory, synchronized execution, and conflict resolution.

## Research Questions

1. How should state be partitioned across devices (user-owned vs. shared)?
2. What consistency model suits assistant workloads (eventual, causal)?
3. How do peers resolve conflicting memories or preferences?
4. Can inference be split across devices (pipeline/tensor parallelism at the edge)?

## Key Components Under Study

- `network/discovery/discovery.py` — peer discovery
- `network/peer/peer_manager.py` — peer lifecycle
- `network/synchronization/synchronizer.py` — state sync
- `network/synchronization/conflict_resolution.py` — merge strategies
- `network/distributed/distributed_memory.py` — shared memory
- `network/distributed/distributed_execution.py` — cross-device execution

## Related Documentation

- Architecture: `docs/architecture/system.md`
- Experiments: [experiments.md](experiments.md)

## Getting Started

```bash
python experiments/federated/run_distributed_memory_test.py --peers 3
```

## Contributing

Distributed experiments must document network conditions (latency, bandwidth, packet loss) as they strongly influence results.