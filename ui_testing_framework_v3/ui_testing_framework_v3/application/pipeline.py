"""
Simple application pipeline to orchestrate core ports
Enhanced with registry integration and configuration
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - import typing-only
    from ui_testing_framework_v3.core.value_objects import URL
    from ui_testing_framework_v3.infrastructure.config import ConfigManager
    from ui_testing_framework_v3.infrastructure.events import EventBus
    from ui_testing_framework_v3.plugins.registry import PluginRegistry
    from ui_testing_framework_v3.ports.extractor import IExtractor
    from ui_testing_framework_v3.ports.formatter import IFormatter
    from ui_testing_framework_v3.ports.test_generator import ITestGenerator


class Pipeline:
    """
    Linear pipeline execution

    Enhanced with:
    - Plugin registry integration
    - Configuration management
    - Event emission
    - Error handling
    """

    def __init__(
        self,
        registry: PluginRegistry,
        config_manager: ConfigManager | None = None,
        event_bus: EventBus | None = None,
    ):
        """Initialize pipeline with dependencies"""
        self._registry = registry
        self._config = config_manager
        self._events = event_bus

    def _emit(self, event_name: str, payload: dict[str, Any]) -> None:
        """Safely emit events if an EventBus is available.

        Avoids raising if _events is None or incorrectly set by callers/tests.
        """
        eb = getattr(self, "_events", None)
        try:
            if eb is not None and hasattr(eb, "emit"):
                eb.emit(event_name, payload)
        except Exception:
            # Never allow event emission to break the pipeline, but record it for debug
            logging.debug("Event emission failed for %s", event_name, exc_info=True)

    async def run(
        self,
        url: URL,
        extractor_name: str | None = None,
        formatter_name: str | None = None,
        generator_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Run the complete pipeline

        Args:
            url: URL to process
            extractor_name: Specific extractor to use
            formatter_name: Specific formatter to use
            generator_name: Specific test generator to use

        Returns:
            Pipeline results with elements, formatted data, and tests
        """
        result: dict[str, Any] = {
            "url": url.value,
            "elements": [],
            "formatted": {},
            "tests": [],
            "errors": [],
            "metadata": {},
        }

        try:
            # Extract elements
            self._emit("pipeline.extract.start", {"url": url.value})

            extractor: IExtractor = self._registry.get("extractor", extractor_name)
            elements = await extractor.extract(url)
            result["elements"] = elements
            result["metadata"]["element_count"] = len(elements)

            self._emit("pipeline.extract.complete", {"count": len(elements)})

            # Format elements
            self._emit("pipeline.format.start", {"count": len(elements)})

            formatter: IFormatter = self._registry.get("formatter", formatter_name)
            formatted = formatter.format(elements)
            result["formatted"] = formatted

            self._emit("pipeline.format.complete", {"formatted": True})

            # Generate tests
            self._emit("pipeline.generate.start", {"elements": len(elements)})

            generator: ITestGenerator = self._registry.get("test_generator", generator_name)
            tests = await generator.generate(formatted)
            result["tests"] = tests
            result["metadata"]["test_count"] = len(tests)

            self._emit("pipeline.generate.complete", {"count": len(tests)})

        except Exception as e:
            error_msg = f"Pipeline failed: {e}"
            result["errors"].append(error_msg)

            self._emit("pipeline.error", {"error": error_msg})

            print(f"ERROR: {error_msg}")

        finally:
            self._emit("pipeline.complete", result["metadata"])

        return result


class LegacyPipeline:
    """
    Legacy pipeline for backward compatibility
    """

    def __init__(self, extractor: IExtractor, formatter: IFormatter, generator: ITestGenerator):
        self._extractor = extractor
        self._formatter = formatter
        self._generator = generator

    async def run(self, url: URL) -> dict[str, Any]:
        elements = await self._extractor.extract(url)
        formatted = self._formatter.format(elements)
        tests = await self._generator.generate(formatted)
        return {"elements": elements, "formatted": formatted, "tests": tests}
