"""
Simple MCP Server Implementation
A lean, fully functional MCP server with basic tools
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Simple MCP Server")

@mcp.tool()
async def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
async def calculate(expression: str) -> float:
    """
    Safely evaluate a mathematical expression.

    Args:
        expression: A mathematical expression (e.g., "2 + 2", "10 * 5")

    Returns:
        The result of the calculation
    """
    # Only allow safe mathematical operations
    allowed_chars = "0123456789+-*/()., "
    if all(c in allowed_chars for c in expression):
        try:
            result = eval(expression)
            return float(result)
        except Exception as e:
            return f"Error: {str(e)}"
    else:
        return "Error: Invalid characters in expression"

@mcp.tool()
async def text_operations(text: str, operation: str) -> str:
    """
    Perform various text operations.

    Args:
        text: The input text
        operation: The operation to perform (uppercase, lowercase, reverse, wordcount)

    Returns:
        The processed text or result
    """
    operations_map = {
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "reverse": text[::-1],
        "wordcount": str(len(text.split()))
    }

    return operations_map.get(operation, "Unknown operation")

@mcp.tool()
async def todo_list(action: str, item: str = "") -> Dict[str, Any]:
    """
    Simple todo list manager.

    Args:
        action: Action to perform (add, remove, list)
        item: Todo item (required for add/remove)

    Returns:
        Current todo list or confirmation message
    """
    if not hasattr(todo_list, "items"):
        todo_list.items = []

    if action == "add" and item:
        todo_list.items.append(item)
        return {"message": f"Added: {item}", "todos": todo_list.items}
    elif action == "remove" and item:
        if item in todo_list.items:
            todo_list.items.remove(item)
            return {"message": f"Removed: {item}", "todos": todo_list.items}
        return {"message": "Item not found", "todos": todo_list.items}
    elif action == "list":
        return {"todos": todo_list.items}
    else:
        return {"error": "Invalid action or missing item"}

@mcp.resource("config://server")
async def get_server_config() -> str:
    """Get server configuration information."""
    return """
    Server Configuration:
    - Name: Simple MCP Server
    - Version: 1.0.0
    - Transport: stdio
    - Tools: 4 (get_current_time, calculate, text_operations, todo_list)
    - Status: Running
    """

@mcp.prompt()
async def analysis_prompt(topic: str) -> str:
    """
    Generate an analysis prompt for a given topic.

    Args:
        topic: The topic to analyze

    Returns:
        A structured prompt for analysis
    """
    return f"""
    Please analyze the following topic: {topic}

    Consider the following aspects:
    1. Key concepts and definitions
    2. Current state and trends
    3. Challenges and opportunities
    4. Future outlook

    Provide a comprehensive but concise analysis.
    """

if __name__ == "__main__":
    # Run the server using stdio transport
    print("Starting Simple MCP Server...")
    print("Server is ready to accept connections via stdio")
    mcp.run(transport="stdio")