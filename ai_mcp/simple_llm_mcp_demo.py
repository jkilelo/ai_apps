"""
Simple Demo: LangGraph + llm.py + MCP Integration
Shows basic usage without complex ReAct patterns
"""

import asyncio
import sys
from pathlib import Path

# Add agents directory to path
agents_dir = Path(__file__).parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

# Import the existing wrapper (uses llm.py WITHOUT modification)
from langgraph_wrapper import get_langgraph_llm

# MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.messages import HumanMessage, SystemMessage


async def simple_llm_demo():
    """Demonstrate using llm.py through the wrapper."""
    print("\n" + "="*60)
    print("DEMO 1: Using llm.py (unmodified) via wrapper")
    print("="*60)

    # Get the LLM using existing wrapper
    llm = get_langgraph_llm(temperature=0.7)

    print("Testing llm.py integration...")

    # Simple conversation
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What model are you? Reply in one sentence.")
    ]

    response = llm.invoke(messages)
    print(f"LLM Response: {response.content}")

    print("\n[OK] llm.py is working through the wrapper!")


async def simple_mcp_demo():
    """Demonstrate using MCP tools directly."""
    print("\n" + "="*60)
    print("DEMO 2: Using MCP tools directly")
    print("="*60)

    mcp_server_path = Path(__file__).parent / "mcp_server.py"

    # Connect to MCP server
    server_params = StdioServerParameters(
        command="python",
        args=[str(mcp_server_path)],
        env=None
    )

    from contextlib import AsyncExitStack
    exit_stack = AsyncExitStack()

    try:
        print("Connecting to MCP server...")
        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport

        session = await exit_stack.enter_async_context(
            ClientSession(read, write)
        )

        await session.initialize()
        print("[OK] Connected to MCP server")

        # Call some tools
        print("\nCalling MCP tools:")

        # Get time
        result = await session.call_tool("get_current_time", {})
        print(f"1. Current time: {result.content[0].text}")

        # Calculate
        result = await session.call_tool("calculate", {"expression": "42 * 10"})
        print(f"2. Calculation (42 * 10): {result.content[0].text}")

        # Text operation
        result = await session.call_tool("text_operations", {
            "text": "hello mcp",
            "operation": "uppercase"
        })
        print(f"3. Text uppercase: {result.content[0].text}")

        print("\n[OK] MCP tools are working!")

    finally:
        await exit_stack.aclose()


async def combined_demo():
    """Simple combined usage of llm.py and MCP."""
    print("\n" + "="*60)
    print("DEMO 3: Combined llm.py + MCP (Manual Orchestration)")
    print("="*60)

    # Get LLM from llm.py wrapper
    llm = get_langgraph_llm(temperature=0.5)

    # Connect to MCP
    mcp_server_path = Path(__file__).parent / "mcp_server.py"
    server_params = StdioServerParameters(
        command="python",
        args=[str(mcp_server_path)],
        env=None
    )

    from contextlib import AsyncExitStack
    exit_stack = AsyncExitStack()

    try:
        # Connect to MCP
        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport
        session = await exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await session.initialize()

        print("Both llm.py and MCP are connected!")
        print("\nSimulating agent behavior manually:")

        # Step 1: User asks a question
        user_query = "What's the current time and what's 50 + 75?"
        print(f"\nUser: {user_query}")

        # Step 2: LLM decides what to do
        messages = [
            SystemMessage(content="You are analyzing what tools to use."),
            HumanMessage(content=f"What tools would you need to answer: '{user_query}'? List them.")
        ]

        llm_response = llm.invoke(messages)
        print(f"\nLLM Analysis: {llm_response.content[:200]}...")

        # Step 3: Execute tools (simulated decision)
        print("\nExecuting tools based on LLM's analysis:")

        # Get time
        time_result = await session.call_tool("get_current_time", {})
        print(f"- Time tool result: {time_result.content[0].text}")

        # Calculate
        calc_result = await session.call_tool("calculate", {"expression": "50 + 75"})
        print(f"- Calculator result: {calc_result.content[0].text}")

        # Step 4: LLM formats the final answer
        messages = [
            SystemMessage(content="Format a nice response based on tool results."),
            HumanMessage(content=f"User asked: '{user_query}'\n\nTool results:\n- Time: {time_result.content[0].text}\n- Calculation: {calc_result.content[0].text}\n\nProvide a friendly response.")
        ]

        final_response = llm.invoke(messages)
        print(f"\nFinal Response: {final_response.content}")

        print("\n[SUCCESS] Combined system working!")
        print("- llm.py provides reasoning (Gemini)")
        print("- MCP provides tools")
        print("- Manual orchestration connects them")

    finally:
        await exit_stack.aclose()


async def main():
    """Run all demos."""
    print("="*60)
    print("Simple Integration Demo")
    print("Using llm.py WITHOUT modification")
    print("="*60)

    # Check llm.py configuration
    try:
        from llm import get_api_key, model
        api_key = get_api_key()
        print(f"[OK] llm.py configured with {model}")
    except Exception as e:
        print(f"[WARNING] llm.py not fully configured: {e}")
        print("Some demos may have limited functionality")

    # Run demos
    await simple_llm_demo()
    await simple_mcp_demo()
    await combined_demo()

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("[OK] llm.py used WITHOUT modification (via import)")
    print("[OK] MCP tools work independently")
    print("[OK] Combined usage demonstrated")
    print("\nThe integration successfully combines:")
    print("  1. llm.py for LLM (Google Gemini)")
    print("  2. MCP for standardized tools")
    print("  3. Can be orchestrated manually or with LangGraph")


if __name__ == "__main__":
    asyncio.run(main())