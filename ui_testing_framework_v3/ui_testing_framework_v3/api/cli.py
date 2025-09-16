"""
CLI entry for extract/generate/list using enhanced registry and infrastructure
Integrates with configuration management and event system
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from ui_testing_framework_v3.adapters.browser.stealth import register as stealth_register
from ui_testing_framework_v3.adapters.formatters.llm_test import (
    register as llm_formatter_register,
)
from ui_testing_framework_v3.adapters.generators.llm_based import (
    register as llm_gen_register,
)
from ui_testing_framework_v3.adapters.generators.simple import (
    register as simple_gen_register,
)
from ui_testing_framework_v3.adapters.storage.sqlite import register as sqlite_register
from ui_testing_framework_v3.application.pipeline import Pipeline
from ui_testing_framework_v3.core.value_objects import URL
from ui_testing_framework_v3.infrastructure.config import ConfigManager
from ui_testing_framework_v3.infrastructure.events import EventBus
from ui_testing_framework_v3.plugins.registry import PluginRegistry


class CLI:
    """
    Enhanced CLI with configuration and event management

    Features:
    - Configuration-driven plugin selection
    - Event emission for monitoring
    - Plugin auto-discovery
    - Error handling and reporting
    """

    def __init__(self, config_path: Path | None = None):
        """Initialize CLI with configuration"""
        self.config = ConfigManager(config_path or Path("config/config.toml"))
        self.events = EventBus()
        self.registry = PluginRegistry(self.config)
        self.pipeline = Pipeline(self.registry, self.config, self.events)

        # Setup event handlers
        self._setup_event_handlers()

        # Register built-in plugins
        self._register_builtin_plugins()

        # Discover external plugins
        self._discover_plugins()

    def _setup_event_handlers(self) -> None:
        """Setup CLI event handlers for monitoring"""

        @self.events.on("pipeline.extract.start")
        def _on_extract_start(data: dict[str, Any], event_id: str) -> None:
            print(f"[{event_id[:8]}] Starting extraction from {data['url']}")

        @self.events.on("pipeline.extract.complete")
        def _on_extract_complete(data: dict[str, Any], event_id: str) -> None:
            print(f"[{event_id[:8]}] Extracted {data['count']} elements")

        @self.events.on("pipeline.generate.complete")
        def _on_generate_complete(data: dict[str, Any], event_id: str) -> None:
            print(f"[{event_id[:8]}] Generated {data['count']} test cases")

        @self.events.on("pipeline.error")
        def _on_pipeline_error(data: dict[str, Any], event_id: str) -> None:
            print(f"[{event_id[:8]}] ERROR: {data['error']}")

    def _register_builtin_plugins(self) -> None:
        """Register built-in adapters"""
        stealth_register(self.registry)
        llm_formatter_register(self.registry)
        sqlite_register(self.registry)
        simple_gen_register(self.registry)
        llm_gen_register(self.registry)

    def _discover_plugins(self) -> None:
        """Discover and register external plugins"""
        # Discover from plugins directory
        plugins_dir = Path("plugins")
        if plugins_dir.exists():
            self.registry.discover_plugins(plugins_dir)

        # Discover from entry points
        self.registry.discover_entry_points()

    async def extract(self, url: str, profile: str | None = None) -> dict[str, Any]:
        """Extract elements from URL"""
        try:
            url_obj = URL(url)
            result = await self.pipeline.run(
                url_obj,
                extractor_name=profile,  # Use profile as extractor name
            )

        except Exception as e:
            error_msg = f"Extract failed: {e}"
            self.events.emit("cli.extract.error", {"error": error_msg})
            return {"error": error_msg, "elements": [], "formatted": {}, "tests": []}
        else:
            # Emit completion event
            self.events.emit(
                "cli.extract.complete",
                {
                    "url": url,
                    "element_count": len(result["elements"]),
                    "success": len(result["errors"]) == 0,
                },
            )

            return result

    async def generate_tests(self, url: str, profile: str | None = None) -> dict[str, Any]:
        """Generate test cases for URL"""
        try:
            url_obj = URL(url)
            result = await self.pipeline.run(
                url_obj,
                extractor_name=profile,
            )

        except Exception as e:
            error_msg = f"Test generation failed: {e}"
            self.events.emit("cli.generate.error", {"error": error_msg})
            return {"error": error_msg, "elements": [], "formatted": {}, "tests": []}
        else:
            # Emit completion event
            self.events.emit(
                "cli.generate.complete",
                {
                    "url": url,
                    "test_count": len(result["tests"]),
                    "success": len(result["errors"]) == 0,
                },
            )

            return result

    def list_plugins(self) -> dict[str, dict[str, Any]]:
        """List available plugins and their capabilities"""
        plugins: dict[str, dict[str, Any]] = {
            "extractors": {
                "available": self.registry.list_adapters("extractor"),
                "default": self.config.get("extractor.default", "stealth"),
                "capabilities": self.registry.get_capabilities("extractor"),
            },
            "formatters": {
                "available": self.registry.list_adapters("formatter"),
                "default": self.config.get("formatter.default", "llm_test"),
                "capabilities": self.registry.get_capabilities("formatter"),
            },
            "generators": {
                "available": self.registry.list_adapters("test_generator"),
                "default": self.config.get("test_generator.default", "simple"),
                "capabilities": self.registry.get_capabilities("test_generator"),
            },
            "storage": {
                "available": self.registry.list_adapters("storage"),
                "default": self.config.get("storage.default", "sqlite"),
                "capabilities": self.registry.get_capabilities("storage"),
            },
        }

        self.events.emit(
            "cli.list.complete",
            {
                "plugin_count": sum(
                    len(section.get("available", [])) for section in plugins.values()
                )
            },
        )

        return plugins

    def show_config(self) -> dict[str, Any]:
        """Show current configuration"""
        return self.config.to_dict()

    def show_events(self, event_type: str | None = None) -> list[dict[str, Any]]:
        """Show event history"""
        return self.events.get_history(event_type)


# Legacy functions for backward compatibility
def _ensure_builtin_plugins() -> None:
    """Legacy function for backward compatibility"""


async def _cmd_extract(url: str, profile: str | None) -> int:
    """Legacy extract command"""
    cli = CLI()
    result = await cli.extract(url, profile)
    if "error" in result:
        print(json.dumps({"error": result["error"]}, indent=2))
        return 1
    print(json.dumps({"formatted": result["formatted"]}, indent=2))
    return 0


async def _cmd_generate(url: str, profile: str | None) -> int:
    """Legacy generate command"""
    cli = CLI()
    result = await cli.generate_tests(url, profile)
    if "error" in result:
        print(json.dumps({"error": result["error"]}, indent=2))
        return 1
    print(
        json.dumps(
            {
                "tests": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "steps": t.steps,
                        "assertions": t.assertions,
                        "priority": t.priority,
                    }
                    for t in result["tests"]
                ]
            },
            indent=2,
        )
    )
    return 0


def _cmd_list() -> int:
    """Legacy list command"""
    cli = CLI()
    plugins = cli.list_plugins()
    print(json.dumps(plugins, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="ui-testing",
        description="UI Testing Framework V3 - Extract elements and generate tests",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # Extract command
    p_extract = sub.add_parser("extract", help="Extract elements from a URL")
    p_extract.add_argument("url", help="URL to extract elements from")
    p_extract.add_argument("profile", nargs="?", help="Extraction profile to use")

    # Generate command
    p_generate = sub.add_parser("generate", help="Generate tests for a URL")
    p_generate.add_argument("url", help="URL to generate tests for")
    p_generate.add_argument("profile", nargs="?", help="Generation profile to use")

    # List command
    sub.add_parser("list", help="List available plugins")

    # Config command
    sub.add_parser("config", help="Show current configuration")

    # Events command
    p_events = sub.add_parser("events", help="Show event history")
    p_events.add_argument("--type", help="Filter by event type")

    args = parser.parse_args(argv)

    # Route commands
    if args.cmd == "list":
        return _cmd_list()
    if args.cmd == "extract":
        return asyncio.run(_cmd_extract(args.url, args.profile))
    if args.cmd == "generate":
        return asyncio.run(_cmd_generate(args.url, args.profile))
    if args.cmd == "config":
        cli = CLI()
        print(json.dumps(cli.show_config(), indent=2))
        return 0
    if args.cmd == "events":
        cli = CLI()
        events = cli.show_events(getattr(args, "type", None))
        print(json.dumps(events, indent=2))
        return 0

    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
