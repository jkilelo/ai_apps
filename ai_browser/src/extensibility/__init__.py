"""Extensibility Layer (Layer 5) - Plugin System and MCP Integration

This module provides the complete plugin system for the AI-First Smart Browser,
including dynamic plugin loading, sandboxing, hook system, and MCP protocol support.
"""

from .interfaces import (
    # Core interfaces
    IPlugin,
    IStealthPlugin,
    IAnalysisPlugin,
    IOptimizationPlugin,
    IHookListener,
    
    # Data classes and enums
    PluginMetadata,
    PluginState,
    PluginType,
    PluginContext,
    PluginResult,
    
    # Exceptions
    PluginException,
    PluginLoadError,
    PluginExecutionError,
    PluginValidationError,
    PluginSandboxViolation
)

from .sandbox import (
    PluginSandbox,
    SandboxConfig,
    SandboxStats,
    create_plugin_sandbox,
    validate_plugin_permissions
)

from .hooks import (
    HookSystem,
    HookType,
    HookPriority,
    HookEvent,
    HookHandler,
    HookResult,
    HookChainResult,
    get_hook_system,
    register_hook,
    trigger_hook
)

from .plugin_manager import (
    PluginManager,
    PluginInfo,
    PluginRegistry,
    DependencyResolver
)

from .mcp import (
    MCPServer,
    MCPClient,
    MCPTool,
    MCPResource,
    MCPPrompt,
    MCPMessage,
    MCPServerInfo,
    MCPClientInfo,
    create_mcp_server,
    create_mcp_client
)

# Version information
__version__ = "2.0.0"
__author__ = "AI Browser Team"

# Global instances
_plugin_manager = None
_hook_system = None
_mcp_server = None
_mcp_client = None


def get_plugin_manager(
    plugin_directories=None,
    enable_hot_reload=True,
    sandbox_config=None
):
    """Get or create global plugin manager instance"""
    global _plugin_manager
    
    if _plugin_manager is None:
        _plugin_manager = PluginManager(
            plugin_directories=plugin_directories,
            enable_hot_reload=enable_hot_reload,
            sandbox_config=sandbox_config
        )
    
    return _plugin_manager


def get_mcp_server(name="AI Browser", plugin_manager=None):
    """Get or create global MCP server instance"""
    global _mcp_server
    
    if _mcp_server is None:
        _mcp_server = MCPServer(
            name=name,
            plugin_manager=plugin_manager or get_plugin_manager()
        )
    
    return _mcp_server


def get_mcp_client(name="AI Browser Client"):
    """Get or create global MCP client instance"""
    global _mcp_client
    
    if _mcp_client is None:
        _mcp_client = MCPClient(name=name)
    
    return _mcp_client


async def initialize_extensibility_layer(
    plugin_directories=None,
    enable_hot_reload=True,
    load_hooks_config=True,
    start_mcp_server=False
):
    """Initialize the complete extensibility layer"""
    from loguru import logger
    
    logger.info("Initializing Extensibility Layer (Layer 5)...")
    
    # Initialize plugin manager
    plugin_manager = get_plugin_manager(
        plugin_directories=plugin_directories,
        enable_hot_reload=enable_hot_reload
    )
    
    await plugin_manager.initialize()
    
    # Initialize hook system with config
    if load_hooks_config:
        hook_system = get_hook_system()
        # Hook system automatically loads .claude/hooks.json if present
    
    # Initialize MCP server if requested
    if start_mcp_server:
        mcp_server = get_mcp_server(plugin_manager=plugin_manager)
        logger.info("MCP server ready for connections")
    
    logger.info("Extensibility layer initialized successfully")
    
    return {
        'plugin_manager': plugin_manager,
        'hook_system': get_hook_system(),
        'mcp_server': _mcp_server,
        'stats': plugin_manager.get_stats()
    }


async def shutdown_extensibility_layer():
    """Shutdown the extensibility layer and cleanup resources"""
    from loguru import logger
    
    logger.info("Shutting down Extensibility Layer...")
    
    # Shutdown plugin manager
    if _plugin_manager:
        await _plugin_manager.shutdown()
    
    # Stop hook system processing
    if _hook_system:
        await _hook_system.stop_event_processing()
    
    # Disconnect MCP client connections
    if _mcp_client:
        for server_id in list(_mcp_client.connections.keys()):
            await _mcp_client.disconnect(server_id)
    
    logger.info("Extensibility layer shutdown complete")


# Convenience functions for common operations

async def load_plugin(plugin_name, plugin_path=None):
    """Load a specific plugin"""
    return await get_plugin_manager().load_plugin(plugin_name, plugin_path)


async def execute_plugin(plugin_name, context=None, **kwargs):
    """Execute a specific plugin"""
    return await get_plugin_manager().execute_plugin(plugin_name, context, **kwargs)


async def trigger_hook_event(hook_name, data=None, context=None):
    """Trigger a hook event"""
    return await get_hook_system().trigger_hook(hook_name, data, context)


def list_available_plugins(plugin_type=None):
    """List available plugins"""
    return get_plugin_manager().list_plugins(plugin_type)


def get_plugin_stats():
    """Get plugin system statistics"""
    return get_plugin_manager().get_stats()


# Export all public interfaces
__all__ = [
    # Core interfaces
    'IPlugin',
    'IStealthPlugin', 
    'IAnalysisPlugin',
    'IOptimizationPlugin',
    'IHookListener',
    
    # Data models
    'PluginMetadata',
    'PluginState', 
    'PluginType',
    'PluginContext',
    'PluginResult',
    
    # Exceptions
    'PluginException',
    'PluginLoadError',
    'PluginExecutionError', 
    'PluginValidationError',
    'PluginSandboxViolation',
    
    # Sandbox
    'PluginSandbox',
    'SandboxConfig',
    'create_plugin_sandbox',
    
    # Hook system
    'HookSystem',
    'HookType',
    'HookEvent',
    'HookResult',
    'get_hook_system',
    'register_hook',
    'trigger_hook',
    
    # Plugin management
    'PluginManager',
    'PluginInfo',
    'get_plugin_manager',
    
    # MCP Protocol
    'MCPServer',
    'MCPClient', 
    'MCPTool',
    'create_mcp_server',
    'create_mcp_client',
    'get_mcp_server',
    'get_mcp_client',
    
    # Initialization
    'initialize_extensibility_layer',
    'shutdown_extensibility_layer',
    
    # Convenience functions
    'load_plugin',
    'execute_plugin',
    'trigger_hook_event',
    'list_available_plugins',
    'get_plugin_stats'
]