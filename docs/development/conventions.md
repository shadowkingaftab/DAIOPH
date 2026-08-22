# Code Conventions

## Language & Style

- **Python 3.11+** with modern syntax (match statements, union types via `|`)
- **Type hints required** on all public functions
- **Docstrings** on all modules, classes, and public functions
- Line length: 88 characters (Black/Ruff default)
- Quotes: double quotes
- Imports: sorted (isort via Ruff)

## Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Modules | snake_case | `liquid_engine.py` |
| Classes | PascalCase | `LiquidEngine` |
| Functions | snake_case | `classify_intent` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Private | leading underscore | `_internal_helper` |

## Project Structure Rules

1. **One responsibility per module**: Each file has a single clear purpose
2. **Package `__init__.py`**: Exports public API only
3. **No circular imports**: Use dependency injection or events
4. **Contracts first**: New subsystems define protocols in `core/contracts/`

## Async Conventions

- I/O-bound operations are `async`
- CPU-bound inference runs in thread pools (`asyncio.to_thread`)
- Never block the event loop

```python
# Good
result = await asyncio.to_thread(model.generate, prompt)

# Bad - blocks event loop
result = model.generate(prompt)
```

## Error Handling

- Raise typed errors from `core/errors/`
- Never catch bare `Exception` without re-raising or logging
- Errors carry context (correlation IDs)

```python
from core.errors.model import ModelLoadError

raise ModelLoadError(
    f"Failed to load {model_name}",
    details={"path": model_path},
)
```

## Testing Conventions

- Test files mirror source structure: `tests/unit/test_<module>.py`
- Test classes: `Test<Feature>`
- Test methods: `test_<behavior>`
- Use fixtures from `tests/fixtures/`
- Async tests use `pytest-asyncio`

## Configuration

- All tunables go in config files, not hardcoded
- Environment variable overrides: `DAIOPH_<SECTION>_<KEY>`
- Secrets only via environment variables, never in code

## Git Conventions

- Branch naming: `feature/<name>`, `fix/<name>`, `docs/<name>`
- Commit messages: imperative mood, conventional commits style
  - `feat: add liquid adaptation controller`
  - `fix: prevent memory leak in replay buffer`
  - `docs: update federation architecture`

## Documentation

- Public APIs documented in `docs/api/`
- Architecture decisions in `docs/decisions/` (ADRs)
- Update relevant docs with behavior changes