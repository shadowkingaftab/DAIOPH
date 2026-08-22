# Debugging Guide

## Diagnostic Tools

### System Diagnostics
```bash
python diagnose.py        # Full system diagnostic
python check_libs.py      # Verify dependencies
python scripts/maintenance/health_check.py
```

### Structured Logging

Logs use structured JSON format (`observability/logging/structured.py`):

```json
{
  "timestamp": "2026-08-22T01:00:00Z",
  "level": "ERROR",
  "logger": "intelligence.liquid",
  "message": "Adaptation failed",
  "correlation_id": "req-abc123",
  "extra": {"strategy": "plasticity_boost"}
}
```

Enable debug logging:
```bash
export DAIOPH_LOG_LEVEL=debug
```

### Tracing

Distributed tracing via `observability/tracing/tracer.py`:
- Every request gets a correlation ID
- Spans track: intent → planning → inference → response
- Export spans to your tracing backend

### Metrics

Prometheus-compatible metrics at `:9090` (`observability/metrics/metrics.py`):
- `daioph_request_latency_seconds`
- `daioph_model_inference_seconds`
- `daioph_memory_operations_total`
- `daioph_learning_updates_total`

## Common Issues

### Model fails to load
```
ERROR: ModelLoadError: Failed to load qwen-0.5b
```
- Check disk space: `df -h data/models`
- Verify model cache: `ls data/models/`
- Re-download: `python scripts/setup/install_models.py`
- Check RAM: model may exceed available memory

### Slow inference
- Check hardware profile: `GET /api/device/profile`
- Verify quantization is enabled for CPU
- Check thermal throttling: `hardware/resource_monitor.py`
- Run benchmark: `python scripts/benchmarking/run_benchmarks.py`

### Memory subsystem errors
- Check database integrity: `sqlite3 data/dev.db "PRAGMA integrity_check;"`
- Run migrations: `python migrations/database/migration_runner.py`
- Inspect event store for corruption

### Event loop blocked
Symptom: API becomes unresponsive intermittently.
- Look for sync I/O in async code paths
- Check for CPU-bound work outside `asyncio.to_thread`
- Profile: `py-spy dump --pid <PID>`

### Federated learning not participating
- Verify server URL in `configs/federated/client.yaml`
- Check battery/WiFi eligibility conditions
- Review privacy budget: accountant may have exhausted ε

## Debug Mode

```bash
DAIOPH_MODE=development python -m uvicorn APIs.rest.app:app --reload
```

Debug mode enables:
- Verbose logging
- Auto-reload on code changes
- Detailed error tracebacks in API responses

## State Inspection

```python
# Inspect intelligence state
from intelligence.state.state_manager import StateManager
sm = StateManager()
print(sm.snapshot())

# Inspect memory
from memory.episodic.episodic_memory import EpisodicMemory
em = EpisodicMemory()
for ep in em.recent(10):
    print(ep)
```

## Getting Help

1. Check logs with correlation ID
2. Run `python diagnose.py` and include output
3. Search existing issues on GitHub
4. Open an issue with the bug report template