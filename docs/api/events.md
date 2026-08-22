# Event System

## Overview

DAIOPH uses an internal event bus (`APIs/events/event_bus.py`) for decoupled communication between subsystems. Events are typed, ordered, and optionally persisted.

## Event Structure

Defined in `core/contracts/events.py`:

```python
@dataclass
class Event:
    id: str
    type: str
    source: str
    timestamp: datetime
    payload: dict
    correlation_id: str | None = None
```

## Event Categories

### Lifecycle Events
| Event | Emitted When |
|-------|--------------|
| `system.booting` | Kernel starts boot sequence |
| `system.ready` | All subsystems ready |
| `system.degraded` | Partial failure detected |
| `system.shutdown` | Shutdown initiated |

### Interaction Events
| Event | Emitted When |
|-------|--------------|
| `input.received` | User input arrives |
| `intent.classified` | Intent determined |
| `response.generated` | Response ready |
| `feedback.received` | User feedback captured |

### Model Events
| Event | Emitted When |
|-------|--------------|
| `model.loading` / `model.loaded` | Model lifecycle |
| `model.inference.start` / `.end` | Inference timing |
| `model.fallback` | Fallback chain activated |

### Memory Events
| Event | Emitted When |
|-------|--------------|
| `memory.stored` | New memory written |
| `memory.consolidated` | Consolidation pass complete |
| `memory.forgotten` | Memory pruned |

### Learning Events
| Event | Emitted When |
|-------|--------------|
| `learning.update.applied` | Model update deployed |
| `learning.update.rolled_back` | Regression detected |
| `federated.round.completed` | FL round finished |

## Subscribing

```python
from APIs.events.event_bus import EventBus

bus = EventBus()

async def on_response(event):
    print(f"Response: {event.payload}")

bus.subscribe("response.generated", on_response)
```

Pattern subscriptions use wildcards:
```python
bus.subscribe("model.*", on_model_event)
```

## Publishing

```python
await bus.publish(Event(
    type="memory.stored",
    source="memory.episodic",
    payload={"id": "ep-123", "importance": 0.7},
))
```

## Delivery Guarantees

- **At-most-once** for transient subscribers (default)
- **Persistent events** (interaction, learning) are journaled to the event store for replay
- Ordering is guaranteed per-source, not globally

## Event Sourcing

Critical state changes are stored as events, enabling:
- State reconstruction via replay (`intelligence/state/state_recovery.py`)
- Audit trails
- Debugging time-travel