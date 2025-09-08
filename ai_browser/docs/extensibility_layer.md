# Extensibility Layer Documentation

## Overview

The Extensibility Layer provides a robust plugin system, Model Context Protocol (MCP) support, and comprehensive hook integration for the AI-First Smart Browser. It enables third-party extensions while maintaining security through sandboxed execution.

**Layer Position**: Layer 5 of 5 in the AI-First Smart Browser architecture

**Core Responsibility**: Plugin management, protocol integration, and system extensibility

## Architecture Compliance

### ✅ What This Layer CAN Do:
- Load and manage plugins dynamically
- Execute plugins in sandboxed environments
- Expose browser capabilities via MCP
- Connect to external MCP services
- Integrate with all other layers
- Manage hooks and event handlers
- Support hot-reload in development

### ❌ What This Layer CANNOT Do:
- Execute untrusted code without sandboxing
- Allow plugins unlimited resource access
- Bypass security restrictions
- Modify core architecture
- Access system resources directly

## Components

### 1. Plugin Interfaces (`interfaces.py`)

Defines the contract for all plugins.

**Core Interfaces:**

#### IPlugin (Base Interface)
```python
class IPlugin(ABC):
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None
    @abstractmethod
    async def execute(self, context: PluginContext) -> PluginResult
    @abstractmethod
    async def cleanup(self) -> None
    @abstractmethod
    def get_metadata(self) -> PluginMetadata
```

#### Specialized Interfaces
- **IStealthPlugin**: Bot detection evasion
- **IAnalysisPlugin**: Page analysis and extraction
- **IOptimizationPlugin**: Performance optimization

**Data Models:**
```python
class PluginMetadata(BaseModel):
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    capabilities: List[str]
    config_schema: Optional[Dict[str, Any]]
```

### 2. Plugin Sandbox (`sandbox.py`)

Provides secure execution environment for plugins.

**Security Features:**
- Resource limits (CPU, memory, execution time)
- Import restrictions with whitelisting
- File system access control
- Static code validation
- Violation tracking and reporting

**Configuration:**
```python
config = SandboxConfig(
    max_memory_mb=100,
    max_execution_time_seconds=30,
    allowed_imports=["re", "json", "datetime"],
    file_access=FileAccessPolicy.READ_ONLY,
    network_access=False
)
```

**Usage:**
```python
sandbox = PluginSandbox(config)
result = await sandbox.execute_plugin(plugin, context)
if result.violations:
    logger.warning(f"Security violations: {result.violations}")
```

### 3. Hook System (`hooks.py`)

Event-driven plugin integration system.

**Hook Types:**
- **PreToolUse**: Before tool execution
- **PostToolUse**: After tool execution
- **UserPromptSubmit**: When user submits prompt
- **SessionStart**: Session initialization
- **Stop**: Task completion
- **Notification**: System notifications

**Configuration (`.claude/hooks.json`):**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "name": "Code Quality Check",
        "matcher": "Write|Edit",
        "pathMatcher": ".*\\.py$",
        "hooks": [
          {
            "type": "command",
            "command": "ruff check $FILE_PATH --fix"
          }
        ]
      }
    ]
  }
}
```

**Integration:**
```python
hook_system = HookSystem()
await hook_system.load_config(".claude/hooks.json")
await hook_system.emit("PostToolUse", context)
```

### 4. Plugin Manager (`plugin_manager.py`)

Central management system for all plugins.

**Features:**
- Dynamic plugin discovery
- Dependency resolution
- Hot-reload support
- Lifecycle management
- Version compatibility checking

**Plugin Directories:**
```python
PLUGIN_DIRS = [
    "plugins/stealth",      # Stealth evasion plugins
    "plugins/analysis",     # Page analysis plugins
    "plugins/optimization", # Performance plugins
    "plugins/custom"        # User custom plugins
]
```

**Usage:**
```python
manager = PluginManager()
await manager.discover_plugins()
await manager.load_plugin("example_stealth_plugin")
result = await manager.execute_plugin(
    "example_stealth_plugin",
    context
)
```

### 5. MCP Protocol (`mcp.py`)

Model Context Protocol implementation for AI interoperability.

#### MCPServer
Exposes browser capabilities as tools.

**Exposed Tools:**
- `browser_navigate`: Navigate to URL
- `browser_click`: Click elements
- `browser_extract`: Extract page data
- `browser_screenshot`: Capture screenshots

**Server Setup:**
```python
server = MCPServer("AI Browser MCP Server")
server.register_tool(
    "browser_navigate",
    browser_navigate_handler,
    description="Navigate browser to URL"
)
await server.start(port=8080)
```

#### MCPClient
Connects to external MCP services.

```python
client = MCPClient("external-service-url")
tools = await client.discover_tools()
result = await client.execute_tool(
    "external_tool",
    {"param": "value"}
)
```

### 6. Stealth Adapter (`stealth_adapter.py`)

Bridges existing stealth system with new plugin architecture.

**Features:**
- Backward compatibility
- Automatic adaptation
- Legacy plugin support
- Migration utilities

```python
adapter = StealthAdapter(stealth_manager)
plugin = adapter.create_plugin_from_legacy(legacy_plugin)
await manager.register_plugin(plugin)
```

## Plugin Development Guide

### Creating a Basic Plugin

```python
from extensibility.interfaces import IPlugin, PluginMetadata, PluginResult

class MyPlugin(IPlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            description="Example plugin",
            author="Developer",
            dependencies=[],
            capabilities=["example"]
        )
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        
    async def execute(self, context: PluginContext) -> PluginResult:
        # Plugin logic here
        return PluginResult(
            success=True,
            data={"message": "Plugin executed"}
        )
    
    async def cleanup(self) -> None:
        # Cleanup resources
        pass
```

### Stealth Plugin Example

```python
class WebDriverEvasion(IStealthPlugin):
    async def apply_to_context(self, context: BrowserContext) -> None:
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
    
    async def test_effectiveness(self, page: Page) -> Dict[str, Any]:
        detected = await page.evaluate("navigator.webdriver")
        return {"webdriver_hidden": detected is None}
```

## Security Considerations

### Sandbox Security Levels

1. **STRICT** (Default)
   - No file system access
   - No network access
   - Limited imports
   - Resource limits enforced

2. **MODERATE**
   - Read-only file access
   - Local network only
   - Extended import list
   - Relaxed resource limits

3. **TRUSTED**
   - Full file system access
   - Network access allowed
   - All imports allowed
   - No resource limits

### Security Best Practices

1. **Always validate plugin metadata** before loading
2. **Use appropriate sandbox level** based on plugin trust
3. **Monitor resource usage** during execution
4. **Log all security violations** for audit
5. **Implement plugin signing** for production
6. **Regular security audits** of plugin code
7. **User consent** for privileged operations

## Hook System Integration

### Available Hooks

| Hook Type | Trigger | Use Case |
|-----------|---------|----------|
| PreToolUse | Before tool execution | Validation, modification |
| PostToolUse | After tool execution | Cleanup, formatting |
| UserPromptSubmit | User input | Analysis, routing |
| SessionStart | Session begins | Initialization |
| Stop | Task complete | Summary, cleanup |
| Notification | System events | Alerts, logging |

### Hook Configuration

Hooks are configured in `.claude/hooks.json`:
- **matcher**: Regex pattern for tool names
- **pathMatcher**: Regex for file paths
- **command**: Shell command to execute
- **async**: Run asynchronously
- **blocking**: Block until complete

## MCP Protocol Integration

### Server Capabilities

The MCP server exposes:
- Browser automation tools
- Page state extraction
- Screenshot capture
- Element interaction
- Navigation control

### Client Integration

Connect to external services:
```python
# Connect to external LLM service
llm_client = MCPClient("http://llm-service:8080")
tools = await llm_client.discover_tools()

# Use external tool
result = await llm_client.execute_tool(
    "analyze_text",
    {"text": page_content}
)
```

## Performance Optimization

### Plugin Loading
- Lazy loading on first use
- Dependency resolution caching
- Parallel initialization when possible

### Execution Optimization
- Resource pooling
- Result caching
- Async execution
- Batch processing support

### Hot Reload
Development mode supports:
- File watching (requires watchdog)
- Automatic reload on changes
- State preservation
- Zero-downtime updates

## Testing Plugins

### Unit Testing
```python
@pytest.mark.asyncio
async def test_plugin():
    plugin = MyPlugin()
    context = PluginContext(data={"test": True})
    result = await plugin.execute(context)
    assert result.success
```

### Integration Testing
```python
@pytest.mark.asyncio
async def test_plugin_in_sandbox():
    sandbox = PluginSandbox()
    manager = PluginManager()
    await manager.load_plugin("my_plugin")
    result = await manager.execute_plugin(
        "my_plugin",
        context,
        sandbox=sandbox
    )
    assert result.success
```

## Troubleshooting

### Common Issues

#### Plugin Not Loading
- Check metadata validity
- Verify dependencies
- Check file permissions
- Review logs for errors

#### Sandbox Violations
- Review allowed imports
- Check resource limits
- Verify file access needs
- Consider security level

#### Hook Not Triggering
- Verify matcher pattern
- Check hook configuration
- Review execution order
- Check async/sync settings

#### MCP Connection Failed
- Verify server URL
- Check network access
- Review authentication
- Check protocol version

## API Reference

### PluginManager
- `discover_plugins()`: Find all plugins
- `load_plugin(name)`: Load specific plugin
- `execute_plugin(name, context)`: Run plugin
- `unload_plugin(name)`: Remove plugin
- `reload_plugin(name)`: Hot reload

### HookSystem
- `load_config(path)`: Load hooks.json
- `emit(event, context)`: Trigger hooks
- `register_handler(event, handler)`: Add handler
- `unregister_handler(event, handler)`: Remove

### MCPServer
- `register_tool(name, handler)`: Add tool
- `start(port)`: Start server
- `stop()`: Stop server

### MCPClient
- `discover_tools()`: Get available tools
- `execute_tool(name, params)`: Run tool
- `subscribe(event)`: Event subscription

## Future Enhancements

- [ ] Plugin marketplace integration
- [ ] Digital signing for plugins
- [ ] Plugin dependency management
- [ ] Visual plugin builder
- [ ] Plugin performance profiling
- [ ] Advanced sandboxing with containers
- [ ] Plugin version management
- [ ] Automated plugin testing

---

*Last Updated: 2025-01-05 | Layer: Extensibility (5/5) | Status: Production Ready*