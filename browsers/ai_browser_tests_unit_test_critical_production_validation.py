#!/usr/bin/env python3
"""
Critical Production Validation Tests for AI Browser v2.0.0

Quick validation tests to ensure the most critical functionality works
for production readiness assessment.
"""

import asyncio
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestCriticalSystemValidation:
    """Quick validation of critical system components."""
    
    def test_critical_imports_work(self):
        """Test that critical modules can be imported without errors."""
        
        # Test execution layer imports
        try:
            from execution.browser_manager import BrowserManager, BrowserConfig
            from execution.stealth_manager import StealthManager
            from execution.action_executor import ActionExecutor
            print("✅ Execution layer imports working")
        except ImportError as e:
            pytest.fail(f"Critical execution layer import failed: {e}")
        
        # Test perception layer imports
        try:
            from perception.state_observer import StateObserver
            from perception.dom_processor import DOMProcessor
            print("✅ Perception layer imports working")
        except ImportError as e:
            pytest.fail(f"Critical perception layer import failed: {e}")
        
        # Test cognition layer imports
        try:
            from cognition.orchestrator import AgentOrchestrator
            from cognition.llm import LLMManager
            from cognition.actions import AgentAction
            print("✅ Cognition layer imports working")
        except ImportError as e:
            pytest.fail(f"Critical cognition layer import failed: {e}")
        
        # Test memory layer imports
        try:
            from memory.memory_manager import MemoryManager
            print("✅ Memory layer imports working")
        except ImportError as e:
            pytest.fail(f"Critical memory layer import failed: {e}")
    
    @pytest.mark.asyncio
    async def test_browser_manager_basic_functionality(self):
        """Test browser manager can launch and close browsers."""
        
        from execution.browser_manager import BrowserManager, BrowserConfig
        
        config = BrowserConfig(
            headless=True,
            browser_type="chromium"
        )
        
        browser_manager = BrowserManager()
        
        try:
            # Test browser launch
            browser = await browser_manager.launch(config)
            assert browser is not None, "Browser failed to launch"
            
            # Test context creation
            context = await browser_manager.new_context()
            assert context is not None, "Context creation failed"
            
            # Test page creation
            page = await context.new_page()
            assert page is not None, "Page creation failed"
            
            print("✅ Browser manager basic functionality working")
            
        except Exception as e:
            pytest.fail(f"Browser manager test failed: {e}")
        finally:
            await browser_manager.close()
    
    @pytest.mark.asyncio
    async def test_memory_manager_initialization(self):
        """Test memory manager can initialize and perform basic operations."""
        
        from memory.memory_manager import MemoryManager
        
        memory_manager = MemoryManager()
        
        try:
            await memory_manager.initialize()
            
            # Test basic functionality exists
            assert hasattr(memory_manager, 'session'), "Session memory not available"
            assert hasattr(memory_manager, 'store_task_step'), "store_task_step method missing"
            assert hasattr(memory_manager, 'get_task_history'), "get_task_history method missing"
            
            print("✅ Memory manager initialization working")
            
        except Exception as e:
            pytest.fail(f"Memory manager test failed: {e}")
        finally:
            await memory_manager.close()
    
    def test_layer_separation_basic(self):
        """Basic test that layers maintain separation."""
        
        # Test that execution layer doesn't directly import LLM
        from execution.browser_manager import BrowserManager
        import inspect
        
        browser_manager_source = inspect.getsource(BrowserManager)
        
        # Should not contain direct LLM imports
        forbidden_terms = ['openai', 'anthropic', 'from cognition.llm']
        for term in forbidden_terms:
            assert term not in browser_manager_source, \
                f"Execution layer contains forbidden import/reference: {term}"
        
        print("✅ Basic layer separation maintained")
    
    @pytest.mark.asyncio
    async def test_stealth_manager_basic(self):
        """Test stealth manager can be initialized and applied."""
        
        from execution.browser_manager import BrowserManager, BrowserConfig
        from execution.stealth_manager import StealthManager
        
        config = BrowserConfig(headless=True, browser_type="chromium")
        browser_manager = BrowserManager()
        stealth_manager = StealthManager()
        
        try:
            browser = await browser_manager.launch(config)
            context = await browser_manager.new_context()
            
            # Test stealth application
            await stealth_manager.apply_stealth_plugins(context)
            
            page = await context.new_page()
            
            # Test basic stealth - webdriver property should be hidden
            webdriver_value = await page.evaluate("navigator.webdriver")
            assert webdriver_value is False or webdriver_value is None, \
                f"Stealth not working: webdriver = {webdriver_value}"
            
            print("✅ Basic stealth functionality working")
            
        except Exception as e:
            pytest.fail(f"Stealth manager test failed: {e}")
        finally:
            await browser_manager.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])