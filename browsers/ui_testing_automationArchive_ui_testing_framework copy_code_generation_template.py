"""
CODE GENERATION TEMPLATE V3
============================
Robust template-based code generation with proven patterns
"""

# Working test template that LLM can safely fill in
PYTEST_PLAYWRIGHT_TEMPLATE = '''#!/usr/bin/env python3
"""
Generated Test Suite for {url}
Generated at: {timestamp}
Framework: Pytest + Playwright
"""

import pytest
import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Add the correct path for imports
# This path is where ui_testing_automation directory exists
import_path = "C:/Users/kleiy/OneDrive/Desktop/python-ai-apps/ai_apps"
if import_path not in sys.path:
    sys.path.insert(0, import_path)

# Import the robust browser module we already have
from ui_testing_framework.browser import UltimateStealthBrowser, StealthConfig
from ui_testing_framework.browser_contracts import StealthLevel, BrowserExtractionResult


class Test{test_class_name}:
    """Test suite for {url}"""
    
    @classmethod
    def setup_class(cls):
        """Setup test class"""
        cls.config = StealthConfig(
            level=StealthLevel.MAXIMUM,
            headless=True,
            timeout=30,
            viewport_width=1920,
            viewport_height=1080
        )
        cls.browser = UltimateStealthBrowser(cls.config)
        cls.base_url = "{url}"
    
    @classmethod  
    def teardown_class(cls):
        """Teardown test class"""
        if hasattr(cls, 'browser'):
            asyncio.run(cls.browser.cleanup())
    
    @pytest.fixture(autouse=True)
    async def setup_method(self):
        """Setup for each test method"""
        await self.browser.initialize()
        yield
        # Cleanup is handled by teardown_class
    
{test_methods}
'''

# Simple, working test method template
TEST_METHOD_TEMPLATE = '''    @pytest.mark.asyncio
    async def test_{method_name}(self):
        """
        Test: {test_name}
        Description: {test_description}
        Category: {test_category}
        """
        # Navigate to the page
        result = await self.browser.extract_elements(self.base_url)
        assert result.success, "Failed to load page"
        assert len(result.elements) > 0, "No elements found on page"
        
        # Test steps
{test_steps}
        
        # Assertions
{test_assertions}
'''

# Simple step template
TEST_STEP_TEMPLATE = '''        # Step: {step_description}
        page = self.browser.page
        {step_code}
'''

# Simple assertion template
ASSERTION_TEMPLATE = '''        assert {condition}, "{message}"'''


def create_safe_method_name(name: str) -> str:
    """Create a safe Python method name"""
    import re
    # Remove non-alphanumeric characters and replace with underscore
    safe_name = re.sub(r'[^a-zA-Z0-9]+', '_', name.lower())
    # Remove leading/trailing underscores
    safe_name = safe_name.strip('_')
    # Ensure it starts with a letter
    if safe_name and not safe_name[0].isalpha():
        safe_name = 'test_' + safe_name
    return safe_name or 'test_default'


def create_safe_class_name(url: str) -> str:
    """Create a safe Python class name from URL"""
    import re
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    
    # Remove www, dots, hyphens
    domain = domain.replace('www.', '').replace('.', '_').replace('-', '_')
    
    # Convert to PascalCase
    parts = domain.split('_')
    class_name = ''.join(p.capitalize() for p in parts if p)
    
    return class_name or 'WebPage'


def generate_test_code_from_template(
    url: str,
    scenarios: list,
    framework: str = "pytest"
) -> str:
    """
    Generate test code using safe templates
    
    This function generates WORKING code by:
    1. Using proven templates
    2. Reusing existing browser.py
    3. Keeping logic simple
    4. Avoiding complex string manipulation
    """
    from datetime import datetime
    
    # Generate safe names
    class_name = create_safe_class_name(url)
    
    # Generate test methods
    test_methods = []
    
    for i, scenario in enumerate(scenarios):
        # Extract scenario details safely
        scenario_name = scenario.get('name', f'Scenario {i+1}')
        description = scenario.get('description', 'Test scenario')
        category = scenario.get('category', 'functional')
        steps = scenario.get('steps', [])
        
        # Create safe method name
        method_name = create_safe_method_name(scenario_name)
        
        # Generate simple test steps
        test_steps_code = []
        for j, step in enumerate(steps):
            step_text = step.get('text', '') if isinstance(step, dict) else str(step)
            step_code = TEST_STEP_TEMPLATE.format(
                step_description=step_text.replace('"', "'"),
                step_code=f'# TODO: Implement step {j+1}'
            )
            test_steps_code.append(step_code)
        
        # Generate simple assertions
        assertions = [
            ASSERTION_TEMPLATE.format(
                condition='page is not None',
                message='Page should be loaded'
            ),
            ASSERTION_TEMPLATE.format(
                condition='len(result.elements) > 0',
                message='Page should have elements'
            )
        ]
        
        # Build test method
        test_method = TEST_METHOD_TEMPLATE.format(
            method_name=method_name,
            test_name=scenario_name.replace('"', "'"),
            test_description=description.replace('"', "'"),
            test_category=category,
            test_steps='\n'.join(test_steps_code) if test_steps_code else '        pass',
            test_assertions='\n'.join(assertions)
        )
        
        test_methods.append(test_method)
    
    # Generate complete test file
    test_code = PYTEST_PLAYWRIGHT_TEMPLATE.format(
        url=url,
        timestamp=datetime.now().isoformat(),
        test_class_name=class_name,
        test_methods='\n'.join(test_methods) if test_methods else '    pass'
    )
    
    return test_code


# Enhanced LLM prompt for code generation with full context
CODE_GENERATION_PROMPT = """You are generating Python test code for web automation.

CRITICAL REQUIREMENTS:
1. Use ONLY the provided template structure - DO NOT create new imports or classes
2. All browser operations MUST use self.browser (UltimateStealthBrowser instance)
3. Use await for all async operations
4. Keep test logic SIMPLE and CLEAR
5. Use single quotes for strings to avoid escaping issues
6. Each test method MUST be properly indented with 4 spaces

ENVIRONMENT CONTEXT:
- Python executable: C:\\Users\\kleiy\\OneDrive\\Desktop\\python-ai-apps\\ai_apps\\.venv\\Scripts\\python.exe
- Working directory: C:\\Users\\kleiy\\OneDrive\\Desktop\\python-ai-apps\\ai_apps\\ui_testing_framework
- Browser module: ui_testing_automation.browser (already imported)
- Test framework: Pytest with pytest-asyncio
- All async methods use @pytest.mark.asyncio decorator

AVAILABLE BROWSER OPERATIONS (all are async):
- await self.browser.initialize() - Initialize browser
- await self.browser.extract_elements(url) - Navigate and extract elements
- self.browser.page - Access Playwright page object
- await self.browser.cleanup() - Cleanup browser

PLAYWRIGHT PAGE OPERATIONS (use self.browser.page):
- await page.click(selector) - Click element
- await page.fill(selector, text) - Fill input field
- await page.wait_for_selector(selector) - Wait for element
- await page.is_visible(selector) - Check visibility
- await page.get_by_text(text) - Find by text
- await page.get_by_role(role) - Find by ARIA role

Generate ONLY the test method implementation code.
Use this exact format for each test method:

    @pytest.mark.asyncio
    async def test_method_name(self):
        '''Test description'''
        # Navigate to page
        result = await self.browser.extract_elements(self.base_url)
        assert result.success, 'Failed to load page'
        
        # Test implementation
        page = self.browser.page
        # Your test steps here using await
        
        # Assertions
        assert condition, 'Error message'

Remember: Keep it SIMPLE, use SINGLE QUOTES, and ALWAYS use await for async operations.
"""