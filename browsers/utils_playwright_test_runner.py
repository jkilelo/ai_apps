"""
Playwright Test Runner
Executes actual Playwright tests for UI testing
"""

import asyncio
import tempfile
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser


class PlaywrightTestRunner:
    """Runs Playwright tests based on generated test cases"""
    
    def __init__(self, browser_type: str = "chromium", timeout: int = 30000):
        self.browser_type = browser_type
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.results: List[Dict[str, Any]] = []
    
    async def initialize(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        browser_launcher = getattr(self.playwright, self.browser_type)
        self.browser = await browser_launcher.launch(headless=True)
    
    async def cleanup(self):
        """Clean up Playwright resources"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def execute_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single test case"""
        test_id = test_case.get("id", "unknown")
        test_name = test_case.get("name", "Unnamed test")
        test_start = datetime.now()
        
        result = {
            "test_id": test_id,
            "test_name": test_name,
            "started_at": test_start.isoformat(),
            "status": "running",
            "logs": [],
            "screenshots": []
        }
        
        try:
            # Create a new page for this test
            page = await self.browser.new_page()
            
            # Set timeout
            page.set_default_timeout(self.timeout)
            
            # Execute test steps
            steps = test_case.get("steps", [])
            for step_idx, step in enumerate(steps):
                step_result = await self._execute_step(page, step, step_idx)
                result["logs"].append(step_result)
                
                if step_result.get("status") == "failed":
                    result["status"] = "failed"
                    result["error"] = step_result.get("error")
                    break
            
            # If all steps passed, mark test as passed
            if result["status"] == "running":
                result["status"] = "passed"
            
            # Take final screenshot
            screenshot_path = f"/tmp/test_{test_id}_final.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            result["screenshots"].append(screenshot_path)
            
            await page.close()
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["logs"].append({
                "message": f"Test execution failed: {str(e)}",
                "level": "error",
                "timestamp": datetime.now().isoformat()
            })
        
        # Calculate duration
        test_end = datetime.now()
        result["completed_at"] = test_end.isoformat()
        result["duration"] = (test_end - test_start).total_seconds()
        
        return result
    
    async def _execute_step(self, page: Page, step: Dict[str, Any], step_idx: int) -> Dict[str, Any]:
        """Execute a single test step"""
        step_type = step.get("type", "action")
        action = step.get("action", "")
        target = step.get("target", "")
        value = step.get("value", "")
        
        step_result = {
            "step_index": step_idx,
            "action": action,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "status": "running"
        }
        
        try:
            # Navigate to URL
            if action == "navigate":
                await page.goto(value or target)
                step_result["message"] = f"Navigated to {value or target}"
            
            # Click element
            elif action == "click":
                await page.click(target)
                step_result["message"] = f"Clicked on {target}"
            
            # Type text
            elif action in ["type", "fill"]:
                await page.fill(target, value)
                step_result["message"] = f"Typed '{value}' into {target}"
            
            # Select option
            elif action == "select":
                await page.select_option(target, value)
                step_result["message"] = f"Selected '{value}' in {target}"
            
            # Check/uncheck
            elif action == "check":
                await page.check(target)
                step_result["message"] = f"Checked {target}"
            
            elif action == "uncheck":
                await page.uncheck(target)
                step_result["message"] = f"Unchecked {target}"
            
            # Wait
            elif action == "wait":
                wait_time = int(value) if value else 1000
                await page.wait_for_timeout(wait_time)
                step_result["message"] = f"Waited for {wait_time}ms"
            
            # Assert text present
            elif action == "assert_text":
                element = await page.wait_for_selector(target)
                text = await element.text_content()
                assert value in text, f"Expected text '{value}' not found in '{text}'"
                step_result["message"] = f"Verified text '{value}' is present"
            
            # Assert element visible
            elif action == "assert_visible":
                await page.wait_for_selector(target, state="visible")
                step_result["message"] = f"Verified {target} is visible"
            
            # Assert URL
            elif action == "assert_url":
                current_url = page.url
                assert value in current_url, f"Expected URL to contain '{value}', but got '{current_url}'"
                step_result["message"] = f"Verified URL contains '{value}'"
            
            # Screenshot
            elif action == "screenshot":
                screenshot_name = value or f"step_{step_idx}.png"
                screenshot_path = f"/tmp/{screenshot_name}"
                await page.screenshot(path=screenshot_path)
                step_result["message"] = f"Screenshot saved to {screenshot_path}"
                step_result["screenshot"] = screenshot_path
            
            else:
                step_result["message"] = f"Unknown action: {action}"
                step_result["status"] = "skipped"
                return step_result
            
            step_result["status"] = "passed"
            
        except Exception as e:
            step_result["status"] = "failed"
            step_result["error"] = str(e)
            step_result["message"] = f"Step failed: {str(e)}"
        
        return step_result
    
    async def run_test_suite(self, test_cases: List[Dict[str, Any]], execution_mode: str = "sequential") -> Dict[str, Any]:
        """Run a suite of test cases"""
        suite_start = datetime.now()
        
        try:
            await self.initialize()
            
            if execution_mode == "parallel":
                # Run tests in parallel
                tasks = [self.execute_test_case(test) for test in test_cases]
                self.results = await asyncio.gather(*tasks)
            else:
                # Run tests sequentially
                self.results = []
                for test_case in test_cases:
                    result = await self.execute_test_case(test_case)
                    self.results.append(result)
            
        finally:
            await self.cleanup()
        
        # Calculate summary
        suite_end = datetime.now()
        summary = {
            "total": len(self.results),
            "passed": len([r for r in self.results if r["status"] == "passed"]),
            "failed": len([r for r in self.results if r["status"] == "failed"]),
            "skipped": len([r for r in self.results if r["status"] == "skipped"]),
            "duration": (suite_end - suite_start).total_seconds(),
            "start_time": suite_start.isoformat(),
            "end_time": suite_end.isoformat()
        }
        
        if summary["total"] > 0:
            summary["pass_rate"] = (summary["passed"] / summary["total"]) * 100
        else:
            summary["pass_rate"] = 0
        
        return {
            "summary": summary,
            "results": self.results
        }


def create_playwright_test_from_generated(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Convert generated test case to Playwright-executable format"""
    
    # Extract element and test information
    element = test_case.get("element", {})
    test_type = test_case.get("type", "functional")
    
    # Build test steps based on element type and test type
    steps = []
    
    # Always start by navigating to the page
    page_url = element.get("page_url", "https://example.com")
    steps.append({
        "type": "action",
        "action": "navigate",
        "target": page_url,
        "value": ""
    })
    
    # Add specific test steps based on element type
    element_type = element.get("type", "unknown")
    selector = element.get("selector", "")
    
    if element_type == "button":
        steps.extend([
            {
                "type": "action",
                "action": "assert_visible",
                "target": selector,
                "value": ""
            },
            {
                "type": "action",
                "action": "click",
                "target": selector,
                "value": ""
            }
        ])
    
    elif element_type == "link":
        steps.extend([
            {
                "type": "action",
                "action": "assert_visible",
                "target": selector,
                "value": ""
            },
            {
                "type": "action",
                "action": "click",
                "target": selector,
                "value": ""
            }
        ])
    
    elif element_type in ["input", "text_input"]:
        steps.extend([
            {
                "type": "action",
                "action": "assert_visible",
                "target": selector,
                "value": ""
            },
            {
                "type": "action",
                "action": "fill",
                "target": selector,
                "value": "Test input value"
            }
        ])
    
    elif element_type == "select":
        steps.extend([
            {
                "type": "action",
                "action": "assert_visible",
                "target": selector,
                "value": ""
            },
            {
                "type": "action",
                "action": "select",
                "target": selector,
                "value": "1"  # Select first option by default
            }
        ])
    
    elif element_type in ["checkbox", "radio"]:
        steps.extend([
            {
                "type": "action",
                "action": "assert_visible",
                "target": selector,
                "value": ""
            },
            {
                "type": "action",
                "action": "check",
                "target": selector,
                "value": ""
            }
        ])
    
    # Add screenshot at the end
    steps.append({
        "type": "action",
        "action": "screenshot",
        "target": "",
        "value": f"test_{test_case.get('id', 'unknown')}_result.png"
    })
    
    return {
        "id": test_case.get("id"),
        "name": test_case.get("name"),
        "type": test_type,
        "element": element,
        "steps": steps
    }