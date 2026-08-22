# ADR-001: Kernel-Based Architecture with Event Loop

## Status

Accepted

## Context

DAIOPH must coordinate many subsystems (intelligence, memory, learning, models, hardware) across diverse deployment targets (desktop, edge, cloud). We needed a foundation that:

1. Manages subsystem lifecycle consistently
2. Supports both interactive (chat) and background (learning, consolidation) workloads
3. Works on single-process edge devices and multi-process cloud deployments
4. Enables graceful degradation when components fail

Alternatives considered:
- **Monolithic request handler**: Simple but no lifecycle management; hard to degrade gracefully
- **Microservices from day one**: Too much operational overhead for edge devices
- **Plugin framework without kernel**: No central state or ordering guarantees

## Decision

Adopt a **kernel-based architecture** (`core/kernel/`) with:

1. **Central boot sequence** that initializes subsystems in dependency order
2. **Async event loop** as the primary execution model
3. **Lifecycle state machine**: `CREATED → BOOTING → READY → DEGRADED → SHUTTING_DOWN → STOPPED`
4. **Protocol-based contracts** (`core/contracts/protocols.py`) that all subsystems implement

```python
class Subsystem(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    def health(self) -> HealthStatus: ...
```

## Consequences

### Positive
- Uniform subsystem behavior across deployment targets
- Graceful degradation is a first-class concept (DEGRADED state)
- Testing is simplified via protocol mocks
- Edge devices run the same kernel in-process; cloud can distribute later

### Negative
- Boot order dependencies require careful management
- Single event loop can become a bottleneck (mitigated by thread pools for CPU work)
- Protocol changes require coordinated updates

### Neutral
- The kernel does not enforce distribution; it enables it when needed