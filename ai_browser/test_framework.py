"""Test script to verify AI Browser Framework installation and basic functionality"""

import asyncio
import sys
import os
from pathlib import Path

# Fix Windows encoding for Unicode
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger

# Configure logger
logger.add("test_framework.log", rotation="10 MB")


async def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        # Execution layer
        from execution.browser_manager import BrowserManager
        from execution.stealth_manager import StealthManager
        from execution.actions import ClickAction, FillAction
        print("[PASS] Execution layer imports successful")
        
        # Perception layer
        from perception.dom_processor import DOMProcessor
        from perception.visual_annotator import VisualAnnotator
        from perception.state_observer import StateObserver
        print("[PASS] Perception layer imports successful")
        
        # Cognition layer
        from cognition.llm import LLMManager
        from cognition.actions import AgentAction
        from cognition.prompts import PromptBuilder
        from cognition.dispatcher import ActionDispatcher
        print("[PASS] Cognition layer imports successful")
        
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False


async def test_browser_launch():
    """Test browser launch and basic interaction"""
    print("\nTesting browser launch...")
    
    try:
        from execution.browser_manager import BrowserManager, BrowserConfig
        
        manager = BrowserManager()
        config = BrowserConfig(headless=True)
        
        browser = await manager.launch(config)
        print("[PASS] Browser launched successfully")
        
        context = await manager.new_context()
        print("[PASS] Context created successfully")
        
        page = await manager.new_page(context)
        print("[PASS] Page created successfully")
        
        # Navigate to a simple page
        await page.goto("https://example.com")
        title = await page.title()
        print(f"[PASS] Navigated to page: {title}")
        
        # Cleanup
        await manager.close()
        print("[PASS] Browser closed successfully")
        
        return True
    except Exception as e:
        print(f"[FAIL] Browser test failed: {e}")
        return False


async def test_stealth_plugins():
    """Test stealth plugin system"""
    print("\nTesting stealth plugins...")
    
    try:
        from execution.stealth_manager import StealthManager
        from execution.browser_manager import BrowserManager
        
        stealth = StealthManager()
        stealth.use_default_plugins()
        
        print(f"[PASS] Loaded {len(stealth.plugins)} stealth plugins")
        
        # List plugins
        for plugin in stealth.plugins:
            print(f"  - {plugin.get_name()}: {plugin.get_description()}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Stealth test failed: {e}")
        return False


async def test_dom_processing():
    """Test DOM processing"""
    print("\nTesting DOM processing...")
    
    try:
        from perception.dom_processor import DOMProcessor
        
        processor = DOMProcessor()
        
        # Test with sample HTML
        sample_html = """
        <html>
            <body>
                <h1>Test Page</h1>
                <p>This is a test paragraph.</p>
                <button id="submit">Submit</button>
                <input type="text" placeholder="Enter text">
                <a href="https://example.com">Link</a>
            </body>
        </html>
        """
        
        result = processor.process_html(sample_html)
        
        print(f"[PASS] DOM processed successfully")
        print(f"  - Extracted {len(processor.interactive_elements)} interactive elements")
        print(f"  - Distilled content length: {len(result.distilled_content)} chars")
        
        return True
    except Exception as e:
        print(f"[FAIL] DOM processing test failed: {e}")
        return False


async def test_llm_providers():
    """Test LLM provider setup"""
    print("\nTesting LLM providers...")
    
    try:
        from cognition.llm import LLMManager
        
        manager = LLMManager()
        
        # Check for available API keys
        providers_available = []
        
        if os.getenv("OPENAI_API_KEY"):
            from cognition.providers import OpenAIProvider
            provider = OpenAIProvider()
            manager.register_provider("openai", provider)
            providers_available.append("OpenAI")
        
        if os.getenv("ANTHROPIC_API_KEY"):
            from cognition.providers import AnthropicProvider
            provider = AnthropicProvider()
            manager.register_provider("anthropic", provider)
            providers_available.append("Anthropic")
        
        if os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
            from cognition.providers import GeminiProvider
            provider = GeminiProvider()
            manager.register_provider("gemini", provider)
            providers_available.append("Gemini")
        
        if providers_available:
            print(f"[PASS] LLM providers available: {', '.join(providers_available)}")
        else:
            print("[WARN] No LLM providers configured (set API keys in .env)")
        
        return True
    except Exception as e:
        print(f"[FAIL] LLM provider test failed: {e}")
        return False


async def test_structured_actions():
    """Test structured action models"""
    print("\nTesting structured actions...")
    
    try:
        from cognition.actions import (
            ClickAction, TypeAction, NavigateAction,
            FinishedAction, FailedAction
        )
        
        # Test action creation
        actions = [
            ClickAction(
                element_id=1,
                justification="Testing click action"
            ),
            TypeAction(
                element_id=2,
                text_to_type="Hello World",
                justification="Testing type action"
            ),
            NavigateAction(
                url="https://example.com",
                justification="Testing navigation"
            ),
            FinishedAction(
                summary="Task completed successfully",
                justification="All steps done"
            )
        ]
        
        print(f"[PASS] Created {len(actions)} structured actions")
        
        # Test serialization
        for action in actions:
            json_data = action.model_dump_json()
            print(f"  - {action.action}: {len(json_data)} bytes")
        
        return True
    except Exception as e:
        print(f"[FAIL] Structured actions test failed: {e}")
        return False


async def test_main_application():
    """Test main application initialization"""
    print("\nTesting main application...")
    
    try:
        from main import AIBrowserAgent
        
        # Create agent with test config
        agent = AIBrowserAgent()
        
        print("[PASS] AI Browser Agent initialized successfully")
        print(f"  - Browser type: {agent.config['browser']['browser_type']}")
        print(f"  - Stealth enabled: {agent.config['stealth']['enabled']}")
        print(f"  - Max iterations: {agent.config['agent']['max_iterations']}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Main application test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("AI Browser Framework Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Browser Launch", test_browser_launch),
        ("Stealth Plugins", test_stealth_plugins),
        ("DOM Processing", test_dom_processing),
        ("LLM Providers", test_llm_providers),
        ("Structured Actions", test_structured_actions),
        ("Main Application", test_main_application)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            print(f"[FAIL] Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "[PASS] PASS" if success else "[FAIL] FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Framework is ready to use.")
    else:
        print(f"\n[WARN] {total - passed} tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)