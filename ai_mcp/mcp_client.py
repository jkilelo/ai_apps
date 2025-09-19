"""
Simple MCP Client Implementation
A lean client to connect to MCP servers and execute tools
"""
import asyncio
import json
from typing import Optional, Dict, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class SimpleMCPClient:
    """Simple MCP Client for connecting to MCP servers."""

    def __init__(self, server_command: str = "python", server_args: list = None):
        """
        Initialize the MCP client.

        Args:
            server_command: Command to start the server
            server_args: Arguments for the server command
        """
        self.server_command = server_command
        self.server_args = server_args or ["mcp_server.py"]
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect(self):
        """Connect to the MCP server."""
        try:
            # Set up server parameters
            server_params = StdioServerParameters(
                command=self.server_command,
                args=self.server_args,
                env=None
            )

            # Create stdio client and session
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            stdio, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(stdio, write)
            )

            # Initialize the session
            result = await self.session.initialize()

            print("[OK] Connected to MCP server successfully!")
            if result and hasattr(result, 'server_info'):
                print(f"  Server: {result.server_info.name if result.server_info else 'Unknown'}")
                print(f"  Version: {result.server_info.version if result.server_info else 'Unknown'}")
            else:
                print("  Server: Connected via stdio")
                print("  Version: 1.0.0")

        except Exception as e:
            print(f"[ERROR] Failed to connect to server: {e}")
            raise

    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.exit_stack:
            await self.exit_stack.aclose()
            print("[OK] Disconnected from server")

    async def list_tools(self) -> list:
        """List all available tools from the server."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        result = await self.session.list_tools()
        return result.tools if result else []

    async def list_resources(self) -> list:
        """List all available resources from the server."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        result = await self.session.list_resources()
        return result.resources if result else []

    async def list_prompts(self) -> list:
        """List all available prompts from the server."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        result = await self.session.list_prompts()
        return result.prompts if result else []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the server.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            The result from the tool
        """
        if not self.session:
            raise RuntimeError("Not connected to server")

        result = await self.session.call_tool(tool_name, arguments)
        return result.content if result else None

    async def read_resource(self, resource_uri: str) -> Any:
        """
        Read a resource from the server.

        Args:
            resource_uri: URI of the resource to read

        Returns:
            The resource content
        """
        if not self.session:
            raise RuntimeError("Not connected to server")

        result = await self.session.read_resource(resource_uri)
        return result.contents if result else None

    async def get_prompt(self, prompt_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Get a prompt from the server.

        Args:
            prompt_name: Name of the prompt to get
            arguments: Arguments for the prompt

        Returns:
            The prompt content
        """
        if not self.session:
            raise RuntimeError("Not connected to server")

        result = await self.session.get_prompt(prompt_name, arguments)
        return result.messages if result else None


async def interactive_demo():
    """Run an interactive demo of the MCP client."""
    client = SimpleMCPClient()

    try:
        # Connect to server
        print("Connecting to MCP server...")
        await client.connect()
        print()

        # List available tools
        print("Available Tools:")
        print("-" * 40)
        tools = await client.list_tools()
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        print()

        # List available resources
        print("Available Resources:")
        print("-" * 40)
        resources = await client.list_resources()
        for resource in resources:
            print(f"  - {resource.uri}: {resource.name}")
        print()

        # List available prompts
        print("Available Prompts:")
        print("-" * 40)
        prompts = await client.list_prompts()
        for prompt in prompts:
            print(f"  - {prompt.name}: {prompt.description}")
        print()

        # Demo tool calls
        print("Tool Demonstrations:")
        print("=" * 40)

        # 1. Get current time
        print("\n1. Getting current time...")
        result = await client.call_tool("get_current_time", {})
        if result and len(result) > 0:
            print(f"   Current time: {result[0].text}")

        # 2. Calculate
        print("\n2. Performing calculation...")
        result = await client.call_tool("calculate", {"expression": "42 * 10 + 7"})
        if result and len(result) > 0:
            print(f"   42 * 10 + 7 = {result[0].text}")

        # 3. Text operations
        print("\n3. Text operations...")
        result = await client.call_tool("text_operations", {
            "text": "Hello MCP World",
            "operation": "uppercase"
        })
        if result and len(result) > 0:
            print(f"   Uppercase: {result[0].text}")

        result = await client.call_tool("text_operations", {
            "text": "Hello MCP World",
            "operation": "reverse"
        })
        if result and len(result) > 0:
            print(f"   Reversed: {result[0].text}")

        # 4. Todo list
        print("\n4. Todo list operations...")
        result = await client.call_tool("todo_list", {
            "action": "add",
            "item": "Learn MCP"
        })
        if result and len(result) > 0:
            print(f"   Added: {result[0].text}")

        result = await client.call_tool("todo_list", {
            "action": "add",
            "item": "Build MCP tools"
        })
        if result and len(result) > 0:
            print(f"   Added: {result[0].text}")

        result = await client.call_tool("todo_list", {
            "action": "list"
        })
        if result and len(result) > 0:
            print(f"   Current todos: {result[0].text}")

        # 5. Read resource
        print("\n5. Reading server config resource...")
        result = await client.read_resource("config://server")
        if result:
            print(f"   {result[0].text if result else 'No content'}")

        # 6. Get prompt
        print("\n6. Getting analysis prompt...")
        result = await client.get_prompt("analysis_prompt", {"topic": "MCP Protocol"})
        if result:
            print(f"   {result[0].content.text if result else 'No prompt'}")

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")

    finally:
        # Disconnect
        print("\nDisconnecting...")
        await client.disconnect()


async def programmatic_example():
    """Example of using the client programmatically."""
    client = SimpleMCPClient()

    try:
        await client.connect()

        # Use the client to call tools
        time_result = await client.call_tool("get_current_time", {})
        calc_result = await client.call_tool("calculate", {"expression": "100 / 4"})

        print(f"Current time: {time_result}")
        print(f"100 / 4 = {calc_result}")

    finally:
        await client.disconnect()


if __name__ == "__main__":
    print("=" * 50)
    print("Simple MCP Client Demo")
    print("=" * 50)
    print()

    # Run the interactive demo
    asyncio.run(interactive_demo())