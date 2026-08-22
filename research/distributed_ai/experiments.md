# Distributed AI Experiments

## Experiment Log

| ID | Date | Experiment | Status | Result |
|----|------|-----------|--------|--------|
| DA-001 | 2026-08 | State partitioning strategies | Planned | — |
| DA-002 | 2026-08 | Consistency model comparison | Planned | — |
| DA-003 | 2026-08 | Conflict resolution effectiveness | Planned | — |
| DA-004 | 2026-08 | Cross-device inference splitting | Planned | — |

## DA-001: State Partitioning Strategies

**Hypothesis**: User-owned partitioning (each device owns its memories) outperforms shared-state for privacy and conflict avoidance.

**Strategies tested**:
1. **User-owned**: Each device owns its data; sync only preferences
2. **Shared memory**: All memories replicated across peers
3. **Hybrid**: Episodic local, semantic shared

**Metrics**: sync traffic, conflict rate, privacy exposure, query latency.

**Results**: TBD

## DA-002: Consistency Model Comparison

**Hypothesis**: Eventual consistency suffices for assistant workloads; causal consistency adds value only for multi-device task handoff.

**Setup**:
- Simulate 3 devices with intermittent connectivity
- Inject concurrent writes; measure divergence and resolution time
- Compare: eventual, causal, read-your-writes

**Results**: TBD

## DA-003: Conflict Resolution Effectiveness

**Hypothesis**: CRDT-based resolution preserves user intent better than last-write-wins for preference conflicts.

**Setup**:
- Generate conflicting preference updates across devices
- Compare: LWW, CRDT merge, user-prompted resolution
- Measure: user satisfaction (simulated), data loss rate

**Results**: TBD

## DA-004: Cross-Device Inference Splitting

**Hypothesis**: Pipeline parallelism across a phone + desktop pair reduces latency for large models vs. phone-only inference.

**Setup**:
- Split model layers: phone (first N layers) + desktop (rest)
- Measure: end-to-end latency vs. local-only, network sensitivity
- Vary network latency: 5ms, 20ms, 50ms

**Results**: TBD

## Methodology Notes

- Network conditions simulated with tc/netem profiles
- All experiments run with 3+ device configurations
- Privacy exposure measured as bytes of user data leaving device