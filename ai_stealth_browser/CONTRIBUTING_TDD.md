# TDD & Contribution Guide

This project enforces Red → Green → Refactor for every feature.

## Workflow

1. Write (or extend) a failing test describing desired behavior.
2. Implement the minimal code to pass.
3. Refactor safely (no behavior change) while tests stay green.
4. Commit with scope + short imperative message.

## Agent Testing (pydantic-ai)

Use `TestModel` to avoid real LLM calls:

```python
from pydantic_ai.models.test import TestModel
from agents.registry import stealth_agent

async def test_stealth_agent_min_schema():
    with stealth_agent.override(model=TestModel(responses=[{"risk_level":"low","actions":[],"justification":"n/a"}])):
        result = await stealth_agent.run("Analyze", deps=None)
        assert result.output.risk_level == "low"
```

Capture messages:

```python
from pydantic_ai import capture_run_messages
with capture_run_messages() as msgs:
    ...
```

## Commands

Use `uv` for everything:

```bash
uv sync
uv run pytest -q
uv run ruff check .
uv run mypy .
```

## Design Patterns Mapping

- Strategy: extraction strategies (future `extraction/strategies/`).
- Facade: `core/facade.py` (high-level orchestration entry point).
- Observer: `core/events.py` EventBus.
- Command: navigation / extraction operations.
- Adapter: temporary shims from monolith to modular APIs.

## PR Quality Gate

- All tests passing.
- No newly introduced ruff errors.
- mypy clean (no `Any` leaks for new code unless justified in docstring).
- Updated docs if public surface changed.

## Naming

- Modules: `snake_case`.
- Pydantic models: `PascalCase`.
- Commands: `<Verb><Noun>Command`.

## Partial Extraction Policy

When moving code out of `stealth_browser.py`:

- Create new module.
- Import back into monolith to preserve API.
- Add `# EXTRACTED: <module>` comment near removed section.

## Future Enhancements

- Introduce property-based tests for extraction scoring.
- Add mutation tests for detection risk analysis.
