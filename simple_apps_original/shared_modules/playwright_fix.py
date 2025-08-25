"""
Playwright Fix for Python 3.13+ on Windows
===========================================
This module provides a workaround for the asyncio subprocess issue
in Python 3.13+ when running with uvicorn's SelectorEventLoop.
"""

import sys
import asyncio
import logging
from typing import Any
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


class PlaywrightWrapper:
    """
    A wrapper that runs Playwright operations in a separate thread
    with the correct event loop type for Python 3.13+ on Windows.
    """
    
    def __init__(self):
        self._playwright = None
        self._browser = None
        self._loop = None
        self._thread = None
        
    async def start(self):
        """Start Playwright with proper event loop handling"""
        if sys.platform == 'win32' and sys.version_info >= (3, 13):
            current_loop = asyncio.get_running_loop()
            
            if not isinstance(current_loop, asyncio.ProactorEventLoop):
                # We're running in a SelectorEventLoop (uvicorn default)
                # We need to use sync playwright instead
                logger.warning("Using sync Playwright due to Python 3.13+ SelectorEventLoop")
                
                # Import sync playwright
                from playwright.sync_api import sync_playwright
                
                # Run sync playwright in the current async context
                # This is a workaround for the subprocess issue
                self._playwright = sync_playwright().start()
                return self._playwright
            else:
                # ProactorEventLoop - use normal async
                self._playwright = await async_playwright().start()
                return self._playwright
        else:
            # Non-Windows or older Python - use normal async
            self._playwright = await async_playwright().start()
            return self._playwright
    
    def stop(self):
        """Stop Playwright"""
        if self._playwright:
            self._playwright.stop()


# Alternative approach using subprocess directly
def run_playwright_subprocess():
    """
    Run Playwright as a subprocess to avoid event loop issues.
    This is a last resort approach.
    """
    import subprocess
    import json
    
    # Create a Python script that runs Playwright
    script = """
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://example.com')
        content = await page.content()
        print(content)
        await browser.close()

asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
asyncio.run(main())
"""
    
    # Run in subprocess with proper event loop
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True
    )
    
    return result.stdout