#!/usr/bin/env python3
"""
MCP Client Implementation
Allows direct communication with MCP servers via stdio
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import AsyncExitStack
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import MCP SDK, fall back to custom implementation
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_SDK_AVAILABLE = True
except ImportError:
    MCP_SDK_AVAILABLE = False
    logger.warning("MCP SDK not available, using custom implementation")


class JSONRPCMessage:
    """JSON-RPC 2.0 message builder"""
    
    _id_counter = 0
    
    @classmethod
    def create_request(cls, method: str, params: Optional[Dict] = None) -> Dict:
        """Create a JSON-RPC request"""
        cls._id_counter += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": cls._id_counter
        }
        if params:
            request["params"] = params
        return request
    
    @classmethod
    def create_notification(cls, method: str, params: Optional[Dict] = None) -> Dict:
        """Create a JSON-RPC notification (no response expected)"""
        notification = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params:
            notification["params"] = params
        return notification


class StdioTransport:
    """Handle stdio communication with server process"""
    
    def __init__(self, process: subprocess.Popen):
        self.process = process
        self._closed = False
    
    async def send(self, message: Dict) -> None:
        """Send a message to the server"""
        if self._closed:
            raise RuntimeError("Transport is closed")
        
        json_str = json.dumps(message)
        data = f"Content-Length: {len(json_str)}\r\n\r\n{json_str}"
        
        self.process.stdin.write(data.encode())
        self.process.stdin.flush()
        logger.debug(f"Sent: {message}")
    
    async def receive(self) -> Optional[Dict]:
        """Receive a message from the server"""
        if self._closed:
            return None
        
        # Read Content-Length header
        header_line = self.process.stdout.readline().decode().strip()
        if not header_line:
            return None
        
        if not header_line.startswith("Content-Length:"):
            logger.error(f"Invalid header: {header_line}")
            return None
        
        content_length = int(header_line.split(":")[1].strip())
        
        # Read empty line after header
        self.process.stdout.readline()
        
        # Read the JSON content
        content = self.process.stdout.read(content_length).decode()
        
        try:
            message = json.loads(content)
            logger.debug(f"Received: {message}")
            return message
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return None
    
    def close(self):
        """Close the transport"""
        if not self._closed:
            self._closed = True
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()


class MCPClient:
    """MCP Client for communicating with servers"""
    
    def __init__(self):
        self.transport: Optional[StdioTransport] = None
        self.server_process: Optional[subprocess.Popen] = None
        self.exit_stack = AsyncExitStack()
        self.tools: Dict[str, Any] = {}
        self.resources: Dict[str, Any] = {}
        self.prompts: List[Any] = []
    
    async def connect(self, server_path: str, python_path: Optional[str] = None) -> bool:
        """Connect to an MCP server
        
        Args:
            server_path: Path to the server Python file
            python_path: Optional path to Python executable
        """
        try:
            # Use provided Python or default
            if python_path is None:
                python_path = sys.executable
            
            logger.info(f"Starting server: {server_path}")
            
            # Start the server process
            self.server_process = subprocess.Popen(
                [python_path, server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False
            )
            
            # Create transport
            self.transport = StdioTransport(self.server_process)
            
            # Initialize connection
            await self._initialize()
            
            logger.info("Successfully connected to MCP server")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    async def _initialize(self) -> None:
        """Initialize the MCP session"""
        # Send initialize request
        init_request = JSONRPCMessage.create_request(
            "initialize",
            {
                "protocolVersion": "0.1.0",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "mcp-python-client",
                    "version": "1.0.0"
                }
            }
        )
        
        await self.transport.send(init_request)
        
        # Wait for response
        response = await self.transport.receive()
        if response and "result" in response:
            logger.info(f"Server info: {response['result'].get('serverInfo', {})}")
            
            # List available tools
            await self._list_tools()
            
            # Send initialized notification
            initialized = JSONRPCMessage.create_notification("notifications/initialized")
            await self.transport.send(initialized)
    
    async def _list_tools(self) -> None:
        """List available tools from the server"""
        list_request = JSONRPCMessage.create_request("tools/list")
        await self.transport.send(list_request)
        
        response = await self.transport.receive()
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            for tool in tools:
                self.tools[tool["name"]] = tool
            logger.info(f"Available tools: {list(self.tools.keys())}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """Call a tool on the server
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool result or None if failed
        """
        if tool_name not in self.tools:
            logger.error(f"Tool '{tool_name}' not found")
            return None
        
        call_request = JSONRPCMessage.create_request(
            "tools/call",
            {
                "name": tool_name,
                "arguments": arguments
            }
        )
        
        await self.transport.send(call_request)
        
        response = await self.transport.receive()
        if response and "result" in response:
            return response["result"]
        elif response and "error" in response:
            logger.error(f"Tool call error: {response['error']}")
        
        return None
    
    async def disconnect(self):
        """Disconnect from the server"""
        if self.transport:
            self.transport.close()
            self.transport = None
        
        if self.server_process:
            self.server_process = None
        
        logger.info("Disconnected from MCP server")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


async def test_mcp_client():
    """Test the MCP client with a server"""
    
    # Path to Python and server
    python_path = r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.venv\Scripts\python.exe"
    server_path = r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_tools\mcp_servers\chunk_server_fixed.py"
    
    print("="*60)
    print("MCP CLIENT TEST")
    print("="*60)
    
    async with MCPClient() as client:
        # Connect to server
        print(f"\nConnecting to: {Path(server_path).name}")
        connected = await client.connect(server_path, python_path)
        
        if connected:
            print("✅ Connected successfully!")
            
            # Show available tools
            print(f"\nAvailable tools: {list(client.tools.keys())}")
            
            # Try to call a tool (example)
            if "chunk_code" in client.tools:
                print("\nCalling chunk_code tool...")
                result = await client.call_tool(
                    "chunk_code",
                    {
                        "content": "def hello():\n    print('Hello')",
                        "strategy": "semantic",
                        "max_size": 100
                    }
                )
                
                if result:
                    print(f"Result: {result}")
                else:
                    print("No result received")
            
            # Small delay before disconnecting
            await asyncio.sleep(1)
            
        else:
            print("❌ Failed to connect")
    
    print("\n✅ Test completed")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_mcp_client())