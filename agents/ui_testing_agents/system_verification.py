#!/usr/bin/env python3
"""
Test script to verify the portable V2 system works
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))


async def test_portable_system():
    """Test all components of portable system"""
    
    print("=" * 70)
    print("TESTING PORTABLE V2 SYSTEM")
    print("=" * 70)
    
    # Test 1: Check imports
    print("\n[TEST 1] Checking imports...")
    try:
        import llm_client
        from test_automation_framework import framework_core
        from test_automation_framework import ai_test_generator
        print("[OK] All imports successful")
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        return False
    
    # Test 2: Check env file
    print("\n[TEST 2] Checking .env file...")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    has_key = False
    if os.getenv('OPENAI_API_KEY'):
        print("[OK] OpenAI API key found")
        has_key = True
    if os.getenv('ANTHROPIC_API_KEY'):
        print("[OK] Anthropic API key found")
        has_key = True
    if os.getenv('GOOGLE_API_KEY'):
        print("[OK] Google API key found")
        has_key = True
    
    if not has_key:
        print("[ERROR] No API keys found in .env")
        print("Please add at least one API key to .env file")
        return False
    
    # Test 3: Test LLM connection
    print("\n[TEST 3] Testing LLM connection...")
    try:
        from llm_client import call_default_llm
        
        response = await call_default_llm(
            [{"role": "user", "content": "Say 'Portable system working'"}],
            temperature=0.1,
            max_tokens=50
        )
        
        print(f"[OK] LLM Response: {response[:100]}...")
    except Exception as e:
        print(f"[ERROR] LLM test failed: {e}")
        return False
    
    # Test 4: Test AI tool
    print("\n[TEST 4] Testing AI scenario generation...")
    try:
        from test_automation_framework.ai_test_generator import generate_ai_scenarios_with_llm
        
        simple_elements = {
            "form_elements": [
                {"type": "text", "name": "email"},
                {"type": "password", "name": "password"}
            ],
            "clickable_elements": [
                {"type": "submit", "text": "Login"}
            ]
        }
        
        scenarios = await generate_ai_scenarios_with_llm(
            simple_elements,
            {"url": "test.com", "purpose": "authentication"},
            max_scenarios=1
        )
        
        print("[OK] AI scenario generated successfully")
        if isinstance(scenarios, dict) and 'scenarios' in scenarios:
            preview = str(scenarios['scenarios'])[:150]
            print(f"Preview: {preview}...")
    except Exception as e:
        print(f"[ERROR] AI tool test failed: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
    print("\nThe portable V2 system is working correctly.")
    print("You can now:")
    print("1. Copy this entire folder to any machine")
    print("2. Run setup.py or setup.bat/setup.sh")
    print("3. Add API keys to .env")
    print("4. Start using the V2 system!")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    print("\nTesting portable V2 system...")
    print("This verifies all components work correctly.\n")
    
    try:
        success = asyncio.run(test_portable_system())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        sys.exit(1)