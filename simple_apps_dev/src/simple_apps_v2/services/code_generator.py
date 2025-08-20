"""
Code generation service.
"""

from typing import Dict, Any

from simple_apps_v2.core.logging import get_logger

logger = get_logger(__name__)


class CodeGenerator:
    """Service for generating test code."""
    
    def __init__(self, code_type: str = "pytest", language: str = "python"):
        """Initialize code generator."""
        self.code_type = code_type
        self.language = language
    
    async def generate_code(
        self,
        extraction_data: Dict[str, Any],
        test_data: Dict[str, Any],
        include_fixtures: bool = True,
        include_page_objects: bool = True
    ) -> Dict[str, str]:
        """Generate test code from test scenarios."""
        logger.info(f"Generating {self.code_type} code in {self.language}")
        
        generated_files = {}
        
        if self.code_type == "pytest" and self.language == "python":
            # Generate pytest files
            generated_files["test_main.py"] = self._generate_pytest_main(test_data)
            
            if include_fixtures:
                generated_files["conftest.py"] = self._generate_pytest_fixtures()
            
            if include_page_objects:
                generated_files["page_objects.py"] = self._generate_page_objects(extraction_data)
            
            generated_files["requirements.txt"] = self._generate_requirements()
            
        elif self.code_type == "playwright" and self.language == "python":
            # Generate Playwright files
            generated_files["test_playwright.py"] = self._generate_playwright_tests(test_data)
            
            if include_page_objects:
                generated_files["pages.py"] = self._generate_playwright_pages(extraction_data)
        
        return generated_files
    
    def _generate_pytest_main(self, test_data: Dict[str, Any]) -> str:
        """Generate main pytest file."""
        code = '''"""
Generated pytest test suite.
"""

import pytest
from playwright.sync_api import Page, expect


class TestWebAutomation:
    """Web automation test suite."""
    
'''
        
        # Generate test methods for each scenario
        for scenario in test_data.get("scenarios", []):
            test_name = scenario["name"].lower().replace(" ", "_")
            code += f'''    def test_{test_name}(self, page: Page):
        """Test: {scenario['name']}"""
'''
            
            # Add steps
            for step in scenario.get("steps", []):
                code += f'''        # {step}
        pass
'''
            
            # Add assertions
            for expected in scenario.get("expected", []):
                code += f'''        # Assert: {expected}
        pass
'''
            code += "\n"
        
        return code
    
    def _generate_pytest_fixtures(self) -> str:
        """Generate pytest fixtures."""
        return '''"""
Pytest fixtures for test suite.
"""

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def browser():
    """Create browser instance."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """Create page for each test."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
'''
    
    def _generate_page_objects(self, extraction_data: Dict[str, Any]) -> str:
        """Generate page object model."""
        code = '''"""
Page Object Model for test suite.
"""

from playwright.sync_api import Page


class BasePage:
    """Base page class."""
    
    def __init__(self, page: Page):
        self.page = page
    
    def navigate(self, url: str):
        """Navigate to URL."""
        self.page.goto(url)
    
    def get_title(self) -> str:
        """Get page title."""
        return self.page.title()


class MainPage(BasePage):
    """Main page object."""
    
'''
        
        # Add methods for interacting with elements
        elements_by_category = extraction_data.get("elements_by_category", {})
        
        for category, elements in elements_by_category.items():
            if elements:
                element = elements[0]  # Use first element as example
                if category == "button":
                    code += f'''    def click_button(self, text: str):
        """Click button by text."""
        self.page.get_by_role("button", name=text).click()
    
'''
                elif category == "form_input":
                    code += f'''    def fill_input(self, name: str, value: str):
        """Fill input field."""
        self.page.fill(f"input[name='{{name}}']", value)
    
'''
                elif category == "link":
                    code += f'''    def click_link(self, text: str):
        """Click link by text."""
        self.page.get_by_role("link", name=text).click()
    
'''
        
        return code
    
    def _generate_requirements(self) -> str:
        """Generate requirements file."""
        return '''pytest>=7.0.0
pytest-playwright>=0.4.0
playwright>=1.40.0
pytest-html>=3.0.0
pytest-xdist>=3.0.0
'''
    
    def _generate_playwright_tests(self, test_data: Dict[str, Any]) -> str:
        """Generate Playwright test file."""
        code = '''"""
Playwright test suite.
"""

from playwright.sync_api import sync_playwright, expect


def test_web_automation():
    """Main test function."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
'''
        
        # Add test steps
        for scenario in test_data.get("scenarios", [])[:3]:  # Limit to 3 for example
            code += f'''        # Test: {scenario['name']}
'''
            for step in scenario.get("steps", []):
                code += f'''        # {step}
'''
            code += '''        
'''
        
        code += '''        browser.close()


if __name__ == "__main__":
    test_web_automation()
'''
        
        return code
    
    def _generate_playwright_pages(self, extraction_data: Dict[str, Any]) -> str:
        """Generate Playwright page objects."""
        return self._generate_page_objects(extraction_data)