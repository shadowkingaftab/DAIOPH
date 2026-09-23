# DAIOPH

**Distributed Adaptive Intelligence Orchestration Platform**

DAIOPH is a modular Python platform for routing and executing AI tasks across local models and cloud services. Its initial applications focus on intent classification, hybrid edge/cloud inference, and decomposition of multi-step prompts into executable task graphs. The repository has since grown to include supporting components for agents, tools and plugins, memory, learning, knowledge retrieval, security, resilience, and deployment.

The project is under active development. The architecture and module layout describe the intended platform scope; individual components may have different levels of implementation and integration. See [ARCHITECTURE.md](ARCHITECTURE.md) for the system design and [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md) for the original orchestration development history.

## Project progress

- Established a Python project foundation with dependency configuration and a lockfile.
- Developed four application paths spanning intent routing, hybrid task orchestration, telemetry, and offline prompt planning and refinement.
- Added modular agent, developer, filesystem, communication, and productivity tools, with a plugin framework.
- Built platform foundations for authentication, authorization, privacy, audit logging, retries, fallback, health monitoring, and recovery.
- Expanded the codebase into knowledge, learning, memory, multimodal, federated, and hardware-aware subsystems; integration and development are ongoing.

## Design overview

DAIOPH is organized around a request flow that can classify an input, select an execution route, decompose complex work, run dependent tasks, and assemble a response. Depending on the application and configuration, execution can use local inference, cloud services, or a hybrid route. The orchestration applications include:

- **Intent classifier and dashboard** (`streamlit_app.py`): routes individual requests using intent classification and presents execution telemetry.
- **Unified orchestrator** (`unified_orchestrator/app.py`): decomposes multi-step prompts and supports parallel DAG execution.
- **Smart orchestrator** (`smart_orchestrator/app.py`): combines prompt decomposition, task routing, and execution metrics.
- **Prompt bifurcation application** (`revolutionary_orchestrator/app.py`): provides a local planner, executor, and refinement workflow.

Shared platform areas are separated into modules for core runtime and contracts, models, orchestration, agents, memory, learning, knowledge, multimodal processing, tools, security, resilience, observability, hardware, APIs, and deployment. The design emphasizes modular interfaces, hardware-aware execution, privacy-conscious local processing, and explicit fallback behavior. See [ARCHITECTURE.md](ARCHITECTURE.md) for the repository map and request-flow details.

## Repository layout

- `core/`, `runtime/`, `execution/`, and `orchestration/` contain runtime, scheduling, planning, and execution foundations.
- `agents/`, `tools/`, and `plugins/` contain agent roles, permissioned tool modules, and plugin scaffolding.
- `models/`, `intelligence/`, `multi_modal/`, and `multimodal/` cover model integrations and AI capabilities.
- `memory/`, `learning/`, and `knowledge/` cover state, adaptation, indexing, retrieval, and provenance.
- `security/`, `resilience/`, and `observability/` provide cross-cutting platform services.
- `APIs/`, `apps/`, and `user_interface/` contain service and user-facing entry points.
- `configs/`, `deployment/`, `hardware/`, and `os_layer/` support configuration and deployment environments.
- `tests/`, `evaluation/`, and `benchmarks/` contain test and evaluation materials.

## Requirements

- Python 3.11 or later
- Git
- Optional: an xAI API key for cloud inference
- Optional: local model files and the runtime dependencies required by the selected local inference path

## Setup

Create and activate a virtual environment, then install the project dependencies:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS or Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set only the values needed for the chosen application. For cloud-backed inference, configure the API credential documented by the example file. Keep credentials out of source control. Local model paths and optional integrations depend on the selected workflow.

## Run an application

Launch the primary dashboard:

```bash
streamlit run streamlit_app.py
```

Other orchestration applications can be launched directly:

```bash
streamlit run unified_orchestrator/app.py
streamlit run smart_orchestrator/app.py
streamlit run revolutionary_orchestrator/app.py
```

The repository also includes API and MCP entry points; their configuration and dependencies may differ from the Streamlit applications. Docker configuration is available in `Dockerfile` and `docker-compose.yml`.

## Configuration and data

Environment examples are provided in `.env.example`, with additional profiles under `configs/`. Model availability, cloud credentials, and optional system dependencies determine which inference paths are usable in a given environment. Review the relevant application and configuration before deployment. Do not commit API keys, downloaded model weights, or user data.

## Development and evaluation

The repository includes tests, evaluation modules, and benchmarks. Their presence does not imply that every subsystem has been validated end to end. Run checks appropriate to the component and environment being changed, and report the exact scope and results when publishing measurements. Dependency configuration is maintained in `requirements.txt` and `pyproject.toml`, with `uv.lock` as the uv lockfile.

## Documentation

- [Architecture overview](ARCHITECTURE.md)
- [Implementation report](IMPLEMENTATION_REPORT.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security notes](SECURITY.md)

## Project status

DAIOPH is an actively evolving research and engineering codebase. Its orchestration applications and platform modules are developed incrementally; compatibility, integration, and operational readiness should be assessed for the specific paths in use. Claims about model quality, latency, reliability, or deployment readiness should be supported by reproducible evaluations for the relevant configuration.

## License

See [LICENSE](LICENSE).
