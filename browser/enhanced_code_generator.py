"""
Enhanced Code Generator with Browser Integration
================================================
This module extends the dynamic test code generator to use the existing
UltimateStealthBrowser infrastructure instead of creating new browser instances.

Key Enhancements:
- Integrates with existing browser infrastructure
- Provides browser context to LLM for proper code generation
- Ensures resource efficiency through browser reuse
- Maintains stealth capabilities across all generated tests
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

from browser.dynamic_test_code_generator import (
    DynamicCodeGenConfig,
    DynamicTestCodeGenerator
)
from browser.browser_integration_adapter import (
    BrowserIntegrationAdapter,
    generate_browser_context_for_llm,
    modify_llm_prompt_for_browser_integration,
    TestGenerationContext
)

logger = logging.getLogger(__name__)


class EnhancedTestCodeGenerator(DynamicTestCodeGenerator):
    """
    Enhanced test code generator that integrates with existing browser infrastructure.
    """
    
    def __init__(self, config: DynamicCodeGenConfig):
        """Initialize with enhanced configuration."""
        super().__init__(config)
        self.browser_adapter = BrowserIntegrationAdapter()
        logger.info("Enhanced generator initialized with browser integration")
    
    async def _generate_base_page(self, extraction_data: Optional[Dict] = None) -> str:
        """Generate base page with browser integration."""
        
        # Get the original base page generation
        original_prompt = self._create_base_page_prompt(extraction_data)
        
        # Add browser integration context
        target_url = extraction_data.get('url', 'https://example.com') if extraction_data else 'https://example.com'
        enhanced_prompt = modify_llm_prompt_for_browser_integration(original_prompt, target_url)
        
        # Generate with enhanced prompt
        code = await self._generate_with_strategy(
            enhanced_prompt,
            "base page with browser integration"
        )
        
        # Ensure proper imports are included
        if "from browser.browser_integration_adapter import" not in code:
            imports = """
import sys
from pathlib import Path

# Add browser directory to path
sys.path.insert(0, r'C:\\Users\\kleiy\\OneDrive\\Desktop\\python-ai-apps\\ai_apps')

from browser.browser_integration_adapter import (
    BrowserIntegrationAdapter,
    PlaywrightCompatibilityLayer
)
"""
            code = imports + "\n\n" + code
        
        return code
    
    def _create_base_page_prompt(self, extraction_data: Optional[Dict] = None) -> str:
        """Create prompt for base page generation with browser integration."""
        
        context = TestGenerationContext(
            extraction_data.get('url', 'https://example.com') if extraction_data else 'https://example.com'
        )
        
        prompt = f"""
Generate a base page class for web automation testing that uses the existing browser infrastructure.

{context.get_imports()}

Requirements:
1. Use BrowserIntegrationAdapter for browser management
2. DO NOT create new browser instances
3. Include methods for common page interactions
4. Use async/await patterns
5. Include proper error handling

The base page should include these methods:
- navigate_to(url): Navigate to a URL using the adapter
- wait_for_element(selector): Wait for element to be visible
- click(selector): Click an element
- fill(selector, value): Fill an input field
- get_text(selector): Get element text
- take_screenshot(name): Take a screenshot
- extract_all_elements(): Use AI-powered element extraction

Example structure:
{context.get_page_object_template()}

Generate a complete, production-ready base page class.
"""
        return prompt
    
    async def _generate_test_file(
        self,
        test_type: str,
        test_cases: List[Dict],
        page_name: str,
        extraction_data: Optional[Dict] = None
    ) -> str:
        """Generate test file with browser integration."""
        
        target_url = extraction_data.get('url', 'https://example.com') if extraction_data else 'https://example.com'
        context = TestGenerationContext(target_url)
        
        # Build enhanced prompt
        prompt = f"""
Generate {test_type} tests for {page_name} using the existing browser infrastructure.

BROWSER INTEGRATION CONTEXT:
{generate_browser_context_for_llm(target_url)}

Required imports:
{context.get_imports()}

Test template to follow:
{context.get_test_template()}

Test cases to implement:
{json.dumps(test_cases, indent=2)}

Requirements:
1. Use BrowserIntegrationAdapter for all browser operations
2. Use async/await patterns with adapter.test_context()
3. DO NOT create new browser instances
4. Include both async and sync versions of tests
5. Use the browser's AI-powered element extraction when beneficial
6. Include proper assertions and error handling
7. Take screenshots on failures

Generate complete, executable test code.
"""
        
        # Generate with enhanced prompt
        code = await self._generate_with_strategy(prompt, f"{test_type} tests")
        
        # Validate and fix imports if needed
        code = self._ensure_browser_imports(code)
        
        return code
    
    def _ensure_browser_imports(self, code: str) -> str:
        """Ensure the generated code has proper browser imports."""
        
        required_imports = [
            "from browser.browser_integration_adapter import BrowserIntegrationAdapter",
            "import asyncio",
            "sys.path.insert(0, r'C:\\Users\\kleiy\\OneDrive\\Desktop\\python-ai-apps\\ai_apps')"
        ]
        
        for imp in required_imports:
            if imp not in code:
                # Add at the beginning
                code = imp + "\n" + code
        
        return code
    
    async def generate_integrated_tests(
        self,
        test_cases_file: str,
        extraction_file: Optional[str] = None,
        target_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate tests with full browser integration.
        
        Args:
            test_cases_file: Path to test cases JSON
            extraction_file: Optional extraction data
            target_url: Optional target URL override
            
        Returns:
            Results dictionary with generated files
        """
        logger.info(f"Generating integrated tests for {target_url or 'extracted URL'}")
        
        # Load test cases
        with open(test_cases_file, 'r') as f:
            test_cases_data = json.load(f)
        
        # Load extraction data if provided
        extraction_data = None
        if extraction_file and Path(extraction_file).exists():
            with open(extraction_file, 'r') as f:
                extraction_data = json.load(f)
        
        # Override URL if provided
        if target_url:
            if extraction_data:
                extraction_data['url'] = target_url
            else:
                extraction_data = {'url': target_url}
        
        # Generate with browser integration
        results = await self.generate_from_test_cases(
            test_cases_file,
            extraction_file
        )
        
        # Add browser adapter file to output
        self._create_browser_adapter_file()
        
        return results
    
    def _create_browser_adapter_file(self):
        """Create a simplified browser adapter in the output directory."""
        
        adapter_content = '''"""
Browser Adapter for Generated Tests
This file provides the bridge to the existing browser infrastructure.
"""

import sys
from pathlib import Path

# Add the browser directory to path
browser_path = Path(r'C:\\Users\\kleiy\\OneDrive\\Desktop\\python-ai-apps\\ai_apps')
if str(browser_path) not in sys.path:
    sys.path.insert(0, str(browser_path))

# Import the actual adapter
try:
    from browser.browser_integration_adapter import (
        BrowserIntegrationAdapter,
        PlaywrightCompatibilityLayer
    )
    BROWSER_AVAILABLE = True
except ImportError:
    print("Warning: Browser integration not available. Using mock.")
    BROWSER_AVAILABLE = False
    
    # Provide mock for testing without the full browser
    class BrowserIntegrationAdapter:
        async def test_context(self, url):
            class MockContext:
                def __aenter__(self):
                    return self
                def __aexit__(self, *args):
                    pass
            return MockContext()

# Export for use in tests
__all__ = ['BrowserIntegrationAdapter', 'PlaywrightCompatibilityLayer', 'BROWSER_AVAILABLE']
'''
        
        # Write to output directory
        output_file = Path(self.config.output_dir) / "browser_adapter.py"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(adapter_content)
        logger.info(f"Created browser adapter at {output_file}")


async def generate_with_browser_integration(
    target_url: str,
    test_cases_file: str,
    output_dir: str = "integrated_tests"
) -> Dict[str, Any]:
    """
    Convenience function to generate tests with browser integration.
    
    Args:
        target_url: The website to test
        test_cases_file: Path to test cases
        output_dir: Where to save generated tests
        
    Returns:
        Generation results
    """
    config = DynamicCodeGenConfig(
        llm_provider="gemini",
        llm_model="gemini-2.5-flash-lite",
        output_dir=output_dir,
        enable_chain_of_thought=True,
        enable_constitutional_ai=True
    )
    
    generator = EnhancedTestCodeGenerator(config)
    
    results = await generator.generate_integrated_tests(
        test_cases_file=test_cases_file,
        target_url=target_url
    )
    
    logger.info(f"Generated {len(results.get('generated_files', []))} files with browser integration")
    
    return results


def create_example_test():
    """Create an example test that demonstrates browser integration."""
    
    example = '''"""
Example Test Using Browser Integration
This demonstrates how generated tests use the existing browser infrastructure.
"""

import asyncio
import pytest
from pathlib import Path
import sys

# Add browser directory to path
sys.path.insert(0, r'C:\\Users\\kleiy\\OneDrive\\Desktop\\python-ai-apps\\ai_apps')

from browser.browser_integration_adapter import BrowserIntegrationAdapter


class TestExampleWithBrowserIntegration:
    """Example test class using the shared browser."""
    
    @pytest.fixture(scope="class")
    async def browser_adapter(self):
        """Provide the browser adapter."""
        adapter = BrowserIntegrationAdapter()
        yield adapter
        # Cleanup handled by adapter
    
    @pytest.mark.asyncio
    async def test_navigation_with_stealth(self, browser_adapter):
        """Test navigation using stealth browser."""
        
        async with browser_adapter.test_context("https://example.com") as (browser, page):
            # The browser has stealth mode enabled
            assert page.url == "https://example.com/"
            
            # Use browser's AI element extraction
            elements = await browser.extract_elements()
            assert len(elements.elements) > 0
            
            # Standard Playwright operations work
            title = await page.title()
            assert "Example" in title
            
            # Take screenshot with stealth browser
            await page.screenshot(path="stealth_test.png")
    
    def test_sync_wrapper(self):
        """Synchronous test wrapper for pytest."""
        adapter = BrowserIntegrationAdapter()
        
        async def async_test():
            async with adapter.test_context("https://example.com") as (browser, page):
                title = await page.title()
                assert "Example" in title
        
        asyncio.run(async_test())


if __name__ == "__main__":
    # Run the example
    asyncio.run(TestExampleWithBrowserIntegration().test_navigation_with_stealth(
        BrowserIntegrationAdapter()
    ))
'''
    
    return example


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate tests with browser integration")
    parser.add_argument("--url", required=True, help="Target website URL")
    parser.add_argument("--test-cases", required=True, help="Path to test cases JSON")
    parser.add_argument("--output", default="integrated_tests", help="Output directory")
    parser.add_argument("--example", action="store_true", help="Generate example test")
    
    args = parser.parse_args()
    
    if args.example:
        example = create_example_test()
        example_file = Path(args.output) / "test_example_integration.py"
        example_file.parent.mkdir(parents=True, exist_ok=True)
        example_file.write_text(example)
        print(f"Created example test at {example_file}")
    else:
        results = asyncio.run(generate_with_browser_integration(
            args.url,
            args.test_cases,
            args.output
        ))
        
        print(f"Generated {len(results.get('generated_files', []))} files")
        print(f"Files saved to {args.output}")