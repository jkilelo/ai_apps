#!/usr/bin/env python3
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
