"""
LangGraph + MCP Integration with llm.py
Uses the EXISTING llm.py from agents directory WITHOUT modification
Combines MCP tools with the Google Gemini model from llm.py
"""

import sys
import os
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add agents directory to path to import existing modules
agents_dir = Path(__file__).parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

# Try to use enhanced wrapper, fall back to original if needed
try:
    # Try the enhanced wrapper with tool binding support
    from langgraph_llm_wrapper_enhanced import get_langgraph_llm_with_tools as get_langgraph_llm
    print("[INFO] Using enhanced wrapper with tool binding support")
except ImportError:
    # Fall back to original wrapper
    from langgraph_wrapper import get_langgraph_llm
    print("[INFO] Using original wrapper (limited tool support)")

# MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient

# LangGraph imports
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool


class LangGraphLLMMCPAgent:
    """
    Integration class that combines:
    1. The existing llm.py (via langgraph_wrapper) for the LLM
    2. MCP servers for tools
    3. LangGraph for agent orchestration

    This class DOES NOT modify llm.py in any way.
    """

    def __init__(self, temperature: float = 0.7, model_kwargs: Optional[Dict] = None):
        """
        Initialize the integrated agent.

        Args:
            temperature: Temperature for the LLM (passed to llm.py's wrapper)
            model_kwargs: Additional kwargs for the model
        """
        # Get the LLM from the existing wrapper (which uses llm.py)
        self.model_kwargs = model_kwargs or {}
        self.model_kwargs['temperature'] = temperature

        # This uses the EXISTING llm.py via the wrapper
        self.llm = get_langgraph_llm(**self.model_kwargs)

        self.agent = None
        self.mcp_client = None
        self.tools = []

    async def connect_mcp_and_build_agent(
        self,
        mcp_server_path: Optional[str] = None,
        server_configs: Optional[Dict[str, Dict]] = None,
        additional_tools: Optional[List] = None
    ):
        """
        Connect to MCP servers and build the agent with combined tools.

        Args:
            mcp_server_path: Path to a single MCP server (optional)
            server_configs: Configuration for multiple MCP servers (optional)
            additional_tools: Additional LangChain tools to include (optional)
        """
        mcp_tools = []

        # Connect to MCP server(s) if provided
        if mcp_server_path:
            print(f"Connecting to MCP server: {mcp_server_path}")
            mcp_tools = await self._connect_single_mcp_server(mcp_server_path)

        elif server_configs:
            print("Connecting to multiple MCP servers...")
            mcp_tools = await self._connect_multiple_mcp_servers(server_configs)

        # Combine MCP tools with additional tools
        self.tools = mcp_tools + (additional_tools or [])

        print(f"Building ReAct agent with {len(self.tools)} tools and llm.py model...")

        # Create the ReAct agent using llm.py's model and all tools
        self.agent = create_react_agent(self.llm, self.tools)

        print("[OK] Agent ready with llm.py model and MCP tools!")

    async def _connect_single_mcp_server(self, server_path: str) -> List:
        """Connect to a single MCP server and get its tools."""
        from contextlib import AsyncExitStack

        server_params = StdioServerParameters(
            command="python",
            args=[server_path],
            env=None
        )

        self.exit_stack = AsyncExitStack()

        try:
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport

            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )

            await session.initialize()

            # Load MCP tools
            tools = await load_mcp_tools(session)
            print(f"[OK] Loaded {len(tools)} tools from MCP server")

            return tools

        except Exception as e:
            print(f"[ERROR] Failed to connect to MCP server: {e}")
            return []

    async def _connect_multiple_mcp_servers(self, server_configs: Dict[str, Dict]) -> List:
        """Connect to multiple MCP servers and get their tools."""
        try:
            self.mcp_client = MultiServerMCPClient(server_configs)
            tools = await self.mcp_client.get_tools()
            print(f"[OK] Loaded {len(tools)} tools from {len(server_configs)} servers")
            return tools

        except Exception as e:
            print(f"[ERROR] Failed to connect to MCP servers: {e}")
            return []

    async def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a message to the agent and get a response.
        Uses llm.py for reasoning and MCP tools for actions.

        Args:
            message: The user message
            system_prompt: Optional system prompt

        Returns:
            The agent's response
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call connect_mcp_and_build_agent() first.")

        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))

        print(f"\nUser: {message}")
        print("Agent (using llm.py) thinking...")

        # The agent uses llm.py for reasoning and MCP tools for actions
        response = await self.agent.ainvoke({"messages": messages})

        final_message = response["messages"][-1].content
        print(f"Agent: {final_message}")

        return final_message

    async def disconnect(self):
        """Disconnect from MCP servers."""
        if hasattr(self, 'exit_stack'):
            await self.exit_stack.aclose()
            print("[OK] Disconnected from MCP")


def create_custom_tools():
    """Create some custom LangChain tools to demonstrate flexibility."""

    @tool
    def get_llm_info() -> str:
        """Get information about the LLM being used."""
        # Import llm.py to get model info WITHOUT modification
        from llm import model as llm_model, get_api_key

        try:
            # Check if API key is configured
            api_key = get_api_key()
            key_status = "configured" if api_key else "not configured"
        except:
            key_status = "not configured"

        return f"Using model: {llm_model} (Google Gemini) via llm.py. API key: {key_status}"

    @tool
    def python_eval(code: str) -> str:
        """Evaluate Python code and return the result."""
        try:
            # Safety check - only allow simple expressions
            if any(danger in code.lower() for danger in ['import', 'exec', 'eval', '__']):
                return "Error: Unsafe code detected"

            result = eval(code)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

    return [get_llm_info, python_eval]


async def demo():
    """
    Demonstration of the integrated system.
    Shows how llm.py, MCP tools, and LangGraph work together.
    """
    print("="*60)
    print("LangGraph + llm.py + MCP Integration Demo")
    print("="*60)
    print("\nThis demo uses:")
    print("1. llm.py for the LLM (Google Gemini) - NO MODIFICATIONS")
    print("2. MCP server for tools")
    print("3. LangGraph for agent orchestration")
    print("="*60)

    # Create the integrated agent
    agent = LangGraphLLMMCPAgent(temperature=0.7)

    # Path to our MCP server
    mcp_server_path = str(Path(__file__).parent / "mcp_server.py")

    # Get custom tools
    custom_tools = create_custom_tools()

    try:
        # Connect to MCP and build agent with all tools
        await agent.connect_mcp_and_build_agent(
            mcp_server_path=mcp_server_path,
            additional_tools=custom_tools
        )

        print("\n" + "="*60)
        print("Testing the integrated agent...")
        print("="*60)

        # Test queries that use both llm.py reasoning and MCP tools
        queries = [
            "What LLM are you using?",  # Uses custom tool
            "What's the current time?",  # Uses MCP tool
            "Calculate 42 * 10 + 7",     # Uses MCP tool
            "Add 'Test llm.py integration' to my todo list",  # Uses MCP tool
            "What's 15 + 27? Use the python_eval tool",  # Uses custom tool
            "Convert 'hello world' to uppercase",  # Uses MCP tool
        ]

        for query in queries:
            await agent.chat(query)
            print("-" * 40)
            await asyncio.sleep(1)

    finally:
        await agent.disconnect()


async def production_example():
    """
    Production-ready example showing how to use the integration.
    """
    print("\n" + "="*60)
    print("Production Example: Multi-Server Configuration")
    print("="*60)

    # Create agent with specific model parameters
    agent = LangGraphLLMMCPAgent(
        temperature=0.5,
        model_kwargs={
            "max_tokens": 1000,
            "top_p": 0.9
        }
    )

    # Configure multiple servers (if available)
    server_configs = {
        "local_mcp": {
            "command": "python",
            "args": [str(Path(__file__).parent / "mcp_server.py")],
            "transport": "stdio"
        }
        # Add more servers as needed
    }

    try:
        # Build agent with multiple servers
        await agent.connect_mcp_and_build_agent(
            server_configs=server_configs,
            additional_tools=create_custom_tools()
        )

        # Use with system prompt for better control
        system_prompt = """You are a helpful assistant that uses available tools when appropriate.
        You have access to MCP tools and custom tools. Use them to provide accurate information."""

        # Interactive session
        result = await agent.chat(
            "Tell me about yourself, then check the time and calculate 100/4",
            system_prompt=system_prompt
        )

    finally:
        await agent.disconnect()


if __name__ == "__main__":
    print("LangGraph + llm.py + MCP Integration")
    print("This uses the EXISTING llm.py WITHOUT any modifications")
    print()

    # Check if llm.py is properly configured
    try:
        from llm import get_api_key, model
        api_key = get_api_key()
        print(f"[OK] llm.py configured with {model}")
    except Exception as e:
        print(f"[WARNING] llm.py configuration issue: {e}")
        print("Make sure GEMINI_API_KEY or GOOGLE_API_KEY is set in environment")

    # Run the demo
    asyncio.run(demo())

    # Run production example
    asyncio.run(production_example())

    print("\n[SUCCESS] Integration complete!")
    print("The system successfully combines:")
    print("  - llm.py (unmodified) for Google Gemini LLM")
    print("  - MCP servers for standardized tools")
    print("  - LangGraph for agent orchestration")