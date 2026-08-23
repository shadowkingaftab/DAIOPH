# ═══════════════════════════════════════════════════════════════════════════
# Makefile — DAIOPH developer commands
#
# Every target maps to a real script/config in this repository.
# Run `make` or `make help` to list them.
#
# Note for Windows users: use `make` via WSL, Git Bash, or choco-make;
# each target is a single plain command you can also run directly.
# ═══════════════════════════════════════════════════════════════════════════

.PHONY: help install install-pip lock \
        run-dashboard run-unified run-smart run-revolutionary \
        test test-unit test-integration lint format \
        docker-build docker-up docker-down \
        train-classifier clean

# ── Default ────────────────────────────────────────────────────────────────
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Environment ────────────────────────────────────────────────────────────
install: ## Install dependencies + dev tools from the lockfile (uv)
	uv sync --extra dev

install-pip: ## Install dependencies with plain pip (no uv)
	pip install -r requirements.txt

lock: ## Regenerate uv.lock after changing pyproject.toml dependencies
	uv lock

# ── Run the four orchestration frameworks (Streamlit) ──────────────────────
run-dashboard: ## Framework 1: intent classifier dashboard (production default)
	streamlit run streamlit_app.py

run-unified: ## Framework 2: unified hybrid DAG orchestrator
	streamlit run unified_orchestrator/app.py

run-smart: ## Framework 3: smart decomposition + telemetry router
	streamlit run smart_orchestrator/app.py

run-revolutionary: ## Framework 4: fully offline LLMCompiler + self-refine
	streamlit run revolutionary_orchestrator/app.py

# ── Quality gates (configured in pyproject.toml) ───────────────────────────
test: ## Run the full pytest suite (tests/ per pyproject testpaths)
	pytest

test-unit: ## Run only the fast unit tests
	pytest tests/unit -q

test-integration: ## Run integration tests
	pytest tests/integration -q

lint: ## Ruff lint check (line length 100, py311)
	ruff check .

format: ## Auto-format code with ruff
	ruff format .

# ── Docker (root Dockerfile + docker-compose.yml) ──────────────────────────
docker-build: ## Build the production container image
	docker compose build

docker-up: ## Build and start the dashboard at http://localhost:8501
	docker compose up --build

docker-down: ## Stop and remove containers
	docker compose down

# ── Classifier fine-tuning (training/train_classifier.py) ──────────────────
train-classifier: ## Fine-tune the intent classifier on training/domain_dataset.json
	python training/train_classifier.py --epochs 5 --eval

# ── Housekeeping ───────────────────────────────────────────────────────────
clean: ## Remove Python caches and build artifacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete