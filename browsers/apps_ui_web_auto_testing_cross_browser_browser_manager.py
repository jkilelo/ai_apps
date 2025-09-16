"""
Cross-Browser Testing Manager
Supports testing across Chrome, Firefox, Safari, Edge and mobile browsers
"""

import asyncio
import logging
import platform
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from playwright.async_api import Browser, BrowserContext, Page, async_playwright
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class BrowserType(Enum):
    """Supported browser types"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"  # Safari
    CHROME = "chrome"
    EDGE = "edge"
    CHROME_MOBILE = "chrome_mobile"
    SAFARI_MOBILE = "safari_mobile"


class DeviceType(Enum):
    """Device types for mobile testing"""
    IPHONE_12 = "iPhone 12"
    IPHONE_13_PRO = "iPhone 13 Pro"
    IPHONE_SE = "iPhone SE"
    PIXEL_5 = "Pixel 5"
    GALAXY_S21 = "Galaxy S21"
    IPAD_PRO = "iPad Pro"
    IPAD_MINI = "iPad Mini"


@dataclass
class BrowserConfig:
    """Configuration for browser instance"""
    browser_type: BrowserType
    headless: bool = True
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    user_agent: Optional[str] = None
    locale: str = "en-US"
    timezone: str = "America/New_York"
    geolocation: Optional[Dict[str, float]] = None
    permissions: List[str] = field(default_factory=list)
    extra_http_headers: Dict[str, str] = field(default_factory=dict)
    device_emulation: Optional[DeviceType] = None
    args: List[str] = field(default_factory=list)
    proxy: Optional[Dict[str, str]] = None
    record_video: bool = False
    record_har: bool = False


@dataclass
class BrowserTestResult:
    """Result from browser-specific test execution"""
    browser: str
    device: Optional[str]
    passed: bool
    duration: float
    errors: List[str]
    warnings: List[str]
    screenshots: List[str]
    video_path: Optional[str]
    har_path: Optional[str]
    console_logs: List[Dict[str, Any]]
    network_logs: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    accessibility_issues: List[Dict[str, Any]]


class CrossBrowserManager:
    """Manages cross-browser testing with Playwright"""
    
    # Predefined device configurations
    DEVICE_CONFIGS = {
        DeviceType.IPHONE_12: {
            "viewport": {"width": 390, "height": 844},
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "device_scale_factor": 3,
            "is_mobile": True,
            "has_touch": True
        },
        DeviceType.IPHONE_13_PRO: {
            "viewport": {"width": 390, "height": 844},
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
            "device_scale_factor": 3,
            "is_mobile": True,
            "has_touch": True
        },
        DeviceType.PIXEL_5: {
            "viewport": {"width": 393, "height": 851},
            "user_agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36",
            "device_scale_factor": 2.75,
            "is_mobile": True,
            "has_touch": True
        },
        DeviceType.GALAXY_S21: {
            "viewport": {"width": 360, "height": 800},
            "user_agent": "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36",
            "device_scale_factor": 3,
            "is_mobile": True,
            "has_touch": True
        },
        DeviceType.IPAD_PRO: {
            "viewport": {"width": 1024, "height": 1366},
            "user_agent": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "device_scale_factor": 2,
            "is_mobile": True,
            "has_touch": True
        }
    }
    
    def __init__(self):
        self.playwright = None
        self.browsers: Dict[str, Browser] = {}
        self.contexts: Dict[str, BrowserContext] = {}
        
    async def initialize(self):
        """Initialize Playwright"""
        if not self.playwright:
            self.playwright = await async_playwright().start()
            logger.info("Playwright initialized for cross-browser testing")
    
    async def cleanup(self):
        """Cleanup all browser instances"""
        for context in self.contexts.values():
            await context.close()
        
        for browser in self.browsers.values():
            await browser.close()
        
        if self.playwright:
            await self.playwright.stop()
        
        self.contexts.clear()
        self.browsers.clear()
        logger.info("Cross-browser manager cleaned up")
    
    async def launch_browser(self, config: BrowserConfig) -> Tuple[Browser, BrowserContext]:
        """Launch a browser with specified configuration"""
        await self.initialize()
        
        # Get browser launcher
        browser_type = config.browser_type.value
        if browser_type == "chrome":
            launcher = self.playwright.chromium
            config.args.extend(["--disable-blink-features=AutomationControlled"])
        elif browser_type == "edge":
            launcher = self.playwright.chromium
            config.args.extend(["--edge"])
        elif browser_type == "firefox":
            launcher = self.playwright.firefox
        elif browser_type == "webkit":
            launcher = self.playwright.webkit
        else:
            launcher = self.playwright.chromium
        
        # Launch browser
        launch_options = {
            "headless": config.headless,
            "args": config.args
        }
        
        if config.proxy:
            launch_options["proxy"] = config.proxy
        
        browser = await launcher.launch(**launch_options)
        
        # Create context with configuration
        context_options = {
            "viewport": config.viewport,
            "locale": config.locale,
            "timezone_id": config.timezone,
            "permissions": config.permissions,
            "extra_http_headers": config.extra_http_headers
        }
        
        if config.user_agent:
            context_options["user_agent"] = config.user_agent
        
        if config.geolocation:
            context_options["geolocation"] = config.geolocation
        
        if config.record_video:
            context_options["record_video_dir"] = "./videos"
        
        if config.record_har:
            context_options["record_har_path"] = f"./har/{browser_type}_{datetime.now().timestamp()}.har"
        
        # Apply device emulation if specified
        if config.device_emulation and config.device_emulation in self.DEVICE_CONFIGS:
            device_config = self.DEVICE_CONFIGS[config.device_emulation]
            context_options.update(device_config)
        
        context = await browser.new_context(**context_options)
        
        # Store references
        browser_key = f"{browser_type}_{id(browser)}"
        self.browsers[browser_key] = browser
        self.contexts[browser_key] = context
        
        return browser, context
    
    async def run_test_on_browser(
        self, 
        config: BrowserConfig, 
        test_function, 
        *args, 
        **kwargs
    ) -> BrowserTestResult:
        """Run a test function on a specific browser configuration"""
        start_time = datetime.now()
        errors = []
        warnings = []
        screenshots = []
        console_logs = []
        network_logs = []
        performance_metrics = {}
        accessibility_issues = []
        
        try:
            # Launch browser
            browser, context = await self.launch_browser(config)
            
            # Create page with event listeners
            page = await context.new_page()
            
            # Set up console log capture
            page.on("console", lambda msg: console_logs.append({
                "type": msg.type,
                "text": msg.text,
                "location": msg.location,
                "timestamp": datetime.now().isoformat()
            }))
            
            # Set up network log capture
            page.on("request", lambda req: network_logs.append({
                "type": "request",
                "url": req.url,
                "method": req.method,
                "timestamp": datetime.now().isoformat()
            }))
            
            page.on("response", lambda resp: network_logs.append({
                "type": "response",
                "url": resp.url,
                "status": resp.status,
                "timestamp": datetime.now().isoformat()
            }))
            
            # Run the test
            result = await test_function(page, *args, **kwargs)
            
            # Capture performance metrics
            if config.browser_type in [BrowserType.CHROMIUM, BrowserType.CHROME, BrowserType.EDGE]:
                performance_metrics = await self._capture_performance_metrics(page)
            
            # Run accessibility audit
            accessibility_issues = await self._run_accessibility_audit(page)
            
            # Take final screenshot
            screenshot_path = f"./screenshots/{config.browser_type.value}_{datetime.now().timestamp()}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            screenshots.append(screenshot_path)
            
            # Get video path if recording
            video_path = None
            if config.record_video:
                video = page.video
                if video:
                    video_path = await video.path()
            
            # Get HAR path if recording
            har_path = None
            if config.record_har and hasattr(context, '_har_path'):
                har_path = context._har_path
            
            # Check for console errors
            for log in console_logs:
                if log["type"] == "error":
                    errors.append(f"Console error: {log['text']}")
                elif log["type"] == "warning":
                    warnings.append(f"Console warning: {log['text']}")
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return BrowserTestResult(
                browser=config.browser_type.value,
                device=config.device_emulation.value if config.device_emulation else None,
                passed=result.get("passed", True) if isinstance(result, dict) else True,
                duration=duration,
                errors=errors,
                warnings=warnings,
                screenshots=screenshots,
                video_path=video_path,
                har_path=har_path,
                console_logs=console_logs,
                network_logs=network_logs,
                performance_metrics=performance_metrics,
                accessibility_issues=accessibility_issues
            )
            
        except Exception as e:
            logger.error(f"Test failed on {config.browser_type.value}: {str(e)}")
            errors.append(str(e))
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return BrowserTestResult(
                browser=config.browser_type.value,
                device=config.device_emulation.value if config.device_emulation else None,
                passed=False,
                duration=duration,
                errors=errors,
                warnings=warnings,
                screenshots=screenshots,
                video_path=None,
                har_path=None,
                console_logs=console_logs,
                network_logs=network_logs,
                performance_metrics=performance_metrics,
                accessibility_issues=accessibility_issues
            )
        
        finally:
            # Cleanup this browser instance
            browser_key = f"{config.browser_type.value}_{id(browser)}"
            if browser_key in self.contexts:
                await self.contexts[browser_key].close()
                del self.contexts[browser_key]
            if browser_key in self.browsers:
                await self.browsers[browser_key].close()
                del self.browsers[browser_key]
    
    async def run_test_on_multiple_browsers(
        self,
        browser_configs: List[BrowserConfig],
        test_function,
        parallel: bool = True,
        *args,
        **kwargs
    ) -> Dict[str, BrowserTestResult]:
        """Run tests on multiple browser configurations"""
        results = {}
        
        if parallel:
            # Run tests in parallel
            tasks = []
            for config in browser_configs:
                task = self.run_test_on_browser(config, test_function, *args, **kwargs)
                tasks.append(task)
            
            test_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for config, result in zip(browser_configs, test_results):
                if isinstance(result, Exception):
                    logger.error(f"Test failed on {config.browser_type.value}: {result}")
                    results[config.browser_type.value] = BrowserTestResult(
                        browser=config.browser_type.value,
                        device=config.device_emulation.value if config.device_emulation else None,
                        passed=False,
                        duration=0,
                        errors=[str(result)],
                        warnings=[],
                        screenshots=[],
                        video_path=None,
                        har_path=None,
                        console_logs=[],
                        network_logs=[],
                        performance_metrics={},
                        accessibility_issues=[]
                    )
                else:
                    results[config.browser_type.value] = result
        else:
            # Run tests sequentially
            for config in browser_configs:
                result = await self.run_test_on_browser(config, test_function, *args, **kwargs)
                results[config.browser_type.value] = result
        
        return results
    
    async def _capture_performance_metrics(self, page: Page) -> Dict[str, Any]:
        """Capture performance metrics from Chromium-based browsers"""
        try:
            # Get navigation timing
            navigation_timing = await page.evaluate("""
                () => {
                    const timing = performance.timing;
                    return {
                        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                        loadComplete: timing.loadEventEnd - timing.navigationStart,
                        firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0,
                        firstContentfulPaint: performance.getEntriesByType('paint')[1]?.startTime || 0
                    };
                }
            """)
            
            # Get resource timing
            resource_timing = await page.evaluate("""
                () => {
                    return performance.getEntriesByType('resource').map(entry => ({
                        name: entry.name,
                        duration: entry.duration,
                        size: entry.transferSize || 0,
                        type: entry.initiatorType
                    }));
                }
            """)
            
            # Get memory usage (Chrome only)
            memory_usage = await page.evaluate("""
                () => {
                    if (performance.memory) {
                        return {
                            usedJSHeapSize: performance.memory.usedJSHeapSize,
                            totalJSHeapSize: performance.memory.totalJSHeapSize,
                            jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                        };
                    }
                    return null;
                }
            """)
            
            return {
                "navigation": navigation_timing,
                "resources": resource_timing,
                "memory": memory_usage,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Failed to capture performance metrics: {e}")
            return {}
    
    async def _run_accessibility_audit(self, page: Page) -> List[Dict[str, Any]]:
        """Run basic accessibility audit"""
        try:
            # Check for images without alt text
            images_without_alt = await page.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img:not([alt])'));
                    return images.map(img => ({
                        type: 'error',
                        category: 'images',
                        message: 'Image missing alt attribute',
                        element: img.outerHTML.substring(0, 100)
                    }));
                }
            """)
            
            # Check for form inputs without labels
            inputs_without_labels = await page.evaluate("""
                () => {
                    const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
                    return inputs.filter(input => {
                        const id = input.id;
                        if (!id) return true;
                        return !document.querySelector(`label[for="${id}"]`);
                    }).map(input => ({
                        type: 'error',
                        category: 'forms',
                        message: 'Form input missing associated label',
                        element: input.outerHTML.substring(0, 100)
                    }));
                }
            """)
            
            # Check for missing page title
            title_issues = await page.evaluate("""
                () => {
                    const title = document.title;
                    if (!title || title.trim() === '') {
                        return [{
                            type: 'error',
                            category: 'document',
                            message: 'Page missing title element'
                        }];
                    }
                    return [];
                }
            """)
            
            # Check for proper heading hierarchy
            heading_issues = await page.evaluate("""
                () => {
                    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
                    const issues = [];
                    let lastLevel = 0;
                    
                    headings.forEach(heading => {
                        const level = parseInt(heading.tagName[1]);
                        if (level - lastLevel > 1) {
                            issues.push({
                                type: 'warning',
                                category: 'structure',
                                message: `Heading hierarchy skip from h${lastLevel} to h${level}`,
                                element: heading.outerHTML.substring(0, 100)
                            });
                        }
                        lastLevel = level;
                    });
                    
                    return issues;
                }
            """)
            
            # Combine all issues
            all_issues = [
                *images_without_alt,
                *inputs_without_labels,
                *title_issues,
                *heading_issues
            ]
            
            return all_issues
            
        except Exception as e:
            logger.warning(f"Failed to run accessibility audit: {e}")
            return []
    
    def get_recommended_browsers(self, include_mobile: bool = True) -> List[BrowserConfig]:
        """Get recommended browser configurations for comprehensive testing"""
        configs = [
            # Desktop browsers
            BrowserConfig(
                browser_type=BrowserType.CHROME,
                viewport={"width": 1920, "height": 1080}
            ),
            BrowserConfig(
                browser_type=BrowserType.FIREFOX,
                viewport={"width": 1920, "height": 1080}
            ),
            BrowserConfig(
                browser_type=BrowserType.WEBKIT,
                viewport={"width": 1920, "height": 1080}
            ),
            BrowserConfig(
                browser_type=BrowserType.EDGE,
                viewport={"width": 1920, "height": 1080}
            ),
            # Different viewport sizes
            BrowserConfig(
                browser_type=BrowserType.CHROME,
                viewport={"width": 1366, "height": 768}  # Common laptop
            ),
            BrowserConfig(
                browser_type=BrowserType.CHROME,
                viewport={"width": 768, "height": 1024}  # Tablet portrait
            )
        ]
        
        if include_mobile:
            configs.extend([
                # Mobile devices
                BrowserConfig(
                    browser_type=BrowserType.WEBKIT,
                    device_emulation=DeviceType.IPHONE_13_PRO
                ),
                BrowserConfig(
                    browser_type=BrowserType.CHROMIUM,
                    device_emulation=DeviceType.PIXEL_5
                ),
                BrowserConfig(
                    browser_type=BrowserType.WEBKIT,
                    device_emulation=DeviceType.IPAD_PRO
                )
            ])
        
        return configs
    
    def generate_compatibility_report(self, results: Dict[str, BrowserTestResult]) -> Dict[str, Any]:
        """Generate browser compatibility report"""
        total_browsers = len(results)
        passed_browsers = sum(1 for r in results.values() if r.passed)
        
        # Group issues by type
        all_errors = []
        all_warnings = []
        performance_summary = {}
        
        for browser, result in results.items():
            all_errors.extend([
                {"browser": browser, "error": error} 
                for error in result.errors
            ])
            all_warnings.extend([
                {"browser": browser, "warning": warning} 
                for warning in result.warnings
            ])
            
            if result.performance_metrics.get("navigation"):
                performance_summary[browser] = {
                    "load_time": result.performance_metrics["navigation"].get("loadComplete", 0),
                    "dom_ready": result.performance_metrics["navigation"].get("domContentLoaded", 0),
                    "first_paint": result.performance_metrics["navigation"].get("firstPaint", 0)
                }
        
        return {
            "summary": {
                "total_browsers": total_browsers,
                "passed": passed_browsers,
                "failed": total_browsers - passed_browsers,
                "compatibility_score": (passed_browsers / total_browsers * 100) if total_browsers > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "browser_results": {
                browser: {
                    "passed": result.passed,
                    "duration": result.duration,
                    "error_count": len(result.errors),
                    "warning_count": len(result.warnings),
                    "accessibility_issues": len(result.accessibility_issues)
                }
                for browser, result in results.items()
            },
            "performance_comparison": performance_summary,
            "common_issues": self._identify_common_issues(results),
            "recommendations": self._generate_compatibility_recommendations(results)
        }
    
    def _identify_common_issues(self, results: Dict[str, BrowserTestResult]) -> List[Dict[str, Any]]:
        """Identify issues that occur across multiple browsers"""
        issue_counter = {}
        
        for browser, result in results.items():
            for error in result.errors:
                if error not in issue_counter:
                    issue_counter[error] = []
                issue_counter[error].append(browser)
        
        common_issues = []
        for issue, browsers in issue_counter.items():
            if len(browsers) > 1:
                common_issues.append({
                    "issue": issue,
                    "affected_browsers": browsers,
                    "severity": "high" if len(browsers) > len(results) / 2 else "medium"
                })
        
        return common_issues
    
    def _generate_compatibility_recommendations(self, results: Dict[str, BrowserTestResult]) -> List[str]:
        """Generate recommendations based on compatibility testing results"""
        recommendations = []
        
        # Check overall pass rate
        pass_rate = sum(1 for r in results.values() if r.passed) / len(results)
        
        if pass_rate == 1.0:
            recommendations.append("Excellent browser compatibility - all tests passed")
        elif pass_rate >= 0.8:
            recommendations.append("Good browser compatibility with minor issues")
        else:
            recommendations.append("Significant browser compatibility issues detected")
        
        # Check for specific browser issues
        for browser, result in results.items():
            if not result.passed:
                if "webkit" in browser.lower() or "safari" in browser.lower():
                    recommendations.append(f"Safari/WebKit compatibility issues - review CSS and JavaScript features")
                elif "firefox" in browser.lower():
                    recommendations.append(f"Firefox compatibility issues - check for vendor-specific features")
        
        # Performance recommendations
        load_times = [
            r.performance_metrics.get("navigation", {}).get("loadComplete", 0)
            for r in results.values()
            if r.performance_metrics.get("navigation")
        ]
        
        if load_times and max(load_times) > 3000:
            recommendations.append("Page load time exceeds 3 seconds on some browsers - consider optimization")
        
        # Accessibility recommendations
        total_a11y_issues = sum(
            len(r.accessibility_issues) 
            for r in results.values()
        )
        
        if total_a11y_issues > 0:
            recommendations.append(f"{total_a11y_issues} accessibility issues found - review WCAG compliance")
        
        return recommendations