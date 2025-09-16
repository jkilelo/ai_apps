"""
Page Object Model Generator for creating reusable test components
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class PageObjectGenerator:
    """
    Generates Page Object Model classes from extracted elements
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.generated_pages: Dict[str, str] = {}
        
        # Configuration
        self.output_dir = Path(self.config.get("output_dir", "./generated_page_objects"))
        self.base_class = self.config.get("base_class", "BasePage")
        self.framework = self.config.get("framework", "playwright")  # playwright, selenium
        self.language = self.config.get("language", "python")  # python, javascript, typescript
        
        logger.info(f"Initialized PageObjectGenerator with config: {self.config}")
    
    def generate_from_elements(self, elements: List[Dict[str, Any]], page_name: str) -> str:
        """Generate Page Object Model from extracted elements"""
        
        if self.language == "python":
            return self.generate_python_page_object(elements, page_name)
        elif self.language == "javascript":
            return self.generate_javascript_page_object(elements, page_name)
        elif self.language == "typescript":
            return self.generate_typescript_page_object(elements, page_name)
        else:
            raise ValueError(f"Unsupported language: {self.language}")
    
    def generate_python_page_object(self, elements: List[Dict[str, Any]], page_name: str) -> str:
        """Generate Python Page Object Model"""
        
        class_name = self._to_class_name(page_name)
        
        # Group elements by type
        buttons = []
        inputs = []
        links = []
        texts = []
        selects = []
        other = []
        
        for element in elements:
            element_type = element.get("type", "").lower()
            tag_name = element.get("tag_name", "").lower()
            
            if element_type == "button" or tag_name == "button":
                buttons.append(element)
            elif element_type in ["text", "email", "password", "search"] or tag_name == "input":
                inputs.append(element)
            elif element_type == "link" or tag_name == "a":
                links.append(element)
            elif tag_name == "select":
                selects.append(element)
            elif element.get("text_content"):
                texts.append(element)
            else:
                other.append(element)
        
        # Generate imports
        if self.framework == "playwright":
            imports = """from playwright.async_api import Page, Locator
from typing import Optional
import logging

logger = logging.getLogger(__name__)
"""
        else:  # selenium
            imports = """from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from typing import Optional
import logging

logger = logging.getLogger(__name__)
"""
        
        # Generate base class
        if self.framework == "playwright":
            base_class_code = """
class BasePage:
    \"\"\"Base page class for all page objects\"\"\"
    
    def __init__(self, page: Page):
        self.page = page
    
    async def navigate_to(self, url: str):
        \"\"\"Navigate to URL\"\"\"
        await self.page.goto(url)
    
    async def get_title(self) -> str:
        \"\"\"Get page title\"\"\"
        return await self.page.title()
    
    async def wait_for_element(self, selector: str, timeout: int = 30000):
        \"\"\"Wait for element to be visible\"\"\"
        await self.page.wait_for_selector(selector, timeout=timeout)
    
    async def click_element(self, selector: str):
        \"\"\"Click an element\"\"\"
        await self.page.click(selector)
    
    async def fill_field(self, selector: str, value: str):
        \"\"\"Fill a form field\"\"\"
        await self.page.fill(selector, value)
    
    async def get_text(self, selector: str) -> str:
        \"\"\"Get element text\"\"\"
        return await self.page.text_content(selector)
    
    async def is_visible(self, selector: str) -> bool:
        \"\"\"Check if element is visible\"\"\"
        return await self.page.is_visible(selector)
"""
        else:  # selenium
            base_class_code = """
class BasePage:
    \"\"\"Base page class for all page objects\"\"\"
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def navigate_to(self, url: str):
        \"\"\"Navigate to URL\"\"\"
        self.driver.get(url)
    
    def get_title(self) -> str:
        \"\"\"Get page title\"\"\"
        return self.driver.title
    
    def wait_for_element(self, locator):
        \"\"\"Wait for element to be visible\"\"\"
        return self.wait.until(EC.visibility_of_element_located(locator))
    
    def click_element(self, locator):
        \"\"\"Click an element\"\"\"
        element = self.wait_for_element(locator)
        element.click()
    
    def fill_field(self, locator, value: str):
        \"\"\"Fill a form field\"\"\"
        element = self.wait_for_element(locator)
        element.clear()
        element.send_keys(value)
    
    def get_text(self, locator) -> str:
        \"\"\"Get element text\"\"\"
        element = self.wait_for_element(locator)
        return element.text
    
    def is_visible(self, locator) -> bool:
        \"\"\"Check if element is visible\"\"\"
        try:
            element = self.driver.find_element(*locator)
            return element.is_displayed()
        except:
            return False
"""
        
        # Generate page class
        page_class = f"\n\nclass {class_name}(BasePage):\n"
        page_class += f'    \"\"\"Page Object Model for {page_name}\"\"\"\n\n'
        
        # Generate locators
        if self.framework == "playwright":
            page_class += "    # Locators\n"
            
            # Button locators
            for i, button in enumerate(buttons):
                var_name = self._generate_variable_name(button, f"button_{i}")
                selector = self._get_best_selector(button)
                page_class += f'    {var_name} = "{selector}"\n'
            
            # Input locators
            for i, input_field in enumerate(inputs):
                var_name = self._generate_variable_name(input_field, f"input_{i}")
                selector = self._get_best_selector(input_field)
                page_class += f'    {var_name} = "{selector}"\n'
            
            # Link locators
            for i, link in enumerate(links):
                var_name = self._generate_variable_name(link, f"link_{i}")
                selector = self._get_best_selector(link)
                page_class += f'    {var_name} = "{selector}"\n'
            
            # Select locators
            for i, select in enumerate(selects):
                var_name = self._generate_variable_name(select, f"select_{i}")
                selector = self._get_best_selector(select)
                page_class += f'    {var_name} = "{selector}"\n'
            
        else:  # selenium
            page_class += "    # Locators\n"
            
            # Button locators
            for i, button in enumerate(buttons):
                var_name = self._generate_variable_name(button, f"button_{i}")
                locator = self._get_selenium_locator(button)
                page_class += f'    {var_name} = {locator}\n'
            
            # Input locators
            for i, input_field in enumerate(inputs):
                var_name = self._generate_variable_name(input_field, f"input_{i}")
                locator = self._get_selenium_locator(input_field)
                page_class += f'    {var_name} = {locator}\n'
            
            # Link locators
            for i, link in enumerate(links):
                var_name = self._generate_variable_name(link, f"link_{i}")
                locator = self._get_selenium_locator(link)
                page_class += f'    {var_name} = {locator}\n'
            
            # Select locators
            for i, select in enumerate(selects):
                var_name = self._generate_variable_name(select, f"select_{i}")
                locator = self._get_selenium_locator(select)
                page_class += f'    {var_name} = {locator}\n'
        
        page_class += "\n"
        
        # Generate action methods
        page_class += "    # Actions\n"
        
        if self.framework == "playwright":
            # Button actions
            for i, button in enumerate(buttons):
                method_name = self._generate_method_name(button, f"click_button_{i}")
                var_name = self._generate_variable_name(button, f"button_{i}")
                page_class += f"""    async def {method_name}(self):
        \"\"\"Click {button.get('text_content', 'button')}\"\"\"
        await self.click_element(self.{var_name})
        logger.info("Clicked {button.get('text_content', 'button')}")
\n"""
            
            # Input actions
            for i, input_field in enumerate(inputs):
                method_name = self._generate_method_name(input_field, f"fill_input_{i}")
                var_name = self._generate_variable_name(input_field, f"input_{i}")
                field_type = input_field.get('type', 'text')
                page_class += f"""    async def {method_name}(self, value: str):
        \"\"\"Fill {field_type} field\"\"\"
        await self.fill_field(self.{var_name}, value)
        logger.info(f"Filled {field_type} field with: {{value}}")
\n"""
            
            # Link actions
            for i, link in enumerate(links):
                method_name = self._generate_method_name(link, f"click_link_{i}")
                var_name = self._generate_variable_name(link, f"link_{i}")
                page_class += f"""    async def {method_name}(self):
        \"\"\"Click {link.get('text_content', 'link')}\"\"\"
        await self.click_element(self.{var_name})
        logger.info("Clicked {link.get('text_content', 'link')}")
\n"""
            
        else:  # selenium
            # Button actions
            for i, button in enumerate(buttons):
                method_name = self._generate_method_name(button, f"click_button_{i}")
                var_name = self._generate_variable_name(button, f"button_{i}")
                page_class += f"""    def {method_name}(self):
        \"\"\"Click {button.get('text_content', 'button')}\"\"\"
        self.click_element(self.{var_name})
        logger.info("Clicked {button.get('text_content', 'button')}")
\n"""
            
            # Input actions
            for i, input_field in enumerate(inputs):
                method_name = self._generate_method_name(input_field, f"fill_input_{i}")
                var_name = self._generate_variable_name(input_field, f"input_{i}")
                field_type = input_field.get('type', 'text')
                page_class += f"""    def {method_name}(self, value: str):
        \"\"\"Fill {field_type} field\"\"\"
        self.fill_field(self.{var_name}, value)
        logger.info(f"Filled {field_type} field with: {{value}}")
\n"""
            
            # Link actions
            for i, link in enumerate(links):
                method_name = self._generate_method_name(link, f"click_link_{i}")
                var_name = self._generate_variable_name(link, f"link_{i}")
                page_class += f"""    def {method_name}(self):
        \"\"\"Click {link.get('text_content', 'link')}\"\"\"
        self.click_element(self.{var_name})
        logger.info("Clicked {link.get('text_content', 'link')}")
\n"""
        
        # Generate verification methods
        page_class += "\n    # Verifications\n"
        
        if self.framework == "playwright":
            page_class += """    async def verify_page_loaded(self) -> bool:
        \"\"\"Verify page is loaded\"\"\"
        try:
            # Add specific element checks here
            return True
        except Exception as e:
            logger.error(f"Page not loaded: {e}")
            return False
\n"""
        else:  # selenium
            page_class += """    def verify_page_loaded(self) -> bool:
        \"\"\"Verify page is loaded\"\"\"
        try:
            # Add specific element checks here
            return True
        except Exception as e:
            logger.error(f"Page not loaded: {e}")
            return False
\n"""
        
        # Combine all parts
        full_code = imports + base_class_code + page_class
        
        # Save to file
        self.save_page_object(full_code, page_name)
        
        return full_code
    
    def generate_javascript_page_object(self, elements: List[Dict[str, Any]], page_name: str) -> str:
        """Generate JavaScript Page Object Model"""
        
        class_name = self._to_class_name(page_name)
        
        # Group elements by type (similar to Python)
        buttons = []
        inputs = []
        links = []
        selects = []
        
        for element in elements:
            element_type = element.get("type", "").lower()
            tag_name = element.get("tag_name", "").lower()
            
            if element_type == "button" or tag_name == "button":
                buttons.append(element)
            elif element_type in ["text", "email", "password", "search"] or tag_name == "input":
                inputs.append(element)
            elif element_type == "link" or tag_name == "a":
                links.append(element)
            elif tag_name == "select":
                selects.append(element)
        
        # Generate JavaScript class
        js_code = f"""class {class_name} {{
    constructor(page) {{
        this.page = page;
        
        // Locators
"""
        
        # Add locators
        for i, button in enumerate(buttons):
            var_name = self._generate_variable_name(button, f"button_{i}")
            selector = self._get_best_selector(button)
            js_code += f'        this.{var_name} = "{selector}";\n'
        
        for i, input_field in enumerate(inputs):
            var_name = self._generate_variable_name(input_field, f"input_{i}")
            selector = self._get_best_selector(input_field)
            js_code += f'        this.{var_name} = "{selector}";\n'
        
        for i, link in enumerate(links):
            var_name = self._generate_variable_name(link, f"link_{i}")
            selector = self._get_best_selector(link)
            js_code += f'        this.{var_name} = "{selector}";\n'
        
        js_code += "    }\n\n"
        
        # Add action methods
        js_code += "    // Actions\n"
        
        for i, button in enumerate(buttons):
            method_name = self._generate_method_name(button, f"clickButton{i}")
            var_name = self._generate_variable_name(button, f"button_{i}")
            js_code += f"""    async {method_name}() {{
        await this.page.click(this.{var_name});
        console.log('Clicked {button.get("text_content", "button")}');
    }}
\n"""
        
        for i, input_field in enumerate(inputs):
            method_name = self._generate_method_name(input_field, f"fillInput{i}")
            var_name = self._generate_variable_name(input_field, f"input_{i}")
            js_code += f"""    async {method_name}(value) {{
        await this.page.fill(this.{var_name}, value);
        console.log(`Filled field with: ${{value}}`);
    }}
\n"""
        
        js_code += """    // Verifications
    async verifyPageLoaded() {
        try {
            // Add specific element checks here
            return true;
        } catch (error) {
            console.error(`Page not loaded: ${error}`);
            return false;
        }
    }
}

module.exports = """ + class_name + ";\n"
        
        # Save to file
        self.save_page_object(js_code, page_name, extension=".js")
        
        return js_code
    
    def generate_typescript_page_object(self, elements: List[Dict[str, Any]], page_name: str) -> str:
        """Generate TypeScript Page Object Model"""
        
        class_name = self._to_class_name(page_name)
        
        # Similar to JavaScript but with type annotations
        ts_code = f"""import {{ Page, Locator }} from '@playwright/test';

export class {class_name} {{
    private page: Page;
"""
        
        # Add typed locators
        buttons = []
        inputs = []
        links = []
        
        for element in elements:
            element_type = element.get("type", "").lower()
            tag_name = element.get("tag_name", "").lower()
            
            if element_type == "button" or tag_name == "button":
                buttons.append(element)
            elif element_type in ["text", "email", "password", "search"] or tag_name == "input":
                inputs.append(element)
            elif element_type == "link" or tag_name == "a":
                links.append(element)
        
        # Declare locator properties
        for i, button in enumerate(buttons):
            var_name = self._generate_variable_name(button, f"button_{i}")
            ts_code += f"    private {var_name}: string;\n"
        
        for i, input_field in enumerate(inputs):
            var_name = self._generate_variable_name(input_field, f"input_{i}")
            ts_code += f"    private {var_name}: string;\n"
        
        ts_code += f"""
    constructor(page: Page) {{
        this.page = page;
        
        // Initialize locators
"""
        
        # Initialize locators
        for i, button in enumerate(buttons):
            var_name = self._generate_variable_name(button, f"button_{i}")
            selector = self._get_best_selector(button)
            ts_code += f'        this.{var_name} = "{selector}";\n'
        
        for i, input_field in enumerate(inputs):
            var_name = self._generate_variable_name(input_field, f"input_{i}")
            selector = self._get_best_selector(input_field)
            ts_code += f'        this.{var_name} = "{selector}";\n'
        
        ts_code += "    }\n\n"
        
        # Add typed methods
        ts_code += "    // Actions\n"
        
        for i, button in enumerate(buttons):
            method_name = self._generate_method_name(button, f"clickButton{i}")
            var_name = self._generate_variable_name(button, f"button_{i}")
            ts_code += f"""    async {method_name}(): Promise<void> {{
        await this.page.click(this.{var_name});
        console.log('Clicked button');
    }}
\n"""
        
        for i, input_field in enumerate(inputs):
            method_name = self._generate_method_name(input_field, f"fillInput{i}")
            var_name = self._generate_variable_name(input_field, f"input_{i}")
            ts_code += f"""    async {method_name}(value: string): Promise<void> {{
        await this.page.fill(this.{var_name}, value);
        console.log(`Filled field with: ${{value}}`);
    }}
\n"""
        
        ts_code += """    // Verifications
    async verifyPageLoaded(): Promise<boolean> {
        try {
            // Add specific element checks here
            return true;
        } catch (error) {
            console.error(`Page not loaded: ${error}`);
            return false;
        }
    }
}\n"""
        
        # Save to file
        self.save_page_object(ts_code, page_name, extension=".ts")
        
        return ts_code
    
    def _to_class_name(self, page_name: str) -> str:
        """Convert page name to class name"""
        # Convert to PascalCase
        parts = page_name.replace("-", "_").replace(" ", "_").split("_")
        return "".join(part.capitalize() for part in parts) + "Page"
    
    def _generate_variable_name(self, element: Dict[str, Any], default: str) -> str:
        """Generate variable name for element"""
        # Try to use meaningful names from element attributes
        element_id = element.get("id", "")
        element_name = element.get("name", "")
        element_text = element.get("text_content", "")
        aria_label = element.get("aria_label", "")
        
        if element_id:
            return self._to_variable_name(element_id)
        elif element_name:
            return self._to_variable_name(element_name)
        elif aria_label:
            return self._to_variable_name(aria_label)
        elif element_text:
            # Use first few words of text
            text_parts = element_text.split()[:3]
            return self._to_variable_name("_".join(text_parts))
        else:
            return default
    
    def _generate_method_name(self, element: Dict[str, Any], default: str) -> str:
        """Generate method name for element action"""
        element_text = element.get("text_content", "")
        aria_label = element.get("aria_label", "")
        element_id = element.get("id", "")
        
        if element_text:
            # Use text content for method name
            text_parts = element_text.split()[:3]
            base_name = "_".join(text_parts)
        elif aria_label:
            base_name = aria_label
        elif element_id:
            base_name = element_id
        else:
            return default
        
        # Add appropriate prefix based on element type
        element_type = element.get("type", "").lower()
        tag_name = element.get("tag_name", "").lower()
        
        if element_type == "button" or tag_name == "button":
            prefix = "click"
        elif element_type in ["text", "email", "password", "search"] or tag_name == "input":
            prefix = "fill"
        elif element_type == "link" or tag_name == "a":
            prefix = "click"
        elif tag_name == "select":
            prefix = "select"
        else:
            prefix = "interact_with"
        
        return f"{prefix}_{self._to_variable_name(base_name)}"
    
    def _to_variable_name(self, text: str) -> str:
        """Convert text to valid variable name"""
        import re
        
        # Remove special characters and convert to snake_case
        text = re.sub(r'[^a-zA-Z0-9_]', '_', text.lower())
        text = re.sub(r'_+', '_', text)  # Remove multiple underscores
        text = text.strip('_')  # Remove leading/trailing underscores
        
        # Ensure it doesn't start with a number
        if text and text[0].isdigit():
            text = f"element_{text}"
        
        return text or "element"
    
    def _get_best_selector(self, element: Dict[str, Any]) -> str:
        """Get the best CSS selector for an element"""
        # Priority: ID > unique attributes > class > tag + text
        
        element_id = element.get("id", "")
        if element_id:
            return f"#{element_id}"
        
        # Check for unique attributes
        name = element.get("name", "")
        if name:
            return f"[name='{name}']"
        
        aria_label = element.get("aria_label", "")
        if aria_label:
            return f"[aria-label='{aria_label}']"
        
        # Use CSS selector if available
        css_selector = element.get("css_selector", "")
        if css_selector:
            return css_selector
        
        # Use class names
        class_names = element.get("class_names", [])
        if class_names:
            return "." + ".".join(class_names[:2])  # Use first 2 classes
        
        # Use tag + text
        tag_name = element.get("tag_name", "div").lower()
        text_content = element.get("text_content", "")
        if text_content:
            return f"{tag_name}:has-text('{text_content[:30]}')"
        
        return tag_name
    
    def _get_selenium_locator(self, element: Dict[str, Any]) -> str:
        """Get Selenium locator tuple for an element"""
        element_id = element.get("id", "")
        if element_id:
            return f"(By.ID, '{element_id}')"
        
        name = element.get("name", "")
        if name:
            return f"(By.NAME, '{name}')"
        
        css_selector = element.get("css_selector", "")
        if css_selector:
            return f"(By.CSS_SELECTOR, '{css_selector}')"
        
        class_names = element.get("class_names", [])
        if class_names:
            return f"(By.CLASS_NAME, '{class_names[0]}')"
        
        tag_name = element.get("tag_name", "div").lower()
        return f"(By.TAG_NAME, '{tag_name}')"
    
    def save_page_object(self, code: str, page_name: str, extension: str = ".py") -> Path:
        """Save generated page object to file"""
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = self._to_variable_name(page_name) + "_page" + extension
        file_path = self.output_dir / filename
        
        # Write code to file
        with open(file_path, 'w') as f:
            f.write(code)
        
        # Store in memory
        self.generated_pages[page_name] = str(file_path)
        
        logger.info(f"Saved page object to: {file_path}")
        
        return file_path
    
    def generate_test_suite_scaffold(self, page_objects: List[str]) -> str:
        """Generate a test suite scaffold using the page objects"""
        
        if self.framework == "playwright" and self.language == "python":
            scaffold = """import pytest
from playwright.async_api import async_playwright
"""
            
            # Import page objects
            for page_object in page_objects:
                page_name = Path(page_object).stem
                class_name = self._to_class_name(page_name.replace("_page", ""))
                scaffold += f"from page_objects.{page_name} import {class_name}\n"
            
            scaffold += """

@pytest.fixture
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        yield browser
        await browser.close()

@pytest.fixture
async def page(browser):
    page = await browser.new_page()
    yield page
    await page.close()


class TestSuite:
    \"\"\"Test suite using Page Object Model\"\"\"
    
    async def test_example(self, page):
        \"\"\"Example test case\"\"\"
        # Initialize page objects
        # page_obj = PageClass(page)
        # await page_obj.navigate_to("https://example.com")
        # await page_obj.click_button()
        # assert await page_obj.verify_page_loaded()
        pass
"""
            
            return scaffold
        
        return ""