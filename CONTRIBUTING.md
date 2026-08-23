# Contributing to DAIOPH

Thank you for considering a contribution! This document explains how to set up,
develop, test, and submit changes to the DAIOPH repository.

## Code of Conduct

Be respectful and constructive. Assume good faith in reviews and discussions.

## Getting Started

### Prerequisites

- **Python 3.11** (pinned in `.python-version`)
- **Git**
- [uv](https://docs.astral.sh/uv/) (recommended) or plain `pip`
- Docker (optional, for containerized runs)

### Setup

```bash
# 1. Clone
git clone https://github.com/shadowkingaftab/DAIOPH.git
cd DAIOPH

# 2. Create an environment and install dependencies
uv sync --extra dev          # preferred; uses uv.lock
# or: pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env         # then fill in GROK_API_KEY if you have one
```

> The core offline pipelines work without any API key. Cloud routes activate
> only when `GROK_API_KEY` is present.

## Development Workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature
   ```
2. Make your changes.
3. Run formatting, lint, type checks, and tests (see below).
4. Commit with a clear message (`feat:`, `fix:`, `docs:`, `refactor:`, `test:` prefixes).
5. Push and open a Pull Request using the provided
   [PR template](.github/pull_request_template.md).

## Code Style

- **Formatting/linting**: [ruff](https://docs.astral.sh/ruff/) — line length 100,
  target Python 3.11 (configured in `pyproject.toml`).
- **Type hints**: public functions should be fully annotated; the CI includes a
  type-check workflow.
- **Docstrings**: every public module, class, and function gets a docstring
  explaining purpose, arguments, returns, and raised exceptions.
- **Error handling**: use the typed hierarchy rooted at `core/errors/base.py`;
  never swallow exceptions silently.
- **Logging**: prefer structured logging over prints; never log secrets or raw
  user content.

```bash
ruff format .
ruff check .
```

## Testing

Tests live under `tests/` (unit, integration, system, end-to-end, security,
resilience). pytest is configured with `testpaths = ["tests"]`.

```bash
pytest                       # full suite
pytest tests/unit -q         # fast subset during development
pytest tests/unit/test_memory.py -q
```

Guidelines:

- Tests must run **offline** — no network, credentials, GPUs, microphones, or browsers.
- Mock external services (Grok API, model downloads); use small in-memory fixtures.
- New features need focused tests; bug fixes need a regression test first when practical.
- Deterministic behavior: seed randomness where relevant.

## What We Look For in Reviews

- Correctness and clear typing/docstrings.
- No pretend functionality: integrations that need unavailable services must raise
  explicit errors or expose dependency-injection seams — not fake success.
- Secure defaults: least privilege, validated inputs, no hardcoded secrets.
- Graceful degradation consistent with the architecture (see `ARCHITECTURE.md`).
- No unnecessary new dependencies; keep CPU-only operation possible.

## Reporting Issues

Use the GitHub issue templates:

- [Bug report](.github/ISSUE_TEMPLATE/bug_report.md)
- [Feature request](.github/ISSUE_TEMPLATE/feature_request.md)
- [Security report](.github/ISSUE_TEMPLATE/security_report.md) — see [`SECURITY.md`](SECURITY.md) for private disclosure.
- [Model issue](.github/ISSUE_TEMPLATE/model_issue.md)

## CI

Pull requests run through GitHub Actions:

| Workflow | Purpose |
|----------|---------|
| `ci.yml` | Overall integration check |
| `tests.yml` | Test suite |
| `lint.yml` | Ruff lint/format |
| `typecheck.yml` | Static type checking |
| `security.yml` | Security scanning |
| `dependency-audit.yml` | Dependency vulnerability audit |
| `docker.yml` | Container build |

All workflows must pass before merge. CODEOWNERS may request additional reviewers
for sensitive paths.

## Licensing

By contributing, you agree that your contributions are licensed under the
[Apache License 2.0](LICENSE).