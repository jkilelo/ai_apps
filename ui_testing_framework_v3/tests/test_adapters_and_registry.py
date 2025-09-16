import asyncio

import pytest

from ui_testing_framework_v3.adapters.browser.stealth import (
    StealthBrowserExtractor,
)
from ui_testing_framework_v3.adapters.browser.stealth import (
    register as register_stealth,
)
from ui_testing_framework_v3.adapters.formatters.llm_test import (
    LLMTestFormatter,
)
from ui_testing_framework_v3.adapters.formatters.llm_test import (
    register as register_llm,
)
from ui_testing_framework_v3.adapters.generators.simple import (
    SimpleTestGenerator,
)
from ui_testing_framework_v3.adapters.generators.simple import (
    register as register_gen,
)
from ui_testing_framework_v3.application.pipeline import Pipeline
from ui_testing_framework_v3.core.value_objects import URL
from ui_testing_framework_v3.plugins.registry import (
    AdapterNotFoundError,
    NoAdapterForPortError,
    PluginRegistry,
    registry,
)


def test_registry_errors() -> None:
    r = PluginRegistry()
    # No adapters for port
    with pytest.raises(NoAdapterForPortError):
        r.get("extractor")
    # Register one and request non-existent name
    r.register("extractor", StealthBrowserExtractor, name="stealth")
    with pytest.raises(AdapterNotFoundError):
        r.get("extractor", "missing")


def test_adapter_classes_basic() -> None:
    # Create a registry and register adapters
    test_registry = PluginRegistry()
    test_registry.register("extractor", StealthBrowserExtractor, name="stealth")
    test_registry.register("formatter", LLMTestFormatter, name="llm_test")
    test_registry.register("test_generator", SimpleTestGenerator, name="simple")

    async def run() -> dict[str, object]:
        p = Pipeline(test_registry)
        return await p.run(URL("https://example.com"))

    res: dict[str, object] = asyncio.run(run())
    assert "formatted" in res
    assert "tests" in res


def test_registry_global_roundtrip() -> None:
    # Ensure idempotent registration and retrieval from global registry
    register_stealth(registry)
    register_llm(registry)
    register_gen(registry)
    assert "stealth" in registry.list_adapters("extractor")
    assert registry.get("extractor", "stealth")
