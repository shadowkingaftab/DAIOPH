# Changelog

All notable changes to DAIOPH are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Fill out the orchestration/agent runtime modules (`orchestration/`, `agents/`).
- REST/WebSocket API hardening and schema coverage (`APIs/`).
- Security subsystem completion: authn/authz, sandbox policies, audit store.
- Resilience suite: circuit breakers, checkpoints, chaos harnesses.
- Multimodal capability-gated pipeline (`multimodal/`).

## [0.1.0] — 2026-05-31

Initial public baseline of the Edge AI Intent Classifier & Orchestration Ecosystem.

### Added

#### Orchestration frameworks

- **Framework 1** — `streamlit_app.py`: deterministic zero-shot intent classifier
  dashboard routing single prompts between edge (Qwen GGUF) and cloud (Grok API).
- **Framework 2** — `unified_orchestrator/`: hierarchical parallel DAG orchestrator
  with NLTK sentence parsing, coreference mapping, and Graphviz DAG visualization.
- **Framework 3** — `smart_orchestrator/`: template-based Bartender decomposition
  with live task metrics and telemetry routing.
- **Framework 4** — `revolutionary_orchestrator/`: fully offline LLMCompiler-style
  planner–executor–refiner pipeline sharing a single local model context.

#### Core capabilities

- Multi-stage task decomposition (tokenization, coreference resolution, clustering)
  with dynamic DAG parallel execution.
- Cloud-to-local fallback with exponential backoff retry (1s → 2s → 4s) and
  automatic ODA→Cloud route switching.
- Dual-role LLMCompiler & Self-Refine pipelines running 100% offline on CPU.
- Model Context Protocol (MCP) server (`mcp_server.py`) for external agent discovery.
- Intent classifier fine-tuning pipeline over `typeform/distilbert-base-uncased-mnli`
  via `training/train_classifier.py` and `training/domain_dataset.json`.

#### Dashboard & UX

- Production telemetry dashboard: success rates, execution latencies, prompt logs,
  routing distributions (Plotly + Pandas).
- Colorful DAG visualization (green=edge, gold=cloud, blue=hybrid, red=failed)
  with node tooltips.
- Multi-language support: auto-detection of Hindi, Spanish, French, German, Arabic
  with translation for edge/hybrid routes; language badge in the UI.
- PDF image OCR preview, time-comparison timer, retry statistics, explain mode,
  example prompt dropdown, premium dark glassmorphism UI.

#### Infrastructure

- Docker multi-stage build (~600 MB production image) with non-root user,
  health checks, and docker-compose deployment with persistent model volume.
- Streamlit Community Cloud optimizations: lazy model loading, import-error
  fallbacks to Grok, thread-safe sequential local inference.
- Environment configuration via `.env.example` (`GROK_API_KEY`,
  `CLASSIFIER_MODEL_PATH`) and hardware tuning knobs (`QWEN_QUANT`, `QWEN_THREADS`,
  `QWEN_GPU_LAYERS`, `QWEN_CTX`).

[Unreleased]: https://github.com/shadowkingaftab/DAIOPH/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/shadowkingaftab/DAIOPH/releases/tag/v0.1.0