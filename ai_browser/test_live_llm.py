"""Test the AI Browser Framework with live LLM connection"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows encoding for Unicode
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import AIBrowserAgent
import json


async def test_live_agent():
    """Test the agent with a real task using live LLM"""
    
    print("=" * 60)
    print("AI Browser Framework - Live LLM Test")
    print("=" * 60)
    
    # Check for API keys
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Gemini": os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    }
    
    available_providers = [name for name, key in api_keys.items() if key]
    
    if not available_providers:
        print("[ERROR] No API keys found in .env file")
        print("Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY")
        return False
    
    print(f"[INFO] Available LLM providers: {', '.join(available_providers)}")
    print()
    
    # Create agent with headless=false for visibility
    config = {
        "browser": {
            "headless": False,  # Set to False so you can see the browser
            "viewport_width": 1920,
            "viewport_height": 1080,
            "browser_type": "chromium"
        },
        "llm": {
            "default_provider": available_providers[0].lower(),  # Use first available
            "providers": {
                "openai": {
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                "anthropic": {
                    "model": "claude-3-sonnet-20240229",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                "gemini": {
                    "model": "gemini-1.5-flash",
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            }
        },
        "stealth": {
            "enabled": True,
            "plugins": ["webdriver_flag", "chrome_runtime", "plugins_array", 
                       "webgl_vendor", "languages", "permissions", "user_agent"]
        },
        "agent": {
            "max_iterations": 15,
            "enable_self_correction": True,
            "capture_screenshots": True,
            "annotate_visuals": True
        }
    }
    
    try:
        print(f"[INFO] Creating AI Browser Agent with {config['llm']['default_provider']} provider...")
        
        # Create agent with custom config
        agent = AIBrowserAgent()
        # Override config
        agent.config = config
        
        # Re-initialize cognition layer with new config
        agent._init_cognition_layer()
        
        print(f"[INFO] Using LLM: {agent.config['llm']['default_provider']}")
        print(f"[INFO] Browser mode: {'Headless' if agent.config['browser']['headless'] else 'Visible'}")
        print(f"[INFO] Stealth enabled: {agent.config['stealth']['enabled']}")
        print()
        
        # Define test tasks
        test_tasks = [
            {
                "name": "Simple Navigation",
                "task": "Navigate to example.com and tell me the main heading text",
                "url": "https://example.com"
            },
            {
                "name": "Search Task",
                "task": "Go to Google and search for 'OpenAI GPT-4' then tell me what you see",
                "url": "https://google.com"
            },
            {
                "name": "Information Extraction",
                "task": "Go to Wikipedia and find information about artificial intelligence",
                "url": "https://wikipedia.org"
            }
        ]
        
        # Let user choose a task
        print("Available test tasks:")
        for i, task in enumerate(test_tasks, 1):
            print(f"{i}. {task['name']}: {task['task']}")
        
        print("\nRunning task 1 (Simple Navigation) as demonstration...")
        selected_task = test_tasks[0]
        
        print(f"\n[TASK] {selected_task['task']}")
        print(f"[URL] {selected_task['url']}")
        print("-" * 60)
        
        # Execute the task
        print("[INFO] Starting browser and executing task...")
        print("[INFO] You should see the browser window open...")
        print()
        
        result = await agent.execute_task(
            task=selected_task['task'],
            start_url=selected_task['url']
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        
        print(f"Success: {result['success']}")
        print(f"Summary: {result['summary']}")
        
        if result['extracted_data']:
            print(f"Extracted Data: {json.dumps(result['extracted_data'], indent=2)}")
        
        if result['errors']:
            print(f"Errors: {result['errors']}")
        
        print(f"\nTotal Actions Taken: {len(result['actions_taken'])}")
        
        # Show action history
        if result['actions_taken']:
            print("\nAction History:")
            for i, action in enumerate(result['actions_taken'][:10], 1):  # Show first 10
                action_type = action['action'].get('action', 'unknown')
                success = action['result']['success']
                status = "[OK]" if success else "[FAIL]"
                print(f"  {i}. {status} {action_type}: {action['action'].get('justification', '')[:60]}")
        
        return result['success']
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_stealth_detection():
    """Test stealth capabilities against bot detection"""
    print("\n" + "=" * 60)
    print("Stealth Detection Test")
    print("=" * 60)
    
    agent = AIBrowserAgent()
    agent.config["browser"]["headless"] = False  # Show browser
    
    print("[INFO] Testing stealth against bot.sannysoft.com...")
    print("[INFO] Browser will open and navigate to bot detection site...")
    
    results = await agent.test_stealth()
    
    print("\nStealth Test Results:")
    print(f"Bot Detected: {results.get('is_bot', 'Unknown')}")
    
    if 'details' in results:
        print("\nDetection Details:")
        for key, value in results['details'].items():
            print(f"  - {key}: {value}")
    
    return not results.get('is_bot', True)


async def main():
    """Main test runner"""
    
    # Test 1: Live LLM with browser automation
    print("\n[TEST 1] Live LLM Browser Automation")
    success1 = await test_live_agent()
    
    # Optional: Test 2: Stealth detection
    print("\n\nWould you like to run the stealth detection test? (y/n)")
    # Auto-run for demo
    print("Auto-running stealth test...")
    success2 = await test_stealth_detection()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Live LLM Test: {'PASSED' if success1 else 'FAILED'}")
    print(f"Stealth Test: {'PASSED' if success2 else 'FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! The AI Browser Framework is working correctly.")
    elif success1:
        print("\n✅ LLM integration is working! Stealth may need tuning.")
    else:
        print("\n⚠️ Please check your API keys and network connection.")


if __name__ == "__main__":
    print("Starting AI Browser Framework with Live LLM...")
    print("Note: The browser window will be visible (headless=False)")
    print()
    
    asyncio.run(main())