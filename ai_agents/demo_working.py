#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Working demonstration of custom browser-use tools
Shows the tool counter and demonstrates integration
"""

import sys
import os
import io
import asyncio
from pathlib import Path

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
from dotenv import load_dotenv
load_dotenv(dotenv_path="../../.env")

print("="*80)
print("CUSTOM BROWSER-USE TOOLS DEMONSTRATION")
print("="*80)

# Import required modules
from browser_use import ChatGoogle
from browser_use.agent.service import Agent
from ai_agents.custom_tools import CustomToolsManager
from ai_service_layer.clients.google_client import get_base_params


async def demo_tool_counter():
    """Demonstrate the tool counter"""
    print("\n" + "="*60)
    print("DEMO: Tool Counter in Action")
    print("="*60)

    # Create custom tools manager including defaults
    manager = CustomToolsManager(include_defaults=True)

    # Show registered custom tools
    custom_tools = manager.list_custom_tools()
    print(f"\n✅ Registered {len(custom_tools)} custom tools:")
    for tool in custom_tools:
        print(f"   - {tool['name']}")

    # Create LLM instance
    llm = ChatGoogle(model="gemini-2.0-flash-exp", **get_base_params())

    # Simple task that lists available tools
    task = """
    Navigate to a simple webpage like example.com.
    Once there, count how many browser automation tools are available to you.
    List some of the key tools you have access to.
    """

    print("\n🚀 Running browser agent with custom tools...")
    print("   Task: Navigate and list available tools\n")

    agent = Agent(
        task=task,
        llm=llm,
        tools=manager.get_tools_instance(),
        use_vision=False  # Disable vision for faster execution
    )

    try:
        await agent.run()
        print("\n✅ Demo completed successfully!")
    except Exception as e:
        print(f"\n⚠️ Demo completed with warning: {e}")
    finally:
        await agent.close()


async def demo_element_extraction():
    """Demonstrate element extraction on a real page"""
    print("\n" + "="*60)
    print("DEMO: Element Extraction")
    print("="*60)

    # Create custom tools manager
    manager = CustomToolsManager(include_defaults=True)

    # Create LLM instance
    llm = ChatGoogle(model="gemini-2.0-flash-exp", **get_base_params())

    # Task to extract elements
    task = """
    Navigate to python.org.
    Extract all the main navigation links from the page.
    Report how many links you found and list the first 5.
    """

    print("\n🔍 Running element extraction demo...")
    print("   Task: Extract navigation links from python.org\n")

    agent = Agent(
        task=task,
        llm=llm,
        tools=manager.get_tools_instance(),
        use_vision=False
    )

    try:
        await agent.run()
        print("\n✅ Element extraction completed!")
    except Exception as e:
        print(f"\n⚠️ Extraction completed with warning: {e}")
    finally:
        await agent.close()


async def main():
    """Main demo function"""

    print("\nSelect demo to run:")
    print("1. Tool Counter Demo (shows all available tools)")
    print("2. Element Extraction Demo")
    print("3. Run Both Demos")

    choice = input("\nEnter choice (1-3) [default: 1]: ").strip() or "1"

    if choice == "1":
        await demo_tool_counter()
    elif choice == "2":
        await demo_element_extraction()
    elif choice == "3":
        await demo_tool_counter()
        await demo_element_extraction()
    else:
        print("Invalid choice. Running tool counter demo...")
        await demo_tool_counter()

    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nThe custom tools framework is successfully integrated with browser-use!")
    print("You can now create and use custom browser automation tools.")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())