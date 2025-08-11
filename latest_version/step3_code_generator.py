#!/usr/bin/env python3
"""
Python Test Code Generator - Step 3 of UI Testing Framework
Generates executable Python test code from Gherkin scenarios using Page Object Model (POM)

Following CODER Strategy:
- Single file implementation (no code duplication)
- TDD-first approach
- Anti-bloat measures
- Comprehensive error handling
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CODER STRATEGIC PLANNING
# ============================================================================
"""
Strategic Analysis:
1. Approach 1: Direct Gherkin-to-Code Translation
   - Pros: Simple, straightforward mapping
   - Cons: Rigid, doesn't handle complex scenarios well
   
2. Approach 2: Template-Based Generation with LLM Enhancement
   - Pros: Flexible, handles complex logic, leverages AI
   - Cons: Requires LLM calls, more complex
   
3. Approach 3: Hybrid Rule-Based + Template System
   - Pros: Fast, deterministic, extensible
   - Cons: More initial setup

Selected Approach: Hybrid (Approach 3)
- Use rule-based parsing for standard Gherkin steps
- Template system for code structure
- Optional LLM enhancement for complex scenarios
"""

# ============================================================================
# DATA MODELS
# ============================================================================

class TestFramework(str, Enum):
    """Supported test frameworks"""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    PYTEST_BDD = "pytest-bdd"

class BrowserFramework(str, Enum):
    """Supported browser automation frameworks"""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    PUPPETEER = "puppeteer"

@dataclass
class GherkinStep:
    """Represents a single Gherkin step"""
    keyword: str  # Given, When, Then, And, But
    text: str
    parameters: List[str] = field(default_factory=list)
    data_table: Optional[List[Dict[str, Any]]] = None
    
    def get_action_type(self) -> str:
        """Determine the action type from step text"""
        text_lower = self.text.lower()
        
        if "navigate" in text_lower or "go to" in text_lower or "open" in text_lower:
            return "navigation"
        elif "click" in text_lower:
            return "click"
        elif "fill" in text_lower or "enter" in text_lower or "type" in text_lower:
            return "input"
        elif "select" in text_lower or "choose" in text_lower:
            return "select"
        elif "should be" in text_lower or "should contain" in text_lower or "verify" in text_lower:
            return "assertion"
        elif "wait" in text_lower:
            return "wait"
        elif "press" in text_lower and "key" in text_lower:
            return "keyboard"
        elif "hover" in text_lower:
            return "hover"
        elif "scroll" in text_lower:
            return "scroll"
        else:
            return "custom"

@dataclass
class GherkinScenario:
    """Represents a Gherkin scenario"""
    name: str
    steps: List[GherkinStep]
    tags: List[str] = field(default_factory=list)
    examples: Optional[List[Dict[str, Any]]] = None
    
    def is_data_driven(self) -> bool:
        """Check if scenario has examples (data-driven)"""
        # Check for examples or if step parameters contain angle brackets (Scenario Outline)
        if self.examples is not None and len(self.examples) > 0:
            return True
        # Check if any step contains <parameter> indicating scenario outline
        for step in self.steps:
            if '<' in step.text and '>' in step.text:
                return True
        return False

@dataclass
class GherkinFeature:
    """Represents a Gherkin feature"""
    name: str
    description: str
    scenarios: List[GherkinScenario]
    background: Optional[List[GherkinStep]] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class PageElement:
    """Represents a page element from extraction"""
    name: str
    selector: str
    selector_type: str  # css, xpath, id, text
    element_type: str  # button, input, link, etc.
    text_content: Optional[str] = None

@dataclass
class PageObject:
    """Represents a Page Object Model class"""
    name: str
    url: str
    elements: List[PageElement]
    methods: List[str] = field(default_factory=list)

@dataclass
class TestCodeConfig:
    """Configuration for test code generation"""
    test_framework: TestFramework = TestFramework.PYTEST
    browser_framework: BrowserFramework = BrowserFramework.PLAYWRIGHT
    use_async: bool = True
    generate_page_objects: bool = True
    generate_fixtures: bool = True
    generate_data_providers: bool = True
    add_logging: bool = True
    add_screenshots: bool = True
    add_retry_logic: bool = True
    max_retries: int = 3
    output_dir: Path = Path("./generated_tests")

# ============================================================================
# GHERKIN PARSER
# ============================================================================

class GherkinParser:
    """Parse Gherkin feature files into structured data"""
    
    def parse_feature_file(self, file_path: Union[str, Path]) -> GherkinFeature:
        """Parse a .feature file"""
        file_path = Path(file_path)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        return self.parse_feature_content(content)
    
    def parse_feature_content(self, content: str) -> GherkinFeature:
        """Parse Gherkin content"""
        lines = content.strip().split('\n')
        
        feature = None
        current_scenario = None
        current_step = None
        scenarios = []
        background_steps = []
        in_background = False
        in_examples = False
        examples_data = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse tags
            if line.startswith('@'):
                tags = [tag.strip() for tag in line.split() if tag.startswith('@')]
                continue
            
            # Parse Feature
            if line.startswith('Feature:'):
                feature_name = line[8:].strip()
                feature = GherkinFeature(
                    name=feature_name,
                    description="",
                    scenarios=[]
                )
            
            # Parse Background
            elif line.startswith('Background:'):
                in_background = True
                current_scenario = None
            
            # Parse Scenario
            elif line.startswith('Scenario:') or line.startswith('Scenario Outline:'):
                in_background = False
                in_examples = False
                
                if current_scenario:
                    scenarios.append(current_scenario)
                
                scenario_name = line.split(':', 1)[1].strip()
                current_scenario = GherkinScenario(
                    name=scenario_name,
                    steps=[]
                )
            
            # Parse Examples
            elif line.startswith('Examples:') or line.strip() == '|':
                in_examples = True
                if line.strip() == '|':
                    # Parse table row
                    row_data = [cell.strip() for cell in line.split('|')[1:-1]]
                    examples_data.append(row_data)
            
            # Parse steps
            elif any(line.startswith(kw) for kw in ['Given ', 'When ', 'Then ', 'And ', 'But ']):
                keyword = line.split()[0]
                step_text = line[len(keyword):].strip()
                
                # Extract parameters (quoted strings)
                parameters = re.findall(r'"([^"]*)"', step_text)
                
                step = GherkinStep(
                    keyword=keyword,
                    text=step_text,
                    parameters=parameters
                )
                
                if in_background:
                    background_steps.append(step)
                elif current_scenario:
                    current_scenario.steps.append(step)
        
        # Add last scenario
        if current_scenario:
            scenarios.append(current_scenario)
        
        if feature:
            feature.scenarios = scenarios
            feature.background = background_steps if background_steps else None
        
        return feature or GherkinFeature(name="Unknown", description="", scenarios=scenarios)

# ============================================================================
# STEP MAPPER
# ============================================================================

class StepMapper:
    """Map Gherkin steps to code actions"""
    
    def __init__(self, browser_framework: BrowserFramework):
        self.browser_framework = browser_framework
        self.step_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[Tuple[re.Pattern, str]]]:
        """Initialize regex patterns for step mapping"""
        return {
            "navigation": [
                (re.compile(r'navigates? to "([^"]*)"'), "navigate_to"),
                (re.compile(r'opens? "([^"]*)"'), "navigate_to"),
                (re.compile(r'goes? to "([^"]*)"'), "navigate_to"),
                (re.compile(r'visits? "([^"]*)"'), "navigate_to"),
            ],
            "click": [
                (re.compile(r'clicks? (?:the |on )?"([^"]*)"'), "click_element"),
                (re.compile(r'clicks? (?:the |on )?([^"]+) (?:button|link|element)'), "click_element"),
                (re.compile(r'clicks? the \'([^\']+)\' element'), "click_element_by_tag"),
            ],
            "input": [
                (re.compile(r'fills? "([^"]*)" with "([^"]*)"'), "fill_field"),
                (re.compile(r'enters? "([^"]*)" in(?:to)? "([^"]*)"'), "fill_field"),
                (re.compile(r'types? "([^"]*)" in(?:to)? "([^"]*)"'), "fill_field"),
            ],
            "assertion": [
                (re.compile(r'page title should be "([^"]*)"'), "assert_title"),
                (re.compile(r'"([^"]*)" should be visible'), "assert_visible"),
                (re.compile(r'should see "([^"]*)"'), "assert_text_present"),
                (re.compile(r'should contain "([^"]*)"'), "assert_contains"),
                (re.compile(r'URL should be "([^"]*)"'), "assert_url"),
                (re.compile(r'redirected to .*"([^"]*)"'), "assert_url_contains"),
            ],
            "wait": [
                (re.compile(r'waits? for "([^"]*)"'), "wait_for_element"),
                (re.compile(r'waits? (\d+) seconds?'), "wait_seconds"),
            ],
            "keyboard": [
                (re.compile(r'presses? the "([^"]*)" key'), "press_key"),
                (re.compile(r'presses? "([^"]*)"'), "press_key"),
            ],
        }
    
    def map_step_to_action(self, step: GherkinStep) -> Tuple[str, List[str]]:
        """Map a Gherkin step to a code action"""
        action_type = step.get_action_type()
        
        if action_type in self.step_patterns:
            for pattern, method_name in self.step_patterns[action_type]:
                match = pattern.search(step.text)
                if match:
                    return method_name, list(match.groups())
        
        # Default mapping based on keywords
        if "navigate" in step.text.lower():
            return "navigate_to", step.parameters
        elif "click" in step.text.lower():
            return "click_element", step.parameters
        elif "fill" in step.text.lower() or "enter" in step.text.lower():
            return "fill_field", step.parameters
        elif "should" in step.text.lower():
            return "assert_condition", step.parameters
        
        return "custom_action", step.parameters

# ============================================================================
# CODE TEMPLATES
# ============================================================================

class CodeTemplates:
    """Templates for generating test code"""
    
    @staticmethod
    def get_pytest_imports() -> str:
        """Get pytest imports"""
        return """import pytest
import asyncio
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
"""
    
    @staticmethod
    def get_playwright_imports() -> str:
        """Get Playwright imports"""
        return """from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from playwright.async_api import expect
"""
    
    @staticmethod
    def get_selenium_imports() -> str:
        """Get Selenium imports"""
        return """from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
"""
    
    @staticmethod
    def get_base_page_class(browser_framework: BrowserFramework) -> str:
        """Get base page class template"""
        if browser_framework == BrowserFramework.PLAYWRIGHT:
            return '''
class BasePage:
    """Base page class for Page Object Model"""
    
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def navigate_to(self, url: str):
        """Navigate to URL"""
        await self.page.goto(url)
        self.logger.info(f"Navigated to: {url}")
    
    async def click_element(self, selector: str):
        """Click an element"""
        await self.page.click(selector)
        self.logger.info(f"Clicked: {selector}")
    
    async def fill_field(self, selector: str, value: str):
        """Fill a form field"""
        await self.page.fill(selector, value)
        self.logger.info(f"Filled {selector} with: {value}")
    
    async def get_text(self, selector: str) -> str:
        """Get element text"""
        return await self.page.text_content(selector)
    
    async def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        return await self.page.is_visible(selector)
    
    async def wait_for_element(self, selector: str, timeout: int = 30000):
        """Wait for element to appear"""
        await self.page.wait_for_selector(selector, timeout=timeout)
    
    async def assert_title(self, expected_title: str):
        """Assert page title"""
        actual_title = await self.page.title()
        assert actual_title == expected_title, f"Title mismatch: {actual_title} != {expected_title}"
    
    async def assert_visible(self, selector: str):
        """Assert element is visible"""
        is_visible = await self.is_visible(selector)
        assert is_visible, f"Element not visible: {selector}"
    
    async def assert_text_present(self, text: str):
        """Assert text is present on page"""
        content = await self.page.content()
        assert text in content, f"Text not found: {text}"
    
    async def assert_url(self, expected_url: str):
        """Assert current URL"""
        current_url = self.page.url
        assert current_url == expected_url, f"URL mismatch: {current_url} != {expected_url}"
    
    async def assert_url_contains(self, partial_url: str):
        """Assert URL contains string"""
        current_url = self.page.url
        assert partial_url in current_url, f"URL does not contain: {partial_url}"
    
    async def press_key(self, key: str):
        """Press a keyboard key"""
        await self.page.keyboard.press(key)
        self.logger.info(f"Pressed key: {key}")
    
    async def take_screenshot(self, name: str):
        """Take a screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"screenshots/{name}_{timestamp}.png"
        await self.page.screenshot(path=path)
        self.logger.info(f"Screenshot saved: {path}")
'''
        else:  # Selenium
            return '''
class BasePage:
    """Base page class for Page Object Model"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def navigate_to(self, url: str):
        """Navigate to URL"""
        self.driver.get(url)
        self.logger.info(f"Navigated to: {url}")
    
    def click_element(self, selector: str):
        """Click an element"""
        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        element.click()
        self.logger.info(f"Clicked: {selector}")
    
    def fill_field(self, selector: str, value: str):
        """Fill a form field"""
        element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        element.clear()
        element.send_keys(value)
        self.logger.info(f"Filled {selector} with: {value}")
    
    def get_text(self, selector: str) -> str:
        """Get element text"""
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        return element.text
    
    def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.is_displayed()
        except:
            return False
    
    def wait_for_element(self, selector: str, timeout: int = 30):
        """Wait for element to appear"""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
    
    def assert_title(self, expected_title: str):
        """Assert page title"""
        actual_title = self.driver.title
        assert actual_title == expected_title, f"Title mismatch: {actual_title} != {expected_title}"
    
    def assert_visible(self, selector: str):
        """Assert element is visible"""
        is_visible = self.is_visible(selector)
        assert is_visible, f"Element not visible: {selector}"
    
    def assert_text_present(self, text: str):
        """Assert text is present on page"""
        content = self.driver.page_source
        assert text in content, f"Text not found: {text}"
    
    def assert_url(self, expected_url: str):
        """Assert current URL"""
        current_url = self.driver.current_url
        assert current_url == expected_url, f"URL mismatch: {current_url} != {expected_url}"
    
    def assert_url_contains(self, partial_url: str):
        """Assert URL contains string"""
        current_url = self.driver.current_url
        assert partial_url in current_url, f"URL does not contain: {partial_url}"
    
    def press_key(self, key: str):
        """Press a keyboard key"""
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(self.driver)
        actions.send_keys(getattr(Keys, key.upper(), key)).perform()
        self.logger.info(f"Pressed key: {key}")
    
    def take_screenshot(self, name: str):
        """Take a screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"screenshots/{name}_{timestamp}.png"
        self.driver.save_screenshot(path)
        self.logger.info(f"Screenshot saved: {path}")
'''
    
    @staticmethod
    def get_pytest_fixtures(browser_framework: BrowserFramework) -> str:
        """Get pytest fixtures"""
        if browser_framework == BrowserFramework.PLAYWRIGHT:
            return '''
@pytest.fixture
async def browser():
    """Browser fixture"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        yield browser
        await browser.close()

@pytest.fixture
async def context(browser: Browser):
    """Browser context fixture"""
    context = await browser.new_context()
    yield context
    await context.close()

@pytest.fixture
async def page(context: BrowserContext):
    """Page fixture"""
    page = await context.new_page()
    yield page
    await page.close()
'''
        else:  # Selenium
            return '''
@pytest.fixture
def driver():
    """WebDriver fixture"""
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()
'''

# ============================================================================
# TEST CODE GENERATOR
# ============================================================================

class PythonTestCodeGenerator:
    """Main class for generating Python test code from Gherkin"""
    
    def __init__(self, config: Optional[TestCodeConfig] = None):
        self.config = config or TestCodeConfig()
        self.parser = GherkinParser()
        self.mapper = StepMapper(self.config.browser_framework)
        self.templates = CodeTemplates()
        self.generated_files: List[Path] = []
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized PythonTestCodeGenerator with config: {self.config}")
    
    def generate(self, step2_output):
        """Generate code from Step 2 contract and return Step 3 contract.
        
        Args:
            step2_output: GherkinGeneration contract from Step 2
            
        Returns:
            CodeGeneration: Contract-compliant output
        """
        from data_contracts import CodeGeneration, GeneratedFile, FileType, GherkinGeneration
        from datetime import datetime
        import time
        
        # Validate input is correct contract type
        if not isinstance(step2_output, GherkinGeneration):
            raise TypeError(f"Expected GherkinGeneration, got {type(step2_output).__name__}")
        
        start_time = time.time()
        success = True
        error_message = None
        files = []
        total_tests = 0
        
        try:
            # Process each feature
            for feature in step2_output.features:
                # Convert to Gherkin text for existing parser
                gherkin_text = self._feature_to_gherkin_text(feature)
                
                # Save as temporary feature file
                temp_feature = self.config.output_dir / f"{feature.name.replace(' ', '_').lower()}.feature"
                temp_feature.write_text(gherkin_text)
                
                # Use internal generation method
                generated = self._generate_from_feature_file_internal(
                    feature_file=temp_feature,
                    elements=[]  # Elements already in feature
                )
                
                # Convert to contract format
                for name, content in generated.items():
                    file_type = FileType.TEST if 'test' in name else FileType.PAGE_OBJECT
                    path = self.config.output_dir / name
                    
                    files.append(GeneratedFile(
                        name=name,
                        path=path,
                        content=content,
                        file_type=file_type
                    ))
                    
                    # Count tests
                    if 'def test_' in content:
                        total_tests += content.count('def test_')
                
        except Exception as e:
            success = False
            error_message = str(e)
            logger.error(f"Code generation failed: {e}")
        
        # Return contract
        return CodeGeneration(
            source_features=step2_output.features,
            timestamp=datetime.now().isoformat(),
            success=success,
            files=files,
            test_framework=self.config.test_framework.value,
            language="python",
            browser_framework=self.config.browser_framework.value,
            metadata={
                "generator_version": "1.0.0",
                "async_enabled": self.config.use_async,
                "retry_enabled": self.config.add_retry_logic
            },
            error_message=error_message,
            generation_time=time.time() - start_time,
            total_tests=total_tests
        )
    
    def _feature_to_gherkin_text(self, feature) -> str:
        """Convert feature object to Gherkin text."""
        lines = []
        lines.append(f"Feature: {feature.name}")
        if feature.description:
            lines.append(f"  {feature.description}")
        lines.append("")
        
        for scenario in feature.scenarios:
            if isinstance(scenario, dict):
                lines.append(f"  Scenario: {scenario.get('name', 'Unnamed')}")
                for step in scenario.get('steps', []):
                    if isinstance(step, dict):
                        lines.append(f"    {step.get('keyword', 'Given')} {step.get('text', '')}")
                    else:
                        lines.append(f"    {step.keyword} {step.text}")
            else:
                lines.append(f"  Scenario: {scenario.name}")
                for step in scenario.steps:
                    lines.append(f"    {step.keyword} {step.text}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_from_feature_file_internal(
        self,
        feature_file: Union[str, Path],
        elements: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, str]:
        """Generate test code from a Gherkin feature file"""
        
        # Parse feature file
        feature = self.parser.parse_feature_file(feature_file)
        
        # Generate code components
        generated_code = {}
        
        # Generate Page Object if requested and elements provided
        if self.config.generate_page_objects and elements:
            page_object_code = self._generate_page_object(feature, elements)
            generated_code["page_object"] = page_object_code
        
        # Generate test file
        test_code = self._generate_test_file(feature)
        generated_code["test_file"] = test_code
        
        # Generate fixtures if requested
        if self.config.generate_fixtures:
            fixtures_code = self._generate_fixtures(feature)
            generated_code["fixtures"] = fixtures_code
        
        # Generate data providers if requested
        if self.config.generate_data_providers:
            data_provider_code = self._generate_data_providers(feature)
            generated_code["data_providers"] = data_provider_code
        
        # Save generated code to files
        self._save_generated_code(feature.name, generated_code)
        
        return generated_code
    
    def _generate_page_object(self, feature: GherkinFeature, elements: List[Dict[str, Any]]) -> str:
        """Generate Page Object Model class"""
        
        class_name = self._to_class_name(feature.name) + "Page"
        
        # Extract unique selectors from steps
        selectors = self._extract_selectors_from_steps(feature)
        
        # Build Page Object class
        code = self._get_imports()
        code += self.templates.get_base_page_class(self.config.browser_framework)
        code += f"\n\nclass {class_name}(BasePage):\n"
        code += f'    """Page Object for {feature.name}"""\n\n'
        
        # Add element locators
        code += "    # Locators\n"
        if elements is None:
            elements = []
        for element in elements[:20]:  # Limit to prevent bloat
            if element.get("id"):
                var_name = self._to_variable_name(element.get("id"))
                code += f'    {var_name} = "#{element.get("id")}"\n'
            elif element.get("css_selector"):
                var_name = self._to_variable_name(element.get("text_content", "element"))
                code += f'    {var_name} = "{element.get("css_selector")}"\n'
        
        code += "\n    # Custom actions\n"
        
        # Generate methods for unique actions in scenarios
        methods = self._generate_page_methods(feature)
        code += methods
        
        return code
    
    def _generate_test_file(self, feature: GherkinFeature) -> str:
        """Generate test file with test cases"""
        
        # Generate imports
        code = self._get_imports()
        
        # Generate fixtures
        code += self.templates.get_pytest_fixtures(self.config.browser_framework)
        
        # Generate base page if not separate
        if not self.config.generate_page_objects:
            code += self.templates.get_base_page_class(self.config.browser_framework)
        
        # Generate test class
        class_name = "Test" + self._to_class_name(feature.name)
        code += f"\n\nclass {class_name}:\n"
        code += f'    """Test suite for {feature.name}"""\n\n'
        
        # Generate setup if background exists
        if feature.background:
            code += self._generate_background_setup(feature.background)
        
        # Generate test methods for each scenario
        for scenario in feature.scenarios:
            code += self._generate_test_method(scenario)
        
        return code
    
    def _generate_test_method(self, scenario: GherkinScenario) -> str:
        """Generate a test method for a scenario"""
        
        method_name = "test_" + self._to_variable_name(scenario.name)
        
        if self.config.browser_framework == BrowserFramework.PLAYWRIGHT:
            code = f"    async def {method_name}(self, page: Page):\n"
        else:
            code = f"    def {method_name}(self, driver):\n"
        
        code += f'        """{scenario.name}"""\n'
        
        # Add logging
        if self.config.add_logging:
            code += f'        logger = logging.getLogger(__name__)\n'
            code += f'        logger.info("Starting test: {scenario.name}")\n\n'
        
        # Initialize page object if using POM
        if self.config.generate_page_objects:
            if self.config.browser_framework == BrowserFramework.PLAYWRIGHT:
                code += f"        page_obj = BasePage(page)\n\n"
            else:
                code += f"        page_obj = BasePage(driver)\n\n"
        
        # Add retry logic if configured
        if self.config.add_retry_logic:
            code += f"        max_retries = {self.config.max_retries}\n"
            code += f"        for attempt in range(max_retries):\n"
            code += f"            try:\n"
            indent = "                "
        else:
            indent = "        "
        
        # Generate code for each step
        for step in scenario.steps:
            step_code = self._generate_step_code(step)
            # Apply indent to each line of step_code
            for line in step_code.split('\n'):
                if line:  # Don't add indent to empty lines
                    code += indent + line + '\n'
        
        # Add screenshot on success
        if self.config.add_screenshots:
            if self.config.browser_framework == BrowserFramework.PLAYWRIGHT:
                code += f'{indent}await page.screenshot(path="screenshots/{method_name}_success.png")\n'
            else:
                code += f'{indent}driver.save_screenshot("screenshots/{method_name}_success.png")\n'
        
        # Complete retry logic
        if self.config.add_retry_logic:
            code += f"{indent}break  # Test passed\n"
            code += f"            except Exception as e:\n"
            code += f'                logger.error(f"Attempt {{attempt + 1}} failed: {{e}}")\n'
            code += f"                if attempt == max_retries - 1:\n"
            code += f"                    raise\n"
            if self.config.browser_framework == BrowserFramework.PLAYWRIGHT:
                code += f"                await asyncio.sleep(2)  # Wait before retry\n"
            else:
                code += f"                import time\n"
                code += f"                time.sleep(2)  # Wait before retry\n"
        
        code += "\n"
        return code
    
    def _generate_step_code(self, step: GherkinStep) -> str:
        """Generate code for a single Gherkin step"""
        
        # Map step to action
        action, params = self.mapper.map_step_to_action(step)
        
        # Generate appropriate code based on action
        if self.config.browser_framework == BrowserFramework.PLAYWRIGHT:
            return self._generate_playwright_step_code(action, params, step)
        else:
            return self._generate_selenium_step_code(action, params, step)
    
    def _generate_playwright_step_code(self, action: str, params: List[str], step: GherkinStep) -> str:
        """Generate Playwright code for a step"""
        
        code = f"# {step.keyword} {step.text}"
        
        if action == "navigate_to":
            url = params[0] if params else "https://example.com"
            code += f'\nawait page.goto("{url}")'
        
        elif action == "click_element":
            selector = self._get_selector_from_text(params[0] if params else "")
            # Use single quotes if selector contains double quotes
            if '"' in selector:
                code += f"\nawait page.click('{selector}')"
            else:
                code += f'\nawait page.click("{selector}")'
        
        elif action == "click_element_by_tag":
            tag = params[0] if params else "button"
            text = params[1] if len(params) > 1 else ""
            # Escape quotes properly
            text_escaped = text.replace('"', '\\"')
            code += f'\nawait page.click(\'{tag}:has-text("{text_escaped}")\')'
        
        elif action == "fill_field":
            if len(params) >= 2:
                field = self._get_selector_from_text(params[0])
                value = params[1]
                code += f'\nawait page.fill("{field}", "{value}")'
            else:
                code += f'\n# TODO: Implement fill field for: {step.text}\npass  # Placeholder'
        
        elif action == "assert_title":
            expected = params[0] if params else ""
            code += f'\nassert await page.title() == "{expected}"'
        
        elif action == "assert_visible":
            selector = self._get_selector_from_text(params[0] if params else "")
            # Use single quotes to avoid escaping issues
            code += f"\nassert await page.is_visible('{selector}')"
        
        elif action == "assert_text_present":
            text = params[0] if params else ""
            code += f'\nassert "{text}" in await page.content()'
        
        elif action == "assert_url":
            url = params[0] if params else ""
            code += f'assert page.url == "{url}"\n'
        
        elif action == "assert_url_contains":
            partial = params[0] if params else ""
            code += f'assert "{partial}" in page.url\n'
        
        elif action == "wait_for_element":
            selector = self._get_selector_from_text(params[0] if params else "")
            code += f'await page.wait_for_selector("{selector}")\n'
        
        elif action == "wait_seconds":
            seconds = params[0] if params else "1"
            code += f'await asyncio.sleep({seconds})\n'
        
        elif action == "press_key":
            key = params[0] if params else "Enter"
            code += f'await page.keyboard.press("{key}")\n'
        
        else:
            code += f'\n# TODO: Implement {action} for: {step.text}\npass  # Placeholder'
        
        return code
    
    def _generate_selenium_step_code(self, action: str, params: List[str], step: GherkinStep) -> str:
        """Generate Selenium code for a step"""
        
        code = f"# {step.keyword} {step.text}"
        
        if action == "navigate_to":
            url = params[0] if params else "https://example.com"
            code += f'driver.get("{url}")\n'
        
        elif action == "click_element":
            selector = self._get_selector_from_text(params[0] if params else "")
            code += f'driver.find_element(By.CSS_SELECTOR, "{selector}").click()\n'
        
        elif action == "fill_field":
            if len(params) >= 2:
                field = self._get_selector_from_text(params[0])
                value = params[1]
                code += f'element = driver.find_element(By.CSS_SELECTOR, "{field}")\n'
                code += f'element.clear()\n'
                code += f'element.send_keys("{value}")\n'
        
        elif action == "assert_title":
            expected = params[0] if params else ""
            code += f'assert driver.title == "{expected}"\n'
        
        elif action == "assert_visible":
            selector = self._get_selector_from_text(params[0] if params else "")
            code += f'element = driver.find_element(By.CSS_SELECTOR, "{selector}")\n'
            code += f'assert element.is_displayed()\n'
        
        elif action == "assert_text_present":
            text = params[0] if params else ""
            code += f'assert "{text}" in driver.page_source\n'
        
        elif action == "assert_url":
            url = params[0] if params else ""
            code += f'assert driver.current_url == "{url}"\n'
        
        elif action == "assert_url_contains":
            partial = params[0] if params else ""
            code += f'assert "{partial}" in driver.current_url\n'
        
        elif action == "wait_for_element":
            selector = self._get_selector_from_text(params[0] if params else "")
            code += f'WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "{selector}")))\n'
        
        elif action == "wait_seconds":
            seconds = params[0] if params else "1"
            code += f'time.sleep({seconds})\n'
        
        elif action == "press_key":
            key = params[0] if params else "ENTER"
            code += f'from selenium.webdriver.common.keys import Keys\n'
            code += f'ActionChains(driver).send_keys(Keys.{key.upper()}).perform()\n'
        
        else:
            code += f'\n# TODO: Implement {action} for: {step.text}\npass  # Placeholder'
        
        return code
    
    def _generate_fixtures(self, feature: GherkinFeature) -> str:
        """Generate test fixtures"""
        code = "# Test Fixtures\n\n"
        code += "import pytest\n\n"
        
        # Generate test data fixture
        code += "@pytest.fixture\n"
        code += "def test_data():\n"
        code += '    """Test data for scenarios"""\n'
        code += "    return {\n"
        
        # Extract test data from scenarios
        for scenario in feature.scenarios:
            if scenario.examples:
                code += f'        "{scenario.name}": {json.dumps(scenario.examples, indent=12)},\n'
        
        code += "    }\n\n"
        
        # Generate user fixture
        code += "@pytest.fixture\n"
        code += "def test_user():\n"
        code += '    """Test user credentials"""\n'
        code += "    return {\n"
        code += '        "username": "testuser@example.com",\n'
        code += '        "password": "TestPassword123!",\n'
        code += "    }\n\n"
        
        return code
    
    def _generate_data_providers(self, feature: GherkinFeature) -> str:
        """Generate data providers for data-driven tests"""
        code = "# Data Providers\n\n"
        
        for scenario in feature.scenarios:
            if scenario.is_data_driven():
                provider_name = self._to_variable_name(scenario.name) + "_data"
                code += f"def {provider_name}():\n"
                code += f'    """Data provider for {scenario.name}"""\n'
                code += f"    return {json.dumps(scenario.examples, indent=8)}\n\n"
        
        return code
    
    def _generate_background_setup(self, background_steps: List[GherkinStep]) -> str:
        """Generate setup method from background steps"""
        
        if self.config.browser_framework == BrowserFramework.PLAYWRIGHT:
            code = "    async def setup_method(self, page: Page):\n"
        else:
            code = "    def setup_method(self, driver):\n"
        
        code += '        """Setup from background steps"""\n'
        
        for step in background_steps:
            step_code = self._generate_step_code(step)
            code += "        " + step_code
        
        code += "\n"
        return code
    
    def _generate_page_methods(self, feature: GherkinFeature) -> str:
        """Generate custom page methods from scenarios"""
        code = ""
        
        # Extract unique actions from all scenarios
        unique_actions = set()
        for scenario in feature.scenarios:
            for step in scenario.steps:
                action_type = step.get_action_type()
                if action_type not in ["navigation", "assertion"]:
                    unique_actions.add((action_type, step.text))
        
        # Generate methods for unique actions
        for action_type, step_text in list(unique_actions)[:10]:  # Limit to prevent bloat
            method_name = self._to_variable_name(step_text)[:30]
            
            if self.config.browser_framework == BrowserFramework.PLAYWRIGHT:
                code += f"    async def {method_name}(self):\n"
                code += f'        """Action: {step_text[:50]}"""\n'
                code += f"        # TODO: Implement {action_type}\n"
                code += f"        pass\n\n"
            else:
                code += f"    def {method_name}(self):\n"
                code += f'        """Action: {step_text[:50]}"""\n'
                code += f"        # TODO: Implement {action_type}\n"
                code += f"        pass\n\n"
        
        return code
    
    def _extract_selectors_from_steps(self, feature: GherkinFeature) -> Set[str]:
        """Extract unique selectors from feature steps"""
        selectors = set()
        
        for scenario in feature.scenarios:
            for step in scenario.steps:
                # Extract quoted strings that might be selectors
                for param in step.parameters:
                    if any(char in param for char in ["#", ".", "[", "="]):
                        selectors.add(param)
        
        return selectors
    
    def _get_selector_from_text(self, text: str) -> str:
        """Convert text to a CSS selector"""
        # If it's already a selector, return as-is
        if any(char in text for char in ["#", ".", "[", "="]):
            return text
        
        # Try to create a text-based selector
        if text:
            # Escape quotes properly
            text_escaped = text.replace('"', '\\"')
            return f':has-text("{text_escaped}")'
        
        return "*"
    
    def _get_imports(self) -> str:
        """Get all necessary imports"""
        code = "#!/usr/bin/env python3\n"
        code += '"""\nGenerated test code from Gherkin scenarios\n"""\n\n'
        
        code += self.templates.get_pytest_imports()
        
        if self.config.browser_framework == BrowserFramework.PLAYWRIGHT:
            code += self.templates.get_playwright_imports()
        else:
            code += self.templates.get_selenium_imports()
        
        code += "\n# Configure logging\n"
        code += "logging.basicConfig(level=logging.INFO)\n"
        code += "logger = logging.getLogger(__name__)\n\n"
        
        return code
    
    def _save_generated_code(self, feature_name: str, generated_code: Dict[str, str]):
        """Save generated code to files"""
        
        base_name = self._to_variable_name(feature_name)
        
        for code_type, code in generated_code.items():
            if code_type == "page_object":
                file_name = f"{base_name}_page.py"
            elif code_type == "test_file":
                file_name = f"test_{base_name}.py"
            elif code_type == "fixtures":
                file_name = f"{base_name}_fixtures.py"
            elif code_type == "data_providers":
                file_name = f"{base_name}_data.py"
            else:
                file_name = f"{base_name}_{code_type}.py"
            
            file_path = self.config.output_dir / file_name
            
            with open(file_path, 'w') as f:
                f.write(code)
            
            self.generated_files.append(file_path)
            logger.info(f"Generated: {file_path}")
    
    def _to_class_name(self, text: str) -> str:
        """Convert text to class name (PascalCase)"""
        words = re.sub(r'[^a-zA-Z0-9\s]', ' ', text).split()
        return ''.join(word.capitalize() for word in words)
    
    def _to_variable_name(self, text: str) -> str:
        """Convert text to variable name (snake_case)"""
        text = re.sub(r'[^a-zA-Z0-9]', '_', text.lower())
        text = re.sub(r'_+', '_', text)
        text = text.strip('_')
        
        # Truncate to reasonable length (max 100 chars for variable names)
        if len(text) > 100:
            text = text[:97] + "_tr"  # _tr suffix indicates truncated
        
        if text and text[0].isdigit():
            text = f"var_{text}"
        
        return text or "element"

# ============================================================================
# LLM ENHANCEMENT (Optional)
# ============================================================================

class LLMCodeEnhancer:
    """Optional LLM enhancement for complex scenarios"""
    
    def __init__(self):
        self.llm_available = self._check_llm_availability()
    
    def _check_llm_availability(self) -> bool:
        """Check if LLM is available"""
        try:
            from llm import query_llm
            return True
        except ImportError:
            return False
    
    async def enhance_code(self, code: str, scenario: GherkinScenario) -> str:
        """Enhance generated code using LLM"""
        if not self.llm_available:
            return code
        
        try:
            from llm import query_llm
            
            prompt = f"""
            Improve this generated test code for the scenario: {scenario.name}
            
            Current code:
            {code}
            
            Requirements:
            1. Make the code more robust
            2. Add better error handling
            3. Improve assertions
            4. Add helpful comments
            
            Return only the improved code.
            """
            
            messages = [
                {"role": "system", "content": "You are an expert test automation engineer."},
                {"role": "user", "content": prompt}
            ]
            
            response = await asyncio.to_thread(
                query_llm,
                "openai",
                "gpt-5",
                messages
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.warning(f"LLM enhancement failed: {e}")
            return code

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def generate_tests_from_gherkin(
    feature_file: Union[str, Path],
    elements_file: Optional[Union[str, Path]] = None,
    config: Optional[TestCodeConfig] = None
) -> Dict[str, str]:
    """
    Main function to generate test code from Gherkin
    
    Args:
        feature_file: Path to .feature file
        elements_file: Optional path to elements JSON file
        config: Test generation configuration
    
    Returns:
        Dictionary of generated code files
    """
    
    # Load elements if provided
    elements = None
    if elements_file:
        with open(elements_file, 'r') as f:
            elements = json.load(f)
    
    # Initialize generator
    generator = PythonTestCodeGenerator(config)
    
    # Generate test code
    generated_code = generator.generate_from_feature_file(feature_file, elements)
    
    logger.info(f"Successfully generated {len(generated_code)} code files")
    
    return generated_code

# CLI Interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python python_test_code_generator.py <feature_file> [elements_file]")
        sys.exit(1)
    
    feature_file = sys.argv[1]
    elements_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Run generation
    generated = asyncio.run(
        generate_tests_from_gherkin(feature_file, elements_file)
    )
    
    print(f"\nGenerated files:")
    for file_type, code in generated.items():
        print(f"  - {file_type}: {len(code)} characters")
    
    print("\nTest code generation complete!")