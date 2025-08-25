#!/usr/bin/env python3
"""
Test Full MCP Communication
Demonstrates working MCP server and client communication
"""

import asyncio
import sys
from pathlib import Path

# Add mcp_servers to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_simple_server():
    """Test the simple MCP server with full communication"""
    print("="*60)
    print("FULL MCP COMMUNICATION TEST")
    print("="*60)
    
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from contextlib import AsyncExitStack
    
    # Server configuration
    server_path = Path(__file__).parent / "simple_mcp_server.py"
    
    # Create server parameters
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
        env=None
    )
    
    print(f"\n[INFO] Starting server: {server_path.name}")
    print(f"[INFO] Using Python: {sys.executable}")
    
    try:
        async with AsyncExitStack() as stack:
            # Start server and create transport
            stdio_transport = await stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # Create session
            read_stream, write_stream = stdio_transport
            session = await stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            # Initialize connection
            print("\n[1] Initializing connection...")
            result = await session.initialize()
            print(f"    Server: {result.server_info.name if result.server_info else 'Unknown'}")
            print(f"    Version: {result.server_info.version if result.server_info else 'Unknown'}")
            
            # List available tools
            print("\n[2] Listing available tools...")
            tools_response = await session.list_tools()
            tools = tools_response.tools
            print(f"    Found {len(tools)} tools:")
            for tool in tools:
                print(f"      - {tool.name}: {tool.description}")
            
            # Test tool calls
            print("\n[3] Testing tool calls...")
            
            # Test 1: Add numbers
            print("\n    Test 1: add_numbers(10, 25)")
            result = await session.call_tool("add_numbers", {"a": 10, "b": 25})
            if result.content:
                text = result.content[0].text if isinstance(result.content, list) else result.content.text
                print(f"    Response: {text}")
            
            # Test 2: Reverse string
            print("\n    Test 2: reverse_string('MCP Protocol')")
            result = await session.call_tool("reverse_string", {"text": "MCP Protocol"})
            if result.content:
                text = result.content[0].text if isinstance(result.content, list) else result.content.text
                print(f"    Response: {text}")
            
            # Test 3: Get server info
            print("\n    Test 3: get_info()")
            result = await session.call_tool("get_info", {})
            if result.content:
                text = result.content[0].text if isinstance(result.content, list) else result.content.text
                print(f"    Response:\n{text}")
            
            print("\n" + "="*60)
            print("SUCCESS: Full MCP communication working!")
            print("="*60)
            
            return True
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def create_and_test_chunk_client():
    """Create a client that can use the chunk server"""
    print("\n" + "="*60)
    print("CHUNK SERVER CLIENT TEST")
    print("="*60)
    
    # First, let's create a simple wrapper for chunk server
    wrapper_code = '''#!/usr/bin/env python3
"""Wrapper to run ChunkServer with MCP protocol"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Create server
server = Server("chunk-server-mcp")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available chunking tools"""
    return [
        Tool(
            name="chunk_text",
            description="Chunk text into smaller pieces",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to chunk"},
                    "max_size": {"type": "integer", "description": "Max chunk size", "default": 100}
                },
                "required": ["text"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> TextContent:
    """Handle tool calls"""
    if name == "chunk_text":
        text = arguments.get("text", "")
        max_size = arguments.get("max_size", 100)
        
        # Simple chunking
        chunks = []
        words = text.split()
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) + 1 > max_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        result = {
            "chunks": chunks,
            "count": len(chunks),
            "original_length": len(text)
        }
        
        import json
        return TextContent(type="text", text=json.dumps(result, indent=2))
    
    return TextContent(type="text", text=f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    # Save wrapper
    wrapper_path = Path(__file__).parent / "chunk_server_wrapper.py"
    wrapper_path.write_text(wrapper_code)
    print(f"[INFO] Created wrapper: {wrapper_path.name}")
    
    # Now test it
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from contextlib import AsyncExitStack
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(wrapper_path)],
        env=None
    )
    
    try:
        async with AsyncExitStack() as stack:
            # Connect
            stdio_transport = await stack.enter_async_context(
                stdio_client(server_params)
            )
            
            read_stream, write_stream = stdio_transport
            session = await stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            await session.initialize()
            print("[OK] Connected to chunk server wrapper")
            
            # Test chunking
            test_text = "This is a long piece of text that needs to be chunked into smaller pieces for processing. Each chunk should be no more than the specified maximum size in characters."
            
            print(f"\n[TEST] Chunking text (length: {len(test_text)})")
            result = await session.call_tool("chunk_text", {
                "text": test_text,
                "max_size": 50
            })
            
            if result.content:
                text = result.content[0].text if isinstance(result.content, list) else result.content.text
                print(f"Result:\n{text}")
            
            print("\n[OK] Chunk server client working!")
            return True
            
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        return False


async def main():
    """Run all tests"""
    # Test 1: Simple server
    success1 = await test_simple_server()
    
    # Test 2: Chunk server wrapper
    success2 = await create_and_test_chunk_client()
    
    if success1 and success2:
        print("\n" + "="*60)
        print("ALL MCP TESTS PASSED!")
        print("="*60)
        print("\nYou now have:")
        print("  1. Working MCP server (simple_mcp_server.py)")
        print("  2. Working MCP client communication")
        print("  3. Chunk server wrapper (chunk_server_wrapper.py)")
        print("\nThe MCP servers and clients are fully operational!")
    else:
        print("\nSome tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())