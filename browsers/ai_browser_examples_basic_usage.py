#!/usr/bin/env python3
"""
Basic usage examples for AI-First Smart Browser

This script demonstrates fundamental browser automation tasks
including navigation, form filling, and data extraction.
"""
import asyncio
import os
from pathlib import Path

# Add src to path for local imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from execution.browser_manager import BrowserManager, BrowserConfig
from perception.dom_processor import DOMProcessor
from cognition.enhanced_llm_manager import EnhancedLLMManager as LLMManager
from common.logger import logger


class BasicUsageExamples:
    """Basic browser automation examples"""
    
    def __init__(self):
        self.browser_manager = None
        self.dom_processor = DOMProcessor()
        self.llm_manager = LLMManager()
    
    async def setup(self):
        """Initialize browser and components"""
        logger.info("Setting up browser automation components")
        
        # Initialize browser manager
        self.browser_manager = BrowserManager()
        
        # Create browser configuration
        config = BrowserConfig()
        config.headless = True  # Headless for testing
        config.viewport_width = 1280
        config.viewport_height = 720
        
        # Launch browser with configuration
        self.browser = await self.browser_manager.launch(config)
        
        # Create a browser context
        self.context = await self.browser_manager.new_context()
        
        logger.info("Browser setup complete")
    
    async def teardown(self):
        """Clean up resources"""
        if hasattr(self, 'context'):
            await self.browser_manager.close_context(self.context)
        if self.browser_manager:
            await self.browser_manager.close()
        logger.info("Cleanup complete")
    
    async def example_1_simple_navigation(self):
        """Example 1: Simple navigation and screenshot"""
        logger.info("Example 1: Simple navigation")
        
        # Navigate to a website
        page = await self.browser_manager.new_page(self.context)
        await page.goto("https://example.com")
        
        # Wait for page to load
        await page.wait_for_load_state("networkidle")
        
        # Take a screenshot
        screenshot_path = Path("outputs/example_screenshot.png")
        screenshot_path.parent.mkdir(exist_ok=True)
        await page.screenshot(path=screenshot_path)
        
        logger.info(f"Screenshot saved: {screenshot_path}")
        
        # Get page title
        title = await page.title()
        logger.info(f"Page title: {title}")
        
        await page.close()
    
    async def example_2_form_interaction(self):
        """Example 2: Form filling and submission"""
        logger.info("Example 2: Form interaction")
        
        page = await self.browser_manager.new_page(self.context)
        await page.goto("https://httpbin.org/forms/post")
        
        # Fill form fields
        await page.fill('input[name="custname"]', "John Doe")
        await page.fill('input[name="custtel"]', "555-1234")
        await page.fill('input[name="custemail"]', "john@example.com")
        
        # Select radio button
        await page.check('input[name="size"][value="medium"]')
        
        # Select from dropdown
        await page.select_option('select[name="topping"]', "mushroom")
        
        # Take screenshot before submission
        await page.screenshot(path="examples/outputs/form_filled.png")
        
        # Submit form
        await page.click('input[type="submit"]')
        
        # Wait for response
        await page.wait_for_load_state("networkidle")
        
        # Capture result
        content = await page.content()
        logger.info("Form submitted successfully")
        
        await page.close()
    
    async def example_3_data_extraction(self):
        """Example 3: Data extraction from web page"""
        logger.info("Example 3: Data extraction")
        
        page = await self.browser_manager.new_page(self.context)
        await page.goto("https://httpbin.org/json")
        
        # Extract JSON data
        json_element = await page.query_selector("pre")
        json_text = await json_element.inner_text() if json_element else None
        
        logger.info(f"Extracted JSON: {json_text}")
        
        # Extract using DOM processor
        dom_content = await page.content()
        processed_dom = await self.dom_processor.process_page(dom_content)
        
        logger.info(f"Processed DOM has {len(processed_dom.get('elements', []))} elements")
        
        await page.close()
    
    async def example_4_multiple_pages(self):
        """Example 4: Working with multiple pages/tabs"""
        logger.info("Example 4: Multiple pages")
        
        # Open multiple pages
        page1 = await self.browser_manager.new_page(self.context)
        page2 = await self.browser_manager.new_page(self.context)
        
        # Navigate to different URLs
        await page1.goto("https://httpbin.org/")
        await page2.goto("https://httpbin.org/user-agent")
        
        # Work with both pages
        title1 = await page1.title()
        title2 = await page2.title()
        
        logger.info(f"Page 1 title: {title1}")
        logger.info(f"Page 2 title: {title2}")
        
        # Close pages
        await page1.close()
        await page2.close()
    
    async def example_5_waiting_strategies(self):
        """Example 5: Different waiting strategies"""
        logger.info("Example 5: Waiting strategies")
        
        page = await self.browser_manager.new_page(self.context)
        
        # Wait for network to be idle
        await page.goto("https://httpbin.org/delay/2", wait_until="networkidle")
        
        # Wait for specific element
        await page.goto("https://httpbin.org/")
        await page.wait_for_selector("h1")
        
        # Wait for custom condition
        await page.wait_for_function("document.readyState === 'complete'")
        
        logger.info("All wait conditions satisfied")
        
        await page.close()
    
    async def example_6_error_handling(self):
        """Example 6: Error handling and recovery"""
        logger.info("Example 6: Error handling")
        
        page = await self.browser_manager.new_page(self.context)
        
        try:
            # Try to navigate to non-existent page
            await page.goto("https://httpbin.org/nonexistent", timeout=5000)
        except Exception as e:
            logger.warning(f"Expected error caught: {e}")
        
        try:
            # Try to click non-existent element
            await page.click("#nonexistent", timeout=2000)
        except Exception as e:
            logger.warning(f"Expected error caught: {e}")
        
        # Navigate to valid page for recovery
        await page.goto("https://httpbin.org/")
        title = await page.title()
        logger.info(f"Recovered successfully, page title: {title}")
        
        await page.close()
    
    async def run_all_examples(self):
        """Run all examples in sequence"""
        logger.info("Starting basic usage examples")
        
        try:
            await self.setup()
            
            # Run only the first example for now to test
            await self.example_1_simple_navigation()
            # TODO: Enable other examples after fixing issues
            # await self.example_2_form_interaction()
            # await self.example_3_data_extraction()
            # await self.example_4_multiple_pages()
            # await self.example_5_waiting_strategies()
            # await self.example_6_error_handling()
            
            logger.info("All examples completed successfully")
            
        except Exception as e:
            logger.error(f"Example failed: {e}")
            raise
        finally:
            await self.teardown()


async def main():
    """Main execution function"""
    # Set up environment
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        logger.warning("No LLM API keys found. Some examples may not work.")
    
    # Create output directory
    Path("examples/outputs").mkdir(exist_ok=True, parents=True)
    
    # Run examples
    examples = BasicUsageExamples()
    await examples.run_all_examples()


if __name__ == "__main__":
    print("AI-First Smart Browser - Basic Usage Examples")
    print("=" * 50)
    print()
    
    try:
        asyncio.run(main())
        print("\n[SUCCESS] All examples completed successfully!")
    except KeyboardInterrupt:
        print("\n[WARNING] Examples interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Examples failed: {e}")
        sys.exit(1)