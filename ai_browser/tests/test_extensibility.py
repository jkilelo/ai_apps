"""Comprehensive test suite for the Extensibility Layer (Layer 5).

Tests plugin system functionality including loading, execution, sandboxing,
hooks, MCP protocol, and integration with existing systems.
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# Import extensibility components
from src.extensibility import (
    # Core interfaces
    IPlugin, IStealthPlugin, IAnalysisPlugin,
    PluginMetadata, PluginType, PluginContext, PluginResult, PluginState,
    
    # Plugin system
    PluginManager, PluginSandbox, SandboxConfig,
    
    # Hook system
    HookSystem, HookType, HookEvent, HookResult,
    
    # MCP protocol
    MCPServer, MCPClient, MCPTool,
    
    # Initialization
    initialize_extensibility_layer, shutdown_extensibility_layer
)

from src.extensibility.stealth_adapter import StealthPluginAdapter, integrate_legacy_stealth_system


class MockPlugin(IPlugin):
    """Mock plugin for testing"""
    
    def __init__(self, name="test_plugin", should_fail=False):
        self.name = name
        self.should_fail = should_fail
        self.initialized = False
        self.executed = False
        self.cleaned_up = False
    
    async def initialize(self, context: PluginContext) -> PluginResult:
        if self.should_fail:
            return PluginResult(success=False, error="Mock initialization failure")
        self.initialized = True
        return PluginResult(success=True, data={"initialized": True})
    
    async def execute(self, context: PluginContext, **kwargs) -> PluginResult:
        if self.should_fail:
            return PluginResult(success=False, error="Mock execution failure")
        self.executed = True
        return PluginResult(success=True, data={"executed": True, "kwargs": kwargs})
    
    async def cleanup(self, context: PluginContext) -> PluginResult:
        self.cleaned_up = True
        return PluginResult(success=True, data={"cleaned_up": True})
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self.name,
            version="1.0.0",
            author="Test Author",
            description="Mock plugin for testing",
            plugin_type=PluginType.CUSTOM,
            min_framework_version="2.0.0"
        )
    
    def is_compatible(self, framework_version: str) -> bool:
        return True
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        return True
    
    async def on_hook(self, hook_name: str, context: PluginContext, data: Any) -> PluginResult:
        return PluginResult(success=True, data={"hook": hook_name})


class MockStealthPlugin(IStealthPlugin):
    """Mock stealth plugin for testing"""
    
    def __init__(self, name="test_stealth_plugin"):
        self.name = name
        self.initialized = False
    
    async def initialize(self, context: PluginContext) -> PluginResult:
        self.initialized = True
        return PluginResult(success=True)
    
    async def execute(self, context: PluginContext, **kwargs) -> PluginResult:
        return PluginResult(success=True, data={"stealth_applied": True})
    
    async def cleanup(self, context: PluginContext) -> PluginResult:
        return PluginResult(success=True)
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self.name,
            version="1.0.0",
            author="Test Author",
            description="Mock stealth plugin",
            plugin_type=PluginType.STEALTH,
            min_framework_version="2.0.0"
        )
    
    def is_compatible(self, framework_version: str) -> bool:
        return True
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        return True
    
    async def on_hook(self, hook_name: str, context: PluginContext, data: Any) -> PluginResult:
        return PluginResult(success=True)
    
    async def apply_to_context(self, browser_context, config: Dict[str, Any]) -> PluginResult:
        return PluginResult(success=True, data={"context_modified": True})
    
    async def apply_to_page(self, page, config: Dict[str, Any]) -> PluginResult:
        return PluginResult(success=True, data={"page_modified": True})
    
    async def test_evasion(self, page) -> Dict[str, Any]:
        return {"stealth_effective": True}
    
    def get_evasion_techniques(self) -> list:
        return ["mock_technique"]


@pytest.fixture
def temp_plugin_dir():
    """Create temporary plugin directory for testing"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        plugin_dir = Path(tmp_dir) / "plugins"
        plugin_dir.mkdir()
        yield str(plugin_dir)


@pytest.fixture
def sample_plugin_file(temp_plugin_dir):
    """Create a sample plugin file"""
    plugin_file = Path(temp_plugin_dir) / "sample_plugin.py"
    plugin_content = '''
from src.extensibility.interfaces import IPlugin, PluginMetadata, PluginType, PluginContext, PluginResult
from typing import Dict, Any

class SamplePlugin(IPlugin):
    async def initialize(self, context: PluginContext) -> PluginResult:
        return PluginResult(success=True)
    
    async def execute(self, context: PluginContext, **kwargs) -> PluginResult:
        return PluginResult(success=True, data={"test": "data"})
    
    async def cleanup(self, context: PluginContext) -> PluginResult:
        return PluginResult(success=True)
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="sample_plugin",
            version="1.0.0",
            author="Test",
            description="Sample plugin",
            plugin_type=PluginType.CUSTOM,
            min_framework_version="2.0.0"
        )
    
    def is_compatible(self, framework_version: str) -> bool:
        return True
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        return True
    
    async def on_hook(self, hook_name: str, context: PluginContext, data: Any) -> PluginResult:
        return PluginResult(success=True)
'''
    plugin_file.write_text(plugin_content)
    return str(plugin_file)


@pytest.mark.asyncio
class TestPluginManager:
    """Test plugin manager functionality"""
    
    async def test_plugin_manager_initialization(self, temp_plugin_dir):
        """Test plugin manager initialization"""
        manager = PluginManager(plugin_directories=[temp_plugin_dir])
        await manager.initialize()
        
        assert manager is not None
        assert temp_plugin_dir in manager.registry.plugin_directories
        assert manager.stats['plugins_discovered'] >= 0
        
        await manager.shutdown()
    
    async def test_plugin_discovery(self, temp_plugin_dir, sample_plugin_file):
        """Test plugin discovery functionality"""
        manager = PluginManager(plugin_directories=[temp_plugin_dir])
        
        discovered = await manager.discover_plugins()
        
        assert "sample_plugin" in discovered
        assert discovered["sample_plugin"] == sample_plugin_file
        
        await manager.shutdown()
    
    async def test_plugin_loading_success(self, temp_plugin_dir, sample_plugin_file):
        """Test successful plugin loading"""
        manager = PluginManager(plugin_directories=[temp_plugin_dir])
        await manager.initialize()
        
        success = await manager.load_plugin("sample_plugin", sample_plugin_file)
        
        assert success is True
        assert "sample_plugin" in manager.registry.plugins
        
        plugin_info = manager.registry.plugins["sample_plugin"]
        assert plugin_info.state == PluginState.ACTIVE
        assert plugin_info.metadata.name == "sample_plugin"
        
        await manager.shutdown()
    
    async def test_plugin_execution(self, temp_plugin_dir, sample_plugin_file):
        """Test plugin execution"""
        manager = PluginManager(plugin_directories=[temp_plugin_dir])
        await manager.initialize()
        
        await manager.load_plugin("sample_plugin", sample_plugin_file)
        
        context = PluginContext(plugin_name="sample_plugin", config={})
        result = await manager.execute_plugin("sample_plugin", context)
        
        assert result.success is True
        assert result.data["test"] == "data"
        
        await manager.shutdown()
    
    async def test_plugin_unloading(self, temp_plugin_dir, sample_plugin_file):
        """Test plugin unloading"""
        manager = PluginManager(plugin_directories=[temp_plugin_dir])
        await manager.initialize()
        
        await manager.load_plugin("sample_plugin", sample_plugin_file)
        assert "sample_plugin" in manager.registry.plugins
        
        success = await manager.unload_plugin("sample_plugin")
        
        assert success is True
        assert "sample_plugin" not in manager.registry.plugins
        
        await manager.shutdown()


@pytest.mark.asyncio
class TestPluginSandbox:
    """Test plugin sandboxing functionality"""
    
    def test_sandbox_configuration(self):
        """Test sandbox configuration"""
        config = SandboxConfig(
            max_memory_mb=50,
            max_cpu_time_seconds=10,
            allowed_imports={'json', 'math'}
        )
        
        sandbox = PluginSandbox(config)
        
        assert sandbox.config.max_memory_mb == 50
        assert sandbox.config.max_cpu_time_seconds == 10
        assert 'json' in sandbox.config.allowed_imports
        assert 'math' in sandbox.config.allowed_imports
    
    def test_restricted_globals_creation(self, temp_plugin_dir):
        """Test creation of restricted globals"""
        sandbox = PluginSandbox()
        
        plugin_path = Path(temp_plugin_dir) / "test.py"
        plugin_path.write_text("# Test plugin")
        
        restricted_globals = sandbox.create_restricted_globals(str(plugin_path))
        
        assert '__builtins__' in restricted_globals
        assert '__name__' in restricted_globals
        assert '__file__' in restricted_globals
        
        # Check that dangerous functions are blocked
        builtins_dict = restricted_globals['__builtins__']
        assert 'eval' not in builtins_dict
        assert 'exec' not in builtins_dict
    
    def test_plugin_code_validation(self, temp_plugin_dir):
        """Test static plugin code validation"""
        sandbox = PluginSandbox()
        
        # Create plugin with dangerous code
        dangerous_plugin = Path(temp_plugin_dir) / "dangerous.py"
        dangerous_plugin.write_text("""
import subprocess
eval("print('hello')")
os.system("ls")
""")
        
        violations = sandbox.validate_plugin_code(str(dangerous_plugin))
        
        assert len(violations) > 0
        assert any("subprocess" in v for v in violations)
        assert any("eval" in v for v in violations)


@pytest.mark.asyncio 
class TestHookSystem:
    """Test hook system functionality"""
    
    async def test_hook_system_initialization(self):
        """Test hook system initialization"""
        hook_system = HookSystem()
        
        assert hook_system is not None
        assert isinstance(hook_system.handlers, dict)
        assert isinstance(hook_system.listeners, dict)
    
    async def test_hook_registration_and_triggering(self):
        """Test hook registration and triggering"""
        hook_system = HookSystem()
        
        # Register a test hook handler
        test_results = []
        
        async def test_handler(event):
            test_results.append(event.data)
            return PluginResult(success=True, data={"handled": True})
        
        from src.extensibility.hooks import HookHandler
        handler = HookHandler(
            name="test_handler",
            callback=test_handler,
            async_handler=True
        )
        
        hook_system.register_hook_handler("test_hook", handler)
        
        # Trigger the hook
        result = await hook_system.trigger_hook("test_hook", data="test_data")
        
        assert result.success is True
        assert len(test_results) == 1
        assert test_results[0] == "test_data"
    
    async def test_hook_priority_ordering(self):
        """Test that hooks execute in priority order"""
        hook_system = HookSystem()
        execution_order = []
        
        async def handler1(event):
            execution_order.append(1)
            return PluginResult(success=True)
        
        async def handler2(event):
            execution_order.append(2)
            return PluginResult(success=True)
        
        async def handler3(event):
            execution_order.append(3)
            return PluginResult(success=True)
        
        from src.extensibility.hooks import HookHandler
        
        # Register handlers with different priorities
        hook_system.register_hook_handler("priority_test", HookHandler(
            name="handler1", callback=handler1, priority=30, async_handler=True
        ))
        hook_system.register_hook_handler("priority_test", HookHandler(
            name="handler2", callback=handler2, priority=10, async_handler=True  # Should execute first
        ))
        hook_system.register_hook_handler("priority_test", HookHandler(
            name="handler3", callback=handler3, priority=20, async_handler=True
        ))
        
        await hook_system.trigger_hook("priority_test")
        
        # Should execute in priority order: 10, 20, 30
        assert execution_order == [2, 3, 1]


@pytest.mark.asyncio
class TestMCPProtocol:
    """Test MCP protocol implementation"""
    
    async def test_mcp_server_initialization(self):
        """Test MCP server initialization"""
        server = MCPServer()
        
        assert server.server_info.name == "AI Browser"
        assert server.server_info.version == "2.0.0"
        assert len(server.tools) > 0  # Should have default browser tools
    
    async def test_tool_registration(self):
        """Test MCP tool registration"""
        server = MCPServer()
        
        async def test_tool_handler(args):
            return {"result": "test"}
        
        server.register_tool(
            name="test_tool",
            description="Test tool",
            input_schema={"type": "object"},
            handler=test_tool_handler
        )
        
        assert "test_tool" in server.tools
        assert server.tools["test_tool"].name == "test_tool"
        assert "test_tool" in server.tool_handlers
    
    async def test_mcp_message_handling(self):
        """Test MCP message handling"""
        server = MCPServer()
        connection_id = "test_connection"
        
        # Test initialize message
        init_message = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {
                "clientInfo": {
                    "name": "Test Client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await server.handle_message(init_message, connection_id)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "1"
        assert "result" in response
        assert "serverInfo" in response["result"]
    
    async def test_mcp_client_initialization(self):
        """Test MCP client initialization"""
        client = MCPClient()
        
        assert client.client_info.name == "AI Browser Client"
        assert client.client_info.version == "2.0.0"
        assert isinstance(client.connections, dict)


@pytest.mark.asyncio
class TestStealthIntegration:
    """Test stealth system integration"""
    
    async def test_stealth_plugin_adapter(self):
        """Test stealth plugin adapter"""
        from src.execution.stealth_manager import WebDriverPlugin
        
        old_plugin = WebDriverPlugin()
        adapter = StealthPluginAdapter(old_plugin)
        
        # Test adapter interface
        metadata = adapter.get_metadata()
        assert metadata.name == "webdriver_flag"
        assert metadata.plugin_type == PluginType.STEALTH
        
        # Test initialization
        context = PluginContext(plugin_name="test", config={})
        result = await adapter.initialize(context)
        assert result.success is True
        
        # Test compatibility
        assert adapter.is_compatible("2.0.0") is True
        assert adapter.is_compatible("1.5.0") is True
    
    async def test_legacy_stealth_system_integration(self, temp_plugin_dir):
        """Test integration with legacy stealth system"""
        manager = PluginManager(plugin_directories=[temp_plugin_dir])
        await manager.initialize()
        
        # Integrate legacy stealth system
        integration = await integrate_legacy_stealth_system(manager)
        
        assert integration is not None
        assert len(integration.adapted_plugins) > 0
        
        # Check that stealth plugins were added to manager
        stealth_plugins = manager.list_plugins(PluginType.STEALTH)
        assert len(stealth_plugins) > 0
        
        await manager.shutdown()


@pytest.mark.asyncio
class TestFullIntegration:
    """Test full extensibility layer integration"""
    
    async def test_extensibility_layer_initialization(self, temp_plugin_dir):
        """Test complete extensibility layer initialization"""
        result = await initialize_extensibility_layer(
            plugin_directories=[temp_plugin_dir],
            enable_hot_reload=False,  # Disable for testing
            load_hooks_config=False,  # Skip hooks config loading
            start_mcp_server=False   # Skip MCP server for testing
        )
        
        assert result is not None
        assert 'plugin_manager' in result
        assert 'hook_system' in result
        assert 'stats' in result
        
        plugin_manager = result['plugin_manager']
        assert plugin_manager is not None
        assert len(plugin_manager.registry.plugin_directories) > 0
        
        await shutdown_extensibility_layer()
    
    async def test_plugin_lifecycle_management(self, temp_plugin_dir, sample_plugin_file):
        """Test complete plugin lifecycle"""
        # Initialize extensibility layer
        result = await initialize_extensibility_layer(
            plugin_directories=[temp_plugin_dir],
            enable_hot_reload=False
        )
        
        plugin_manager = result['plugin_manager']
        
        # Load plugin
        success = await plugin_manager.load_plugin("sample_plugin", sample_plugin_file)
        assert success is True
        
        # Execute plugin
        context = PluginContext(plugin_name="sample_plugin", config={})
        exec_result = await plugin_manager.execute_plugin("sample_plugin", context)
        assert exec_result.success is True
        
        # Disable plugin
        disable_success = await plugin_manager.disable_plugin("sample_plugin")
        assert disable_success is True
        
        plugin_info = plugin_manager.get_plugin_info("sample_plugin")
        assert plugin_info.state == PluginState.DISABLED
        
        # Re-enable plugin
        enable_success = await plugin_manager.enable_plugin("sample_plugin")
        assert enable_success is True
        
        plugin_info = plugin_manager.get_plugin_info("sample_plugin")
        assert plugin_info.state == PluginState.ACTIVE
        
        # Unload plugin
        unload_success = await plugin_manager.unload_plugin("sample_plugin")
        assert unload_success is True
        
        assert "sample_plugin" not in plugin_manager.registry.plugins
        
        await shutdown_extensibility_layer()


@pytest.mark.asyncio 
class TestErrorHandling:
    """Test error handling and edge cases"""
    
    async def test_plugin_loading_failure(self, temp_plugin_dir):
        """Test plugin loading failure handling"""
        manager = PluginManager(plugin_directories=[temp_plugin_dir])
        await manager.initialize()
        
        # Try to load non-existent plugin
        success = await manager.load_plugin("nonexistent_plugin")
        
        assert success is False
        assert manager.stats['plugins_failed'] > 0
        
        await manager.shutdown()
    
    async def test_plugin_execution_failure(self):
        """Test plugin execution failure handling"""
        manager = PluginManager(plugin_directories=[])
        
        # Register a failing plugin
        failing_plugin = MockPlugin("failing_plugin", should_fail=True)
        from src.extensibility.plugin_manager import PluginInfo
        
        plugin_info = PluginInfo(
            plugin=failing_plugin,
            metadata=failing_plugin.get_metadata(),
            state=PluginState.ACTIVE
        )
        
        manager.registry.plugins["failing_plugin"] = plugin_info
        
        # Try to execute failing plugin
        result = await manager.execute_plugin("failing_plugin")
        
        assert result.success is False
        assert "Mock execution failure" in result.error
        
        await manager.shutdown()
    
    async def test_hook_error_handling(self):
        """Test hook system error handling"""
        hook_system = HookSystem()
        
        # Register failing hook handler
        async def failing_handler(event):
            raise Exception("Handler failure")
        
        from src.extensibility.hooks import HookHandler
        handler = HookHandler(
            name="failing_handler",
            callback=failing_handler,
            async_handler=True
        )
        
        hook_system.register_hook_handler("test_hook", handler)
        
        # Trigger hook - should handle error gracefully
        result = await hook_system.trigger_hook("test_hook")
        
        assert result.success is False  # Overall chain failed due to error
        assert len(result.errors) > 0


if __name__ == "__main__":
    # Run basic smoke test
    async def smoke_test():
        print("Running extensibility layer smoke test...")
        
        # Test basic initialization
        result = await initialize_extensibility_layer(
            enable_hot_reload=False,
            load_hooks_config=False,
            start_mcp_server=False
        )
        
        print(f"✅ Initialization successful: {result['stats']}")
        
        # Test hook system
        from src.extensibility import get_hook_system, trigger_hook_event
        hook_system = get_hook_system()
        hook_result = await trigger_hook_event("test_hook", data="test")
        print(f"✅ Hook system working: {hook_result.success}")
        
        # Cleanup
        await shutdown_extensibility_layer()
        print("✅ Extensibility layer smoke test completed successfully")
    
    asyncio.run(smoke_test())