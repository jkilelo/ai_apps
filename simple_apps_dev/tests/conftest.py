"""
Pytest configuration and fixtures for Simple Apps v2.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, Any
from unittest.mock import AsyncMock, Mock

import pytest
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simple_apps_v2.core.config import get_settings
from simple_apps_v2.core.logging import setup_logging
from simple_apps_v2.services.browser import BrowserService
from simple_apps_v2.services.llm import LLMService
from simple_apps_v2.core.models import BrowserConfig


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    # Fix for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings():
    """Get application settings for tests."""
    # Override settings for testing
    os.environ["DEBUG"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["BROWSER_HEADLESS"] = "true"
    
    return get_settings()


@pytest.fixture(scope="session", autouse=True)
def setup_test_logging(settings):
    """Setup logging for tests."""
    setup_logging(level="DEBUG", rich_console=False)


@pytest.fixture
def browser_config() -> BrowserConfig:
    """Browser configuration for tests."""
    return BrowserConfig(
        headless=True,
        viewport_width=1280,
        viewport_height=720,
        timeout=30000,
        navigation_timeout=30000,
    )


@pytest.fixture
async def browser_service(browser_config) -> AsyncGenerator[BrowserService, None]:
    """Browser service instance for tests."""
    service = BrowserService(browser_config)
    await service.start()
    yield service
    await service.stop()


@pytest.fixture
async def playwright_browser() -> AsyncGenerator[Browser, None]:
    """Raw Playwright browser instance."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def browser_context(playwright_browser: Browser) -> AsyncGenerator[BrowserContext, None]:
    """Browser context for isolated testing."""
    context = await playwright_browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    yield context
    await context.close()


@pytest.fixture
async def page(browser_context: BrowserContext) -> AsyncGenerator[Page, None]:
    """Page instance for testing."""
    page = await browser_context.new_page()
    yield page
    await page.close()


@pytest.fixture
def mock_llm_service() -> Mock:
    """Mock LLM service for testing without API calls."""
    mock_service = Mock(spec=LLMService)
    
    # Mock successful response
    mock_response = Mock()
    mock_response.success = True
    mock_response.content = '{"test": "response"}'
    mock_response.provider = "mock"
    mock_response.model = "mock-model"
    mock_response.response_time = 0.1
    mock_response.tokens_used = 100
    
    mock_service.query_async = AsyncMock(return_value=mock_response)
    mock_service.query_sync = Mock(return_value=mock_response)
    mock_service.analyze_elements = AsyncMock(return_value={"summary": "Mock analysis"})
    
    return mock_service


@pytest.fixture
def sample_elements() -> list[Dict[str, Any]]:
    """Sample extracted elements for testing."""
    return [
        {
            "selector": "#login-button",
            "tag_name": "button",
            "element_type": "button",
            "category": "button",
            "text": "Login",
            "visible": True,
            "enabled": True,
            "clickable": True,
            "x": 100,
            "y": 200,
            "width": 80,
            "height": 30,
        },
        {
            "selector": "#username",
            "tag_name": "input",
            "element_type": "text",
            "category": "form_input",
            "placeholder": "Enter username",
            "visible": True,
            "enabled": True,
            "clickable": False,
            "x": 50,
            "y": 150,
            "width": 200,
            "height": 25,
        },
        {
            "selector": "a[href='/home']",
            "tag_name": "a", 
            "element_type": "link",
            "category": "navigation",
            "text": "Home",
            "href": "/home",
            "visible": True,
            "enabled": True,
            "clickable": True,
            "x": 10,
            "y": 10,
            "width": 50,
            "height": 20,
        }
    ]


@pytest.fixture
def sample_extraction_result(sample_elements) -> Dict[str, Any]:
    """Sample extraction result for testing."""
    return {
        "success": True,
        "url": "https://example.com",
        "total_elements": len(sample_elements),
        "elements": sample_elements,
        "elements_by_category": {
            "button": [sample_elements[0]],
            "form_input": [sample_elements[1]],
            "navigation": [sample_elements[2]],
        },
        "extraction_time": 1.5,
        "llm_analysis": {
            "summary": "Sample analysis",
            "critical_elements": ["#login-button"],
            "recommendations": ["Test login functionality"],
        },
        "metadata": {
            "page_title": "Test Page",
            "page_url": "https://example.com",
            "extracted_at": "2024-01-01T00:00:00",
        }
    }


@pytest.fixture
def sample_test_scenarios() -> list[Dict[str, Any]]:
    """Sample test scenarios for testing."""
    return [
        {
            "id": "test_login",
            "title": "User Login Test",
            "description": "Test user login functionality",
            "category": "authentication",
            "priority": "critical",
            "given": ["User is on login page"],
            "when": ["User enters credentials", "User clicks login"],
            "then": ["User is redirected to dashboard"],
            "target_elements": ["#username", "#password", "#login-button"],
        },
        {
            "id": "test_navigation",
            "title": "Navigation Test",
            "description": "Test main navigation links",
            "category": "navigation",
            "priority": "high",
            "given": ["User is on home page"],
            "when": ["User clicks navigation link"],
            "then": ["User is taken to correct page"],
            "target_elements": ["a[href='/home']", "a[href='/about']"],
        }
    ]


@pytest.fixture
def temp_test_directory(tmp_path: Path) -> Path:
    """Temporary directory for test file operations."""
    test_dir = tmp_path / "test_output"
    test_dir.mkdir()
    return test_dir


@pytest.fixture
def mock_playwright():
    """Mock Playwright for tests that don't need real browser."""
    mock_playwright = Mock()
    mock_browser = Mock()
    mock_context = Mock()
    mock_page = Mock()
    
    # Setup mock chain
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    
    # Mock page methods
    mock_page.goto = AsyncMock()
    mock_page.title = AsyncMock(return_value="Test Page")
    mock_page.url = "https://example.com"
    mock_page.screenshot = AsyncMock(return_value=b"fake_screenshot_data")
    mock_page.evaluate = AsyncMock(return_value=[])
    mock_page.close = AsyncMock()
    mock_context.close = AsyncMock()
    mock_browser.close = AsyncMock()
    
    return mock_playwright


# Pytest hooks
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"  
    )
    config.addinivalue_line(
        "markers", "browser: mark test as requiring browser automation"
    )
    config.addinivalue_line(
        "markers", "llm: mark test as requiring LLM API access"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add integration marker to integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add e2e marker to e2e tests
        if "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        
        # Add browser marker to browser tests
        if "browser" in item.nodeid or "playwright" in item.nodeid:
            item.add_marker(pytest.mark.browser)
        
        # Add llm marker to LLM tests
        if "llm" in item.nodeid:
            item.add_marker(pytest.mark.llm)


@pytest.fixture(autouse=True)
def cleanup_env_vars():
    """Cleanup environment variables after each test."""
    original_env = dict(os.environ)
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)