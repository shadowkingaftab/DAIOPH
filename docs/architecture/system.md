# System Architecture

## Overview

DAIOPH (Distributed Adaptive Intelligence Operating Platform for Humans) is a modular, offline-first AI operating platform that runs on devices ranging from edge hardware to cloud infrastructure.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                       │
│  (Desktop / Web / Mobile / CLI / Streamlit)              │
├─────────────────────────────────────────────────────────┤
│                      API Layer                           │
│         (REST / WebSocket / gRPC / Events)               │
├─────────────────────────────────────────────────────────┤
│                     Core Kernel                          │
│   (Boot / Runtime / Event Loop / Lifecycle)              │
├──────────────┬──────────────┬───────────────────────────┤
│ Intelligence │    Memory    │        Learning            │
│ (Liquid,     │ (Short-term, │ (Continual, Adaptation,   │
│ Intent,      │ Episodic,    │ Feedback, Evolution)      │
│ Reasoning)   │ Semantic...) │                            │
├──────────────┴──────────────┴───────────────────────────┤
│                Models & Multi-Modal                      │
│   (Local LLMs / Remote APIs / Vision / Speech)           │
├─────────────────────────────────────────────────────────┤
│           Hardware Abstraction & OS Layer                │
│  (CPU/GPU Detection / Filesystem / Automation)           │
└─────────────────────────────────────────────────────────┘
```

## Design Principles

1. **Offline-first**: All core functionality works without network connectivity.
2. **Hardware-adaptive**: Models and behavior scale to available compute.
3. **Privacy-preserving**: Data stays on-device; federated learning uses DP.
4. **Modular**: Each subsystem communicates through well-defined contracts.
5. **Resilient**: Graceful degradation and fallback at every layer.

## Subsystem Boundaries

| Subsystem | Location | Responsibility |
|-----------|----------|----------------|
| Kernel | `core/kernel/` | Boot, runtime, event loop, lifecycle |
| Contracts | `core/contracts/` | Protocols, commands, events, messages |
| Identity | `core/identity/` | Device, user, session identity |
| Configuration | `core/configuration/` | Config loading, profiles, feature flags |
| Intelligence | `intelligence/` | Liquid engine, intent, reasoning, cognition |
| Memory | `memory/` | Short-term, episodic, semantic, procedural |
| Learning | `learning/` | Continual learning, adaptation, evolution |
| Models | `models/` | Registry, local providers, remote providers |
| Multi-modal | `multi_modal/` | Input routing, speech, vision, video |
| Agents | `agents/` | Planner, executor, monitor, verifier roles |
| Hardware | `hardware/` | Detection, CPU/GPU, energy management |
| OS Layer | `os_layer/` | Desktop, filesystem, automation |
| Federation | `federated/` | Client/server FL with privacy |
| Network | `network/` | Discovery, transport, synchronization |

## Data Flow

1. User input arrives via an interface → API layer.
2. Kernel event loop dispatches to the intelligence subsystem.
3. Intent classification determines the action required.
4. Reasoning/planning decomposes complex tasks.
5. Models generate responses (local-first routing).
6. Memory records interactions for future learning.
7. Feedback loops update adaptation strategies.

See individual architecture documents for details on each subsystem.