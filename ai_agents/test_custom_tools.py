"""
Test script for custom browser-use tools
Verifies that all custom tools work correctly
"""

import asyncio
import sys
import os
import io
from pathlib import Path

# Force UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from browser_use import ChatGoogle
from browser_use.agent.service import Agent
from custom_tools import CustomToolsManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../../.env")

# Import the Google client
from ai_service_layer.clients.google_client import get_client as gclient
from ai_service_layer.clients.google_client import get_base_params


async def test_tool_counter():
    """Test the tool counter functionality"""
    print("\n" + "="*60)
    print("TEST 1: Tool Counter")
    print("="*60)

    try:
        # Create custom tools manager
        manager = CustomToolsManager(include_defaults=True)

        # Create LLM instance
        llm = ChatGoogle(model="gemini-2.0-flash-exp", **get_base_params())

        # Test counting tools
        task = """
        Use the count_tools action to count all available tools.
        Set the parameters to:
        - include_custom: true
        - include_default: true
        - detailed: false

        Display the results showing total number of tools.
        """

        print("✅ Testing tool counter...")
        agent = Agent(task=task, llm=llm, tools=manager.get_tools_instance())
        await agent.run()
        await agent.close()

        print("✅ Tool counter test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Tool counter test failed: {e}")
        return False


async def test_element_extractor():
    """Test the advanced element extractor"""
    print("\n" + "="*60)
    print("TEST 2: Advanced Element Extractor")
    print("="*60)

    try:
        # Create custom tools manager
        manager = CustomToolsManager(include_defaults=True)

        # Create LLM instance
        llm = ChatGoogle(model="gemini-2.0-flash-exp", **get_base_params())

        # Test element extraction
        task = """
        Navigate to example.com and use the extract_elements_advanced action
        with these parameters:
        - selector_type: "links"
        - include_hidden: false
        - extract_attributes: true

        Show how many links were found.
        """

        print("✅ Testing element extractor...")
        agent = Agent(task=task, llm=llm, tools=manager.get_tools_instance())
        await agent.run()
        await agent.close()

        print("✅ Element extractor test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Element extractor test failed: {e}")
        return False


async def test_network_monitor():
    """Test the network monitor"""
    print("\n" + "="*60)
    print("TEST 3: Network Monitor")
    print("="*60)

    try:
        # Create custom tools manager
        manager = CustomToolsManager(include_defaults=True)

        # Create LLM instance
        llm = ChatGoogle(model="gemini-2.0-flash-exp", **get_base_params())

        # Test network monitoring
        task = """
        Navigate to python.org and use the monitor_network action
        with these parameters:
        - duration: 5
        - filter_type: null

        Monitor for 5 seconds and report how many network requests were captured.
        """

        print("✅ Testing network monitor...")
        agent = Agent(task=task, llm=llm, tools=manager.get_tools_instance())
        await agent.run()
        await agent.close()

        print("✅ Network monitor test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Network monitor test failed: {e}")
        return False


async def test_integration():
    """Test integration with existing browser-use functionality"""
    print("\n" + "="*60)
    print("TEST 4: Integration Test")
    print("="*60)

    try:
        # Create custom tools manager
        manager = CustomToolsManager(include_defaults=True)

        # Create LLM instance
        llm = ChatGoogle(model="gemini-2.0-flash-exp", **get_base_params())

        # Test using custom tools alongside default browser actions
        task = """
        1. Navigate to www.python.org
        2. Use count_tools to show we have both custom and default tools
        3. Click on the "Downloads" link using standard browser action
        4. Use extract_elements_advanced to find all buttons on the downloads page
        """

        print("✅ Testing integration with default browser-use tools...")
        agent = Agent(task=task, llm=llm, tools=manager.get_tools_instance())
        await agent.run()
        await agent.close()

        print("✅ Integration test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


async def quick_test():
    """Run a quick test to verify basic functionality"""
    print("\n" + "="*60)
    print("QUICK TEST: Basic Functionality")
    print("="*60)

    try:
        # Create custom tools manager
        manager = CustomToolsManager(include_defaults=True)

        # Verify custom tools were registered
        custom_tools = manager.list_custom_tools()
        print(f"✅ Registered {len(custom_tools)} custom tools:")
        for tool in custom_tools:
            print(f"   - {tool['name']}: {tool['description']}")

        # Create LLM instance
        llm = ChatGoogle(model="gemini-2.0-flash-exp", **get_base_params())

        # Simple test task
        task = """
        Use the count_tools action to count all available tools and display the total count.
        Show the number of custom tools and default tools separately.
        """

        print("\n✅ Running quick functionality test...")
        agent = Agent(task=task, llm=llm, tools=manager.get_tools_instance())
        await agent.run()
        await agent.close()

        print("✅ Quick test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("\n" + "="*80)
    print("CUSTOM BROWSER-USE TOOLS TEST SUITE")
    print("="*80)

    print("\nSelect test to run:")
    print("1. Quick functionality test (recommended)")
    print("2. Tool counter test")
    print("3. Element extractor test")
    print("4. Network monitor test")
    print("5. Integration test")
    print("6. Run all tests")

    choice = input("\nSelect test (1-6) [default: 1]: ").strip() or "1"

    results = []

    if choice == "1":
        results.append(await quick_test())
    elif choice == "2":
        results.append(await test_tool_counter())
    elif choice == "3":
        results.append(await test_element_extractor())
    elif choice == "4":
        results.append(await test_network_monitor())
    elif choice == "5":
        results.append(await test_integration())
    elif choice == "6":
        results.append(await quick_test())
        results.append(await test_tool_counter())
        results.append(await test_element_extractor())
        results.append(await test_network_monitor())
        results.append(await test_integration())
    else:
        print("Invalid choice. Running quick test...")
        results.append(await quick_test())

    # Summary
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)

    if all(results):
        print("✅ ALL TESTS PASSED!")
    else:
        failed = len([r for r in results if not r])
        print(f"❌ {failed} test(s) failed")

    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())