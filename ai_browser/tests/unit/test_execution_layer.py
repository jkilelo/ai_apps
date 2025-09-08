"""Unit tests for the Execution Layer components.

Tests BrowserManager, StealthManager, ActionExecutor and Actions
while ensuring strict layer separation (NO LLM calls).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from datetime import datetime
from typing import Dict, Any

from src.execution.browser_manager import BrowserManager, BrowserConfig
from src.execution.stealth_manager import StealthManager, WebDriverPlugin, ChromeRuntimePlugin
from src.execution.action_executor import (
    ActionExecutor,
    ActionConfig,
    ActionType,
    ExecutionContext,
)
from src.execution.actions import (
    ClickAction,
    TypeAction,
    NavigateAction,
    ScrollAction,
    ActionResult,
    ScreenshotAction,
    ExtractTextAction,
)


class TestBrowserManager:
    """Test BrowserManager functionality."""
    
    @pytest.mark.asyncio
    async def test_browser_launch_default_config(self):
        """Test browser launch with default configuration."""
        with patch('src.execution.browser_manager.async_playwright') as mock_playwright:
            # Setup mock
            mock_pw_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.return_value.start = AsyncMock(return_value=mock_pw_instance)
            
            # Test
            manager = BrowserManager()
            browser = await manager.launch()
            
            # Assertions
            assert browser == mock_browser
            assert manager.browser == mock_browser
            mock_pw_instance.chromium.launch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_browser_launch_custom_config(self):
        """Test browser launch with custom configuration."""
        config = BrowserConfig(
            browser_type="firefox",
            headless=True,
            viewport_width=1280,
            viewport_height=720,
            user_agent="TestAgent/1.0"
        )
        
        with patch('src.execution.browser_manager.async_playwright') as mock_playwright:
            # Setup mock
            mock_pw_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_pw_instance.firefox.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.return_value.start = AsyncMock(return_value=mock_pw_instance)
            
            # Test
            manager = BrowserManager()
            browser = await manager.launch(config)
            
            # Assertions
            assert browser == mock_browser
            assert manager.config == config
            mock_pw_instance.firefox.launch.assert_called_once_with(
                headless=True,
                slow_mo=0
            )
    
    @pytest.mark.asyncio
    async def test_new_context_creation(self):
        """Test browser context creation."""
        with patch('src.execution.browser_manager.async_playwright') as mock_playwright:
            # Setup mock
            mock_pw_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.return_value.start = AsyncMock(return_value=mock_pw_instance)
            
            # Test
            manager = BrowserManager()
            await manager.launch()
            context = await manager.new_context()
            
            # Assertions
            assert context == mock_context
            assert context in manager.contexts
            mock_browser.new_context.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_new_page_creation(self):
        """Test page creation in context."""
        with patch('src.execution.browser_manager.async_playwright') as mock_playwright:
            # Setup mock
            mock_pw_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()
            mock_context.new_page = AsyncMock(return_value=mock_page)
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.return_value.start = AsyncMock(return_value=mock_pw_instance)
            
            # Test
            manager = BrowserManager()
            await manager.launch()
            page = await manager.new_page()
            
            # Assertions
            assert page == mock_page
            mock_context.new_page.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_browser_cleanup(self):
        """Test proper browser cleanup."""
        with patch('src.execution.browser_manager.async_playwright') as mock_playwright:
            # Setup mock
            mock_pw_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.return_value.start = AsyncMock(return_value=mock_pw_instance)
            
            # Test
            manager = BrowserManager()
            await manager.launch()
            await manager.new_context()
            await manager.close()
            
            # Assertions
            mock_context.close.assert_called_once()
            mock_browser.close.assert_called_once()
            mock_pw_instance.stop.assert_called_once()
            assert manager.browser is None
            assert len(manager.contexts) == 0
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test BrowserManager as async context manager."""
        with patch('src.execution.browser_manager.async_playwright') as mock_playwright:
            # Setup mock
            mock_pw_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.return_value.start = AsyncMock(return_value=mock_pw_instance)
            
            # Test
            async with BrowserManager() as manager:
                assert manager.browser == mock_browser
            
            # Verify cleanup was called
            mock_browser.close.assert_called_once()


class TestStealthManager:
    """Test StealthManager functionality."""
    
    @pytest.mark.asyncio
    async def test_stealth_manager_initialization(self):
        """Test StealthManager initialization with default plugins."""
        manager = StealthManager()
        
        # Check default plugins are loaded
        assert len(manager.plugins) > 0
        plugin_names = [p.get_name() for p in manager.plugins]
        assert "webdriver_flag" in plugin_names
        assert "chrome_runtime" in plugin_names
    
    @pytest.mark.asyncio
    async def test_apply_stealth_to_context(self):
        """Test applying stealth to browser context."""
        mock_context = AsyncMock()
        
        manager = StealthManager()
        await manager.apply_to_context(mock_context)
        
        # Verify add_init_script was called for each plugin
        assert mock_context.add_init_script.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_apply_stealth_to_page(self):
        """Test applying stealth to specific page."""
        mock_page = AsyncMock()
        
        manager = StealthManager()
        await manager.apply_to_page(mock_page)
        
        # Verify evaluate was called for each plugin
        assert mock_page.evaluate.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_register_custom_plugin(self):
        """Test registering custom stealth plugin."""
        class CustomPlugin:
            def get_name(self):
                return "custom_plugin"
            
            def get_description(self):
                return "Custom test plugin"
            
            def get_priority(self):
                return 10
            
            async def apply_to_context(self, context):
                await context.add_init_script("// Custom script")
            
            async def apply_to_page(self, page):
                await page.evaluate("// Custom page script")
        
        manager = StealthManager()
        custom_plugin = CustomPlugin()
        manager.register_plugin(custom_plugin)
        
        assert custom_plugin in manager.plugins
        plugin_names = [p.get_name() for p in manager.plugins]
        assert "custom_plugin" in plugin_names
    
    def test_webdriver_plugin(self):
        """Test WebDriver detection removal plugin."""
        plugin = WebDriverPlugin()
        
        assert plugin.get_name() == "webdriver_flag"
        assert plugin.get_priority() == 1
        assert "webdriver" in plugin.get_description().lower()
    
    def test_chrome_runtime_plugin(self):
        """Test Chrome runtime plugin."""
        plugin = ChromeRuntimePlugin()
        
        assert plugin.get_name() == "chrome_runtime"
        assert plugin.get_priority() == 2
        assert "chrome" in plugin.get_description().lower()


class TestActionExecutor:
    """Test ActionExecutor functionality."""
    
    def test_action_executor_initialization(self):
        """Test ActionExecutor initialization with default actions."""
        executor = ActionExecutor()
        
        # Check default actions are registered
        assert ActionType.CLICK in executor.action_registry
        assert ActionType.TYPE in executor.action_registry
        assert ActionType.NAVIGATE in executor.action_registry
        assert ActionType.SCROLL in executor.action_registry
        assert ActionType.SCREENSHOT in executor.action_registry
    
    @pytest.mark.asyncio
    async def test_execute_click_action(self):
        """Test executing a click action."""
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_locator = AsyncMock()
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        executor = ActionExecutor()
        config = ActionConfig(
            type=ActionType.CLICK,
            selector="button#submit",
            timeout=5000
        )
        context = ExecutionContext(
            page=mock_page,
            context=mock_context
        )
        
        result = await executor.execute_action(config, context)
        
        # Assertions
        assert result.success is True
        mock_page.locator.assert_called_with("button#submit")
        mock_locator.click.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_type_action(self):
        """Test executing a type action."""
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_locator = AsyncMock()
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        executor = ActionExecutor()
        config = ActionConfig(
            type=ActionType.TYPE,
            selector="input#email",
            text="test@example.com",
            timeout=5000
        )
        context = ExecutionContext(
            page=mock_page,
            context=mock_context
        )
        
        result = await executor.execute_action(config, context)
        
        # Assertions
        assert result.success is True
        mock_page.locator.assert_called_with("input#email")
        mock_locator.type.assert_called_once_with("test@example.com", delay=50)
    
    @pytest.mark.asyncio
    async def test_execute_sequence(self):
        """Test executing a sequence of actions."""
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_locator = AsyncMock()
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        executor = ActionExecutor()
        actions = [
            ActionConfig(type=ActionType.NAVIGATE, url="https://example.com"),
            ActionConfig(type=ActionType.WAIT, timeout=1000),
            ActionConfig(type=ActionType.CLICK, selector="button"),
        ]
        context = ExecutionContext(
            page=mock_page,
            context=mock_context
        )
        
        # Mock the navigate action
        mock_page.goto = AsyncMock()
        
        results = await executor.execute_sequence(actions, context)
        
        # Assertions
        assert len(results) == 3
        assert all(isinstance(r, ActionResult) for r in results)
        assert len(context.execution_log) == 3
    
    @pytest.mark.asyncio
    async def test_execute_with_retry(self):
        """Test action execution with retry logic."""
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_locator = AsyncMock()
        
        # First call fails, second succeeds
        mock_locator.click = AsyncMock(side_effect=[Exception("Failed"), None])
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        executor = ActionExecutor()
        config = ActionConfig(
            type=ActionType.CLICK,
            selector="button",
            retry_count=2
        )
        context = ExecutionContext(
            page=mock_page,
            context=mock_context
        )
        
        result = await executor.execute_action(config, context)
        
        # Should succeed after retry
        assert result.success is True
        assert result.retry_count == 1
    
    @pytest.mark.asyncio
    async def test_execute_with_screenshots(self):
        """Test action execution with screenshot capture."""
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_locator = AsyncMock()
        mock_page.locator = MagicMock(return_value=mock_locator)
        mock_page.screenshot = AsyncMock(return_value=b"screenshot_data")
        
        executor = ActionExecutor()
        config = ActionConfig(
            type=ActionType.CLICK,
            selector="button",
            screenshot_before=True,
            screenshot_after=True
        )
        context = ExecutionContext(
            page=mock_page,
            context=mock_context
        )
        
        result = await executor.execute_action(config, context)
        
        # Screenshots should be taken
        assert mock_page.screenshot.call_count >= 2
        assert len(context.screenshots) >= 2
    
    def test_execution_summary(self):
        """Test getting execution summary."""
        mock_page = MagicMock()
        mock_context = MagicMock()
        
        executor = ActionExecutor()
        context = ExecutionContext(
            page=mock_page,
            context=mock_context,
            start_time=datetime.now()
        )
        
        # Add some execution logs
        context.log_action("click", ActionResult(success=True), 100)
        context.log_action("type", ActionResult(success=True), 200)
        context.log_action("navigate", ActionResult(success=False, error="Failed"), 300)
        
        summary = executor.get_execution_summary(context)
        
        assert summary["total_actions"] == 3
        assert summary["successful_actions"] == 2
        assert summary["failed_actions"] == 1
        assert summary["total_duration_ms"] == 600
        assert summary["average_duration_ms"] == 200


class TestActions:
    """Test individual action implementations."""
    
    @pytest.mark.asyncio
    async def test_click_action(self):
        """Test ClickAction execution."""
        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        action = ClickAction()
        result = await action.execute(mock_page, selector="button")
        
        assert result.success is True
        assert result.data["selector"] == "button"
        mock_locator.click.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_type_action(self):
        """Test TypeAction execution."""
        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        action = TypeAction()
        result = await action.execute(
            mock_page,
            selector="input",
            text="test text"
        )
        
        assert result.success is True
        assert result.data["text_length"] == 9
        mock_locator.type.assert_called_once_with("test text", delay=50)
    
    @pytest.mark.asyncio
    async def test_navigate_action(self):
        """Test NavigateAction execution."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        
        action = NavigateAction()
        result = await action.execute(mock_page, url="https://example.com")
        
        assert result.success is True
        assert result.data["url"] == "https://example.com"
        mock_page.goto.assert_called_once_with("https://example.com", wait_until="networkidle")
    
    @pytest.mark.asyncio
    async def test_scroll_action(self):
        """Test ScrollAction execution."""
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value={"x": 0, "y": 500})
        
        action = ScrollAction()
        result = await action.execute(
            mock_page,
            direction="down",
            distance=500
        )
        
        assert result.success is True
        assert result.data["direction"] == "down"
        assert result.data["distance"] == 500
        mock_page.evaluate.assert_called()
    
    @pytest.mark.asyncio
    async def test_screenshot_action(self):
        """Test ScreenshotAction execution."""
        mock_page = AsyncMock()
        mock_page.screenshot = AsyncMock(return_value=b"screenshot_data")
        
        action = ScreenshotAction()
        result = await action.execute(mock_page, filename="test.png")
        
        assert result.success is True
        assert "test.png" in result.data
        mock_page.screenshot.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_text_action(self):
        """Test ExtractTextAction execution."""
        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        mock_locator.text_content = AsyncMock(return_value="Extracted text")
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        action = ExtractTextAction()
        result = await action.execute(mock_page, selector="div.content")
        
        assert result.success is True
        assert result.data == "Extracted text"
        mock_locator.text_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_action_with_element_map(self):
        """Test action execution with element ID and map."""
        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        element_map = {
            1: "button#submit",
            2: "input#email",
            3: "div.content"
        }
        
        action = ClickAction()
        result = await action.execute(
            mock_page,
            element_id=1,
            element_map=element_map
        )
        
        assert result.success is True
        mock_page.locator.assert_called_with("button#submit")
    
    @pytest.mark.asyncio
    async def test_action_error_handling(self):
        """Test action error handling."""
        mock_page = AsyncMock()
        mock_page.locator = MagicMock(side_effect=Exception("Element not found"))
        
        action = ClickAction()
        result = await action.execute(mock_page, selector="button")
        
        assert result.success is False
        assert "Element not found" in result.error
        assert result.duration_ms is not None