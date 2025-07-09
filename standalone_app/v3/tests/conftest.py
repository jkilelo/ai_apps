"""
Pytest configuration for AI Apps v3 testing
Handles Playwright setup, fixtures, and test evidence collection
"""
import os
import pytest
import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Dict, Generator
import json

# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8004")
HEADLESS = os.getenv("TEST_HEADLESS", "false").lower() == "true"
SLOW_MO = int(os.getenv("TEST_SLOW_MO", "100"))
TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30000"))

# Evidence paths
EVIDENCE_BASE = Path(__file__).parent.parent / "test_reports"
SCREENSHOTS_DIR = EVIDENCE_BASE / "screenshots"
VIDEOS_DIR = EVIDENCE_BASE / "videos"
TRACES_DIR = EVIDENCE_BASE / "traces"

# Ensure directories exist
for directory in [SCREENSHOTS_DIR, VIDEOS_DIR, TRACES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def browser():
    """Launch browser instance for all tests"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        yield browser
        await browser.close()


@pytest.fixture(scope="function")
async def context(browser: Browser, request):
    """Create browser context with video recording"""
    test_name = request.node.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    context_options = {
        "base_url": BASE_URL,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
        "record_video_dir": str(VIDEOS_DIR),
        "record_video_size": {"width": 1280, "height": 720},
        "user_agent": "Mozilla/5.0 (Testing) AI-Apps-v3-Tests/1.0"
    }
    
    # Add mobile viewport for mobile tests
    if "mobile" in test_name:
        context_options["viewport"] = {"width": 375, "height": 812}
        context_options["user_agent"] = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 "
            "Mobile/15E148 Safari/604.1"
        )
        context_options["has_touch"] = True
        context_options["is_mobile"] = True
    
    context = await browser.new_context(**context_options)
    
    # Start tracing
    await context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True
    )
    
    yield context
    
    # Save trace
    trace_path = TRACES_DIR / f"{test_name}_{timestamp}.zip"
    await context.tracing.stop(path=str(trace_path))
    
    # Close context
    await context.close()
    
    # Rename video file
    if context.pages:
        page = context.pages[0]
        video = page.video
        if video:
            video_path = await video.path()
            if video_path and Path(video_path).exists():
                new_video_path = VIDEOS_DIR / f"{test_name}_{timestamp}.webm"
                Path(video_path).rename(new_video_path)


@pytest.fixture(scope="function")
async def page(context: BrowserContext, request):
    """Create page for test with automatic failure screenshots"""
    page = await context.new_page()
    page.set_default_timeout(TIMEOUT)
    
    # Test metadata
    test_name = request.node.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Navigate to base URL
    await page.goto("/")
    
    # Add console message collection
    console_messages = []
    page.on("console", lambda msg: console_messages.append({
        "type": msg.type,
        "text": msg.text,
        "time": datetime.now().isoformat()
    }))
    
    # Add network error collection
    network_errors = []
    page.on("requestfailed", lambda req: network_errors.append({
        "url": req.url,
        "failure": req.failure,
        "time": datetime.now().isoformat()
    }))
    
    yield page
    
    # Save test evidence
    evidence_data = {
        "test_name": test_name,
        "timestamp": timestamp,
        "console_messages": console_messages,
        "network_errors": network_errors,
        "test_passed": not request.node.rep_call.failed if hasattr(request.node, "rep_call") else True
    }
    
    # Take screenshot on failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshot_path = SCREENSHOTS_DIR / f"{test_name}_{timestamp}_failure.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        evidence_data["failure_screenshot"] = str(screenshot_path)
    
    # Save evidence JSON
    evidence_path = EVIDENCE_BASE / "evidence" / f"{test_name}_{timestamp}.json"
    evidence_path.parent.mkdir(exist_ok=True)
    with open(evidence_path, "w") as f:
        json.dump(evidence_data, f, indent=2)


@pytest.fixture
def take_screenshot(page: Page):
    """Helper fixture to take screenshots during tests"""
    async def _take_screenshot(name: str, full_page: bool = True):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = SCREENSHOTS_DIR / f"{name}_{timestamp}.png"
        await page.screenshot(path=str(screenshot_path), full_page=full_page)
        return str(screenshot_path)
    
    return _take_screenshot


@pytest.fixture
def assert_accessibility(page: Page):
    """Helper fixture for accessibility assertions"""
    async def _assert_accessibility():
        # Check for basic accessibility
        violations = []
        
        # Check for alt text on images
        images = await page.query_selector_all("img:not([alt])")
        if images:
            violations.append(f"Found {len(images)} images without alt text")
        
        # Check for labels on form inputs
        inputs = await page.query_selector_all("input:not([aria-label]):not([id])")
        for inp in inputs:
            input_id = await inp.get_attribute("id")
            if not input_id:
                label = await page.query_selector(f"label[for='{input_id}']")
                if not label:
                    violations.append("Found input without label")
        
        # Check for heading hierarchy
        headings = await page.query_selector_all("h1, h2, h3, h4, h5, h6")
        prev_level = 0
        for heading in headings:
            tag_name = await heading.evaluate("el => el.tagName")
            level = int(tag_name[1])
            if prev_level > 0 and level > prev_level + 1:
                violations.append(f"Heading hierarchy broken: {tag_name} after h{prev_level}")
            prev_level = level
        
        assert not violations, f"Accessibility violations: {violations}"
    
    return _assert_accessibility


@pytest.fixture
def measure_performance(page: Page):
    """Helper fixture to measure page performance"""
    async def _measure_performance():
        metrics = await page.evaluate("""() => {
            const navigation = performance.getEntriesByType('navigation')[0];
            const paint = performance.getEntriesByType('paint');
            
            return {
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                firstPaint: paint.find(p => p.name === 'first-paint')?.startTime,
                firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime,
                resourceCount: performance.getEntriesByType('resource').length
            };
        }""")
        
        return metrics
    
    return _measure_performance


# Pytest hooks
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Make test result available to fixtures"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "smoke: Quick smoke tests")
    config.addinivalue_line("markers", "mobile: Mobile-specific tests")
    config.addinivalue_line("markers", "desktop: Desktop-specific tests")
    config.addinivalue_line("markers", "critical: Critical path tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_html_report_title(report):
    """Set HTML report title"""
    report.title = "AI Apps v3 - Test Report"