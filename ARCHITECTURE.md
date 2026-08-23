# DAIOPH Architecture

**DAIOPH** — *Distributed Adaptive Intelligence Operating Platform* — is a modular,
offline-first AI platform that orchestrates prompt workflows across **local edge
models** (Qwen2-0.5B / Qwen-1.8B GGUF via llama.cpp) and **cloud models**
(xAI Grok API), with graceful cloud-to-local fallback at every layer.

This document is the top-level overview. Detailed per-subsystem notes live in
[`docs/architecture/`](docs/architecture/) and decision records in
[`docs/decisions/`](docs/decisions/).

---

## High-Level Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                          │
│   (Streamlit dashboards / Web / Desktop / CLI / Mobile)      │
├─────────────────────────────────────────────────────────────┤
│                       API Layer                              │
│        (REST / WebSocket / Events / gRPC scaffold)           │
├─────────────────────────────────────────────────────────────┤
│                    Orchestration & Agents                    │
│  (Planning → DAG execution → Hybrid routing → Synthesis)     │
├─────────────────────────────────────────────────────────────┤
│                      Core Kernel                             │
│    (Boot / Runtime / Event loop / Lifecycle / Scheduler)     │
├───────────────┬────────────────┬────────────────────────────┤
│  Intelligence │     Memory     │         Learning           │
│  (Liquid,     │ (Short-term,   │ (Continual, Adaptation,    │
│  Intent,      │ Episodic,      │ Feedback, Evolution)       │
│  Reasoning)   │ Semantic…)     │                            │
├───────────────┴────────────────┴────────────────────────────┤
│                 Models & Multi-Modal                         │
│   (Local GGUF providers / Remote APIs / Vision / Speech)     │
├─────────────────────────────────────────────────────────────┤
│          Knowledge, Security, Resilience, Observability      │
├─────────────────────────────────────────────────────────────┤
│            Hardware Abstraction & OS Layer                   │
│   (CPU/GPU detection / Filesystem / Automation / Tools)      │
└─────────────────────────────────────────────────────────────┘
```

## Design Principles

1. **Offline-first** — planning, execution, and self-refinement run fully on CPU;
   the cloud is an optimization, never a requirement.
2. **Hardware-adaptive** — model scale, thread counts, and quantization adjust to
   detected compute; capabilities are *detected*, never assumed.
3. **Privacy-preserving** — data stays on-device by default; optional federation
   layers use differential privacy and secure aggregation.
4. **Modular contracts** — subsystems communicate through typed protocols in
   `core/contracts/` rather than direct coupling.
5. **Resilient** — retry with backoff, circuit breakers, checkpoints, rollback,
   and graceful degradation at every boundary.
6. **Honest capability reporting** — integrations that require unavailable
   services raise explicit errors or expose injection seams; nothing fakes success.

## Repository Map

| Path | Responsibility |
|------|----------------|
| `core/` | Kernel (boot, runtime, event loop, lifecycle), contracts, identity, configuration, Grok client, hybrid orchestration |
| `intelligence/` | Liquid engine, intent classification, reasoning, cognition, state management |
| `memory/` | Short-term, episodic, semantic, procedural, preference stores; consolidation; privacy |
| `learning/` | Continual learning, adaptation, feedback, training utilities, evolution |
| `models/` | Model registry, local providers (Qwen/Llama/Whisper/vision), remote providers (Grok/OpenAI), optimization, lifecycle |
| `liquid_core/` | Adaptive scaling, continual learning, federated aggregation around the liquid engine |
| `multi_modal/`, `multimodal/` | Input routing, speech, vision, video, documents, sensors, fusion |
| `agents/` | Role agents: planner, executor, coder, analyst, researcher, monitor, supervisor, verifier |
| `orchestration/` | Agent runtime, planning/DAG, execution engines, hybrid routing, result synthesis |
| `execution/` | DAG generation, task scheduling, fallback management, result aggregation |
| `runtime/` | Acceleration backends, hardware profiling, platform adapters, resource managers |
| `hardware/` | Hardware detection, CPU/GPU modules, energy manager, resource monitor |
| `os_layer/` | Desktop integration, filesystem management, application control, automation |
| `knowledge/` | Ingestion, indexing, ontology, provenance, retrieval |
| `security/` | Authentication, authorization, encryption, sandboxing, secrets, threat detection, audit |
| `resilience/` | Retry, circuit breakers, fallbacks, health monitoring, chaos testing, recovery |
| `federated/` | Client/server federated learning with differential privacy |
| `network/` | Peer discovery, transport, synchronization, distributed execution |
| `observability/` | Structured logging, correlation IDs, metrics, tracing, telemetry privacy |
| `evaluation/` | Intelligence, learning, model, multimodal, orchestration, security benchmarks |
| `APIs/` | REST app, WebSocket server, event bus, schemas |
| `apps/` | Streamlit, CLI, desktop, web, mobile frontends |
| `tools/` | Permissioned tool registry: filesystem, web, developer, productivity, communication, system |
| `plugins/` | Official plugin manifests/scaffolds and community plugin docs |
| `configs/` | Environment profiles (development/testing/production/edge/federated) |
| `deployment/` | Docker, Kubernetes/Helm, Terraform, edge installers |
| `tests/` | Unit, integration, system, end-to-end, security, resilience suites |

## Request Data Flow

1. Input arrives via a UI (`streamlit_app.py`, REST API, or CLI).
2. The intent classifier routes the request: **edge**, **cloud**, or **hybrid**.
3. Complex prompts are decomposed into task DAGs (`orchestration/planning/`).
4. Tasks execute in parallel where dependencies allow
   (`orchestration/execution/`), each routed by policy (`orchestration/hybrid/`).
5. Cloud failures degrade to local engines via retry + fallback managers.
6. Results are synthesized, validated, and returned with telemetry
   (latency, routing distribution, retries) attached.
7. Interactions are recorded to memory for future adaptation and learning.

## Key Entry Points

| Entry point | Description |
|-------------|-------------|
| `streamlit_app.py` | Framework 1: intent classifier dashboard (production default) |
| `unified_orchestrator/app.py` | Framework 2: hierarchical parallel DAG orchestrator |
| `smart_orchestrator/app.py` | Framework 3: decomposition + telemetry router |
| `revolutionary_orchestrator/app.py` | Framework 4: fully offline LLMCompiler + self-refine |
| `mcp_server.py` | Model Context Protocol server for external agent discovery |
| `APIs/rest/app.py` | REST API surface (edge deployment mode) |

## Cross-Cutting Concerns

- **Configuration**: layered profiles under `configs/` merged by `core/configuration/`.
- **Errors**: typed hierarchy rooted in `core/errors/base.py`.
- **Observability**: correlation IDs flow from API entry to every log/metric/span;
  user content is redacted before export (`observability/telemetry/privacy_filter.py`).
- **Security**: least-privilege tool permissions, sandbox policies, audit events;
  see [`SECURITY.md`](SECURITY.md).