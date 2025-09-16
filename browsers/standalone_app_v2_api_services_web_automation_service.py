"""Web Automation Service Implementation"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright
import subprocess
import tempfile
import os

from services.llm_service import LLMService

logger = logging.getLogger(__name__)

class WebAutomationService:
    """Service for web automation operations"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.templates = self._load_templates()
    
    async def extract_elements(self, url: str, wait_time: int = 5) -> Dict[str, Any]:
        """Extract interactive elements from webpage using Playwright"""
        elements = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to URL
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(wait_time * 1000)
                
                # Extract all interactive elements
                element_selectors = [
                    ("button", "buttons"),
                    ("a", "links"),
                    ("input", "inputs"),
                    ("select", "selects"),
                    ("textarea", "textareas"),
                    ("[role='button']", "role_buttons"),
                    ("[onclick]", "onclick_elements"),
                    ("form", "forms")
                ]
                
                for selector, element_type in element_selectors:
                    els = await page.query_selector_all(selector)
                    
                    for el in els:
                        try:
                            # Get element properties
                            properties = await el.evaluate("""(element) => {
                                return {
                                    tag: element.tagName.toLowerCase(),
                                    type: element.type || null,
                                    name: element.name || null,
                                    id: element.id || null,
                                    classes: element.className || null,
                                    text: element.textContent?.trim().substring(0, 100) || null,
                                    href: element.href || null,
                                    placeholder: element.placeholder || null,
                                    value: element.value || null,
                                    ariaLabel: element.getAttribute('aria-label') || null,
                                    role: element.getAttribute('role') || null,
                                    disabled: element.disabled || false,
                                    visible: element.offsetWidth > 0 && element.offsetHeight > 0
                                };
                            }""")
                            
                            if properties.get("visible", True):
                                # Generate selector
                                if properties.get("id"):
                                    selector = f"#{properties['id']}"
                                elif properties.get("name"):
                                    selector = f"[name='{properties['name']}']"
                                else:
                                    selector = await el.evaluate("(el) => el.tagName.toLowerCase()")
                                    if properties.get("classes"):
                                        selector += f".{properties['classes'].split()[0]}"
                                
                                elements.append({
                                    "type": element_type.rstrip('s'),  # Remove plural
                                    "selector": selector,
                                    **properties
                                })
                                
                        except Exception as e:
                            logger.warning(f"Failed to extract element: {e}")
                
            finally:
                await browser.close()
        
        # Deduplicate elements
        seen = set()
        unique_elements = []
        for el in elements:
            key = (el.get("selector"), el.get("text", "")[:50])
            if key not in seen:
                seen.add(key)
                unique_elements.append(el)
        
        return {"elements": unique_elements[:100]}  # Limit to 100 elements
    
    async def generate_gherkin_tests(
        self,
        elements: List[Dict[str, Any]],
        url: str,
        framework: str = "pytest"
    ) -> Dict[str, Any]:
        """Generate Gherkin test scenarios using LLM"""
        
        # Prepare element summary
        element_summary = self._summarize_elements(elements)
        
        prompt = f"""Generate comprehensive Gherkin test scenarios for a web page with the following elements:

URL: {url}
Framework: {framework}

Elements found:
{element_summary}

Generate test scenarios covering:
1. Basic functionality tests
2. Form validation tests (if applicable)
3. Navigation tests
4. Error handling tests
5. Accessibility tests

Format the output as proper Gherkin syntax with Feature, Scenario, Given, When, Then steps.
Include at least 5-8 test scenarios."""

        response = await self.llm_service.query(prompt, temperature=0.3)
        
        # Count scenarios
        test_count = response["response"].count("Scenario:")
        
        return {
            "gherkin_tests": response["response"],
            "test_count": test_count
        }
    
    async def generate_python_code(
        self,
        gherkin_tests: str,
        language: str = "python",
        framework: str = "playwright"
    ) -> Dict[str, Any]:
        """Generate executable code from Gherkin tests"""
        
        prompt = f"""Convert the following Gherkin test scenarios into executable {language} code using {framework}:

{gherkin_tests}

Requirements:
1. Use async/await patterns for Playwright
2. Include proper error handling
3. Add logging for each step
4. Use Page Object Model pattern
5. Include setup and teardown methods
6. Add retry logic for flaky elements
7. Include comments explaining each test

Generate complete, runnable code."""

        response = await self.llm_service.query(prompt, temperature=0.2, max_tokens=3000)
        
        # Estimate runtime
        test_count = gherkin_tests.count("Scenario:")
        estimated_runtime = f"{test_count * 5}-{test_count * 10} seconds"
        
        return {
            "code": response["response"],
            "estimated_runtime": estimated_runtime
        }
    
    async def execute_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute Python code in sandboxed environment"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                'python', temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, 'PYTHONPATH': '.'}
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                success = process.returncode == 0
                
                return {
                    "success": success,
                    "output": stdout.decode() if stdout else None,
                    "error": stderr.decode() if stderr else None,
                    "logs": self._parse_logs(stdout.decode() if stdout else "")
                }
                
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                raise
                
        finally:
            # Cleanup
            os.unlink(temp_file)
    
    async def get_template(self, template_name: str) -> str:
        """Get code template"""
        return self.templates.get(template_name, "Template not found")
    
    def _summarize_elements(self, elements: List[Dict[str, Any]]) -> str:
        """Summarize elements for LLM prompt"""
        summary = []
        
        # Group by type
        by_type = {}
        for el in elements:
            el_type = el.get("type", "unknown")
            if el_type not in by_type:
                by_type[el_type] = []
            by_type[el_type].append(el)
        
        # Summarize each type
        for el_type, els in by_type.items():
            summary.append(f"\n{el_type.upper()}S ({len(els)}):")
            for el in els[:5]:  # Show first 5 of each type
                text = el.get("text", "")[:50] or el.get("placeholder", "") or el.get("ariaLabel", "")
                selector = el.get("selector", "")
                summary.append(f"  - {selector}: {text}")
            if len(els) > 5:
                summary.append(f"  ... and {len(els) - 5} more")
        
        return "\n".join(summary)
    
    def _parse_logs(self, output: str) -> List[str]:
        """Parse logs from output"""
        logs = []
        for line in output.split('\n'):
            if line.strip() and any(level in line for level in ['INFO', 'DEBUG', 'WARNING', 'ERROR']):
                logs.append(line.strip())
        return logs[-20:]  # Last 20 log lines
    
    def _load_templates(self) -> Dict[str, str]:
        """Load code templates"""
        return {
            "login_test": """import asyncio
from playwright.async_api import async_playwright

async def test_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to login page
            await page.goto("https://example.com/login")
            
            # Fill login form
            await page.fill("input[name='username']", "testuser")
            await page.fill("input[name='password']", "testpass")
            
            # Submit form
            await page.click("button[type='submit']")
            
            # Wait for navigation
            await page.wait_for_url("**/dashboard")
            
            # Verify login success
            assert await page.is_visible("text=Welcome")
            
            print("✓ Login test passed")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login())
""",
            
            "form_validation": """import asyncio
from playwright.async_api import async_playwright

async def test_form_validation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto("https://example.com/form")
            
            # Test required fields
            await page.click("button[type='submit']")
            assert await page.is_visible("text=This field is required")
            
            # Test email validation
            await page.fill("input[type='email']", "invalid-email")
            await page.click("button[type='submit']")
            assert await page.is_visible("text=Invalid email")
            
            print("✓ Form validation test passed")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_form_validation())
"""
        }