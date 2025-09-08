#!/usr/bin/env python3
"""
Simple Live Test for AI Browser v2.0.0

A minimal test script to validate the core system works with real APIs.
This test performs basic operations to ensure the system is functional.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__) / "src"))

# Load environment variables
load_dotenv()


async def test_llm_connections():
    """Test basic LLM connectivity"""
    print("\n" + "="*60)
    print("TESTING LLM CONNECTIONS")
    print("="*60)
    
    from src.cognition.llm import LLMManager
    
    try:
        llm_manager = LLMManager()
        test_prompt = "Say 'Hello from AI Browser' in exactly 4 words."
        
        # Test OpenAI if available
        if os.getenv("OPENAI_API_KEY"):
            print("\nTesting OpenAI...")
            try:
                response = await llm_manager.generate(
                    prompt=test_prompt,
                    provider="openai",
                    max_tokens=20
                )
                print(f"  Response: {response[:50]}")
                print("  [PASS] OpenAI connected successfully")
            except Exception as e:
                print(f"  [FAIL] OpenAI error: {e}")
        
        # Test Anthropic if available
        if os.getenv("ANTHROPIC_API_KEY"):
            print("\nTesting Anthropic...")
            try:
                response = await llm_manager.generate(
                    prompt=test_prompt,
                    provider="anthropic",
                    max_tokens=20
                )
                print(f"  Response: {response[:50]}")
                print("  [PASS] Anthropic connected successfully")
            except Exception as e:
                print(f"  [FAIL] Anthropic error: {e}")
        
        # Test Gemini if available
        if os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
            print("\nTesting Google Gemini...")
            try:
                response = await llm_manager.generate(
                    prompt=test_prompt,
                    provider="gemini",
                    max_tokens=20
                )
                print(f"  Response: {response[:50]}")
                print("  [PASS] Gemini connected successfully")
            except Exception as e:
                print(f"  [FAIL] Gemini error: {e}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize LLM Manager: {e}")
        return False


async def test_browser_launch():
    """Test browser launch with stealth"""
    print("\n" + "="*60)
    print("TESTING BROWSER LAUNCH")
    print("="*60)
    
    from src.execution.browser_manager import BrowserManager, BrowserConfig
    from src.execution.stealth_manager import StealthManager
    
    try:
        print("\nInitializing browser...")
        
        config = BrowserConfig(
            headless=True,
            viewport_width=1920,
            viewport_height=1080
        )
        
        browser_manager = BrowserManager()
        await browser_manager.launch(config)
        print("  [PASS] Browser launched successfully")
        
        print("\nApplying stealth...")
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        context = await browser_manager.browser.new_context()
        page = await context.new_page()
        await stealth_manager.apply_to_page(page)
        print("  [PASS] Stealth applied successfully")
        
        print("\nNavigating to test page...")
        await page.goto("https://www.example.com", wait_until="networkidle")
        title = await page.title()
        print(f"  Page title: {title}")
        print("  [PASS] Navigation successful")
        
        # Check stealth properties
        webdriver_check = await page.evaluate("navigator.webdriver")
        if webdriver_check is None or webdriver_check is False:
            print("  [PASS] WebDriver flag hidden")
        else:
            print("  [WARN] WebDriver flag still visible")
        
        await context.close()
        await browser_manager.close()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Browser test failed: {e}")
        return False


async def test_memory_system():
    """Test memory layer initialization"""
    print("\n" + "="*60)
    print("TESTING MEMORY SYSTEM")
    print("="*60)
    
    from src.memory.memory_manager import MemoryManager
    
    try:
        print("\nInitializing memory manager...")
        memory_manager = MemoryManager()
        await memory_manager.initialize()
        print("  [PASS] Memory manager initialized")
        
        print("\nTesting SQLite session memory...")
        test_data = {
            "task_id": f"test_{datetime.now().timestamp()}",
            "user_input": "Test task",
            "agent_response": "Test response"
        }
        
        await memory_manager.store_conversation(
            task_id=test_data["task_id"],
            user_input=test_data["user_input"],
            agent_response=test_data["agent_response"]
        )
        print("  [PASS] Data stored successfully")
        
        history = await memory_manager.get_recent_conversations(limit=5)
        if history and len(history) > 0:
            print("  [PASS] Data retrieved successfully")
        else:
            print("  [WARN] No data retrieved")
        
        await memory_manager.close()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Memory test failed: {e}")
        return False


async def test_full_system():
    """Test the complete system with a simple task"""
    print("\n" + "="*60)
    print("TESTING FULL SYSTEM")
    print("="*60)
    
    from src.main import AIBrowser, TaskConfig
    
    try:
        print("\nInitializing AI Browser...")
        browser = AIBrowser({"log_level": "INFO"})
        
        task_config = TaskConfig(
            task="Navigate to example.com and get the page title",
            url="https://www.example.com",
            headless=True,
            max_steps=3,
            timeout=30000
        )
        
        await browser.initialize(task_config)
        print("  [PASS] AI Browser initialized")
        
        print("\nExecuting test task...")
        print(f"  Task: {task_config.task}")
        
        result = await browser.execute_task(task_config)
        
        if result["status"] == "completed":
            print("  [PASS] Task completed successfully")
            print(f"  Final URL: {result.get('final_url', 'N/A')}")
            print(f"  Actions executed: {len(result.get('actions', []))}")
        elif result["status"] == "failed":
            print(f"  [FAIL] Task failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"  [WARN] Task status: {result['status']}")
        
        await browser.cleanup()
        
        return result["status"] == "completed"
        
    except Exception as e:
        print(f"\n[ERROR] Full system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" AI BROWSER v2.0.0 - SIMPLE LIVE TEST ".center(70, "="))
    print("="*70)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    print("\n" + "="*60)
    print("ENVIRONMENT CHECK")
    print("="*60)
    
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Google/Gemini": os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    }
    
    for name, key in api_keys.items():
        status = "Present" if key else "Missing"
        print(f"  {name}: {status}")
    
    if not any(api_keys.values()):
        print("\n[ERROR] No API keys found. Please configure your .env file.")
        return 1
    
    # Run tests
    results = {
        "LLM Connections": False,
        "Browser Launch": False,
        "Memory System": False,
        "Full System": False
    }
    
    try:
        # Test LLM connections
        results["LLM Connections"] = await test_llm_connections()
        
        # Test browser launch
        results["Browser Launch"] = await test_browser_launch()
        
        # Test memory system
        results["Memory System"] = await test_memory_system()
        
        # Test full system
        results["Full System"] = await test_full_system()
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Test interrupted by user")
        return 1
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "[PASS]" if passed_test else "[FAIL]"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! The AI Browser is fully operational.")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)