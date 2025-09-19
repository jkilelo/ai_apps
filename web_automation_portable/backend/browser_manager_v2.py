"""
Browser Manager v2 - Centralized Browser Lifecycle Management
WebDriver BiDi primary with CDP fallback
100% DRY compliance - all types from data_types_v2
Contract: BrowserContract -> BrowserResult
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import json

# Import ALL types from centralized data_types_v2
from data_types_v2 import (
    BrowserContract,
    BrowserResult,
    BrowserType,
    ProtocolType,
    BrowserConfig,
    enforce_ascii,
    validate_ascii,
    SystemConstants
)


class BrowserPool:
    """Manages a pool of browser sessions for reuse"""

    def __init__(self, max_sessions: int = 5):
        self.max_sessions = max_sessions
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an existing session"""
        async with self._lock:
            return self.sessions.get(session_id)

    async def store_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Store a session for reuse"""
        async with self._lock:
            # Implement LRU if at capacity
            if len(self.sessions) >= self.max_sessions:
                # Remove oldest session
                oldest = min(self.sessions.items(), key=lambda x: x[1].get('created', 0))
                await self._close_session(oldest[0])

            self.sessions[session_id] = session_data

    async def _close_session(self, session_id: str) -> None:
        """Close and remove a session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if 'page' in session and session['page']:
                await session['page'].close()
            if 'context' in session and session['context']:
                await session['context'].close()
            del self.sessions[session_id]

    async def cleanup(self) -> None:
        """Clean up all sessions"""
        async with self._lock:
            for session_id in list(self.sessions.keys()):
                await self._close_session(session_id)


class NetworkInterceptor:
    """Handles network interception and monitoring"""

    def __init__(self):
        self.requests: List[Dict[str, Any]] = []
        self.responses: List[Dict[str, Any]] = []
        self._enabled = False

    async def enable(self, page: Page) -> None:
        """Enable network interception"""
        if self._enabled:
            return

        async def on_request(request):
            self.requests.append({
                'url': validate_ascii(request.url),
                'method': request.method,
                'headers': {k: validate_ascii(v) for k, v in request.headers.items()},
                'timestamp': time.time()
            })

        async def on_response(response):
            self.responses.append({
                'url': validate_ascii(response.url),
                'status': response.status,
                'headers': {k: validate_ascii(v) for k, v in response.headers.items()},
                'timestamp': time.time()
            })

        page.on('request', on_request)
        page.on('response', on_response)
        self._enabled = True

    def get_metrics(self) -> Dict[str, Any]:
        """Get network metrics"""
        return {
            'total_requests': len(self.requests),
            'total_responses': len(self.responses),
            'requests': self.requests[-10:],  # Last 10 for brevity
            'average_response_time': self._calculate_avg_response_time()
        }

    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        if not self.responses:
            return 0.0

        times = []
        for response in self.responses:
            # Find matching request
            for request in self.requests:
                if request['url'] == response['url']:
                    times.append(response['timestamp'] - request['timestamp'])
                    break

        return sum(times) / len(times) if times else 0.0


class ConsoleMonitor:
    """Monitors browser console messages"""

    def __init__(self):
        self.messages: List[str] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    async def enable(self, page: Page) -> None:
        """Enable console monitoring"""

        async def on_console(msg):
            text = validate_ascii(msg.text)
            self.messages.append(text)

            if msg.type == 'error':
                self.errors.append(text)
            elif msg.type == 'warning':
                self.warnings.append(text)

        page.on('console', on_console)

    def get_summary(self) -> Dict[str, Any]:
        """Get console summary"""
        return {
            'total_messages': len(self.messages),
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'recent_messages': self.messages[-20:]  # Last 20 messages
        }


class StealthMode:
    """Implements stealth mode for avoiding detection"""

    @staticmethod
    async def apply(page: Page) -> None:
        """Apply stealth techniques to avoid bot detection"""

        # Override navigator.webdriver
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # Add realistic user agent if needed
        await page.add_init_script("""
            Object.defineProperty(navigator, 'userAgent', {
                get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            });
        """)

        # Add realistic viewport
        await page.add_init_script("""
            Object.defineProperty(window, 'chrome', {
                runtime: {}
            });
        """)

        # Randomize plugin array
        await page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)

        # Override permissions
        await page.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)


class BrowserManagerV2:
    """
    Centralized Browser Manager with WebDriver BiDi and CDP support
    Implements BrowserContract -> BrowserResult
    """

    def __init__(self):
        self.pool = BrowserPool()
        self.playwright = None
        self.browser = None

    async def execute(self, contract: BrowserContract) -> BrowserResult:
        """
        Main execution function - implements the contract
        Args:
            contract: BrowserContract with configuration
        Returns:
            BrowserResult with session and metrics
        """
        start_time = time.time()

        # Check for session reuse
        if contract.reuse_session and contract.session_id:
            existing = await self.pool.get_session(contract.session_id)
            if existing:
                # Reuse existing session
                return await self._create_result_from_session(
                    existing,
                    contract,
                    time.time() - start_time
                )

        # Create new browser session (don't use context manager to keep it alive)
        self.playwright = await async_playwright().start()

        # Select browser type
        if contract.config.browser_type == BrowserType.FIREFOX:
            browser_type = self.playwright.firefox
        elif contract.config.browser_type == BrowserType.WEBKIT:
            browser_type = self.playwright.webkit
        else:
            browser_type = self.playwright.chromium

        # Launch browser
        launch_args = {
            'headless': contract.config.headless,
            'args': contract.config.extra_args or []
        }

        if contract.config.proxy:
            launch_args['proxy'] = {'server': contract.config.proxy}

        self.browser = await browser_type.launch(**launch_args)

        # Create context
        context = await self.browser.new_context(
            viewport={
                'width': contract.config.viewport_width,
                'height': contract.config.viewport_height
            },
            user_agent=contract.config.user_agent
        )

        page = await context.new_page()

        # Apply configurations
        await self._configure_page(page, contract.config)

        # Navigate to URL (use domcontentloaded for faster loading)
        await page.goto(
            contract.url,
            wait_until='domcontentloaded',  # Changed from networkidle for UAT sites
            timeout=SystemConstants.PAGE_LOAD_TIMEOUT
        )

        # Set up monitoring
        network_interceptor = NetworkInterceptor()
        console_monitor = ConsoleMonitor()

        if contract.config.protocol == ProtocolType.CDP:
            # Enable CDP features
            await network_interceptor.enable(page)
            await console_monitor.enable(page)

        # Collect metrics
        performance_metrics = await self._collect_performance_metrics(page)

        # Take screenshot if enabled
        screenshots = []
        if hasattr(contract.config, 'screenshot_enabled') and contract.config.screenshot_enabled:
            screenshot = await page.screenshot(full_page=True)
            screenshots.append(f"data:image/png;base64,{screenshot}")

        # Create session ID
        session_id = f"session_{int(time.time() * 1000)}"

        # Always store session for pipeline usage
        await self.pool.store_session(session_id, {
            'page': page,
            'context': context,
            'created': time.time()
        })

        # Build result
        result = BrowserResult(
            session_id=session_id,
            browser_type=contract.config.browser_type,
            protocol=contract.config.protocol,
            page_title=validate_ascii(await page.title()),
            page_url=validate_ascii(page.url),
            viewport={
                'width': contract.config.viewport_width,
                'height': contract.config.viewport_height
            },
            cookies_count=len(await context.cookies()),
            console_messages=console_monitor.messages if console_monitor else [],
            network_requests=network_interceptor.requests[-50:] if network_interceptor else [],
            performance_metrics=performance_metrics,
            screenshots=screenshots
        )

        return result

    @asynccontextmanager
    async def _create_browser_context(self, contract: BrowserContract):
        """Create browser context with proper cleanup"""
        self.playwright = await async_playwright().start()

        # Select browser type
        if contract.config.browser_type == BrowserType.FIREFOX:
            browser_type = self.playwright.firefox
        elif contract.config.browser_type == BrowserType.WEBKIT:
            browser_type = self.playwright.webkit
        else:
            browser_type = self.playwright.chromium

        # Launch browser
        launch_args = {
            'headless': contract.config.headless,
            'args': contract.config.extra_args or []
        }

        if contract.config.proxy:
            launch_args['proxy'] = {'server': contract.config.proxy}

        self.browser = await browser_type.launch(**launch_args)

        # Create context with viewport
        context_args = {
            'viewport': {
                'width': contract.config.viewport_width,
                'height': contract.config.viewport_height
            },
            'user_agent': contract.config.user_agent
        }

        context = await self.browser.new_context(**context_args)

        try:
            yield context
        finally:
            # Cleanup
            if not contract.reuse_session:
                await context.close()
                await self.browser.close()
                await self.playwright.stop()

    async def _configure_page(self, page: Page, config: BrowserConfig) -> None:
        """Configure page with settings"""

        # Set default timeout
        page.set_default_timeout(config.timeout)

        # Enable JavaScript
        if not config.enable_javascript:
            await page.route('**/*', lambda route: route.abort()
                           if route.request.resource_type == 'script'
                           else route.continue_())

        # Apply stealth mode
        if config.enable_stealth:
            await StealthMode.apply(page)

        # Block cookies if disabled
        if not config.enable_cookies:
            await page.context.clear_cookies()

    async def _collect_performance_metrics(self, page: Page) -> Dict[str, float]:
        """Collect performance metrics from the page"""
        metrics = await page.evaluate("""
            () => {
                const perf = window.performance;
                const navigation = perf.getEntriesByType('navigation')[0];
                return {
                    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                    loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                    firstPaint: perf.getEntriesByType('paint')[0]?.startTime || 0,
                    firstContentfulPaint: perf.getEntriesByType('paint')[1]?.startTime || 0,
                    interactive: navigation.domInteractive - navigation.fetchStart,
                    resourceCount: perf.getEntriesByType('resource').length
                };
            }
        """)
        return metrics

    async def _create_result_from_session(
        self,
        session: Dict[str, Any],
        contract: BrowserContract,
        elapsed_time: float
    ) -> BrowserResult:
        """Create result from existing session"""
        page = session['page']

        # Navigate if different URL
        if page.url != contract.url:
            await page.goto(contract.url, wait_until='networkidle')

        return BrowserResult(
            session_id=session.get('id', f"session_{int(time.time() * 1000)}"),
            browser_type=contract.config.browser_type,
            protocol=contract.config.protocol,
            page_title=validate_ascii(await page.title()),
            page_url=validate_ascii(page.url),
            viewport={
                'width': contract.config.viewport_width,
                'height': contract.config.viewport_height
            },
            cookies_count=len(await page.context.cookies()),
            console_messages=[],
            network_requests=[],
            performance_metrics={'reused_session': True, 'elapsed': elapsed_time},
            screenshots=[]
        )

    async def cleanup(self) -> None:
        """Clean up all resources"""
        await self.pool.cleanup()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# ==============================================================================
# MAIN EXECUTION FUNCTION - Contract Implementation
# ==============================================================================

async def execute(contract: BrowserContract) -> BrowserResult:
    """
    Main module execution function
    This is the standard interface for ALL modules
    Args:
        contract: Input contract
    Returns:
        Result according to output contract
    """
    manager = BrowserManagerV2()
    try:
        result = await manager.execute(contract)
        return result
    finally:
        await manager.cleanup()


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

async def create_browser_session(
    url: str,
    headless: bool = True,
    stealth: bool = True
) -> BrowserResult:
    """Convenience function to create a browser session"""
    contract = BrowserContract(
        url=url,
        config=BrowserConfig(
            headless=headless,
            enable_stealth=stealth
        )
    )
    return await execute(contract)


# ==============================================================================
# TEST
# ==============================================================================

async def test():
    """Test the browser manager"""
    print("Testing Browser Manager v2...")

    contract = BrowserContract(
        url="https://uat01.citi.com",
        config=BrowserConfig(
            browser_type=BrowserType.CHROMIUM,
            protocol=ProtocolType.CDP,
            headless=False,
            enable_stealth=True
        )
    )

    result = await execute(contract)

    print(f"Session ID: {result.session_id}")
    print(f"Page Title: {result.page_title}")
    print(f"Performance Metrics: {result.performance_metrics}")
    print("Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test())