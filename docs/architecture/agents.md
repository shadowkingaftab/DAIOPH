# Agents Architecture

## Overview

DAIOPH uses a multi-agent architecture where specialized agents collaborate to accomplish complex tasks. All agents inherit from a common base class.

## Base Agent (`agents/base/`)

### Agent (`agent.py`)
Abstract base class providing:
- Lifecycle management (initialize, run, shutdown)
- Message handling interface
- State persistence hooks

### State (`state.py`)
Agent state representation:
- Current status (idle, working, waiting, error)
- Task queue and history
- Resource usage tracking

### Goal (`goal.py`)
Goal specification:
- Objective description
- Success criteria
- Constraints and deadlines
- Priority levels

### Memory (`memory.py`)
Per-agent memory interface:
- Short-term scratch space
- Access to shared memory subsystems

## Agent Roles

| Agent | Location | Responsibility |
|-------|----------|----------------|
| Supervisor | `agents/supervisor/` | Orchestrate other agents |
| Planner | `agents/planner/` | Create execution plans |
| Executor | `agents/executor/` | Run tasks |
| Monitor | `agents/monitor/` | Track health and progress |
| Verifier | `agents/verifier/` | Validate outputs |
| Researcher | `agents/researcher/` | Information gathering |
| Coder | `agents/coder/` | Code generation tasks |
| Analyst | `agents/analyst/` | Data analysis |

## Communication

Agents communicate via:
1. **Direct messages**: Point-to-point request/response
2. **Event bus**: Broadcast notifications
3. **Shared memory**: Blackboard pattern for results

## Agent Lifecycle

```
IDLE → ASSIGNED → WORKING → COMPLETED
  ↑                  │
  └──── FAILED ←─────┘
```

## Scaling Considerations

On edge devices:
- Agents run in-process (no separate processes)
- Lightweight agent implementations
- Optional agent roles can be disabled

On cloud:
- Agents may be distributed across workers
- Queue-based task distribution