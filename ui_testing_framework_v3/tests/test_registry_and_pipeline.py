import asyncio
from typing import Any

from ui_testing_framework_v3.adapters.browser.stealth import register as register_stealth
from ui_testing_framework_v3.adapters.formatters.llm_test import (
    register as register_llm_formatter,
)
from ui_testing_framework_v3.adapters.generators.simple import register as register_simple
from ui_testing_framework_v3.adapters.storage.sqlite import register as register_sqlite
from ui_testing_framework_v3.application.pipeline import Pipeline
from ui_testing_framework_v3.core.value_objects import URL
from ui_testing_framework_v3.plugins.registry import registry


def _register_builtins() -> None:
    # idempotent registrations
    register_stealth(registry)
    register_llm_formatter(registry)
    register_sqlite(registry)
    register_simple(registry)


def test_registry_lists_plugins() -> None:
    _register_builtins()
    assert "stealth" in registry.list_adapters("extractor")
    assert "llm_test" in registry.list_adapters("formatter")
    assert "sqlite" in registry.list_adapters("storage")
    assert "simple" in registry.list_adapters("test_generator")


def test_pipeline_smoke_extract() -> None:
    _register_builtins()

    async def run() -> dict[str, Any]:
        p = Pipeline(registry)
        return await p.run(URL("https://example.com"))

    res: dict[str, Any] = asyncio.run(run())
    assert "formatted" in res
    assert "tests" in res
