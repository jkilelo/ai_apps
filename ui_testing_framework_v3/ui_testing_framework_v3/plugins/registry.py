"""Central plugin registry supporting registration and retrieval."""

from __future__ import annotations

import importlib.util
import sys
from collections import defaultdict
from typing import TYPE_CHECKING, Any

# Prefer top-level import to satisfy linters; fallback for older Python handled in method
try:  # pragma: no cover - environment dependent
    from importlib import metadata as importlib_metadata
except Exception:  # pragma: no cover - defensive fallback
    importlib_metadata = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from pathlib import Path

    from ui_testing_framework_v3.infrastructure.config import ConfigManager


class NoAdapterForPortError(Exception):
    def __init__(self, port: str) -> None:
        super().__init__(port)


class AdapterNotFoundError(Exception):
    def __init__(self, port: str, name: str, available: list[str]) -> None:
        # Keep message construction inside the exception per TRY003
        message = f"{port}:{name}:{','.join(available)}"
        super().__init__(message)


class PluginDiscoveryError(Exception):
    """Raised when plugin discovery fails"""

    def __init__(self, plugin_name: str, error: str) -> None:
        super().__init__(f"Failed to load plugin {plugin_name}: {error}")


class ImportlibMetadataUnavailableError(Exception):
    """Raised when importlib.metadata is unavailable at runtime."""

    def __init__(self) -> None:
        super().__init__("importlib.metadata unavailable")


class PluginRegistry:
    """
    Central registry for all plugins in the system

    Features:
    - Register adapters for ports
    - Auto-discovery of plugins
    - Configuration injection
    - Instance caching (singleton pattern)
    - Hot-swapping support
    """

    def __init__(self, config_manager: ConfigManager | None = None) -> None:
        self._registry: dict[str, dict[str, type[object]]] = defaultdict(dict)
        self._instances: dict[str, Any] = {}
        self._config_manager = config_manager

    def register(self, port: str, adapter_class: type[object], name: str | None = None) -> None:
        """
        Register an adapter for a port

        Args:
            port: Port name (e.g., 'extractor', 'formatter')
            adapter_class: The adapter class to register
            name: Optional name for the adapter. Uses class name if not provided
        """
        adapter_name = name or adapter_class.__name__
        self._registry[port][adapter_name] = adapter_class
        # Clear any cached instance so hot-swapping works
        cache_key = f"{port}:{adapter_name}"
        self._instances.pop(cache_key, None)

    def get(self, port: str, name: str | None = None) -> Any:
        """
        Get an adapter instance (cached with configuration injection)

        Args:
            port: Port name
            name: Adapter name. Uses configured default or first available

        Returns:
            Adapter instance with injected configuration
        """
        if not name:
            # Use configured default
            if self._config_manager:
                name = self._config_manager.get(f"{port}.default")

            # Or first registered adapter
            if not name:
                if port not in self._registry or not self._registry[port]:
                    raise NoAdapterForPortError(port)
                name = next(iter(self._registry[port].keys()))

        cache_key = f"{port}:{name}"
        if cache_key in self._instances:
            return self._instances[cache_key]

        adapter_class = self._registry.get(port, {}).get(name)
        if not adapter_class:
            available = list(self._registry.get(port, {}).keys())
            raise AdapterNotFoundError(port, name, available)

        # Create with config injection
        instance = None
        port_config = {}

        if self._config_manager:
            port_config = self._config_manager.get(port, {})

        # Try different instantiation methods
        try:
            # Try with config parameter
            instance = adapter_class(port_config)  # type: ignore[call-arg]
        except TypeError:
            try:
                # Try no-args constructor
                instance = adapter_class()
            except Exception as e:
                print(f"Warning: Failed to instantiate {adapter_class.__name__}: {e}")
                instance = adapter_class()  # Final fallback

        self._instances[cache_key] = instance
        return instance

    def list_adapters(self, port: str) -> list[str]:
        """List all registered adapters for a port"""
        return list(self._registry.get(port, {}).keys())

    def discover_plugins(self, plugin_dir: Path) -> None:
        """
        Auto-discover and register plugins from directory

        Plugins must:
        1. Be Python files in plugin_dir
        2. Have a register() function that takes registry as parameter
        3. Call registry.register() in register() function
        """
        if not plugin_dir.exists():
            return

        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.stem.startswith("_"):
                continue

            try:
                # Load module
                module_name = f"plugin_{plugin_file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, plugin_file)
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)

                # Add to sys.modules temporarily for imports
                sys.modules[module_name] = module

                try:
                    spec.loader.exec_module(module)

                    # Register if has register function
                    if hasattr(module, "register"):
                        module.register(self)
                        print(f"Discovered plugin: {plugin_file.stem}")

                finally:
                    # Clean up sys.modules
                    sys.modules.pop(module_name, None)

            except Exception as e:
                raise PluginDiscoveryError(plugin_file.stem, str(e)) from e

    def discover_entry_points(self, group: str = "ui_testing_framework.plugins") -> None:
        """
        Discover plugins via entry points

        Args:
            group: Entry point group name
        """
        try:
            if importlib_metadata is None:  # pragma: no cover - older Python
                raise ImportlibMetadataUnavailableError()

            # Use ternary for entry points selection
            eps = importlib_metadata.entry_points()
            entry_points = eps.select(group=group) if hasattr(eps, "select") else []  # type: ignore[misc]

            for entry_point in entry_points:  # type: ignore[misc]
                try:
                    register_func = entry_point.load()  # type: ignore[misc]
                    register_func(self)  # type: ignore[misc]
                    name = getattr(entry_point, "name", "unknown")  # type: ignore[misc]
                    print(f"Discovered entry point plugin: {name}")
                except Exception as e:
                    name = getattr(entry_point, "name", "unknown")  # type: ignore[misc]
                    print(f"Failed to load entry point {name}: {e}")

        except ImportError:
            # importlib.metadata not available in older Python
            pass
        except Exception as e:
            print(f"Entry point discovery failed: {e}")

    def get_capabilities(self, port: str) -> dict[str, dict[str, Any]]:
        """Get capabilities of all adapters for a port"""
        capabilities: dict[str, dict[str, Any]] = {}

        for adapter_name in self.list_adapters(port):
            try:
                adapter = self.get(port, adapter_name)
                if hasattr(adapter, "get_capabilities"):
                    capabilities[adapter_name] = adapter.get_capabilities()
            except Exception as e:
                capabilities[adapter_name] = {"error": str(e)}

        return capabilities

    def clear_cache(self, port: str | None = None, name: str | None = None) -> None:
        """Clear cached instances"""
        if port and name:
            cache_key = f"{port}:{name}"
            self._instances.pop(cache_key, None)
        elif port:
            keys_to_remove = [k for k in self._instances if k.startswith(f"{port}:")]
            for key in keys_to_remove:
                del self._instances[key]
        else:
            self._instances.clear()


# Global registry instance
registry = PluginRegistry()
