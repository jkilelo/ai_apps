# conftest.py

"""
Pytest configuration file for Playwright test automation.

This file sets up necessary fixtures, hooks, and configuration for running
Playwright tests with pytest.
"""

import logging
import os
import pytest
from logging import Logger
from typing import Generator, Any

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    sync_playwright,
    Playwright,
)

# --- Configuration ---

# Load configuration from environment variables
BASE_URL: str = os.environ.get("BASE_URL", "https://github.com")
HEADLESS: bool = os.environ.get("HEADLESS", "true").lower() == "true"
SLOW_MO: int = int(os.environ.get("SLOW_MO", "0"))
SCREENSHOT_ON_FAILURE: bool = os.environ.get("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO").upper()

# --- Logging Setup ---

def setup_logging() -> None:
    """Sets up the logging configuration."""
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    # Prevent adding multiple handlers if conftest is imported multiple times
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

setup_logging()
logger: Logger = logging.getLogger(__name__)
logger.info(f"Logging level set to: {LOG_LEVEL}")
logger.info(f"Base URL: {BASE_URL}")
logger.info(f"Headless mode: {HEADLESS}")
logger.info(f"Slow motion: {SLOW_MO}")
logger.info(f"Screenshot on failure: {SCREENSHOT_ON_FAILURE}")

# --- Custom Markers ---

def pytest_configure(config: pytest.Config) -> None:
    """Adds custom markers to pytest configuration."""
    config.addinivalue_line(
        "markers", "smoke: marks tests as smoke tests"
    )
    config.addinivalue_line(
        "markers", "regression: marks tests as regression tests"
    )
    config.addinivalue_line(
        "markers", "ui: marks tests as UI tests"
    )
    logger.info("Custom pytest markers configured.")

# --- Fixtures ---

@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """
    Provides a Playwright instance for the entire test session.

    Yields:
        Playwright: An initialized Playwright instance.
    """
    logger.info("Starting Playwright session...")
    try:
        with sync_playwright() as p:
            yield p
        logger.info("Playwright session ended.")
    except Exception as e:
        logger.error(f"Error during Playwright initialization: {e}")
        pytest.fail(f"Failed to initialize Playwright: {e}")

@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Generator[Browser, None, None]:
    """
    Provides a browser instance (Chromium) for the entire test session.

    Args:
        playwright_instance: The Playwright instance.

    Yields:
        Browser: A configured browser instance.
    """
    browser_type = "chromium"  # Default to chromium
    logger.info(f"Launching {browser_type} browser...")
    browser: Browser | None = None
    try:
        browser = playwright_instance.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO,
            args=["--start-maximized"]  # Try to maximize the window
        )
        yield browser
        logger.info("Closing browser...")
        browser.close()
        logger.info("Browser closed.")
    except Exception as e:
        logger.error(f"Error launching or closing browser: {e}")
        if browser:
            try:
                browser.close()
            except Exception as close_err:
                logger.error(f"Error during browser cleanup: {close_err}")
        pytest.fail(f"Failed to launch or manage browser: {e}")

@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Provides a browser context for each test function.

    Args:
        browser: The browser instance.

    Yields:
        BrowserContext: A configured browser context.
    """
    logger.info("Creating new browser context...")
    context: BrowserContext | None = None
    try:
        context = browser.new_context(
            locale="en-US",
            timezone_id="UTC",
            extra_http_headers={
                "Accept-Language": "en-US",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"  # Example User-Agent
            }
        )
        logger.info("New browser context created.")
        yield context
        logger.info("Closing browser context...")
        context.close()
        logger.info("Browser context closed.")
    except Exception as e:
        logger.error(f"Error creating or closing browser context: {e}")
        if context:
            try:
                context.close()
            except Exception as close_err:
                logger.error(f"Error during context cleanup: {close_err}")
        pytest.fail(f"Failed to create or manage browser context: {e}")


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """
    Provides a new page for each test function.

    Args:
        context: The browser context.

    Yields:
        Page: A new page object.
    """
    logger.info("Creating new page...")
    page_obj: Page | None = None
    try:
        page_obj = context.new_page()
        logger.info("New page created.")
        # Navigate to the base URL by default
        logger.info(f"Navigating to base URL: {BASE_URL}")
        page_obj.goto(BASE_URL)
        logger.info(f"Navigation to {BASE_URL} successful.")
        yield page_obj
        logger.info("Closing page...")
        # Page is automatically closed when context is closed, but explicit close is good practice
        if page_obj:
            try:
                page_obj.close()
                logger.info("Page closed.")
            except Exception as close_err:
                logger.error(f"Error during page cleanup: {close_err}")
    except Exception as e:
        logger.error(f"Error creating, navigating, or closing page: {e}")
        if page_obj:
            try:
                page_obj.close()
            except Exception as close_err:
                logger.error(f"Error during page cleanup after error: {close_err}")
        pytest.fail(f"Failed to create, navigate, or manage page: {e}")

# --- Hooks ---

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo
) -> None:
    """
    A pytest hook that captures screenshots on test failure.

    This hook wraps around the standard test execution and, if a test fails,
    it attempts to take a screenshot using the 'page' fixture if available.
    """
    outcome = yield
    report = outcome.get_result()

    # Check if the test failed and if a 'page' fixture is available
    if report.when == "call" and report.failed:
        logger.warning(f"Test '{item.name}' failed. Attempting to take screenshot.")
        if SCREENSHOT_ON_FAILURE:
            # Access the 'page' fixture from the test item's metadata
            # The page fixture is typically the last fixture yielded for a function-scoped fixture
            page_fixture = item.funcargs.get("page")
            if page_fixture and isinstance(page_fixture, Page):
                try:
                    screenshot_path = f"screenshots/failure_{item.name}.png"
                    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                    page_fixture.screenshot(path=screenshot_path)
                    logger.info(f"Screenshot saved to: {screenshot_path}")
                    # Optionally, attach the screenshot to the report if using pytest-html or similar
                    # report.extra = getattr(report, "extra", [])
                    # report.extra.append(pytest_html.extras.png(screenshot_path))
                except Exception as e:
                    logger.error(f"Failed to take screenshot for '{item.name}': {e}")
            else:
                logger.warning(
                    "Page fixture not found or not a Playwright Page object. "
                    "Cannot take screenshot."
                )
        else:
            logger.info("Screenshot on failure is disabled.")


# --- Helper Functions (Optional but good practice) ---

def get_base_url() -> str:
    """Returns the configured base URL."""
    return BASE_URL

def get_logger() -> Logger:
    """Returns the configured logger instance."""
    return logger

# Example usage of fixtures in a test file (e.g., test_example.py):
"""
# test_example.py

import pytest
from playwright.sync_api import Page

from conftest import get_base_url, get_logger

logger = get_logger()

@pytest.mark.ui
def test_page_title(page: Page) -> None:
    logger.info("Testing page title...")
    expected_title = "GitHub: Let’s build from here"
    assert page.title() == expected_title, f"Expected title '{expected_title}', but got '{page.title()}'"
    logger.info("Page title test passed.")

@pytest.mark.regression
def test_navigation(page: Page) -> None:
    logger.info("Testing navigation to another page...")
    about_url = f"{get_base_url()}/about"
    page.goto(about_url)
    assert page.url == about_url, f"Expected URL '{about_url}', but got '{page.url}'"
    logger.info("Navigation test passed.")

def test_element_visibility(page: Page) -> None:
    logger.info("Testing element visibility...")
    # Example: Find the GitHub logo (adjust selector if needed)
    logo_selector = 'a[aria-label="GitHub"] svg'
    logo_element = page.locator(logo_selector)
    assert logo_element.is_visible(), "GitHub logo should be visible on the homepage"
    logger.info("Element visibility test passed.")
"""

