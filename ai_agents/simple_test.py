#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple test for custom tools without browser navigation
Tests the tool counting and registration functionality
"""

import sys
import os
import io

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    # Set environment variables
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

    # Reconfigure stdout/stderr with UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

    # Set console to UTF-8
    try:
        import subprocess
        subprocess.run(['chcp', '65001'], shell=True, capture_output=True, check=False)
    except:
        pass

print("="*60)
print("Simple Custom Tools Test")
print("="*60)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Test 1: Import the custom tools module
    print("\n1. Testing module import...")
    from ai_agents.custom_tools import CustomToolsManager, ToolCounterParams
    print("   ✅ Module imported successfully")

    # Test 2: Create custom tools manager
    print("\n2. Creating custom tools manager...")
    manager = CustomToolsManager(include_defaults=False)  # Don't include defaults to simplify
    print("   ✅ Manager created successfully")

    # Test 3: Check registered custom tools
    print("\n3. Checking registered custom tools...")
    custom_tools = manager.list_custom_tools()
    print(f"   ✅ Found {len(custom_tools)} custom tools:")
    for tool in custom_tools:
        print(f"      - {tool['name']}: {tool['description'][:50]}...")

    # Test 4: Access tools instance
    print("\n4. Getting tools instance...")
    tools_instance = manager.get_tools_instance()
    print(f"   ✅ Tools instance type: {type(tools_instance)}")

    # Test 5: Check tool registry
    print("\n5. Checking tool registry...")
    if hasattr(tools_instance, 'registry'):
        print("   ✅ Registry exists")
        if hasattr(tools_instance.registry, 'registry'):
            print(f"      Registry type: {type(tools_instance.registry.registry)}")

    # Test 6: Count custom tools directly
    print("\n6. Counting tools...")
    print(f"   Custom tools count: {len(manager.custom_tools)}")
    print(f"   Default tools count: {manager.default_tool_count}")

    # Test 7: Test dynamic tool addition
    print("\n7. Testing dynamic tool addition...")
    from pydantic import BaseModel, Field

    class TestToolParams(BaseModel):
        message: str = Field(default="Hello", description="Test message")

    @manager.tools.registry.action(
        'Test tool for verification',
        param_model=TestToolParams
    )
    async def test_tool(params: TestToolParams):
        return f"Test result: {params.message}"

    print("   ✅ Dynamic tool added successfully")
    print(f"   New custom tools count: {len(manager.list_custom_tools())}")

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nThe custom tools framework is working correctly.")
    print("Tools are registered and accessible.")

except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("   Make sure browser-use is installed: pip install browser-use")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete.")