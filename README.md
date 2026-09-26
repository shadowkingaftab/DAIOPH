<div align="center">
  <img src="assets/readme-banner.svg" alt="DAIOPH — Local-first AI, built to think, route, and act" width="100%" />
</div>

<div align="center">
  <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img alt="Local-first AI" src="https://img.shields.io/badge/AI-Local--first-0891B2?style=flat-square" />
  <img alt="Active development" src="https://img.shields.io/badge/Status-Active%20development-7C3AED?style=flat-square" />
</div>

<br />

**DAIOPH (Distributed Adaptive Intelligence Operating Platform)** is a Python platform for coordinating AI work across local models and cloud services. It brings together intent routing, task planning, agent execution, and supporting services for memory, learning, tools, and system resilience.

The project began with edge inference and hybrid orchestration. Its current architecture extends that foundation into a modular platform, while individual subsystems continue to mature and integrate.

> **Research and development status** · Active development. Capabilities vary by module and application; the architecture describes the platform direction, and should not be read as a claim that every component is production-ready.

## Progress at a glance

- Set up the Python project foundation, dependency management, and application entry points.
- Developed four orchestration applications, from intent routing to task graphs and local planning with refinement.
- Added role-based agents, a tool framework, and plugin scaffolding.
- Built security and reliability foundations, including access control, privacy, auditing, retries, fallback, and recovery.
- Extended the platform into memory, knowledge retrieval, learning, multimodal processing, federation, and hardware adaptation.

## Architecture

Requests move through a simple idea: **understand → plan → execute → assemble**. Depending on the workflow and available configuration, execution can use local inference, cloud services, or a hybrid route.

```mermaid
flowchart LR
    U[Apps and interfaces] --> A[API layer]
    A --> O[Orchestration and agents]
    O --> P[Planning and task DAG]
    P --> X[Hybrid execution]
    X --> M[Local or remote models]
    M --> S[Result synthesis]
    S --> U
    O -.-> C[Core runtime and contracts]
    X -.-> R[Security and resilience]
    O -.-> K[Memory, learning, and knowledge]
    X -.-> T[Telemetry and evaluation]
    X -.-> H[Hardware and OS layer]
    classDef interface fill:#0E7490,color:#fff,stroke:#67E8F9,stroke-width:2px
    classDef orchestration fill:#4338CA,color:#fff,stroke:#A5B4FC,stroke-width:2px
    classDef execution fill:#6D28D9,color:#fff,stroke:#C4B5FD,stroke-width:2px
    classDef support fill:#164E63,color:#fff,stroke:#22D3EE,stroke-width:1px
    class U,A interface
    class O,P orchestration
    class X,M,S execution
    class C,R,K,T,H support
```

Core design themes are local-first inference where supported, adaptive routing, modular subsystem contracts, resilient execution, and explicit reporting of integration requirements.

## Choose an application

| Workflow | Entry point | What it explores |
|---|---|---|
| Intent routing | `streamlit_app.py` | Classify prompts, select a route, and inspect execution telemetry. |
| Unified orchestration | `unified_orchestrator/app.py` | Decompose multi-step work and coordinate parallel tasks. |
| Smart orchestration | `smart_orchestrator/app.py` | Combine decomposition, routing, and task metrics. |
| Prompt bifurcation | `revolutionary_orchestrator/app.py` | Explore local planning, execution, and refinement. |

The repository also contains REST, WebSocket, event, and gRPC API areas; Streamlit, CLI, web, desktop, and mobile application modules; and an MCP server entry point. Some are evolving or scaffolded surfaces.

## Quick start

**Requirements:** Python 3.11+, plus any model files and optional services required by your chosen workflow.

```bash
python -m venv .venv
```

Activate the environment and install dependencies:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`. Set `GROK_API_KEY` for Grok-backed inference; local Qwen settings are also described in the example. Then launch the primary dashboard:

```bash
streamlit run streamlit_app.py
```

Other orchestration apps can be started with `streamlit run <entry-point>`. Docker files are provided in `Dockerfile` and `docker-compose.yml`.

<details>
<summary><strong>Explore the codebase</strong></summary>

- **Runtime & orchestration:** `core/`, `runtime/`, `execution/`, `orchestration/`
- **Agents & extensions:** `agents/`, `tools/`, `plugins/`
- **Models & intelligence:** `models/`, `intelligence/`, `liquid_core/`
- **Context & adaptation:** `memory/`, `knowledge/`, `learning/`, `federated/`
- **Modalities & environment:** `multi_modal/`, `multimodal/`, `hardware/`, `os_layer/`, `network/`
- **Trust & evaluation:** `security/`, `resilience/`, `observability/`, `evaluation/`, `benchmarks/`, `tests/`
- **Interfaces & operations:** `APIs/`, `apps/`, `user_interface/`, `configs/`, `deployment/`

</details>

## Development notes

Dependencies are listed in `requirements.txt` and `pyproject.toml`; `uv.lock` records the uv lock state. Test, evaluation, and benchmark resources are included, but coverage and integration differ across subsystems. When sharing performance or quality results, report the exact application, model, configuration, and evaluation procedure.

## Project links

[Super README / complete project guide](docs/PROJECT_GUIDE.md) · [Architecture](ARCHITECTURE.md) · [Implementation report](IMPLEMENTATION_REPORT.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [License](LICENSE)
