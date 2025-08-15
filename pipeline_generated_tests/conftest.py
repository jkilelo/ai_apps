# conftest.py

import logging
import os
import pytest
from typing import Generator, Any
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright


# --- Configuration ---
# Load configuration from environment variables
BASE_URL: str = os.environ.get("BASE_URL", "https://github.com")
HEADLESS_MODE: bool = os.environ.get("HEADLESS_MODE", "true").lower() == "true"
SLOW_MO: int = int(os.environ.get("SLOW_MO", "0"))  # Milliseconds delay between steps
SCREENSHOT_ON_FAILURE: bool = os.environ.get(
    "SCREENSHOT_ON_FAILURE", "true"
).lower() == "true"
LOG_LEVEL: int = getattr(
    logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO
)

# --- Logging Setup ---
def setup_logging() -> None:
    """Sets up the logging configuration."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


setup_logging()
logger = logging.getLogger(__name__)

# --- Custom Markers ---
def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as a regression test"
    )
    logger.info("Custom pytest markers registered.")


# --- Fixtures ---
@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    """
    Provides a Playwright browser instance for the entire test session.

    Yields:
        Browser: An instance of a Playwright browser (chromium).
    """
    logger.info("Starting Playwright browser session.")
    try:
        with sync_playwright() as p:
            # Consider using different browsers based on configuration if needed
            browser_instance = p.chromium.launch(
                headless=HEADLESS_MODE,
                slow_mo=SLOW_MO
            )
            yield browser_instance
            logger.info("Closing Playwright browser session.")
            browser_instance.close()
    except Exception as e:
        logger.error(f"Error initializing Playwright browser: {e}")
        pytest.fail(f"Could not start browser: {e}")


@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Provides a Playwright browser context for each test function.

    Args:
        browser (Browser): The Playwright browser instance.

    Yields:
        BrowserContext: A new browser context.
    """
    logger.info("Creating new browser context.")
    try:
        context_instance = browser.new_context()
        yield context_instance
        logger.info("Closing browser context.")
        context_instance.close()
    except Exception as e:
        logger.error(f"Error creating browser context: {e}")
        pytest.fail(f"Could not create context: {e}")


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """
    Provides a Playwright page instance for each test function.

    Args:
        context (BrowserContext): The Playwright browser context.

    Yields:
        Page: A new page within the context.
    """
    logger.info("Creating new page.")
    try:
        page_instance = context.new_page()
        # Navigate to the base URL
        page_instance.goto(BASE_URL)
        logger.info(f"Navigated to base URL: {BASE_URL}")
        yield page_instance
        logger.info("Closing page.")
        page_instance.close()
    except Exception as e:
        logger.error(f"Error creating or navigating page: {e}")
        pytest.fail(f"Could not create or navigate page: {e}")


# --- Hooks ---
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Any:
    """
    Pytest hook to capture test outcomes and take screenshots on failure.

    Args:
        item (pytest.Item): The test item being run.
        call (pytest.CallInfo): Information about the test call.

    Returns:
        Any: The test report object.
    """
    # Execute all other pytest_runtest_makereport hooks
    outcome = yield
    report = outcome.get_result()

    # We only care about failed tests
    if report.when == "call" and report.failed:
        logger.warning(f"Test failed: {item.name}")
        if SCREENSHOT_ON_FAILURE:
            logger.info("Attempting to take screenshot on failure.")
            # Try to get the page object from the test item's fixtures
            page_fixture = item.funcargs.get("page", None)
            if page_fixture:
                try:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    screenshot_path = f"screenshots/failed_test_{item.name}_{timestamp}.png"
                    os.makedirs("screenshots", exist_ok=True)
                    page_fixture.screenshot(path=screenshot_path)
                    logger.info(f"Screenshot saved to: {screenshot_path}")
                    # Optionally attach screenshot path to report for better integration
                    # report.extra = [(screenshot_path, "Screenshot on Failure")]
                except Exception as e:
                    logger.error(f"Failed to take screenshot for {item.name}: {e}")
            else:
                logger.warning(
                    "Could not find 'page' fixture for screenshot. "
                    "Ensure the test function uses the 'page' fixture."
                )
    return report


# For screenshot hook to work, we need datetime
import datetime

# --- Helper Functions (Optional but good practice) ---
def get_base_url() -> str:
    """Returns the configured base URL."""
    return BASE_URL

def is_headless() -> bool:
    """Returns the configured headless mode status."""
    return HEADLESS_MODE

def get_slow_mo() -> int:
    """Returns the configured slow motion delay."""
    return SLOW_MO


# Example of how to use the fixtures in a test file (e.g., test_example.py):
"""
# test_example.py
import pytest
from playwright.sync_api import Page

def test_page_title(page: Page):
    assert "GitHub" in page.title()

def test_navigate_to_about(page: Page):
    page.locator("a", has_text="About").click()
    assert "GitHub, Inc." in page.content()
"""
