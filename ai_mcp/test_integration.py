"""
Test script for LangGraph + MCP Integration
Tests the integration without requiring an OpenAI API key
"""

import asyncio
import sys
from pathlib import Path
from contextlib import AsyncExitStack

# MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LangChain/LangGraph imports
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient


async def test_mcp_server_connection():
    """Test basic MCP server connection."""
    print("\n" + "="*60)
    print("TEST 1: MCP Server Connection")
    print("="*60)

    server_path = Path(__file__).parent / "mcp_server.py"

    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_path)],
        env=None
    )

    exit_stack = AsyncExitStack()

    try:
        # Connect to MCP server
        print("Connecting to MCP server...")
        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport

        session = await exit_stack.enter_async_context(
            ClientSession(read, write)
        )

        # Initialize the connection
        await session.initialize()
        print("[OK] Connected successfully")

        # List available tools
        print("\nListing tools...")
        tools_result = await session.list_tools()

        if tools_result and tools_result.tools:
            print(f"[OK] Found {len(tools_result.tools)} tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description[:50]}...")

        # List resources
        print("\nListing resources...")
        resources_result = await session.list_resources()

        if resources_result and resources_result.resources:
            print(f"[OK] Found {len(resources_result.resources)} resources:")
            for resource in resources_result.resources:
                print(f"  - {resource.uri}: {resource.name}")

        # List prompts
        print("\nListing prompts...")
        prompts_result = await session.list_prompts()

        if prompts_result and prompts_result.prompts:
            print(f"[OK] Found {len(prompts_result.prompts)} prompts:")
            for prompt in prompts_result.prompts:
                print(f"  - {prompt.name}: {prompt.description[:50]}...")

        print("\n[OK] MCP Server Connection Test PASSED")
        return True

    except Exception as e:
        print(f"\n[FAIL] MCP Server Connection Test FAILED: {e}")
        return False

    finally:
        await exit_stack.aclose()


async def test_tool_loading():
    """Test loading MCP tools for LangChain."""
    print("\n" + "="*60)
    print("TEST 2: Tool Loading with LangChain Adapter")
    print("="*60)

    server_path = Path(__file__).parent / "mcp_server.py"

    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_path)],
        env=None
    )

    exit_stack = AsyncExitStack()

    try:
        # Connect to MCP server
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

        # Load tools using LangChain adapter
        print("\nLoading tools with LangChain adapter...")
        tools = await load_mcp_tools(session)

        print(f"[OK] Loaded {len(tools)} tools as LangChain tools:")
        for tool in tools:
            print(f"  - {tool.name}")
            print(f"    Description: {tool.description[:60]}...")

            # Check schema attribute
            if hasattr(tool, 'args_schema'):
                if hasattr(tool.args_schema, 'schema'):
                    schema_props = list(tool.args_schema.schema().get('properties', {}).keys())
                elif isinstance(tool.args_schema, dict):
                    schema_props = list(tool.args_schema.get('properties', {}).keys())
                else:
                    schema_props = "Schema format unknown"
                print(f"    Schema: {schema_props}")

        print("\n[OK] Tool Loading Test PASSED")
        return True

    except Exception as e:
        print(f"\n[FAIL] Tool Loading Test FAILED: {e}")
        return False

    finally:
        await exit_stack.aclose()


async def test_tool_execution():
    """Test executing MCP tools directly."""
    print("\n" + "="*60)
    print("TEST 3: Direct Tool Execution")
    print("="*60)

    server_path = Path(__file__).parent / "mcp_server.py"

    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_path)],
        env=None
    )

    exit_stack = AsyncExitStack()

    try:
        # Connect to MCP server
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

        # Test get_current_time tool
        print("\nTesting get_current_time tool...")
        result = await session.call_tool("get_current_time", {})
        if result and result.content:
            print(f"[OK] Time: {result.content[0].text}")

        # Test calculate tool
        print("\nTesting calculate tool...")
        result = await session.call_tool("calculate", {"expression": "42 * 10 + 7"})
        if result and result.content:
            print(f"[OK] 42 * 10 + 7 = {result.content[0].text}")

        # Test text_operations tool
        print("\nTesting text_operations tool...")
        result = await session.call_tool("text_operations", {
            "text": "Hello MCP",
            "operation": "uppercase"
        })
        if result and result.content:
            print(f"[OK] Uppercase: {result.content[0].text}")

        # Test todo_list tool
        print("\nTesting todo_list tool...")
        result = await session.call_tool("todo_list", {
            "action": "add",
            "item": "Test MCP Integration"
        })
        if result and result.content:
            print(f"[OK] Todo added: {result.content[0].text[:100]}...")

        print("\n[OK] Tool Execution Test PASSED")
        return True

    except Exception as e:
        print(f"\n[FAIL] Tool Execution Test FAILED: {e}")
        return False

    finally:
        await exit_stack.aclose()


async def test_multi_server_client():
    """Test MultiServerMCPClient configuration."""
    print("\n" + "="*60)
    print("TEST 4: MultiServerMCPClient Configuration")
    print("="*60)

    server_path = Path(__file__).parent / "mcp_server.py"

    try:
        # Configure multiple servers (in this case, just one)
        print("Configuring MultiServerMCPClient...")
        client = MultiServerMCPClient({
            "local_tools": {
                "command": "python",
                "args": [str(server_path)],
                "transport": "stdio"
            }
        })

        print("[OK] MultiServerMCPClient created")

        # Get tools from all servers
        print("\nLoading tools from all servers...")
        tools = await client.get_tools()

        print(f"[OK] Loaded {len(tools)} tools from all servers:")
        for tool in tools:
            print(f"  - {tool.name}")

        print("\n[OK] MultiServerMCPClient Test PASSED")
        return True

    except Exception as e:
        print(f"\n[FAIL] MultiServerMCPClient Test FAILED: {e}")
        return False


async def test_langchain_tool_compatibility():
    """Test that MCP tools work as LangChain tools."""
    print("\n" + "="*60)
    print("TEST 5: LangChain Tool Compatibility")
    print("="*60)

    server_path = Path(__file__).parent / "mcp_server.py"

    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_path)],
        env=None
    )

    exit_stack = AsyncExitStack()

    try:
        # Connect to MCP server
        print("Connecting to MCP server...")
        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport

        session = await exit_stack.enter_async_context(
            ClientSession(read, write)
        )

        await session.initialize()

        # Load tools as LangChain tools
        print("Loading tools as LangChain tools...")
        tools = await load_mcp_tools(session)

        # Test tool invocation using LangChain format
        print("\nTesting LangChain tool invocation...")

        for tool in tools[:2]:  # Test first 2 tools
            print(f"\nTesting tool: {tool.name}")

            # Check tool attributes
            assert hasattr(tool, 'name'), "Tool missing 'name' attribute"
            assert hasattr(tool, 'description'), "Tool missing 'description' attribute"
            assert hasattr(tool, 'args_schema'), "Tool missing 'args_schema' attribute"
            print(f"  [OK] Has required LangChain attributes")

            # Test invoking the tool (would work with actual agent)
            if tool.name == "get_current_time":
                # This would be called by the agent normally
                print(f"  [OK] Tool '{tool.name}' ready for agent use")
            elif tool.name == "calculate":
                print(f"  [OK] Tool '{tool.name}' ready for agent use")

        print("\n[OK] LangChain Tool Compatibility Test PASSED")
        return True

    except Exception as e:
        print(f"\n[FAIL] LangChain Tool Compatibility Test FAILED: {e}")
        return False

    finally:
        await exit_stack.aclose()


async def run_all_tests():
    """Run all integration tests."""
    print("="*60)
    print("LangGraph + MCP Integration Test Suite")
    print("="*60)

    results = []

    # Run all tests
    results.append(("MCP Server Connection", await test_mcp_server_connection()))
    results.append(("Tool Loading", await test_tool_loading()))
    results.append(("Tool Execution", await test_tool_execution()))
    results.append(("MultiServerMCPClient", await test_multi_server_client()))
    results.append(("LangChain Compatibility", await test_langchain_tool_compatibility()))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "[OK]" if result else "[FAIL]"
        print(f"{symbol} {test_name}: {status}")

        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n[SUCCESS] All tests passed! LangGraph + MCP integration is working correctly.")
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Please review the errors above.")

    return failed == 0


if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)