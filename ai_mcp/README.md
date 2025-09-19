# Simple MCP (Model Context Protocol) Implementation

A lean, fully functional implementation of MCP server and client in Python, following the 2025 specification.

## What is MCP?

The Model Context Protocol (MCP) is an open standard created by Anthropic for connecting AI models to external tools and data sources. It provides a universal protocol that replaces fragmented integrations with a single, standardized approach.

## Features

### MCP Server (`mcp_server.py`)
- **4 Built-in Tools:**
  - `get_current_time`: Returns current date and time
  - `calculate`: Safely evaluates mathematical expressions
  - `text_operations`: Performs text transformations (uppercase, lowercase, reverse, word count)
  - `todo_list`: Simple in-memory todo list manager

- **1 Resource:**
  - `config://server`: Server configuration information

- **1 Prompt Template:**
  - `analysis_prompt`: Generates structured analysis prompts

### MCP Client (`mcp_client.py`)
- Connect to any MCP server via stdio transport
- List available tools, resources, and prompts
- Execute tools with parameters
- Read resources
- Get prompt templates
- Interactive demo mode

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server Standalone

```bash
python mcp_server.py
```

The server will start and wait for client connections via stdio.

### Running the Client Demo

```bash
python mcp_client.py
```

This will:
1. Connect to the server
2. List all available tools, resources, and prompts
3. Demonstrate each tool with example calls
4. Show results in a formatted output

### Programmatic Client Usage

```python
import asyncio
from mcp_client import SimpleMCPClient

async def main():
    client = SimpleMCPClient()

    try:
        # Connect to server
        await client.connect()

        # Call a tool
        result = await client.call_tool("calculate", {"expression": "10 * 5"})
        print(f"Result: {result}")

        # Read a resource
        config = await client.read_resource("config://server")
        print(f"Config: {config}")

    finally:
        await client.disconnect()

asyncio.run(main())
```

## Architecture

```
┌─────────┐     stdio     ┌─────────┐
│  Client ├──────────────►│  Server │
└─────────┘               └─────────┘
     │                         │
     ├─ call_tool()           ├─ @mcp.tool()
     ├─ read_resource()       ├─ @mcp.resource()
     └─ get_prompt()          └─ @mcp.prompt()
```

## MCP 2025 Features Implemented

- ✅ JSON-RPC 2.0 message format
- ✅ Stdio transport
- ✅ Tools (executable functions)
- ✅ Resources (readable content)
- ✅ Prompts (templates)
- ✅ Async/await support
- ✅ FastMCP framework for simplified server creation
- ✅ Type hints and docstrings

## Adding Custom Tools

Edit `mcp_server.py` and add new tools using the decorator pattern:

```python
@mcp.tool()
async def my_custom_tool(param1: str, param2: int) -> dict:
    """
    Tool description here.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    # Your tool logic here
    return {"result": "success"}
```

## Security Considerations

- The `calculate` tool only allows safe mathematical operations
- No file system access by default
- Runs in isolated stdio transport mode
- Input validation on all tool parameters

## Next Steps

To extend this implementation:

1. **Add More Tools**: Weather API, database queries, file operations
2. **Implement SSE Transport**: For HTTP-based communication
3. **Add Authentication**: OAuth 2.1 resource server support
4. **Create Tool Packages**: Reusable tool collections
5. **Build UI Client**: Web interface for tool execution

## License

MIT

## References

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [Official Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Anthropic MCP Announcement](https://www.anthropic.com/news/model-context-protocol)