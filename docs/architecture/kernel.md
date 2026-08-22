# Kernel Architecture

## Overview

The kernel is the heart of DAIOPH. It manages the boot sequence, runtime state, event loop, and lifecycle of all subsystems.

## Components

### Boot (`core/kernel/boot.py`)
- Loads configuration from profiles and environment
- Initializes identity (device, user, session)
- Wires subsystems together in dependency order
- Performs health checks before declaring readiness

### Runtime (`core/kernel/runtime.py`)
- Holds references to all active subsystem instances
- Provides a service locator pattern for dependency access
- Manages runtime state transitions

### Event Loop (`core/kernel/event_loop.py`)
- Asynchronous event processing pipeline
- Priority queues for critical vs. background events
- Backpressure handling when overloaded

### Lifecycle (`core/kernel/lifecycle.py`)
- State machine: `CREATED → BOOTING → READY → DEGRADED → SHUTTING_DOWN → STOPPED`
- Hooks for pre/post transitions
- Graceful degradation on partial failures

### Shutdown (`core/kernel/shutdown.py`)
- Ordered teardown of subsystems (reverse of boot order)
- Flushes pending writes to persistent storage
- Emits final metrics and logs

## Boot Sequence

```
1. Load configuration (defaults → profile → environment overrides)
2. Initialize logging and observability
3. Detect hardware capabilities
4. Initialize identity providers
5. Start memory subsystems
6. Load model registry
7. Start intelligence engines
8. Bind API endpoints
9. Mark system READY
```

## Contracts

All subsystems implement protocols defined in `core/contracts/protocols.py`:

```python
class Subsystem(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    def health(self) -> HealthStatus: ...
```

## Error Handling

Errors are categorized in `core/errors/`:
- `runtime.py`: Kernel-level failures
- `execution.py`: Task execution failures
- `model.py`: Model loading/inference failures
- `memory.py`: Memory subsystem failures
- `security.py`: Security violations

Each error type has a defined recovery strategy handled by the resilience layer.