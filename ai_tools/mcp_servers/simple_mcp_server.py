#!/usr/bin/env python3
"""
Simple MCP Server for Testing
A minimal working MCP server that exposes tools via stdio
"""

import asyncio
import json
from typing import Any, Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Create server instance
server = Server("simple-test-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="add_numbers",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="reverse_string",
            description="Reverse a string",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to reverse"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="get_info",
            description="Get server information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> TextContent:
    """Handle tool calls"""
    
    if name == "add_numbers":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a + b
        return TextContent(type="text", text=f"Result: {a} + {b} = {result}")
    
    elif name == "reverse_string":
        text = arguments.get("text", "")
        reversed_text = text[::-1]
        return TextContent(type="text", text=f"Reversed: '{reversed_text}'")
    
    elif name == "get_info":
        info = {
            "server": "Simple Test Server",
            "version": "1.0.0",
            "status": "running",
            "tools": ["add_numbers", "reverse_string", "get_info"]
        }
        return TextContent(type="text", text=json.dumps(info, indent=2))
    
    else:
        return TextContent(type="text", text=f"Unknown tool: {name}")

async def main():
    """Run the server"""
    # Run server via stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())