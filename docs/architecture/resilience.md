# Resilience Architecture

## Overview

DAIOPH is designed to degrade gracefully rather than fail catastrophically. The resilience layer provides fallbacks, recovery, and chaos-tested reliability.

## Principles

1. **Never lose user data**: Writes are journaled before processing
2. **Degrade, don't fail**: Reduced functionality beats no functionality
3. **Self-healing**: Automatic recovery from transient failures
4. **Observable failures**: All failures are logged and metricized

## Fallback Strategies (`execution/fallback_manager.py`)

### Model Fallback Chain
```
Primary local model
  → Alternative local model
    → Quantized/smaller model
      → Remote API (if online)
        → Cached/template response
```

### Component Fallbacks
- Vector store unavailable → linear scan fallback
- FAISS unavailable → brute-force similarity
- Postgres unavailable → SQLite fallback
- GPU unavailable → CPU inference

## Recovery Patterns

### Retry with Backoff
- Exponential backoff: 1s, 2s, 4s, 8s (max 5 attempts)
- Jitter to prevent thundering herds

### Circuit Breaker
- Opens after N consecutive failures
- Half-open state probes recovery
- Prevents cascade failures

### Checkpoint/Resume
- Long-running pipelines checkpoint progress
- Resume from last checkpoint after restart
- State snapshots in `intelligence/state/state_snapshot.py`

### State Recovery (`intelligence/state/state_recovery.py`)
- Automatic state restoration on boot
- Detects corrupted state → rebuilds from events
- Event sourcing enables replay-based recovery

## Health Monitoring

### Monitor Agent (`agents/monitor/agent.py`)
- Continuous subsystem health checks
- Escalation to supervisor on degradation
- Automatic restart of failed components

### Health Endpoints
- `/health`: Liveness (is the process running?)
- `/ready`: Readiness (can we serve requests?)

## Chaos Testing (`tests/resilience/`)

Resilience is validated through:
- **Fallback tests**: Verify each fallback activates correctly
- **Recovery tests**: Verify state restoration after crashes
- **Chaos tests**: Random component failure injection

## Degradation Levels

| Level | Behavior |
|-------|----------|
| Full | All features operational |
| Degraded | Non-critical features disabled |
| Minimal | Core chat only, small models |
| Offline | No remote calls, cached responses |

The system automatically moves between levels based on resource availability and error rates.