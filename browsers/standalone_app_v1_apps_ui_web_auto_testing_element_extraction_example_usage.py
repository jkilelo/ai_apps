#!/usr/bin/env python3
"""
Advanced Web Crawler - Usage Examples

This file demonstrates how to use the advanced web crawler with various configurations
and scenarios for comprehensive web element extraction.
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
from crawler import AdvancedWebCrawler


async def basic_example():
    """Basic crawling example with default settings"""
    print("=== Basic Crawling Example ===")
    
    async with async_playwright() as playwright:
        crawler = AdvancedWebCrawler()
        await crawler.initialize(playwright)
        
        try:
            # Crawl a website
            result = await crawler.crawl_website("https://example.com", max_depth=1, max_pages=5)
            
            print(f"Successfully crawled: {result.title}")
            print(f"Found {len(result.elements)} elements")
            print(f"Crawl duration: {result.crawl_duration:.2f} seconds")
            
            # Save results
            output_path = Path("basic_crawl_results.json")
            with open(output_path, "w") as f:
                json.dump({
                    "url": result.url,
                    "title": result.title,
                    "elements_count": len(result.elements),
                    "page_type": result.page_structure.page_type,
                    "accessibility_score": result.page_structure.accessibility_score,
                    "crawl_stats": result.metadata
                }, f, indent=2)
            
            print(f"Results saved to {output_path}")
            
        finally:
            await crawler.cleanup()


async def stealth_crawling_example():
    """Stealth crawling with anti-detection features"""
    print("\\n=== Stealth Crawling Example ===")
    
    config = {
        "browser": "chromium",
        "headless": True,
        "anti_detection": {
            "randomize_delays": True,
            "min_delay": 1.0,
            "max_delay": 3.0,
            "randomize_viewport": True,
            "rotate_user_agents": True,
            "use_stealth_mode": True,
            "simulate_human_behavior": True,
            "avoid_bot_patterns": True,
            "randomize_mouse_movements": True
        },
        "retry_config": {
            "max_retries": 5,
            "base_delay": 2.0,
            "max_delay": 60.0,
            "backoff_factor": 2.5
        }
    }
    
    async with async_playwright() as playwright:
        crawler = AdvancedWebCrawler(config)
        await crawler.initialize(playwright)
        
        try:
            # Crawl a protected or detection-sensitive website
            result = await crawler.crawl_website("https://httpbin.org/user-agent", max_depth=1, max_pages=1)
            
            print(f"Stealth crawl completed: {result.success}")
            print(f"Elements found: {len(result.elements)}")
            print(f"Retries needed: {result.metadata.get('retries', 0)}")
            print(f"CAPTCHA detected: {result.metadata.get('captcha_detected', 0)}")
            
        except Exception as e:
            print(f"Stealth crawling failed: {e}")
        finally:
            await crawler.cleanup()


async def comprehensive_analysis_example():
    """Comprehensive analysis with AI and ML features"""
    print("\\n=== Comprehensive Analysis Example ===")
    
    config = {
        "browser": "chromium",
        "headless": False,  # Show browser for demo
        "anti_detection": {
            "simulate_human_behavior": True,
            "randomize_delays": True
        }
    }
    
    async with async_playwright() as playwright:
        crawler = AdvancedWebCrawler(config)
        await crawler.initialize(playwright)
        
        try:
            # Crawl a complex website
            result = await crawler.crawl_website("https://github.com", max_depth=2, max_pages=3)
            
            print(f"\\nAnalysis Results for {result.url}:")
            print(f"- Page Type: {result.page_structure.page_type}")
            print(f"- Total Elements: {len(result.elements)}")
            print(f"- Accessibility Score: {result.page_structure.accessibility_score:.2f}")
            print(f"- Has Navigation: {result.page_structure.has_navigation}")
            print(f"- Has Forms: {result.page_structure.has_forms}")
            print(f"- Shadow DOM Elements: {result.metadata.get('shadow_dom_elements', 0)}")
            print(f"- Dynamic Elements: {result.metadata.get('dynamic_elements', 0)}")
            
            # Analyze element types
            element_types = {}
            detection_methods = {}
            
            for element in result.elements:
                element_type = element.element_type.value
                detection_method = element.detection_method.value
                
                element_types[element_type] = element_types.get(element_type, 0) + 1
                detection_methods[detection_method] = detection_methods.get(detection_method, 0) + 1
            
            print("\\nElement Types Found:")
            for elem_type, count in sorted(element_types.items()):
                print(f"  {elem_type}: {count}")
            
            print("\\nDetection Methods Used:")
            for method, count in sorted(detection_methods.items()):
                print(f"  {method}: {count}")
            
            # Show high-confidence semantic detections
            semantic_elements = [e for e in result.elements if e.detection_method.value == "semantic_ai"]
            if semantic_elements:
                print("\\nHigh-Confidence Semantic Detections:")
                for elem in semantic_elements[:5]:  # Show first 5
                    pattern = elem.semantic_analysis.get("pattern_matched", "unknown")
                    confidence = elem.confidence_score
                    print(f"  {elem.element_type.value} ({pattern}): {confidence:.2f} confidence")
            
            # Demonstrate interaction simulation
            print("\\n=== Testing Element Interactions ===")
            interaction_results = await crawler.simulate_advanced_interactions(
                await crawler.context.new_page(), result.elements
            )
            
            print(f"Interaction Tests:")
            print(f"- Total: {interaction_results['total_interactions']}")
            print(f"- Successful: {interaction_results['successful_interactions']}")
            print(f"- Failed: {interaction_results['failed_interactions']}")
            
            # Save comprehensive results
            comprehensive_results = {
                "crawl_summary": {
                    "url": result.url,
                    "title": result.title,
                    "success": result.success,
                    "duration": result.crawl_duration,
                    "elements_count": len(result.elements)
                },
                "page_structure": {
                    "type": result.page_structure.page_type,
                    "accessibility_score": result.page_structure.accessibility_score,
                    "has_navigation": result.page_structure.has_navigation,
                    "has_forms": result.page_structure.has_forms,
                    "responsive_analysis": result.page_structure.responsive_breakpoints
                },
                "element_analysis": {
                    "types_distribution": element_types,
                    "detection_methods": detection_methods,
                    "semantic_detections": len(semantic_elements),
                    "shadow_dom_elements": result.metadata.get('shadow_dom_elements', 0)
                },
                "interaction_testing": interaction_results,
                "crawl_stats": result.metadata
            }
            
            output_path = Path("comprehensive_analysis.json")
            with open(output_path, "w") as f:
                json.dump(comprehensive_results, f, indent=2)
            
            print(f"\\nComprehensive results saved to {output_path}")
            
        finally:
            await crawler.cleanup()


async def element_extraction_showcase():
    """Showcase different element extraction capabilities"""
    print("\\n=== Element Extraction Showcase ===")
    
    async with async_playwright() as playwright:
        crawler = AdvancedWebCrawler()
        await crawler.initialize(playwright)
        
        try:
            # Test on a form-heavy website
            result = await crawler.crawl_website("https://httpbin.org/forms/post", max_depth=1)
            
            print(f"\\nElement Extraction Results:")
            
            for element in result.elements[:10]:  # Show first 10 elements
                print(f"\\n--- Element: {element.element_id} ---")
                print(f"Type: {element.element_type.value}")
                print(f"Tag: {element.tag_name}")
                print(f"Text: {element.text_content[:50]}...")
                print(f"Detection Method: {element.detection_method.value}")
                print(f"Confidence: {element.confidence_score:.2f}")
                
                if element.locators:
                    best_locator = element.locators[0]
                    print(f"Best Locator: {best_locator.strategy.value} = '{best_locator.value}'")
                    print(f"Locator Reliability: {best_locator.reliability_score:.2f}")
                
                if element.interactions:
                    print(f"Possible Interactions: {', '.join(element.interactions[:3])}")
                
                if element.accessibility.get("aria_label"):
                    print(f"ARIA Label: {element.accessibility['aria_label']}")
            
        finally:
            await crawler.cleanup()


async def main():
    """Run all examples"""
    print("Advanced Web Crawler - Usage Examples")
    print("=" * 50)
    
    try:
        await basic_example()
        await stealth_crawling_example()
        await comprehensive_analysis_example()
        await element_extraction_showcase()
        
        print("\\n" + "=" * 50)
        print("All examples completed successfully!")
        print("Check the generated JSON files for detailed results.")
        
    except KeyboardInterrupt:
        print("\\nExamples interrupted by user")
    except Exception as e:
        print(f"\\nError running examples: {e}")


if __name__ == "__main__":
    # Install required browsers if needed
    print("Installing Playwright browsers...")
    import subprocess
    subprocess.run(["playwright", "install", "chromium"], check=False)
    
    # Run examples
    asyncio.run(main())