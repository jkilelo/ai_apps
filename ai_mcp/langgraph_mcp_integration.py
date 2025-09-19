"""
LangGraph + MCP Integration Example
Demonstrates how to use MCP servers with LangGraph agents
"""

import asyncio
import os
from typing import Dict, Any, List
from contextlib import AsyncExitStack

# MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LangChain/LangGraph imports
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


class LangGraphMCPAgent:
    """
    A LangGraph agent that integrates with MCP servers.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the agent with a specific model."""
        self.model_name = model_name
        self.model = None
        self.agent = None
        self.mcp_client = None

    async def connect_single_server(self, server_path: str):
        """
        Connect to a single MCP server and create an agent with its tools.

        Args:
            server_path: Path to the MCP server Python file
        """
        print(f"Connecting to MCP server: {server_path}")

        # Create server parameters for stdio connection
        server_params = StdioServerParameters(
            command="python",
            args=[server_path],
            env=None
        )

        # Use async context managers for proper resource management
        self.exit_stack = AsyncExitStack()

        try:
            # Connect to MCP server
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport

            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )

            # Initialize the connection
            await session.initialize()
            print("[OK] Connected to MCP server")

            # Load MCP tools
            tools = await load_mcp_tools(session)
            print(f"[OK] Loaded {len(tools)} tools from MCP server")

            # List available tools
            for tool in tools:
                print(f"  - {tool.name}: {tool.description[:60]}...")

            # Create the model
            self.model = ChatOpenAI(
                model=self.model_name,
                temperature=0
            )

            # Create ReAct agent with MCP tools
            self.agent = create_react_agent(self.model, tools)
            print(f"[OK] Created ReAct agent with {self.model_name}")

        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            await self.exit_stack.aclose()
            raise

    async def connect_multiple_servers(self, server_configs: Dict[str, Dict]):
        """
        Connect to multiple MCP servers and create an agent with combined tools.

        Args:
            server_configs: Dictionary mapping server names to configurations

        Example:
            {
                "math": {
                    "command": "python",
                    "args": ["/path/to/math_server.py"],
                    "transport": "stdio"
                },
                "weather": {
                    "url": "http://localhost:8000/mcp",
                    "transport": "streamable_http"
                }
            }
        """
        print("Connecting to multiple MCP servers...")

        try:
            # Create multi-server client
            self.mcp_client = MultiServerMCPClient(server_configs)

            # Get all tools from all servers
            tools = await self.mcp_client.get_tools()
            print(f"[OK] Loaded {len(tools)} tools from {len(server_configs)} servers")

            # List tools by server
            for server_name in server_configs:
                print(f"\nServer: {server_name}")
                server_tools = [t for t in tools if server_name in str(t)]
                for tool in server_tools[:3]:  # Show first 3 tools
                    print(f"  - {tool.name}")

            # Create the model
            self.model = ChatOpenAI(
                model=self.model_name,
                temperature=0
            )

            # Create ReAct agent with combined tools
            self.agent = create_react_agent(self.model, tools)
            print(f"\n[OK] Created ReAct agent with all tools")

        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            raise

    async def chat(self, message: str) -> str:
        """
        Send a message to the agent and get a response.

        Args:
            message: The user message

        Returns:
            The agent's response
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call connect_* method first.")

        print(f"\nUser: {message}")
        print("Agent thinking...")

        # Invoke the agent
        response = await self.agent.ainvoke({
            "messages": [HumanMessage(content=message)]
        })

        # Extract the final message
        final_message = response["messages"][-1].content

        print(f"Agent: {final_message}")
        return final_message

    async def batch_chat(self, messages: List[str]) -> List[str]:
        """
        Process multiple messages in batch.

        Args:
            messages: List of user messages

        Returns:
            List of agent responses
        """
        responses = []
        for message in messages:
            response = await self.chat(message)
            responses.append(response)
        return responses

    async def disconnect(self):
        """Disconnect from MCP servers."""
        if hasattr(self, 'exit_stack'):
            await self.exit_stack.aclose()
            print("[OK] Disconnected from MCP server")
        if self.mcp_client:
            # MultiServerMCPClient cleanup if needed
            pass


async def demo_single_server():
    """Demo using our custom MCP server with LangGraph."""
    print("=" * 60)
    print("LangGraph + Single MCP Server Demo")
    print("=" * 60)

    # Path to our MCP server
    mcp_server_path = r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_mcp\mcp_server.py"

    # Create agent
    agent = LangGraphMCPAgent(model_name="gpt-4o-mini")

    try:
        # Connect to MCP server
        await agent.connect_single_server(mcp_server_path)

        # Test various capabilities
        queries = [
            "What time is it?",
            "Calculate 42 * 10 + 7",
            "Convert 'hello world' to uppercase",
            "Add 'Learn LangGraph' to my todo list",
            "What's on my todo list?",
            "Reverse the text 'LangGraph MCP Integration'"
        ]

        for query in queries:
            await agent.chat(query)
            await asyncio.sleep(1)  # Small delay between queries

    finally:
        await agent.disconnect()


async def demo_multiple_servers():
    """Demo using multiple MCP servers with LangGraph."""
    print("=" * 60)
    print("LangGraph + Multiple MCP Servers Demo")
    print("=" * 60)

    # Configure multiple servers
    server_configs = {
        "local_tools": {
            "command": "python",
            "args": [r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ai_mcp\mcp_server.py"],
            "transport": "stdio"
        }
        # Add more servers here as needed
        # "weather": {
        #     "url": "http://localhost:8000/mcp",
        #     "transport": "streamable_http"
        # }
    }

    # Create agent
    agent = LangGraphMCPAgent(model_name="gpt-4o-mini")

    try:
        # Connect to multiple servers
        await agent.connect_multiple_servers(server_configs)

        # Test combined capabilities
        await agent.chat("What tools do you have available?")
        await agent.chat("Calculate the sum of 100 and 200, then tell me the current time")

    except Exception as e:
        print(f"Demo failed: {e}")


async def demo_without_openai():
    """Demo showing the structure without requiring OpenAI API."""
    print("=" * 60)
    print("LangGraph + MCP Structure Demo (No API Key Required)")
    print("=" * 60)

    print("\nThis demo shows the integration structure.")
    print("To run with actual LLM, set OPENAI_API_KEY environment variable.")

    print("\n1. Single Server Connection:")
    print("   - Connect to MCP server via stdio")
    print("   - Load tools using load_mcp_tools()")
    print("   - Create ReAct agent with create_react_agent()")

    print("\n2. Multiple Server Connection:")
    print("   - Use MultiServerMCPClient")
    print("   - Combine tools from multiple sources")
    print("   - Single agent with access to all tools")

    print("\n3. Agent Capabilities:")
    print("   - Reasoning and Acting (ReAct) pattern")
    print("   - Tool calling based on user queries")
    print("   - Context awareness across conversations")

    print("\n4. Available MCP Tools from our server:")
    print("   - get_current_time: Get current date/time")
    print("   - calculate: Evaluate math expressions")
    print("   - text_operations: Text transformations")
    print("   - todo_list: Manage a todo list")


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if os.getenv("OPENAI_API_KEY"):
        print("OpenAI API key detected. Running full demo...\n")

        # Run single server demo
        asyncio.run(demo_single_server())

        print("\n" + "=" * 60 + "\n")

        # Run multiple server demo
        asyncio.run(demo_multiple_servers())
    else:
        print("No OpenAI API key found.")
        print("Set OPENAI_API_KEY environment variable to run the full demo.")
        print("")

        # Run structure demo without API
        asyncio.run(demo_without_openai())