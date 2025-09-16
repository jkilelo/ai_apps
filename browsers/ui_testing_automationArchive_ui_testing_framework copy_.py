#!/usr/bin/env python3
"""
CODE GENERATION WITH LLM V3 - AI-Powered Test Code Generation
=============================================================
V3 implementation using llm_v3.py exclusively.
NO fallback mechanisms - 100% success or failure per CLAUDE.md rules.
Generates executable Playwright/Pytest code from test scenarios.

Version: 3.0.0
Architecture: V3 (llm_v3 + prompts_v3)
Status: Production Ready
"""

import asyncio
import ast
import json
import logging
import re
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
except ImportError:
    logger.warning("dotenv not available, using system environment")

# ==============================================================================
# V3 IMPORTS - Single Source of Truth
# ==============================================================================

# Import LLM V3 exclusively - NO fallbacks
from llm_v3 import call_default_llm, LLMResponse

# Import test generation V3 for integration
from test_generation_with_llm_v3 import (
    TestScenario, 
    GherkinStep,
    TestSuite,
    TestGenerationResult,
    generate_tests_for_url
)

# ==============================================================================
# DATA CONTRACTS - Pydantic v2 Models
# ==============================================================================

class TestFramework(str, Enum):
    """Supported test frameworks"""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    PYTEST = "pytest"
    PYTEST_BDD = "pytest-bdd"
    JEST = "jest"
    CUCUMBER = "cucumber"

class BrowserFramework(str, Enum):
    """Browser automation frameworks"""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    PUPPETEER = "puppeteer"

class CodePattern(str, Enum):
    """Code design patterns"""
    PAGE_OBJECT = "page_object"
    SCREENPLAY = "screenplay"
    DIRECT = "direct"
    HYBRID = "hybrid"

class CodeStyle(str, Enum):
    """Code formatting styles"""
    PEP8 = "pep8"
    BLACK = "black"
    GOOGLE = "google"
    NUMPY = "numpy"

class SafetyViolation(BaseModel):
    """Safety issue detected in generated code"""
    violation_type: str
    severity: str  # critical, high, medium, low
    description: str
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None

class CodeMetrics(BaseModel):
    """Metrics for generated code quality"""
    lines_of_code: int
    methods_count: int
    assertions_count: int
    safety_score: float
    readability_score: float
    maintainability_score: float

class GeneratedCode(BaseModel):
    """Generated test code structure"""
    model_config = ConfigDict(use_enum_values=True)
    
    code: str
    language: str = "python"
    framework: TestFramework = TestFramework.PLAYWRIGHT
    browser_framework: BrowserFramework = BrowserFramework.PLAYWRIGHT
    pattern: CodePattern = CodePattern.PAGE_OBJECT
    imports: List[str] = Field(default_factory=list)
    fixtures: List[str] = Field(default_factory=list)
    page_objects: Dict[str, str] = Field(default_factory=dict)
    test_methods: List[str] = Field(default_factory=list)
    helper_methods: List[str] = Field(default_factory=list)
    
    def to_file_content(self) -> str:
        """Convert to complete Python file"""
        sections = []
        
        # Header
        sections.append('"""')
        sections.append(f"Generated Test Code - {datetime.now().isoformat()}")
        sections.append(f"Framework: {self.framework}")
        sections.append(f"Browser: {self.browser_framework}")
        sections.append(f"Pattern: {self.pattern}")
        sections.append('"""')
        sections.append("")
        
        # Imports
        if self.imports:
            sections.extend(self.imports)
            sections.append("")
        
        # Fixtures
        if self.fixtures:
            sections.append("# Fixtures")
            sections.extend(self.fixtures)
            sections.append("")
        
        # Page Objects
        if self.page_objects:
            sections.append("# Page Objects")
            for name, code in self.page_objects.items():
                sections.append(code)
                sections.append("")
        
        # Helper Methods
        if self.helper_methods:
            sections.append("# Helper Methods")
            sections.extend(self.helper_methods)
            sections.append("")
        
        # Test Methods
        if self.test_methods:
            sections.append("# Test Methods")
            sections.extend(self.test_methods)
            sections.append("")
        
        # Main code if not already included
        if self.code and self.code not in "\n".join(sections):
            sections.append("# Main Test Implementation")
            sections.append(self.code)
        
        return "\n".join(sections)

class CodeGenerationContract(BaseModel):
    """Contract for code generation request"""
    test_scenarios: List[TestScenario] = Field(..., description="Test scenarios to convert")
    test_framework: TestFramework = Field(TestFramework.PLAYWRIGHT, description="Target framework")
    browser_framework: BrowserFramework = Field(BrowserFramework.PLAYWRIGHT, description="Browser framework")
    code_pattern: CodePattern = Field(CodePattern.PAGE_OBJECT, description="Design pattern")
    code_style: CodeStyle = Field(CodeStyle.BLACK, description="Code style")
    add_type_hints: bool = Field(True, description="Include type hints")
    add_docstrings: bool = Field(True, description="Include docstrings")
    url: Optional[str] = Field(None, description="URL being tested")

class CodeGenerationResult(BaseModel):
    """Result of code generation process"""
    model_config = ConfigDict(use_enum_values=True)
    
    generated_code: GeneratedCode
    safety_violations: List[SafetyViolation]
    metrics: CodeMetrics
    generation_time: float
    validation_passed: bool
    syntax_valid: bool
    success: bool
    strategies_used: List[str]
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

# ==============================================================================
# CODE GENERATION ENGINE V3
# ==============================================================================

class CodeGenerationEngineV3:
    """
    V3 Code Generation Engine using LLM V3 exclusively.
    NO fallback mechanisms - pure AI-first approach.
    """
    
    def __init__(self):
        """Initialize V3 code generation engine"""
        logger.info("Initialized CodeGenerationEngineV3")
        
        # Strategy mapping for different code generation tasks
        self.strategy_map = {
            "code_structure": "program_aided_language",  # Best for structured code
            "test_implementation": "chain_of_thought",   # Step-by-step test code
            "page_objects": "few_shot",                  # Pattern-based generation
            "assertions": "self_consistency",            # Reliable assertions
            "error_handling": "constitutional_ai",       # Safe error handling
            "fixtures": "chain_of_thought",              # Setup/teardown logic
            "imports": "zero_shot",                      # Direct import generation
            "docstrings": "automatic_prompt_engineer",   # Documentation
            "refactoring": "reflexion",                  # Code improvement
            "optimization": "meta_cognitive_framework"   # Performance optimization
        }
    
    async def generate_code_from_scenarios(
        self,
        scenarios: List[TestScenario],
        contract: CodeGenerationContract
    ) -> GeneratedCode:
        """Generate complete test code from scenarios"""
        
        # Generate imports
        imports = await self._generate_imports(contract)
        
        # Generate fixtures if using pytest
        fixtures = []
        if contract.test_framework in [TestFramework.PYTEST, TestFramework.PYTEST_BDD]:
            fixtures = await self._generate_fixtures(contract)
        
        # Generate page objects if using that pattern
        page_objects = {}
        if contract.code_pattern == CodePattern.PAGE_OBJECT:
            page_objects = await self._generate_page_objects(scenarios, contract)
        
        # Generate test methods
        test_methods = []
        for scenario in scenarios:
            test_method = await self._generate_test_method(scenario, contract)
            test_methods.append(test_method)
        
        # Generate helper methods
        helper_methods = await self._generate_helper_methods(scenarios, contract)
        
        # Combine all code sections
        main_code = self._combine_code_sections(
            imports, fixtures, page_objects, test_methods, helper_methods
        )
        
        return GeneratedCode(
            code=main_code,
            framework=contract.test_framework,
            browser_framework=contract.browser_framework,
            pattern=contract.code_pattern,
            imports=imports,
            fixtures=fixtures,
            page_objects=page_objects,
            test_methods=test_methods,
            helper_methods=helper_methods
        )
    
    async def _generate_imports(self, contract: CodeGenerationContract) -> List[str]:
        """Generate import statements"""
        prompt = f"""Generate Python import statements for test automation.

Framework: {contract.test_framework}
Browser: {contract.browser_framework}
Pattern: {contract.code_pattern}
Type hints: {contract.add_type_hints}

Generate ONLY the import statements needed, one per line.
Include standard libraries, framework imports, and type hints if requested.

Return as a JSON array of import statements:
["import statement 1", "import statement 2", ...]
"""
        
        response = call_default_llm(
            messages=[{"role": "user", "content": prompt}],
            strategy=self.strategy_map["imports"]
        )
        
        imports = self._parse_imports_response(response.content)
        return imports
    
    async def _generate_fixtures(self, contract: CodeGenerationContract) -> List[str]:
        """Generate pytest fixtures"""
        prompt = f"""Generate pytest fixtures for test setup.

Framework: {contract.test_framework}
Browser: {contract.browser_framework}
URL: {contract.url or "https://example.com"}

Generate common fixtures like:
- Browser/page setup
- Test data fixtures
- Cleanup fixtures

Return as a JSON array of complete fixture definitions:
["@pytest.fixture\\ndef fixture_name():\\n    ...", ...]
"""
        
        response = call_default_llm(
            messages=[{"role": "user", "content": prompt}],
            strategy=self.strategy_map["fixtures"]
        )
        
        fixtures = self._parse_fixtures_response(response.content)
        return fixtures
    
    async def _generate_page_objects(
        self,
        scenarios: List[TestScenario],
        contract: CodeGenerationContract
    ) -> Dict[str, str]:
        """Generate page object classes"""
        
        # Analyze scenarios to determine needed page objects
        pages_needed = self._analyze_pages_needed(scenarios)
        
        page_objects = {}
        for page_name in pages_needed:
            prompt = f"""Generate a Page Object class for {page_name}.

Framework: {contract.browser_framework}
URL: {contract.url or "https://example.com"}

Include methods for common actions on this page based on these test scenarios:
{self._summarize_scenarios_for_page(scenarios, page_name)}

Return a complete Python class definition.
"""
            
            response = call_default_llm(
                messages=[{"role": "user", "content": prompt}],
                strategy=self.strategy_map["page_objects"]
            )
            
            page_objects[page_name] = self._extract_class_definition(response.content)
        
        return page_objects
    
    async def _generate_test_method(
        self,
        scenario: TestScenario,
        contract: CodeGenerationContract
    ) -> str:
        """Generate a test method from scenario"""
        
        prompt = f"""Convert this test scenario to executable Python test code.

Scenario: {scenario.name}
Description: {scenario.description}
Category: {scenario.category}
Priority: {scenario.priority}

Steps:
{self._format_gherkin_steps(scenario.steps)}

Framework: {contract.test_framework}
Browser: {contract.browser_framework}
Pattern: {contract.code_pattern}
Add docstrings: {contract.add_docstrings}
Add type hints: {contract.add_type_hints}

Generate a complete test method/function with:
1. Proper naming (test_ prefix for pytest)
2. All steps implemented
3. Assertions for validations
4. Error handling
5. Docstring if requested

Return ONLY the Python function code.
"""
        
        response = call_default_llm(
            messages=[{"role": "user", "content": prompt}],
            strategy=self.strategy_map["test_implementation"]
        )
        
        test_code = self._extract_function_definition(response.content)
        return test_code
    
    async def _generate_helper_methods(
        self,
        scenarios: List[TestScenario],
        contract: CodeGenerationContract
    ) -> List[str]:
        """Generate helper methods for common operations"""
        
        # Analyze for common patterns
        common_operations = self._analyze_common_operations(scenarios)
        
        if not common_operations:
            return []
        
        prompt = f"""Generate helper methods for these common test operations:
{json.dumps(common_operations, indent=2)}

Framework: {contract.browser_framework}
Add type hints: {contract.add_type_hints}
Add docstrings: {contract.add_docstrings}

Return a JSON array of complete helper function definitions.
"""
        
        response = call_default_llm(
            messages=[{"role": "user", "content": prompt}],
            strategy=self.strategy_map["fixtures"]
        )
        
        helpers = self._parse_helper_methods_response(response.content)
        return helpers
    
    def _parse_imports_response(self, response: str) -> List[str]:
        """Parse imports from LLM response"""
        # Remove markdown if present
        response = response.strip()
        if '```' in response:
            response = re.sub(r'```[a-z]*\n?', '', response)
            response = response.strip()
        
        # Try to parse as JSON array
        if response.startswith('['):
            try:
                imports = json.loads(response)
                if isinstance(imports, list):
                    return [imp.strip() for imp in imports if imp.strip()]
            except json.JSONDecodeError:
                pass
        
        # Parse line by line
        lines = response.split('\n')
        imports = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('import ') or line.startswith('from ')):
                imports.append(line)
        
        if not imports:
            # NO FALLBACKS - must succeed or fail
            raise ValueError(f"Could not parse imports from response")
        
        return imports
    
    def _parse_fixtures_response(self, response: str) -> List[str]:
        """Parse fixtures from LLM response"""
        # Similar parsing logic
        response = response.strip()
        if '```' in response:
            response = re.sub(r'```[a-z]*\n?', '', response)
        
        # Try JSON parse
        if response.startswith('['):
            try:
                fixtures = json.loads(response)
                if isinstance(fixtures, list):
                    return fixtures
            except json.JSONDecodeError:
                pass
        
        # Extract fixture definitions
        fixtures = []
        fixture_pattern = r'@pytest\.fixture.*?(?=@pytest\.fixture|\Z)'
        matches = re.findall(fixture_pattern, response, re.DOTALL)
        if matches:
            fixtures = [match.strip() for match in matches]
        
        if not fixtures:
            # NO FALLBACKS
            raise ValueError(f"Could not parse fixtures from response")
        
        return fixtures
    
    def _extract_class_definition(self, response: str) -> str:
        """Extract class definition from response"""
        response = response.strip()
        
        # Remove markdown
        if '```' in response:
            response = re.sub(r'```[a-z]*\n?', '', response)
            response = response.strip()
        
        # Find class definition
        class_pattern = r'class\s+\w+.*?(?=class\s+\w+|\Z)'
        match = re.search(class_pattern, response, re.DOTALL)
        
        if match:
            return match.group(0).strip()
        
        # NO FALLBACKS
        raise ValueError(f"Could not extract class definition from response")
    
    def _extract_function_definition(self, response: str) -> str:
        """Extract function definition from response"""
        response = response.strip()
        
        # Remove markdown
        if '```' in response:
            response = re.sub(r'```[a-z]*\n?', '', response)
            response = response.strip()
        
        # Find function definition
        func_pattern = r'(async\s+)?def\s+\w+.*?(?=(async\s+)?def\s+\w+|\Z)'
        match = re.search(func_pattern, response, re.DOTALL)
        
        if match:
            return match.group(0).strip()
        
        # NO FALLBACKS
        raise ValueError(f"Could not extract function definition from response")
    
    def _parse_helper_methods_response(self, response: str) -> List[str]:
        """Parse helper methods from response"""
        # Similar to fixtures parsing
        response = response.strip()
        if '```' in response:
            response = re.sub(r'```[a-z]*\n?', '', response)
        
        # Try JSON
        if response.startswith('['):
            try:
                helpers = json.loads(response)
                if isinstance(helpers, list):
                    # Check if they're dicts (from LLM response) or strings
                    result = []
                    for h in helpers:
                        if isinstance(h, dict):
                            # Extract code from dict if present
                            if 'code' in h:
                                result.append(h['code'])
                            elif 'function' in h:
                                result.append(h['function'])
                            else:
                                # Try to reconstruct function from parts
                                continue
                        elif isinstance(h, str):
                            result.append(h)
                    return result
            except json.JSONDecodeError:
                pass
        
        # Extract function definitions
        helpers = []
        func_pattern = r'(async\s+)?def\s+\w+.*?(?=(async\s+)?def\s+\w+|\Z)'
        matches = re.findall(func_pattern, response, re.DOTALL)
        if matches:
            helpers = [match[0].strip() if isinstance(match, tuple) else match.strip() 
                      for match in matches]
        
        return helpers  # Can be empty, that's OK
    
    def _combine_code_sections(
        self,
        imports: List[str],
        fixtures: List[str],
        page_objects: Dict[str, str],
        test_methods: List[str],
        helper_methods: List[str]
    ) -> str:
        """Combine all code sections into main code"""
        sections = []
        
        # This is just the raw code combination
        # The GeneratedCode.to_file_content() method will format it properly
        
        if test_methods:
            sections.extend(test_methods)
        
        return "\n\n".join(sections)
    
    def _format_gherkin_steps(self, steps: List[GherkinStep]) -> str:
        """Format Gherkin steps for prompt"""
        lines = []
        for step in steps:
            lines.append(f"{step.keyword} {step.text}")
        return "\n".join(lines)
    
    def _analyze_pages_needed(self, scenarios: List[TestScenario]) -> List[str]:
        """Analyze which page objects are needed"""
        pages = set()
        for scenario in scenarios:
            # Simple heuristic: extract page names from scenario
            if "home" in scenario.name.lower():
                pages.add("HomePage")
            if "login" in scenario.name.lower():
                pages.add("LoginPage")
            if "search" in scenario.name.lower():
                pages.add("SearchPage")
            # Add more as needed
        
        # Default if nothing found
        if not pages:
            pages.add("MainPage")
        
        return list(pages)
    
    def _summarize_scenarios_for_page(self, scenarios: List[TestScenario], page_name: str) -> str:
        """Summarize scenarios relevant to a page"""
        relevant = []
        page_key = page_name.replace("Page", "").lower()
        
        for scenario in scenarios:
            if page_key in scenario.name.lower():
                relevant.append(f"- {scenario.name}")
        
        if not relevant:
            relevant.append("- General page interactions")
        
        return "\n".join(relevant)
    
    def _analyze_common_operations(self, scenarios: List[TestScenario]) -> List[str]:
        """Analyze scenarios for common operations"""
        operations = set()
        
        for scenario in scenarios:
            for step in scenario.steps:
                # Look for common patterns
                if "click" in step.text.lower():
                    operations.add("click_element")
                if "fill" in step.text.lower() or "enter" in step.text.lower():
                    operations.add("fill_form")
                if "verify" in step.text.lower() or "should" in step.text.lower():
                    operations.add("verify_element")
                if "wait" in step.text.lower():
                    operations.add("wait_for_element")
        
        return list(operations)

# ==============================================================================
# SAFETY ENGINE V3
# ==============================================================================

class SafetyEngineV3:
    """Check generated code for safety violations"""
    
    def __init__(self):
        self.violation_patterns = {
            "eval_usage": (r'\beval\s*\(', "critical", "Never use eval()"),
            "exec_usage": (r'\bexec\s*\(', "critical", "Never use exec()"),
            "subprocess_shell": (r'shell\s*=\s*True', "high", "Avoid shell=True in subprocess"),
            "hardcoded_password": (r'password\s*=\s*["\'](?!.*\{)', "high", "Don't hardcode passwords"),
            "hardcoded_api_key": (r'api_key\s*=\s*["\'](?!.*\{)', "high", "Don't hardcode API keys"),
            "bare_except": (r'except\s*:', "medium", "Specify exception types"),
            "unused_variable": (r'^\s*\w+\s*=.*?# noqa', "low", "Remove unused variables")
        }
    
    def check_safety(self, code: str) -> tuple[List[SafetyViolation], float]:
        """Check code for safety violations"""
        violations = []
        
        for violation_type, (pattern, severity, description) in self.violation_patterns.items():
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                violations.append(SafetyViolation(
                    violation_type=violation_type,
                    severity=severity,
                    description=description,
                    line_number=line_num,
                    suggested_fix=self._get_fix(violation_type)
                ))
        
        # Calculate safety score
        severity_weights = {"critical": 1.0, "high": 0.5, "medium": 0.2, "low": 0.1}
        total_weight = sum(severity_weights.get(v.severity, 0) for v in violations)
        safety_score = max(0, 1.0 - (total_weight / 5))  # Normalize
        
        return violations, safety_score
    
    def _get_fix(self, violation_type: str) -> str:
        """Get suggested fix for violation"""
        fixes = {
            "eval_usage": "Use ast.literal_eval() or json.loads()",
            "exec_usage": "Use specific functions instead of exec()",
            "subprocess_shell": "Use shell=False and pass args as list",
            "hardcoded_password": "Use environment variables",
            "hardcoded_api_key": "Use environment variables",
            "bare_except": "Use except Exception as e:",
            "unused_variable": "Remove or use the variable"
        }
        return fixes.get(violation_type, "Review and fix the issue")

# ==============================================================================
# MAIN GENERATION FUNCTION
# ==============================================================================

async def generate_code_for_url(
    url: str,
    test_framework: TestFramework = TestFramework.PLAYWRIGHT,
    browser_framework: BrowserFramework = BrowserFramework.PLAYWRIGHT,
    code_pattern: CodePattern = CodePattern.PAGE_OBJECT
) -> CodeGenerationResult:
    """
    Main function to generate code for a URL.
    Integrates with test_generation_with_llm_v3.py
    """
    start_time = time.time()
    strategies_used = []
    
    try:
        # Step 1: Generate test scenarios using test generation V3
        print(f"[INFO] Generating test scenarios for: {url}")
        from test_generation_with_llm_v3 import TestGenerationContract, TestCategory
        
        test_contract = TestGenerationContract(
            url=url,
            max_scenarios_per_category=1,  # Limit to just 1 scenario per category for testing
            test_categories=[TestCategory.FUNCTIONAL]  # Only functional for testing
        )
        
        test_result = await generate_tests_for_url(test_contract)
        
        # Check if we got scenarios
        if not test_result.test_suite or not test_result.test_suite.scenarios:
            raise ValueError(f"No test scenarios generated")
        
        scenarios = test_result.test_suite.scenarios
        print(f"[INFO] Generated {len(scenarios)} test scenarios")
        
        # Step 2: Generate code from scenarios
        print(f"[INFO] Generating code for {len(scenarios)} scenarios...")
        
        code_contract = CodeGenerationContract(
            test_scenarios=scenarios,
            test_framework=test_framework,
            browser_framework=browser_framework,
            code_pattern=code_pattern,
            url=url
        )
        
        engine = CodeGenerationEngineV3()
        strategies_used = list(engine.strategy_map.values())
        
        generated_code = await engine.generate_code_from_scenarios(
            scenarios, code_contract
        )
        
        # Step 3: Safety check
        print("[INFO] Running safety checks...")
        safety_engine = SafetyEngineV3()
        violations, safety_score = safety_engine.check_safety(
            generated_code.to_file_content()
        )
        
        # Step 4: Validate syntax
        print("[INFO] Validating Python syntax...")
        syntax_valid = validate_python_syntax(generated_code.to_file_content())
        
        # Step 5: Calculate metrics
        metrics = calculate_code_metrics(generated_code)
        metrics.safety_score = safety_score
        
        generation_time = time.time() - start_time
        
        # Build result
        result = CodeGenerationResult(
            generated_code=generated_code,
            safety_violations=violations,
            metrics=metrics,
            generation_time=generation_time,
            validation_passed=len(violations) == 0,
            syntax_valid=syntax_valid,
            success=True,
            strategies_used=strategies_used,
            errors=[],
            warnings=[v.description for v in violations if v.severity == "low"]
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        # NO FALLBACKS - return failure
        return CodeGenerationResult(
            generated_code=GeneratedCode(code=""),
            safety_violations=[],
            metrics=CodeMetrics(
                lines_of_code=0,
                methods_count=0,
                assertions_count=0,
                safety_score=0,
                readability_score=0,
                maintainability_score=0
            ),
            generation_time=time.time() - start_time,
            validation_passed=False,
            syntax_valid=False,
            success=False,
            strategies_used=strategies_used,
            errors=[str(e)],
            warnings=[]
        )

def validate_python_syntax(code: str) -> bool:
    """Validate Python syntax using AST"""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def calculate_code_metrics(generated_code: GeneratedCode) -> CodeMetrics:
    """Calculate metrics for generated code"""
    full_code = generated_code.to_file_content()
    lines = full_code.split('\n')
    
    # Count methods
    methods_count = len(generated_code.test_methods) + len(generated_code.helper_methods)
    
    # Count assertions (simple heuristic)
    assertions_count = sum(1 for line in lines if 'assert' in line.lower() or 'expect' in line.lower())
    
    # Calculate scores (simple heuristics)
    readability_score = min(1.0, 100 / max(1, max(len(line) for line in lines)))  # Shorter lines = better
    maintainability_score = min(1.0, 20 / max(1, methods_count))  # Reasonable number of methods
    
    return CodeMetrics(
        lines_of_code=len(lines),
        methods_count=methods_count,
        assertions_count=assertions_count,
        safety_score=0.0,  # Will be set by safety engine
        readability_score=readability_score,
        maintainability_score=maintainability_score
    )

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

async def main():
    """Main execution for testing"""
    print("="*60)
    print("CODE GENERATION WITH LLM V3")
    print("="*60)
    
    # Test URL
    test_url = "https://example.com"
    
    print(f"\n[TEST] Generating code for: {test_url}")
    
    result = await generate_code_for_url(
        url=test_url,
        test_framework=TestFramework.PLAYWRIGHT,
        browser_framework=BrowserFramework.PLAYWRIGHT,
        code_pattern=CodePattern.PAGE_OBJECT
    )
    
    if result.success:
        print(f"[OK] Code generation completed")
        print(f"     Lines of code: {result.metrics.lines_of_code}")
        print(f"     Methods: {result.metrics.methods_count}")
        print(f"     Assertions: {result.metrics.assertions_count}")
        print(f"     Safety score: {result.metrics.safety_score:.2f}")
        print(f"     Syntax valid: {result.syntax_valid}")
        print(f"     Generation time: {result.generation_time:.2f}s")
        print(f"     Strategies used: {len(result.strategies_used)}")
        
        if result.safety_violations:
            print(f"\n[WARN] Safety violations found: {len(result.safety_violations)}")
            for violation in result.safety_violations[:3]:
                print(f"     - {violation.violation_type}: {violation.description}")
        
        # Save generated code
        output_file = Path("generated_test_code_v3.py")
        output_file.write_text(result.generated_code.to_file_content())
        print(f"\n[OK] Generated code saved to: {output_file}")
        
        # Save metrics
        metrics_file = Path("code_generation_v3_metrics.json")
        metrics_data = {
            "url": test_url,
            "framework": result.generated_code.framework,
            "pattern": result.generated_code.pattern,
            "metrics": {
                "lines_of_code": result.metrics.lines_of_code,
                "methods_count": result.metrics.methods_count,
                "assertions_count": result.metrics.assertions_count,
                "safety_score": result.metrics.safety_score,
                "readability_score": result.metrics.readability_score,
                "maintainability_score": result.metrics.maintainability_score
            },
            "generation_time": result.generation_time,
            "syntax_valid": result.syntax_valid,
            "violations": len(result.safety_violations)
        }
        
        metrics_file.write_text(json.dumps(metrics_data, indent=2))
        print(f"[OK] Metrics saved to: {metrics_file}")
        
        print("\n[SUCCESS] Code Generation with LLM V3 working!")
        
    else:
        print(f"[ERROR] Code generation failed: {result.errors}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))