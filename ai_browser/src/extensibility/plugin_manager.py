"""Plugin Manager for dynamic plugin discovery, loading, and lifecycle management.

This module provides comprehensive plugin management capabilities including hot-reload,
dependency resolution, version compatibility checking, and plugin registry management.
"""

import asyncio
import json
import importlib.util
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
import inspect
from loguru import logger

# packaging module import is not used in current implementation
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    logger.warning("Watchdog module not available - hot reload functionality will be limited")

from .interfaces import (
    IPlugin, IStealthPlugin, IAnalysisPlugin, IOptimizationPlugin,
    PluginMetadata, PluginState, PluginType, PluginContext, PluginResult,
    PluginException, PluginLoadError, PluginExecutionError, PluginValidationError
)
from .sandbox import PluginSandbox, SandboxConfig, create_plugin_sandbox
from .hooks import HookSystem, get_hook_system


@dataclass
class PluginInfo:
    """Information about a loaded plugin"""
    plugin: IPlugin
    metadata: PluginMetadata
    state: PluginState = PluginState.LOADED
    last_modified: datetime = field(default_factory=datetime.now)
    load_time: float = 0.0
    error_count: int = 0
    last_error: Optional[str] = None
    file_path: Optional[str] = None
    module_name: Optional[str] = None
    dependencies_resolved: bool = False
    hot_reload_enabled: bool = True


@dataclass
class PluginRegistry:
    """Registry of available and loaded plugins"""
    plugins: Dict[str, PluginInfo] = field(default_factory=dict)
    plugin_directories: List[str] = field(default_factory=list)
    discovered_plugins: Dict[str, str] = field(default_factory=dict)  # name -> file_path
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    load_order: List[str] = field(default_factory=list)


if HAS_WATCHDOG:
    class PluginFileWatcher(FileSystemEventHandler):
        """File system watcher for hot-reload functionality"""
        
        def __init__(self, plugin_manager: 'PluginManager'):
            self.plugin_manager = plugin_manager
            self.reload_cooldown: Dict[str, float] = {}
            self.cooldown_seconds = 2.0  # Prevent rapid reloads
        
        def on_modified(self, event):
            """Handle file modification events"""
            if event.is_directory or not event.src_path.endswith('.py'):
                return
            
            plugin_path = Path(event.src_path)
            plugin_name = plugin_path.stem
            
            # Check cooldown
            current_time = time.time()
            if plugin_name in self.reload_cooldown:
                if current_time - self.reload_cooldown[plugin_name] < self.cooldown_seconds:
                    return
            
            self.reload_cooldown[plugin_name] = current_time
            
            # Schedule reload
            asyncio.create_task(self.plugin_manager.reload_plugin(plugin_name))
            logger.info(f"Plugin file modified, scheduling reload: {plugin_name}")
else:
    # Mock implementation when watchdog is not available
    class PluginFileWatcher:
        def __init__(self, plugin_manager: 'PluginManager'):
            self.plugin_manager = plugin_manager


class DependencyResolver:
    """Resolves plugin dependencies and determines load order"""
    
    @staticmethod
    def resolve_load_order(plugins: Dict[str, PluginMetadata]) -> List[str]:
        """Resolve plugin load order using topological sort"""
        
        # Build dependency graph
        graph = {}
        for plugin_name, metadata in plugins.items():
            graph[plugin_name] = metadata.dependencies
        
        # Topological sort
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(plugin_name: str):
            if plugin_name in temp_visited:
                raise PluginValidationError(
                    plugin_name,
                    f"Circular dependency detected involving {plugin_name}"
                )
            
            if plugin_name in visited:
                return
            
            temp_visited.add(plugin_name)
            
            # Visit dependencies first
            if plugin_name in graph:
                for dep in graph[plugin_name]:
                    if dep in plugins:  # Only consider available plugins
                        visit(dep)
            
            temp_visited.remove(plugin_name)
            visited.add(plugin_name)
            result.append(plugin_name)
        
        # Visit all plugins
        for plugin_name in plugins:
            if plugin_name not in visited:
                visit(plugin_name)
        
        return result
    
    @staticmethod
    def check_dependencies(plugin_metadata: PluginMetadata, available_plugins: Set[str]) -> List[str]:
        """Check if plugin dependencies are satisfied"""
        missing_deps = []
        
        for dep in plugin_metadata.dependencies:
            if dep not in available_plugins:
                missing_deps.append(dep)
        
        return missing_deps


class PluginManager:
    """Central plugin management system"""
    
    def __init__(
        self,
        plugin_directories: Optional[List[str]] = None,
        enable_hot_reload: bool = True,
        sandbox_config: Optional[SandboxConfig] = None
    ):
        self.registry = PluginRegistry()
        self.hook_system = get_hook_system()
        self.enable_hot_reload = enable_hot_reload
        self.file_observer: Optional[Observer] = None
        self.watcher: Optional[PluginFileWatcher] = None
        self.sandbox = PluginSandbox(sandbox_config or SandboxConfig())
        
        # Default plugin directories
        if plugin_directories is None:
            plugin_directories = [
                "plugins/stealth",
                "plugins/analysis", 
                "plugins/optimization",
                "plugins/custom"
            ]
        
        self.registry.plugin_directories = plugin_directories
        
        # Framework version for compatibility checks
        self.framework_version = "2.0.0"
        
        # Plugin statistics
        self.stats = {
            'plugins_discovered': 0,
            'plugins_loaded': 0,
            'plugins_failed': 0,
            'hot_reloads': 0,
            'total_load_time': 0.0
        }
    
    async def initialize(self) -> None:
        """Initialize the plugin manager"""
        logger.info("Initializing Plugin Manager...")
        
        # Ensure plugin directories exist
        for directory in self.registry.plugin_directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Start hot reload watcher if enabled
        if self.enable_hot_reload:
            await self.start_hot_reload_watcher()
        
        # Discover and load plugins
        await self.discover_plugins()
        await self.load_all_plugins()
        
        logger.info(f"Plugin Manager initialized with {len(self.registry.plugins)} plugins")
    
    async def discover_plugins(self) -> Dict[str, str]:
        """Discover all plugins in configured directories"""
        discovered = {}
        
        for directory in self.registry.plugin_directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                continue
            
            for plugin_file in dir_path.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                
                plugin_name = plugin_file.stem
                discovered[plugin_name] = str(plugin_file)
                
                logger.debug(f"Discovered plugin: {plugin_name} at {plugin_file}")
        
        self.registry.discovered_plugins = discovered
        self.stats['plugins_discovered'] = len(discovered)
        
        return discovered
    
    async def load_plugin(self, plugin_name: str, plugin_path: Optional[str] = None) -> bool:
        """Load a single plugin"""
        
        if plugin_path is None:
            plugin_path = self.registry.discovered_plugins.get(plugin_name)
            if plugin_path is None:
                raise PluginLoadError(plugin_name, f"Plugin file not found")
        
        start_time = time.time()
        
        try:
            # Validate plugin code before loading
            violations = self.sandbox.validate_plugin_code(plugin_path)
            if violations:
                raise PluginValidationError(
                    plugin_name,
                    f"Plugin validation failed: {', '.join(violations)}"
                )
            
            # Load plugin module in sandbox
            module, sandbox_stats = self.sandbox.load_plugin_module(plugin_path)
            
            # Find plugin class
            plugin_class = self.find_plugin_class(module)
            if not plugin_class:
                raise PluginLoadError(plugin_name, "No valid plugin class found")
            
            # Instantiate plugin
            plugin_instance = plugin_class()
            
            # Validate plugin interface
            if not self.validate_plugin_interface(plugin_instance):
                raise PluginValidationError(plugin_name, "Plugin does not implement required interface")
            
            # Get plugin metadata
            metadata = plugin_instance.get_metadata()
            
            # Check version compatibility
            if not plugin_instance.is_compatible(self.framework_version):
                raise PluginValidationError(
                    plugin_name,
                    f"Plugin incompatible with framework version {self.framework_version}"
                )
            
            # Check dependencies
            missing_deps = DependencyResolver.check_dependencies(
                metadata,
                set(self.registry.plugins.keys())
            )
            
            # Create plugin info
            load_time = time.time() - start_time
            plugin_info = PluginInfo(
                plugin=plugin_instance,
                metadata=metadata,
                state=PluginState.LOADED,
                load_time=load_time,
                file_path=plugin_path,
                module_name=module.__name__,
                dependencies_resolved=len(missing_deps) == 0
            )
            
            # Store plugin
            self.registry.plugins[plugin_name] = plugin_info
            
            # Initialize plugin
            context = PluginContext(
                plugin_name=plugin_name,
                config=metadata.dict() if hasattr(metadata, 'dict') else {}
            )
            
            init_result = await plugin_instance.initialize(context)
            if not init_result.success:
                raise PluginExecutionError(
                    plugin_name,
                    f"Plugin initialization failed: {init_result.error}"
                )
            
            plugin_info.state = PluginState.ACTIVE
            
            # Register hooks
            await self.register_plugin_hooks(plugin_instance, metadata)
            
            # Trigger plugin load hook
            await self.hook_system.trigger_hook(
                "PluginLoad",
                data={'plugin_name': plugin_name, 'metadata': metadata},
                context=context
            )
            
            # Update statistics
            self.stats['plugins_loaded'] += 1
            self.stats['total_load_time'] += load_time
            
            logger.info(
                f"Successfully loaded plugin '{plugin_name}' "
                f"(v{metadata.version}) in {load_time:.3f}s"
            )
            
            return True
            
        except Exception as e:
            # Update error statistics
            self.stats['plugins_failed'] += 1
            
            # Store error information
            if plugin_name in self.registry.plugins:
                self.registry.plugins[plugin_name].state = PluginState.ERROR
                self.registry.plugins[plugin_name].last_error = str(e)
                self.registry.plugins[plugin_name].error_count += 1
            
            logger.error(f"Failed to load plugin '{plugin_name}': {e}")
            
            # Trigger plugin error hook
            await self.hook_system.trigger_hook(
                "PluginError",
                data={'plugin_name': plugin_name, 'error': str(e)},
                context=PluginContext(plugin_name=plugin_name, config={})
            )
            
            return False
    
    def find_plugin_class(self, module) -> Optional[Type[IPlugin]]:
        """Find the main plugin class in a module"""
        
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (issubclass(obj, IPlugin) and 
                obj != IPlugin and 
                obj.__module__ == module.__name__):
                return obj
        
        return None
    
    def validate_plugin_interface(self, plugin: IPlugin) -> bool:
        """Validate that plugin implements required interface"""
        required_methods = [
            'initialize', 'execute', 'cleanup', 'get_metadata',
            'is_compatible', 'validate_config', 'on_hook'
        ]
        
        for method in required_methods:
            if not hasattr(plugin, method):
                return False
            if not callable(getattr(plugin, method)):
                return False
        
        return True
    
    async def register_plugin_hooks(self, plugin: IPlugin, metadata: PluginMetadata) -> None:
        """Register plugin hooks with the hook system"""
        
        for hook_name in metadata.hooks:
            # Create hook handler that calls plugin's on_hook method
            async def hook_handler(event, plugin_ref=plugin, hook_ref=hook_name):
                context = PluginContext(
                    plugin_name=metadata.name,
                    config={}
                )
                return await plugin_ref.on_hook(hook_ref, context, event.data)
            
            # Register with hook system
            from .hooks import HookHandler
            handler = HookHandler(
                name=f"{metadata.name}_{hook_name}",
                callback=hook_handler,
                priority=metadata.priority,
                plugin_name=metadata.name,
                async_handler=True
            )
            
            self.hook_system.register_hook_handler(hook_name, handler)
    
    async def load_all_plugins(self) -> None:
        """Load all discovered plugins in dependency order"""
        
        if not self.registry.discovered_plugins:
            await self.discover_plugins()
        
        # First pass: collect metadata for dependency resolution
        plugin_metadata = {}
        for plugin_name, plugin_path in self.registry.discovered_plugins.items():
            try:
                # Load just to get metadata
                module, _ = self.sandbox.load_plugin_module(plugin_path)
                plugin_class = self.find_plugin_class(module)
                if plugin_class:
                    temp_instance = plugin_class()
                    plugin_metadata[plugin_name] = temp_instance.get_metadata()
                    
            except Exception as e:
                logger.error(f"Failed to get metadata for plugin {plugin_name}: {e}")
        
        # Resolve load order
        try:
            load_order = DependencyResolver.resolve_load_order(plugin_metadata)
            self.registry.load_order = load_order
            
            logger.info(f"Plugin load order: {' -> '.join(load_order)}")
            
        except Exception as e:
            logger.error(f"Failed to resolve plugin dependencies: {e}")
            # Fallback to simple alphabetical order
            load_order = sorted(self.registry.discovered_plugins.keys())
        
        # Load plugins in order
        for plugin_name in load_order:
            if plugin_name in self.registry.discovered_plugins:
                await self.load_plugin(plugin_name)
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        
        if plugin_name not in self.registry.plugins:
            return False
        
        plugin_info = self.registry.plugins[plugin_name]
        
        try:
            # Call plugin cleanup
            context = PluginContext(
                plugin_name=plugin_name,
                config=plugin_info.metadata.dict() if hasattr(plugin_info.metadata, 'dict') else {}
            )
            
            cleanup_result = await plugin_info.plugin.cleanup(context)
            if not cleanup_result.success:
                logger.warning(f"Plugin cleanup failed: {cleanup_result.error}")
            
            # Unregister hooks
            for hook_name in plugin_info.metadata.hooks:
                handler_name = f"{plugin_name}_{hook_name}"
                self.hook_system.unregister_hook_handler(hook_name, handler_name)
            
            # Remove from module cache
            if plugin_info.module_name and plugin_info.module_name in sys.modules:
                del sys.modules[plugin_info.module_name]
            
            # Remove from registry
            del self.registry.plugins[plugin_name]
            
            # Trigger plugin unload hook
            await self.hook_system.trigger_hook(
                "PluginUnload",
                data={'plugin_name': plugin_name},
                context=context
            )
            
            logger.info(f"Successfully unloaded plugin: {plugin_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    async def reload_plugin(self, plugin_name: str) -> bool:
        """Hot-reload a specific plugin"""
        
        if not self.enable_hot_reload:
            logger.warning(f"Hot reload disabled for plugin: {plugin_name}")
            return False
        
        plugin_info = self.registry.plugins.get(plugin_name)
        if not plugin_info or not plugin_info.hot_reload_enabled:
            return False
        
        try:
            # Save current state if possible
            saved_state = None
            if hasattr(plugin_info.plugin, 'get_state'):
                saved_state = await plugin_info.plugin.get_state()
            
            # Unload current plugin
            await self.unload_plugin(plugin_name)
            
            # Load new version
            success = await self.load_plugin(plugin_name)
            
            if success and saved_state:
                # Restore state if possible
                new_plugin = self.registry.plugins[plugin_name].plugin
                if hasattr(new_plugin, 'set_state'):
                    await new_plugin.set_state(saved_state)
            
            if success:
                self.stats['hot_reloads'] += 1
                logger.info(f"Successfully hot-reloaded plugin: {plugin_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to hot-reload plugin {plugin_name}: {e}")
            return False
    
    async def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a disabled plugin"""
        if plugin_name in self.registry.plugins:
            plugin_info = self.registry.plugins[plugin_name]
            if plugin_info.state == PluginState.DISABLED:
                plugin_info.state = PluginState.ACTIVE
                logger.info(f"Enabled plugin: {plugin_name}")
                return True
        return False
    
    async def disable_plugin(self, plugin_name: str) -> bool:
        """Disable an active plugin without unloading"""
        if plugin_name in self.registry.plugins:
            plugin_info = self.registry.plugins[plugin_name]
            if plugin_info.state == PluginState.ACTIVE:
                plugin_info.state = PluginState.DISABLED
                logger.info(f"Disabled plugin: {plugin_name}")
                return True
        return False
    
    async def execute_plugin(
        self,
        plugin_name: str,
        context: Optional[PluginContext] = None,
        **kwargs
    ) -> PluginResult:
        """Execute a specific plugin"""
        
        if plugin_name not in self.registry.plugins:
            return PluginResult(
                success=False,
                error=f"Plugin '{plugin_name}' not found"
            )
        
        plugin_info = self.registry.plugins[plugin_name]
        
        if plugin_info.state != PluginState.ACTIVE:
            return PluginResult(
                success=False,
                error=f"Plugin '{plugin_name}' is not active (state: {plugin_info.state.value})"
            )
        
        if context is None:
            context = PluginContext(
                plugin_name=plugin_name,
                config=plugin_info.metadata.dict() if hasattr(plugin_info.metadata, 'dict') else {}
            )
        
        try:
            result = await plugin_info.plugin.execute(context, **kwargs)
            return result
            
        except Exception as e:
            plugin_info.error_count += 1
            plugin_info.last_error = str(e)
            
            return PluginResult(
                success=False,
                error=f"Plugin execution failed: {str(e)}"
            )
    
    async def start_hot_reload_watcher(self) -> None:
        """Start file system watcher for hot reload"""
        
        if not self.enable_hot_reload:
            return
            
        if not HAS_WATCHDOG:
            logger.warning("Hot reload disabled - watchdog module not available")
            return
        
        self.watcher = PluginFileWatcher(self)
        self.file_observer = Observer()
        
        for directory in self.registry.plugin_directories:
            if Path(directory).exists():
                self.file_observer.schedule(
                    self.watcher,
                    str(directory),
                    recursive=True
                )
        
        self.file_observer.start()
        logger.info("Started hot-reload watcher for plugin directories")
    
    async def stop_hot_reload_watcher(self) -> None:
        """Stop file system watcher"""
        if self.file_observer and HAS_WATCHDOG:
            self.file_observer.stop()
            self.file_observer.join()
            logger.info("Stopped hot-reload watcher")
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a specific plugin"""
        return self.registry.plugins.get(plugin_name)
    
    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[str]:
        """List loaded plugins, optionally filtered by type"""
        plugins = []
        
        for name, info in self.registry.plugins.items():
            if plugin_type is None or info.metadata.plugin_type == plugin_type:
                plugins.append(name)
        
        return plugins
    
    def get_stats(self) -> Dict[str, Any]:
        """Get plugin manager statistics"""
        active_plugins = len([
            info for info in self.registry.plugins.values()
            if info.state == PluginState.ACTIVE
        ])
        
        return {
            **self.stats,
            'active_plugins': active_plugins,
            'disabled_plugins': len(self.registry.plugins) - active_plugins,
            'plugin_directories': len(self.registry.plugin_directories),
            'average_load_time': (
                self.stats['total_load_time'] / max(1, self.stats['plugins_loaded'])
            )
        }
    
    async def shutdown(self) -> None:
        """Shutdown plugin manager and cleanup"""
        logger.info("Shutting down Plugin Manager...")
        
        # Stop hot reload watcher
        await self.stop_hot_reload_watcher()
        
        # Unload all plugins
        plugin_names = list(self.registry.plugins.keys())
        for plugin_name in plugin_names:
            await self.unload_plugin(plugin_name)
        
        logger.info("Plugin Manager shutdown complete")