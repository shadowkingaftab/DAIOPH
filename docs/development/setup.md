# Development Setup

## Prerequisites

- Python 3.11+ (see `.python-version`)
- Git
- Optional: CUDA-capable GPU for accelerated inference
- Optional: Node.js 18+ for web frontend development

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/shadowkingaftab/DAIOPH.git
cd DAIOPH
```

### 2. Create Virtual Environment

Using `uv` (recommended):
```bash
uv sync
```

Or with pip:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (API keys are optional for local-only mode)
```

### 4. Run Setup Script

```bash
python scripts/setup/setup.py
python scripts/setup/initialize_data.py
```

### 5. Download Models (Optional)

```bash
python scripts/setup/install_models.py
```

### 6. Start Development Server

```bash
python scripts/development/dev_server.py
```

The API is now available at `http://localhost:8000` with docs at `/docs`.

## Development Tools

### Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# With coverage
pytest --cov=. tests/
```

### Linting & Formatting

```bash
ruff check .
ruff format .
```

### Type Checking

```bash
mypy .
```

### Makefile Shortcuts

```bash
make help      # List available targets
make test      # Run tests
make lint      # Run linters
make dev       # Start dev server
```

## IDE Setup

VS Code users: recommended extensions and settings are in `.vscode/`. Open the workspace and accept the recommended extensions.

## Verify Installation

```bash
python check_libs.py   # Verify dependencies
python diagnose.py     # Run system diagnostics
```

## Troubleshooting

See [debugging.md](debugging.md) for common issues and solutions.