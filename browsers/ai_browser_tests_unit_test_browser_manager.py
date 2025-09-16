"""Unit tests for BrowserManager"""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from src.execution.browser_manager import BrowserManager


class TestBrowserManager:
    """Test cases for BrowserManager"""
    
    @pytest.mark.asyncio
    async def test_browser_launch(self):
        """Test browser can launch successfully"""
        manager = BrowserManager()
        
        # Mock playwright browser for testing
        with patch.object(manager, '_launch_playwright') as mock_launch:
            mock_browser = AsyncMock()
            mock_launch.return_value = mock_browser
            
            browser = await manager.launch()
            assert browser is not None
            mock_launch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stealth_mode_enabled(self):
        """Test stealth mode is properly configured"""
        manager = BrowserManager(config={'stealth': True})
        
        with patch.object(manager, '_apply_stealth_config') as mock_stealth:
            mock_stealth.return_value = True
            
            await manager.launch()
            mock_stealth.assert_called()
    
    @pytest.mark.asyncio
    async def test_browser_close(self):
        """Test browser closes properly"""
        manager = BrowserManager()
        
        with patch.object(manager, '_browser') as mock_browser:
            mock_browser.close = AsyncMock()
            await manager.close()
            mock_browser.close.assert_called_once()
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config
        config = {'headless': True, 'stealth': True}
        manager = BrowserManager(config=config)
        assert manager.config['headless'] is True
        
        # Invalid config should use defaults
        manager = BrowserManager(config={'invalid_key': 'value'})
        assert 'headless' in manager.config  # Should have default values
    
    @pytest.mark.asyncio
    async def test_context_creation(self):
        """Test browser context creation"""
        manager = BrowserManager()
        
        with patch.object(manager, '_browser') as mock_browser:
            mock_context = AsyncMock()
            mock_browser.new_context.return_value = mock_context
            
            context = await manager.create_context()
            assert context is not None
            mock_browser.new_context.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_page_creation(self):
        """Test page creation within context"""
        manager = BrowserManager()
        
        with patch.object(manager, '_context') as mock_context:
            mock_page = AsyncMock()
            mock_context.new_page.return_value = mock_page
            
            page = await manager.create_page()
            assert page is not None
            mock_context.new_page.assert_called_once()
    
    def test_viewport_configuration(self):
        """Test viewport configuration"""
        config = {'viewport_width': 1920, 'viewport_height': 1080}
        manager = BrowserManager(config=config)
        
        assert manager.config['viewport_width'] == 1920
        assert manager.config['viewport_height'] == 1080
    
    @pytest.mark.asyncio
    async def test_user_agent_setting(self):
        """Test custom user agent setting"""
        custom_ua = "Mozilla/5.0 (Test Browser)"
        manager = BrowserManager(config={'user_agent': custom_ua})
        
        with patch.object(manager, '_context') as mock_context:
            await manager.set_user_agent(custom_ua)
            mock_context.set_extra_http_headers.assert_called()


@pytest.mark.integration
class TestBrowserManagerIntegration:
    """Integration tests requiring actual browser"""
    
    @pytest.mark.asyncio
    async def test_real_browser_launch(self):
        """Test with real Playwright browser (slow test)"""
        manager = BrowserManager(config={'headless': True})
        
        try:
            browser = await manager.launch()
            assert browser is not None
            
            # Test basic navigation
            page = await manager.create_page()
            await page.goto('about:blank')
            assert page.url == 'about:blank'
            
        finally:
            await manager.close()
    
    @pytest.mark.asyncio
    async def test_stealth_implementation(self):
        """Test stealth features work with real browser"""
        manager = BrowserManager(config={'headless': True, 'stealth': True})
        
        try:
            await manager.launch()
            page = await manager.create_page()
            
            # Test webdriver detection evasion
            webdriver_value = await page.evaluate('() => navigator.webdriver')
            assert webdriver_value is None or webdriver_value is False
            
            # Test plugins array
            plugins_length = await page.evaluate('() => navigator.plugins.length')
            assert plugins_length > 0  # Should have fake plugins
            
        finally:
            await manager.close()