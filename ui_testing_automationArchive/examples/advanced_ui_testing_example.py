"""
Advanced UI Testing Example
Demonstrates the enhanced element extraction with dynamic content handling,
multimodal analysis, and self-healing test generation
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.append('/var/www/ai_apps')

from apps.ui_web_auto_testing.element_extraction.crawler import ProfileCrawler
from apps.ui_web_auto_testing.element_extraction.profiles import ProfileManager
from apps.ui_web_auto_testing.element_extraction.dynamic_content_handler import DynamicContentHandler
from apps.ui_web_auto_testing.element_extraction.multimodal_analyzer import MultimodalElementAnalyzer
from apps.ui_web_auto_testing.test_generation.self_healing_generator import SelfHealingTestGenerator
from playwright.async_api import async_playwright
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_advanced_extraction():
    """Demonstrate advanced element extraction on a dynamic website"""
    
    logger.info("=== Starting Advanced UI Testing Demo ===")
    
    # Initialize components
    crawler = ProfileCrawler()
    profile_manager = ProfileManager()
    dynamic_handler = DynamicContentHandler()
    visual_analyzer = MultimodalElementAnalyzer()
    test_generator = SelfHealingTestGenerator()
    
    # Target website (using a complex SPA)
    target_url = "https://react-shopping-cart-eight.vercel.app/"  # Example React e-commerce site
    
    async with async_playwright() as p:
        # Launch browser with specific settings for dynamic content
        browser = await p.chromium.launch(
            headless=False,  # Set to True for production
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        try:
            logger.info(f"Navigating to {target_url}")
            await page.goto(target_url, wait_until='networkidle')
            
            # Step 1: Initialize dynamic content handler
            logger.info("\n--- Step 1: Dynamic Content Analysis ---")
            await dynamic_handler.initialize(page)
            
            # Wait for dynamic content to stabilize
            await dynamic_handler.wait_for_dynamic_content(page)
            
            # Get dynamic regions summary
            dynamic_summary = dynamic_handler.get_dynamic_regions_summary()
            logger.info(f"Detected framework: {dynamic_summary['framework']}")
            logger.info(f"Found {dynamic_summary['total_regions']} dynamic regions")
            
            for region in dynamic_summary['regions'][:3]:  # Show top 3
                logger.info(f"  - {region['selector']}: {region['type']} "
                          f"(updates {region['update_frequency']:.2f}/sec)")
            
            # Step 2: Visual analysis with multimodal LLM
            logger.info("\n--- Step 2: Visual Analysis ---")
            screenshot = await page.screenshot(full_page=True)
            
            page_context = {
                "url": target_url,
                "framework": dynamic_summary['framework'],
                "title": await page.title()
            }
            
            visual_analysis = await visual_analyzer.analyze_screenshot(
                screenshot,
                page_context,
                include_test_suggestions=True
            )
            
            logger.info(f"Layout type: {visual_analysis.layout_type}")
            logger.info(f"Accessibility score: {visual_analysis.accessibility_score:.2f}")
            logger.info(f"Found {len(visual_analysis.visual_elements)} visual elements")
            
            # Show some detected elements
            for elem in visual_analysis.visual_elements[:5]:
                logger.info(f"  - {elem.element_type.value}: {elem.text_content or 'No text'} "
                          f"(confidence: {elem.confidence:.2f})")
            
            # Step 3: Traditional DOM extraction with enhancements
            logger.info("\n--- Step 3: Enhanced DOM Extraction ---")
            
            # Use QA Automation profile for comprehensive extraction
            profile = profile_manager.get_profile("qa_automation_tester")()
            
            # Initialize crawler
            await crawler.initialize()
            crawler.page = page  # Use existing page
            
            # Extract elements
            dom_elements = []
            element_count = 0
            
            async for element in crawler._extract_elements_from_page(page, profile):
                dom_elements.append(element)
                element_count += 1
                
                if element_count % 10 == 0:
                    logger.info(f"  Extracted {element_count} elements...")
            
            logger.info(f"Total DOM elements extracted: {len(dom_elements)}")
            
            # Step 4: Handle infinite scroll if detected
            scroll_containers = await page.evaluate(dynamic_handler.INFINITE_SCROLL_DETECTION)
            if scroll_containers:
                logger.info("\n--- Step 4: Handling Infinite Scroll ---")
                logger.info(f"Found {len(scroll_containers)} scroll containers")
                
                # Load more content
                new_content = await dynamic_handler.handle_infinite_scroll(page, max_scrolls=3)
                logger.info(f"Loaded {len(new_content)} additional elements via scrolling")
            
            # Step 5: Merge visual and DOM analysis
            logger.info("\n--- Step 5: Merging Visual and DOM Analysis ---")
            
            merged_elements = visual_analyzer.merge_with_dom_elements(
                visual_analysis.visual_elements,
                dom_elements
            )
            
            logger.info(f"Merged analysis: {len(merged_elements)} total elements")
            
            # Count elements with visual enhancements
            visual_enhanced = sum(1 for e in merged_elements if 'visual_analysis' in e)
            logger.info(f"Elements enhanced with visual data: {visual_enhanced}")
            
            # Step 6: Generate self-healing tests
            logger.info("\n--- Step 6: Self-Healing Test Generation ---")
            
            # Create test scenarios based on detected elements
            test_scenarios = [
                {
                    "name": "Add Product to Cart",
                    "description": "Test adding a product to shopping cart",
                    "priority": "high",
                    "tags": ["e-commerce", "critical-path"],
                    "steps": [
                        {
                            "action": "click",
                            "element_id": "product_1",
                            "wait_condition": "visible"
                        },
                        {
                            "action": "click",
                            "element_id": "add_to_cart_btn",
                            "assertions": [
                                {"type": "visible", "target": "cart_count"},
                                {"type": "text", "target": "cart_count", "expected": "1"}
                            ]
                        }
                    ],
                    "expected_results": [
                        "Product is added to cart",
                        "Cart count increases by 1",
                        "Cart total is updated"
                    ]
                }
            ]
            
            # Generate resilient locators for key elements
            key_elements = merged_elements[:10]  # Top 10 elements
            
            for i, element in enumerate(key_elements):
                element['id'] = f'element_{i}'
                element['test_id'] = f'test_elem_{i}'
            
            # Generate self-healing test
            healing_test = test_generator.generate_test_with_healing(
                test_scenarios[0],
                key_elements
            )
            
            logger.info(f"Generated test: {healing_test.test_name}")
            logger.info(f"Test has {len(healing_test.steps)} steps with self-healing locators")
            
            # Show locator strategies for first element
            if healing_test.steps:
                first_locator = healing_test.steps[0].locator
                logger.info(f"\nLocator strategies for first element:")
                logger.info(f"  Primary: {first_locator.primary['strategy']} = "
                          f"{first_locator.primary['value'][:50]}...")
                logger.info(f"  Fallbacks: {len(first_locator.fallbacks)} strategies available")
                
                for fb in first_locator.fallbacks[:3]:
                    logger.info(f"    - {fb['strategy']}: {fb['value'][:50]}...")
            
            # Generate Playwright code
            test_code = test_generator.generate_playwright_test(healing_test)
            
            # Save test code
            output_path = Path("/var/www/ai_apps/generated_tests")
            output_path.mkdir(exist_ok=True)
            
            test_file = output_path / f"{healing_test.test_id}.py"
            test_file.write_text(test_code)
            
            logger.info(f"\nGenerated test saved to: {test_file}")
            
            # Step 7: Accessibility analysis
            logger.info("\n--- Step 7: Accessibility Analysis ---")
            
            accessibility_issues = await visual_analyzer.detect_accessibility_issues(
                screenshot,
                dom_elements
            )
            
            if 'issues' in accessibility_issues:
                logger.info(f"Found {len(accessibility_issues['issues'])} accessibility issues")
                for issue in accessibility_issues['issues'][:3]:
                    logger.info(f"  - {issue}")
            
            # Step 8: Compare states (simulate interaction)
            logger.info("\n--- Step 8: State Comparison ---")
            
            # Take screenshot before action
            before_screenshot = await page.screenshot()
            
            # Perform an action (click first button)
            buttons = await page.query_selector_all('button')
            if buttons:
                await buttons[0].click()
                await page.wait_for_timeout(1000)
                
                # Take screenshot after action
                after_screenshot = await page.screenshot()
                
                # Compare states
                state_changes = await visual_analyzer.compare_screenshots(
                    before_screenshot,
                    after_screenshot,
                    "Clicked first button"
                )
                
                logger.info("State changes detected:")
                for change in state_changes.get('changes_detected', [])[:3]:
                    logger.info(f"  - {change}")
            
            # Summary
            logger.info("\n=== Test Generation Summary ===")
            logger.info(f"✓ Detected {dynamic_summary['framework']} framework")
            logger.info(f"✓ Found {dynamic_summary['total_regions']} dynamic regions")
            logger.info(f"✓ Extracted {len(merged_elements)} total elements")
            logger.info(f"✓ Enhanced {visual_enhanced} elements with visual analysis")
            logger.info(f"✓ Generated {len(healing_test.steps)} self-healing test steps")
            logger.info(f"✓ Identified {len(accessibility_issues.get('issues', []))} accessibility issues")
            
        except Exception as e:
            logger.error(f"Error during testing: {e}", exc_info=True)
            
        finally:
            await browser.close()
    
    logger.info("\n=== Demo Complete ===")


async def test_specific_framework(framework_url: str, framework_name: str):
    """Test a specific framework's demo site"""
    
    logger.info(f"\n=== Testing {framework_name} Application ===")
    
    dynamic_handler = DynamicContentHandler()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(framework_url)
            await dynamic_handler.initialize(page)
            
            # Detect framework
            detected = await dynamic_handler.detect_framework(page)
            logger.info(f"Detected framework: {detected.value}")
            
            # Wait for content
            await dynamic_handler.wait_for_dynamic_content(page)
            
            # Get dynamic regions
            await page.wait_for_timeout(2000)  # Let mutations accumulate
            regions = dynamic_handler.get_dynamic_regions_summary()
            
            logger.info(f"Dynamic regions in {framework_name}:")
            for region in regions['regions']:
                logger.info(f"  - {region['selector']}: {region['type']}")
                
        finally:
            await browser.close()


async def main():
    """Run all examples"""
    
    # Main comprehensive test
    await test_advanced_extraction()
    
    # Test specific frameworks
    framework_tests = [
        ("https://todomvc.com/examples/react/", "React"),
        ("https://todomvc.com/examples/vue/", "Vue"),
        ("https://todomvc.com/examples/angular/", "Angular")
    ]
    
    for url, name in framework_tests:
        try:
            await test_specific_framework(url, name)
        except Exception as e:
            logger.error(f"Failed to test {name}: {e}")


if __name__ == "__main__":
    asyncio.run(main())