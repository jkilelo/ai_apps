"""Model Context Protocol (MCP) implementation for browser extensibility.

This module provides MCP server and client implementations to expose browser
capabilities as tools and connect to external MCP services for enhanced functionality.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Callable, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger

# MCP protocol types and interfaces
class MCPMessageType(Enum):
    """MCP message types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


class MCPMethod(Enum):
    """Standard MCP methods"""
    INITIALIZE = "initialize"
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"
    SAMPLING_CREATE_MESSAGE = "sampling/createMessage"


class MCPCapability(BaseModel):
    """MCP capability description"""
    name: str = Field(..., description="Capability name")
    version: Optional[str] = Field(None, description="Capability version")


class MCPServerInfo(BaseModel):
    """MCP server information"""
    name: str = Field(..., description="Server name")
    version: str = Field(..., description="Server version")
    protocol_version: str = Field("2024-11-05", description="MCP protocol version")
    capabilities: List[MCPCapability] = Field(default_factory=list)


class MCPClientInfo(BaseModel):
    """MCP client information"""
    name: str = Field(..., description="Client name")
    version: str = Field(..., description="Client version")


class MCPTool(BaseModel):
    """MCP tool definition"""
    name: str = Field(..., description="Tool name")
    description: Optional[str] = Field(None, description="Tool description")
    inputSchema: Dict[str, Any] = Field(..., description="JSON schema for input")


class MCPResource(BaseModel):
    """MCP resource definition"""
    uri: str = Field(..., description="Resource URI")
    name: str = Field(..., description="Resource name")
    description: Optional[str] = Field(None, description="Resource description")
    mimeType: Optional[str] = Field(None, description="MIME type")


class MCPPrompt(BaseModel):
    """MCP prompt definition"""
    name: str = Field(..., description="Prompt name")
    description: Optional[str] = Field(None, description="Prompt description")
    arguments: List[Dict[str, Any]] = Field(default_factory=list)


class MCPMessage(BaseModel):
    """Base MCP message"""
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    id: Optional[str] = Field(None, description="Message ID")
    method: Optional[str] = Field(None, description="Method name")
    params: Optional[Dict[str, Any]] = Field(None, description="Parameters")
    result: Optional[Any] = Field(None, description="Result data")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")


@dataclass
class MCPConnection:
    """MCP connection state"""
    connection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    connected: bool = False
    initialized: bool = False
    client_info: Optional[MCPClientInfo] = None
    server_info: Optional[MCPServerInfo] = None
    capabilities: List[str] = field(default_factory=list)
    last_activity: datetime = field(default_factory=datetime.now)


class MCPServer:
    """MCP Server implementation for exposing browser capabilities"""
    
    def __init__(
        self,
        name: str = "AI Browser",
        version: str = "2.0.0",
        plugin_manager: Optional['PluginManager'] = None
    ):
        self.server_info = MCPServerInfo(
            name=name,
            version=version,
            capabilities=[
                MCPCapability(name="tools"),
                MCPCapability(name="resources"),
                MCPCapability(name="prompts")
            ]
        )
        
        self.plugin_manager = plugin_manager
        self.connections: Dict[str, MCPConnection] = {}
        
        # Tool registry
        self.tools: Dict[str, MCPTool] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        
        # Resource registry
        self.resources: Dict[str, MCPResource] = {}
        self.resource_handlers: Dict[str, Callable] = {}
        
        # Prompt registry
        self.prompts: Dict[str, MCPPrompt] = {}
        self.prompt_handlers: Dict[str, Callable] = {}
        
        # Message handlers
        self.message_handlers = {
            MCPMethod.INITIALIZE.value: self._handle_initialize,
            MCPMethod.TOOLS_LIST.value: self._handle_tools_list,
            MCPMethod.TOOLS_CALL.value: self._handle_tools_call,
            MCPMethod.RESOURCES_LIST.value: self._handle_resources_list,
            MCPMethod.RESOURCES_READ.value: self._handle_resources_read,
            MCPMethod.PROMPTS_LIST.value: self._handle_prompts_list,
            MCPMethod.PROMPTS_GET.value: self._handle_prompts_get,
        }
        
        # Initialize default browser tools
        self._register_browser_tools()
    
    def _register_browser_tools(self) -> None:
        """Register default browser automation tools"""
        
        # Page navigation tool
        self.register_tool(
            name="navigate",
            description="Navigate to a URL",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to"
                    }
                },
                "required": ["url"]
            },
            handler=self._handle_navigate
        )
        
        # Element click tool
        self.register_tool(
            name="click",
            description="Click on an element",
            input_schema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for element"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to identify element"
                    }
                }
            },
            handler=self._handle_click
        )
        
        # Text input tool
        self.register_tool(
            name="type",
            description="Type text into an input field",
            input_schema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for input element"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    }
                },
                "required": ["selector", "text"]
            },
            handler=self._handle_type
        )
        
        # Page capture tool
        self.register_tool(
            name="capture_page",
            description="Capture page state (DOM + screenshot)",
            input_schema={
                "type": "object",
                "properties": {
                    "include_screenshot": {
                        "type": "boolean",
                        "description": "Include screenshot in capture",
                        "default": True
                    }
                }
            },
            handler=self._handle_capture_page
        )
        
        # Plugin execution tool
        if self.plugin_manager:
            self.register_tool(
                name="execute_plugin",
                description="Execute a loaded plugin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "plugin_name": {
                            "type": "string",
                            "description": "Name of plugin to execute"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Plugin execution parameters"
                        }
                    },
                    "required": ["plugin_name"]
                },
                handler=self._handle_execute_plugin
            )
    
    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable
    ) -> None:
        """Register a new MCP tool"""
        
        tool = MCPTool(
            name=name,
            description=description,
            inputSchema=input_schema
        )
        
        self.tools[name] = tool
        self.tool_handlers[name] = handler
        
        logger.debug(f"Registered MCP tool: {name}")
    
    def register_resource(
        self,
        uri: str,
        name: str,
        description: str,
        mime_type: str,
        handler: Callable
    ) -> None:
        """Register a new MCP resource"""
        
        resource = MCPResource(
            uri=uri,
            name=name,
            description=description,
            mimeType=mime_type
        )
        
        self.resources[uri] = resource
        self.resource_handlers[uri] = handler
        
        logger.debug(f"Registered MCP resource: {name}")
    
    def register_prompt(
        self,
        name: str,
        description: str,
        arguments: List[Dict[str, Any]],
        handler: Callable
    ) -> None:
        """Register a new MCP prompt"""
        
        prompt = MCPPrompt(
            name=name,
            description=description,
            arguments=arguments
        )
        
        self.prompts[name] = prompt
        self.prompt_handlers[name] = handler
        
        logger.debug(f"Registered MCP prompt: {name}")
    
    async def handle_message(self, message: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle incoming MCP message"""
        
        try:
            # Parse message
            mcp_message = MCPMessage(**message)
            
            # Update connection activity
            if connection_id in self.connections:
                self.connections[connection_id].last_activity = datetime.now()
            
            # Handle request
            if mcp_message.method:
                handler = self.message_handlers.get(mcp_message.method)
                if handler:
                    result = await handler(mcp_message, connection_id)
                    return {
                        "jsonrpc": "2.0",
                        "id": mcp_message.id,
                        "result": result
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": mcp_message.id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {mcp_message.method}"
                        }
                    }
            
            # Handle response (for client mode)
            if mcp_message.result or mcp_message.error:
                return await self._handle_response(mcp_message, connection_id)
            
        except Exception as e:
            logger.error(f"Error handling MCP message: {e}")
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _handle_initialize(self, message: MCPMessage, connection_id: str) -> Dict[str, Any]:
        """Handle initialize request"""
        
        # Extract client info
        params = message.params or {}
        client_info = MCPClientInfo(**params.get("clientInfo", {}))
        
        # Create or update connection
        if connection_id not in self.connections:
            self.connections[connection_id] = MCPConnection()
        
        connection = self.connections[connection_id]
        connection.client_info = client_info
        connection.server_info = self.server_info
        connection.initialized = True
        connection.connected = True
        
        logger.info(f"MCP client initialized: {client_info.name} v{client_info.version}")
        
        return {
            "serverInfo": self.server_info.dict(),
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"listChanged": True},
                "prompts": {"listChanged": True}
            }
        }
    
    async def _handle_tools_list(self, message: MCPMessage, connection_id: str) -> Dict[str, Any]:
        """Handle tools list request"""
        return {
            "tools": [tool.dict() for tool in self.tools.values()]
        }
    
    async def _handle_tools_call(self, message: MCPMessage, connection_id: str) -> Dict[str, Any]:
        """Handle tool call request"""
        
        params = message.params or {}
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tool_handlers:
            raise Exception(f"Tool not found: {tool_name}")
        
        handler = self.tool_handlers[tool_name]
        
        try:
            result = await handler(arguments)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing tool: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _handle_resources_list(self, message: MCPMessage, connection_id: str) -> Dict[str, Any]:
        """Handle resources list request"""
        return {
            "resources": [resource.dict() for resource in self.resources.values()]
        }
    
    async def _handle_resources_read(self, message: MCPMessage, connection_id: str) -> Dict[str, Any]:
        """Handle resource read request"""
        
        params = message.params or {}
        uri = params.get("uri")
        
        if uri not in self.resource_handlers:
            raise Exception(f"Resource not found: {uri}")
        
        handler = self.resource_handlers[uri]
        
        try:
            content = await handler(uri)
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": self.resources[uri].mimeType,
                        "text": content
                    }
                ]
            }
        except Exception as e:
            raise Exception(f"Error reading resource: {str(e)}")
    
    async def _handle_prompts_list(self, message: MCPMessage, connection_id: str) -> Dict[str, Any]:
        """Handle prompts list request"""
        return {
            "prompts": [prompt.dict() for prompt in self.prompts.values()]
        }
    
    async def _handle_prompts_get(self, message: MCPMessage, connection_id: str) -> Dict[str, Any]:
        """Handle prompt get request"""
        
        params = message.params or {}
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if prompt_name not in self.prompt_handlers:
            raise Exception(f"Prompt not found: {prompt_name}")
        
        handler = self.prompt_handlers[prompt_name]
        
        try:
            result = await handler(arguments)
            return result
        except Exception as e:
            raise Exception(f"Error generating prompt: {str(e)}")
    
    async def _handle_response(self, message: MCPMessage, connection_id: str) -> Dict[str, Any]:
        """Handle response message (for client mode)"""
        # This would be implemented if acting as a client
        pass
    
    # Browser tool handlers
    async def _handle_navigate(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle navigate tool call"""
        # This would integrate with the browser execution layer
        # For now, return a placeholder
        return {
            "status": "success",
            "message": f"Would navigate to: {arguments.get('url')}"
        }
    
    async def _handle_click(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle click tool call"""
        selector = arguments.get("selector")
        text = arguments.get("text")
        
        return {
            "status": "success",
            "message": f"Would click element: {selector or text}"
        }
    
    async def _handle_type(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle type tool call"""
        selector = arguments.get("selector")
        text = arguments.get("text")
        
        return {
            "status": "success",
            "message": f"Would type '{text}' into: {selector}"
        }
    
    async def _handle_capture_page(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capture page tool call"""
        include_screenshot = arguments.get("include_screenshot", True)
        
        return {
            "status": "success",
            "message": f"Would capture page (screenshot: {include_screenshot})"
        }
    
    async def _handle_execute_plugin(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle execute plugin tool call"""
        plugin_name = arguments.get("plugin_name")
        parameters = arguments.get("parameters", {})
        
        if not self.plugin_manager:
            return {
                "status": "error",
                "message": "Plugin manager not available"
            }
        
        try:
            result = await self.plugin_manager.execute_plugin(plugin_name, **parameters)
            return {
                "status": "success" if result.success else "error",
                "data": result.data,
                "error": result.error
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


class MCPClient:
    """MCP Client implementation for connecting to external MCP servers"""
    
    def __init__(
        self,
        name: str = "AI Browser Client",
        version: str = "2.0.0"
    ):
        self.client_info = MCPClientInfo(name=name, version=version)
        self.connections: Dict[str, MCPConnection] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        
        # Available tools, resources, and prompts from connected servers
        self.available_tools: Dict[str, Dict[str, MCPTool]] = {}  # server_id -> tools
        self.available_resources: Dict[str, Dict[str, MCPResource]] = {}  # server_id -> resources
        self.available_prompts: Dict[str, Dict[str, MCPPrompt]] = {}  # server_id -> prompts
    
    async def connect(self, server_id: str, transport: Any) -> bool:
        """Connect to an MCP server"""
        
        try:
            # Create connection
            connection = MCPConnection(connection_id=server_id)
            self.connections[server_id] = connection
            
            # Send initialize request
            init_message = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "clientInfo": self.client_info.dict()
                }
            }
            
            response = await self._send_request(server_id, init_message)
            
            if response and "result" in response:
                # Process server info
                server_info_data = response["result"].get("serverInfo", {})
                connection.server_info = MCPServerInfo(**server_info_data)
                connection.initialized = True
                connection.connected = True
                
                # Discover available capabilities
                await self._discover_capabilities(server_id)
                
                logger.info(f"Connected to MCP server: {connection.server_info.name}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {server_id}: {e}")
        
        return False
    
    async def disconnect(self, server_id: str) -> None:
        """Disconnect from an MCP server"""
        
        if server_id in self.connections:
            connection = self.connections[server_id]
            connection.connected = False
            
            # Clean up
            del self.connections[server_id]
            if server_id in self.available_tools:
                del self.available_tools[server_id]
            if server_id in self.available_resources:
                del self.available_resources[server_id]
            if server_id in self.available_prompts:
                del self.available_prompts[server_id]
            
            logger.info(f"Disconnected from MCP server: {server_id}")
    
    async def _discover_capabilities(self, server_id: str) -> None:
        """Discover available tools, resources, and prompts from server"""
        
        # Discover tools
        try:
            tools_response = await self._send_request(server_id, {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/list"
            })
            
            if tools_response and "result" in tools_response:
                tools_data = tools_response["result"].get("tools", [])
                self.available_tools[server_id] = {
                    tool_data["name"]: MCPTool(**tool_data)
                    for tool_data in tools_data
                }
                logger.debug(f"Discovered {len(self.available_tools[server_id])} tools from {server_id}")
        
        except Exception as e:
            logger.warning(f"Failed to discover tools from {server_id}: {e}")
        
        # Discover resources
        try:
            resources_response = await self._send_request(server_id, {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "resources/list"
            })
            
            if resources_response and "result" in resources_response:
                resources_data = resources_response["result"].get("resources", [])
                self.available_resources[server_id] = {
                    resource_data["uri"]: MCPResource(**resource_data)
                    for resource_data in resources_data
                }
                logger.debug(f"Discovered {len(self.available_resources[server_id])} resources from {server_id}")
        
        except Exception as e:
            logger.warning(f"Failed to discover resources from {server_id}: {e}")
        
        # Discover prompts
        try:
            prompts_response = await self._send_request(server_id, {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "prompts/list"
            })
            
            if prompts_response and "result" in prompts_response:
                prompts_data = prompts_response["result"].get("prompts", [])
                self.available_prompts[server_id] = {
                    prompt_data["name"]: MCPPrompt(**prompt_data)
                    for prompt_data in prompts_data
                }
                logger.debug(f"Discovered {len(self.available_prompts[server_id])} prompts from {server_id}")
        
        except Exception as e:
            logger.warning(f"Failed to discover prompts from {server_id}: {e}")
    
    async def call_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a tool on a connected MCP server"""
        
        if server_id not in self.connections:
            raise Exception(f"Not connected to server: {server_id}")
        
        if (server_id not in self.available_tools or
            tool_name not in self.available_tools[server_id]):
            raise Exception(f"Tool not available: {tool_name}")
        
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(server_id, request)
        
        if response and "result" in response:
            return response["result"]
        elif response and "error" in response:
            raise Exception(f"Tool call error: {response['error']['message']}")
        else:
            raise Exception("No response received")
    
    async def read_resource(self, server_id: str, uri: str) -> str:
        """Read a resource from a connected MCP server"""
        
        if server_id not in self.connections:
            raise Exception(f"Not connected to server: {server_id}")
        
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "resources/read",
            "params": {"uri": uri}
        }
        
        response = await self._send_request(server_id, request)
        
        if response and "result" in response:
            contents = response["result"].get("contents", [])
            if contents:
                return contents[0].get("text", "")
        elif response and "error" in response:
            raise Exception(f"Resource read error: {response['error']['message']}")
        
        return ""
    
    async def get_prompt(
        self,
        server_id: str,
        prompt_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get a prompt from a connected MCP server"""
        
        if server_id not in self.connections:
            raise Exception(f"Not connected to server: {server_id}")
        
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "prompts/get",
            "params": {
                "name": prompt_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(server_id, request)
        
        if response and "result" in response:
            return response["result"]
        elif response and "error" in response:
            raise Exception(f"Prompt error: {response['error']['message']}")
        
        return {}
    
    async def _send_request(self, server_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to MCP server (transport-specific implementation needed)"""
        # This would need to be implemented with actual transport
        # (WebSocket, stdio, etc.)
        
        # Placeholder implementation
        logger.debug(f"Would send MCP request to {server_id}: {message['method']}")
        
        # Return mock response for tools/list as example
        if message['method'] == 'tools/list':
            return {
                "jsonrpc": "2.0",
                "id": message["id"],
                "result": {
                    "tools": []
                }
            }
        
        return {"jsonrpc": "2.0", "id": message["id"], "result": {}}
    
    def list_available_tools(self) -> Dict[str, List[str]]:
        """List all available tools by server"""
        return {
            server_id: list(tools.keys())
            for server_id, tools in self.available_tools.items()
        }
    
    def list_available_resources(self) -> Dict[str, List[str]]:
        """List all available resources by server"""
        return {
            server_id: list(resources.keys())
            for server_id, resources in self.available_resources.items()
        }
    
    def list_available_prompts(self) -> Dict[str, List[str]]:
        """List all available prompts by server"""
        return {
            server_id: list(prompts.keys())
            for server_id, prompts in self.available_prompts.items()
        }
    
    def get_connection_status(self) -> Dict[str, bool]:
        """Get connection status for all servers"""
        return {
            server_id: connection.connected
            for server_id, connection in self.connections.items()
        }


# Utility functions for MCP integration

async def create_mcp_server(
    name: str = "AI Browser",
    plugin_manager: Optional['PluginManager'] = None,
    additional_tools: Optional[Dict[str, Callable]] = None
) -> MCPServer:
    """Create and configure an MCP server"""
    
    server = MCPServer(name=name, plugin_manager=plugin_manager)
    
    # Register additional tools if provided
    if additional_tools:
        for tool_name, handler in additional_tools.items():
            # This would need proper schema definition
            server.register_tool(
                name=tool_name,
                description=f"Custom tool: {tool_name}",
                input_schema={"type": "object"},
                handler=handler
            )
    
    return server


async def create_mcp_client(name: str = "AI Browser Client") -> MCPClient:
    """Create and configure an MCP client"""
    return MCPClient(name=name)