#!/usr/bin/env python3
"""
Working MCP Client
A client that can communicate with MCP servers using the official SDK
"""

import asyncio
import logging
from typing import Optional, Any, Dict
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClient:
    """MCP Client using the official SDK"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
    
    async def connect_to_server(self, server_script_path: str) -> bool:
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server Python script
        
        Returns:
            True if connected successfully
        """
        try:
            # Create server parameters for stdio connection
            server_params = StdioServerParameters(
                command="python",
                args=[server_script_path],
                env=None
            )
            
            # Start the server process and create stdio transport
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # Unpack the transport
            read_stream, write_stream = stdio_transport
            
            # Create and initialize the session
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            # Initialize the connection
            await self.session.initialize()
            
            logger.info("Successfully connected to MCP server")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    async def list_tools(self) -> list:
        """List available tools from the server"""
        if not self.session:
            logger.error("Not connected to server")
            return []
        
        try:
            response = await self.session.list_tools()
            tools = response.tools if hasattr(response, 'tools') else []
            logger.info(f"Available tools: {[tool.name for tool in tools]}")
            return tools
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """Call a tool on the server
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
        
        Returns:
            Tool result as string or None if failed
        """
        if not self.session:
            logger.error("Not connected to server")
            return None
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            
            # Extract text from result
            if hasattr(result, 'content'):
                if isinstance(result.content, list) and len(result.content) > 0:
                    return result.content[0].text
                elif hasattr(result.content, 'text'):
                    return result.content.text
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Failed to call tool '{tool_name}': {e}")
            return None
    
    async def disconnect(self):
        """Disconnect from the server"""
        await self.exit_stack.aclose()
        logger.info("Disconnected from server")


async def test_simple_server():
    """Test the simple MCP server"""
    print("\n" + "="*60)
    print("TESTING SIMPLE MCP SERVER")
    print("="*60)
    
    client = MCPClient()
    
    # Use the full path to Python in venv
    import sys
    server_path = r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_tools\mcp_servers\simple_mcp_server.py"
    
    # Update server parameters to use the venv Python
    from mcp import StdioServerParameters
    server_params = StdioServerParameters(
        command=sys.executable,  # Use current Python executable
        args=[server_path],
        env=None
    )
    
    # Connect using the custom parameters
    try:
        # Create transport
        from mcp.client.stdio import stdio_client
        async with AsyncExitStack() as stack:
            stdio_transport = await stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # Create session
            read_stream, write_stream = stdio_transport
            session = await stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            # Initialize
            await session.initialize()
            print("[OK] Connected to server")
            
            # List tools
            response = await session.list_tools()
            tools = response.tools if hasattr(response, 'tools') else []
            print(f"\nAvailable tools:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test add_numbers tool
            print("\n[TEST] Calling add_numbers(5, 3)...")
            result = await session.call_tool("add_numbers", {"a": 5, "b": 3})
            if result and hasattr(result, 'content'):
                if isinstance(result.content, list):
                    print(f"Result: {result.content[0].text}")
                else:
                    print(f"Result: {result.content}")
            
            # Test reverse_string tool
            print("\n[TEST] Calling reverse_string('Hello MCP')...")
            result = await session.call_tool("reverse_string", {"text": "Hello MCP"})
            if result and hasattr(result, 'content'):
                if isinstance(result.content, list):
                    print(f"Result: {result.content[0].text}")
                else:
                    print(f"Result: {result.content}")
            
            # Test get_info tool
            print("\n[TEST] Calling get_info()...")
            result = await session.call_tool("get_info", {})
            if result and hasattr(result, 'content'):
                if isinstance(result.content, list):
                    print(f"Result: {result.content[0].text}")
                else:
                    print(f"Result: {result.content}")
            
            print("\n[OK] All tests completed successfully!")
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_chunk_server():
    """Test the ChunkServer"""
    print("\n" + "="*60)
    print("TESTING CHUNK SERVER")
    print("="*60)
    
    import sys
    server_path = r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_tools\mcp_servers\chunk_server_fixed.py"
    
    from mcp import StdioServerParameters
    from mcp.client.stdio import stdio_client
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_path],
        env=None
    )
    
    try:
        async with AsyncExitStack() as stack:
            # Start server
            stdio_transport = await stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # Create session
            read_stream, write_stream = stdio_transport
            session = await stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            # Initialize
            await session.initialize()
            print("[OK] Connected to ChunkServer")
            
            # List available tools
            response = await session.list_tools()
            tools = response.tools if hasattr(response, 'tools') else []
            print(f"\nAvailable tools in ChunkServer:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n[OK] ChunkServer is accessible via MCP!")
            
    except Exception as e:
        print(f"[ERROR] Failed to connect to ChunkServer: {e}")


async def main():
    """Run all tests"""
    # Test simple server first
    await test_simple_server()
    
    # Then test the actual ChunkServer
    await test_chunk_server()
    
    print("\n" + "="*60)
    print("MCP CLIENT TESTING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())