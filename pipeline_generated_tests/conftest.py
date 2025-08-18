"""
Pytest conftest.py for Playwright test automation.

This file sets up pytest fixtures for Playwright, including browser,
context, and page. It also configures custom markers, handles
environment variables for configuration, sets up logging, and
implements a hook to take screenshots on test failures.
"""

import logging
import os
import pytest
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    sync_playwright,
)
from typing import Generator

# --- Configuration ---
# Load configuration from environment variables
BASE_URL = os.environ.get("PLAYWRIGHT_BASE_URL", "https://github.com")


# --- Logging Setup ---
def setup_logging():
    """Configures the logging format and level."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger("playwright").setLevel(logging.WARNING)  # Reduce Playwright's verbosity


setup_logging()
logger = logging.getLogger(__name__)

# --- Custom Markers ---
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "smoke: marks tests as smoke tests",
    )
    config.addinivalue_line(
        "markers",
        "regression: marks tests as regression tests",
    )


# --- Fixtures ---
@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    """
    Provides a Playwright browser instance.

    This fixture is session-scoped, meaning the browser is launched once
    per test session and reused across all tests.

    Yields:
        Browser: An instance of a Playwright browser.
    """
    logger.info("Launching browser...")
    try:
        with sync_playwright() as p:
            # You can specify different browser types here, e.g., 'firefox', 'webkit'
            browser_instance = p.chromium.launch()
            yield browser_instance
            logger.info("Closing browser...")
            browser_instance.close()
    except Exception as e:
        logger.error(f"Error launching or closing browser: {e}")
        pytest.fail(f"Failed to initialize browser: {e}")


@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Provides a Playwright browser context.

    This fixture is function-scoped, meaning a new context is created for
    each test function. This ensures test isolation.

    Args:
        browser (Browser): The Playwright browser instance (from the 'browser' fixture).

    Yields:
        BrowserContext: An instance of a Playwright browser context.
    """
    logger.info("Creating new browser context...")
    try:
        context_instance = browser.new_context()
        yield context_instance
        logger.info("Closing browser context...")
        context_instance.close()
    except Exception as e:
        logger.error(f"Error creating or closing browser context: {e}")
        pytest.fail(f"Failed to initialize browser context: {e}")


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """
    Provides a Playwright page object.

    This fixture is function-scoped, meaning a new page is created for
    each test function.

    Args:
        context (BrowserContext): The Playwright browser context instance
                                  (from the 'context' fixture).

    Yields:
        Page: An instance of a Playwright page.
    """
    logger.info("Creating new page...")
    try:
        page_instance = context.new_page()
        # Navigate to the base URL by default for each page
        page_instance.goto(BASE_URL)
        logger.info(f"Navigated to base URL: {BASE_URL}")
        yield page_instance
        logger.info("Closing page...")
        page_instance.close()
    except Exception as e:
        logger.error(f"Error creating or closing page, or navigating: {e}")
        pytest.fail(f"Failed to initialize page or navigate: {e}")


# --- Hooks ---
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook to capture test outcomes and take screenshots on failure.
    """
    outcome = yield
    report = outcome.get_result()

    # Only process if the test item has a page fixture, indicating Playwright usage
    # and if the test failed.
    if report.when == "call" and report.failed:
        logger.warning(f"Test '{item.name}' failed. Attempting to take screenshot.")
        try:
            # Access the page fixture if it's available for this test item.
            # This assumes the page fixture is directly used or indirectly by other fixtures.
            page = item.funcargs.get("page")
            if page and isinstance(page, Page):
                screenshot_path = f"screenshots/{item.name}.png"
                os.makedirs("screenshots", exist_ok=True)
                page.screenshot(path=screenshot_path)
                logger.info(f"Screenshot saved to: {screenshot_path}")
                # Optionally add the screenshot path to the report
                report.extra = getattr(report, "extra", [])
                report.extra.append(pytest.File(screenshot_path))
            else:
                logger.warning("Page fixture not available or not a Playwright Page object for screenshot.")
        except Exception as e:
            logger.error(f"Error taking screenshot for '{item.name}': {e}")

# Example of how to use the fixtures in a test file (e.g., test_example.py):
"""
# test_example.py
import pytest

# Apply custom markers
@pytest.mark.smoke
def test_github_homepage_title(page: Page):
    assert page.title() == "GitHub: Let’s build from here"

@pytest.mark.regression
def test_github_login_form_visibility(page: Page):
    # Example: Navigate to login page and check if form elements are visible
    page.goto("https://github.com/login")
    assert page.is_visible("input[name='login']")
    assert page.is_visible("input[name='password']")
"""
