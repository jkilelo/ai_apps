"""
Pytest Configuration and Fixtures for AI Browser Testing
Provides mock objects, test data, and helper functions
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel


# Test configuration
TEST_TIMEOUT = 30  # seconds
TEST_DATA_DIR = Path(__file__).parent / "test_data"


# =============================================================================
# Browser Fixtures
# =============================================================================

@pytest.fixture
async def mock_browser():
    """Mock Playwright browser for testing"""
    browser = AsyncMock()
    
    # Mock page
    page = AsyncMock()
    page.url = "https://example.com"
    page.title = AsyncMock(return_value="Example Page")
    page.content = AsyncMock(return_value="<html><body>Test content</body></html>")
    page.screenshot = AsyncMock(return_value=b"fake_screenshot_data")
    page.evaluate = AsyncMock(return_value={"width": 1920, "height": 1080})
    
    # Mock selectors
    page.query_selector = AsyncMock(return_value=AsyncMock())
    page.query_selector_all = AsyncMock(return_value=[AsyncMock() for _ in range(3)])
    
    # Mock actions
    page.click = AsyncMock()
    page.fill = AsyncMock()
    page.type = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.goto = AsyncMock()
    
    # Connect browser to page
    browser.new_page = AsyncMock(return_value=page)
    browser.close = AsyncMock()
    
    return browser


@pytest.fixture
async def mock_browser_context():
    """Mock browser context with stealth"""
    context = AsyncMock()
    context.add_init_script = AsyncMock()
    context.set_extra_http_headers = AsyncMock()
    context.clear_cookies = AsyncMock()
    context.storage_state = AsyncMock(return_value={})
    
    return context


# =============================================================================
# LLM Fixtures
# =============================================================================

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for action generation"""
    return {
        "action": "click",
        "selector": "button[type='submit']",
        "reasoning": "User wants to submit the form",
        "confidence": 0.95,
        "fallback_selectors": [
            "input[type='submit']",
            ".submit-button"
        ]
    }


@pytest.fixture
def mock_llm_client():
    """Mock LLM client (OpenAI/Anthropic/Google)"""
    client = MagicMock()
    
    # Mock completion
    completion = MagicMock()
    completion.choices = [
        MagicMock(message=MagicMock(content='{"action": "click", "selector": "button"}'))
    ]
    
    client.chat.completions.create = MagicMock(return_value=completion)
    
    return client


@pytest.fixture
def mock_multi_llm_providers():
    """Mock multiple LLM providers for testing fallbacks"""
    providers = {
        "openai": AsyncMock(return_value={"provider": "openai", "response": "OpenAI response"}),
        "anthropic": AsyncMock(return_value={"provider": "anthropic", "response": "Claude response"}),
        "google": AsyncMock(return_value={"provider": "google", "response": "Gemini response"})
    }
    return providers


# =============================================================================
# Memory Fixtures
# =============================================================================

@pytest.fixture
async def mock_sqlite_memory():
    """Mock SQLite memory storage"""
    memory = AsyncMock()
    memory.store = AsyncMock()
    memory.retrieve = AsyncMock(return_value=[])
    memory.search = AsyncMock(return_value=[])
    memory.clear = AsyncMock()
    
    return memory


@pytest.fixture
async def mock_vector_store():
    """Mock Qdrant vector store"""
    store = AsyncMock()
    store.add_documents = AsyncMock()
    store.search = AsyncMock(return_value=[
        {"id": "1", "score": 0.95, "payload": {"text": "Similar document"}}
    ])
    store.delete = AsyncMock()
    
    return store


@pytest.fixture
async def mock_graph_db():
    """Mock FalkorDB graph database"""
    db = AsyncMock()
    db.query = AsyncMock(return_value=[])
    db.create_node = AsyncMock()
    db.create_edge = AsyncMock()
    db.find_path = AsyncMock(return_value=[])
    
    return db


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_dom():
    """Sample DOM structure for testing"""
    return {
        "url": "https://example.com",
        "title": "Test Page",
        "elements": [
            {
                "tag": "button",
                "text": "Submit",
                "attributes": {"type": "submit", "class": "btn-primary"},
                "selector": "button.btn-primary",
                "interactive": True,
                "visible": True
            },
            {
                "tag": "input",
                "attributes": {"type": "text", "name": "username"},
                "selector": "input[name='username']",
                "interactive": True,
                "visible": True
            },
            {
                "tag": "a",
                "text": "Click here",
                "attributes": {"href": "/next-page"},
                "selector": "a[href='/next-page']",
                "interactive": True,
                "visible": True
            }
        ]
    }


@pytest.fixture
def sample_screenshot():
    """Sample screenshot data"""
    # Create a small PNG-like byte array (not a real PNG)
    return b'\x89PNG\r\n\x1a\n' + b'\x00' * 100


@pytest.fixture
def sample_page_state():
    """Complete page state for testing"""
    return {
        "url": "https://example.com",
        "title": "Test Page",
        "dom": {
            "interactive_elements": 15,
            "forms": 2,
            "buttons": 5,
            "links": 8
        },
        "screenshot": "base64_encoded_screenshot",
        "timestamp": "2025-01-01T00:00:00Z",
        "metadata": {
            "viewport": {"width": 1920, "height": 1080},
            "cookies": 3,
            "local_storage_items": 5
        }
    }


@pytest.fixture
def sample_task():
    """Sample user task for testing"""
    return {
        "id": "task_123",
        "description": "Search for Python tutorials and save the first 5 results",
        "url": "https://google.com",
        "steps": [
            "Navigate to Google",
            "Enter 'Python tutorials' in search box",
            "Click search button",
            "Extract first 5 results",
            "Save to memory"
        ],
        "expected_output": "List of tutorial links"
    }


# =============================================================================
# Plugin Fixtures
# =============================================================================

@pytest.fixture
def mock_stealth_plugin():
    """Mock stealth plugin"""
    plugin = AsyncMock()
    plugin.name = "webdriver_fix"
    plugin.apply = AsyncMock()
    plugin.is_compatible = MagicMock(return_value=True)
    plugin.get_metadata = MagicMock(return_value={
        "name": "webdriver_fix",
        "version": "1.0.0",
        "description": "Remove webdriver detection"
    })
    
    return plugin


@pytest.fixture
def mock_plugin_manager():
    """Mock plugin manager"""
    manager = AsyncMock()
    manager.load_plugins = AsyncMock()
    manager.apply_plugins = AsyncMock()
    manager.get_loaded_plugins = MagicMock(return_value=["webdriver_fix", "canvas_noise"])
    
    return manager


# =============================================================================
# Error Simulation Fixtures
# =============================================================================

@pytest.fixture
def browser_timeout_error():
    """Simulate browser timeout error"""
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError
    return PlaywrightTimeoutError("Timeout 30000ms exceeded")


@pytest.fixture
def llm_rate_limit_error():
    """Simulate LLM rate limit error"""
    return Exception("Rate limit exceeded. Please retry after 60 seconds.")


@pytest.fixture
def network_error():
    """Simulate network error"""
    return ConnectionError("Failed to establish connection")


# =============================================================================
# Helper Functions
# =============================================================================

@pytest.fixture
def create_temp_file(tmp_path):
    """Create temporary file for testing"""
    def _create(filename: str, content: str) -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path
    return _create


@pytest.fixture
async def async_timeout():
    """Async timeout context manager for tests"""
    async def _timeout(seconds: int = TEST_TIMEOUT):
        return asyncio.wait_for
    return _timeout


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables"""
    def _set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)
    return _set_env


# =============================================================================
# Assertion Helpers
# =============================================================================

@pytest.fixture
def assert_called_with_timeout():
    """Assert async mock was called within timeout"""
    async def _assert(mock_obj, timeout=1):
        for _ in range(int(timeout * 10)):
            if mock_obj.called:
                return True
            await asyncio.sleep(0.1)
        raise AssertionError(f"Mock not called within {timeout}s")
    return _assert


@pytest.fixture
def assert_browser_action():
    """Assert browser action was performed correctly"""
    def _assert(page_mock, action_type: str, selector: str):
        if action_type == "click":
            page_mock.click.assert_called_with(selector)
        elif action_type == "fill":
            page_mock.fill.assert_called()
        elif action_type == "type":
            page_mock.type.assert_called()
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    return _assert


# =============================================================================
# Performance Testing
# =============================================================================

@pytest.fixture
def measure_performance():
    """Measure async operation performance"""
    import time
    
    async def _measure(operation, expected_duration: float):
        start = time.perf_counter()
        result = await operation()
        duration = time.perf_counter() - start
        
        assert duration < expected_duration, \
            f"Operation took {duration:.2f}s, expected < {expected_duration}s"
        
        return result, duration
    
    return _measure


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "stealth: marks tests that require stealth features"
    )
    config.addinivalue_line(
        "markers", "llm: marks tests that use LLM providers"
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Test Data Loaders
# =============================================================================

@pytest.fixture
def load_test_data():
    """Load test data from JSON files"""
    def _load(filename: str) -> Dict[str, Any]:
        file_path = TEST_DATA_DIR / f"{filename}.json"
        if file_path.exists():
            return json.loads(file_path.read_text())
        return {}
    return _load


@pytest.fixture
def save_test_output(tmp_path):
    """Save test output for debugging"""
    def _save(filename: str, content: Any):
        output_path = tmp_path / "test_output"
        output_path.mkdir(exist_ok=True)
        
        file_path = output_path / filename
        if isinstance(content, dict) or isinstance(content, list):
            file_path.write_text(json.dumps(content, indent=2))
        else:
            file_path.write_text(str(content))
        
        return file_path
    return _save