#!/usr/bin/env python3
"""
Demo script showing Shadow DOM extraction capabilities
Tests the new shadow DOM support in browser.py
"""

import asyncio
import logging
from browser import UltimateStealthBrowser, StealthConfig, StealthLevel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def demo_shadow_dom_extraction():
    """Demonstrate shadow DOM extraction on real websites"""
    
    # Test URLs known to have shadow DOM
    test_sites = [
        {
            "name": "YouTube",
            "url": "https://www.youtube.com",
            "description": "Video player controls use shadow DOM"
        },
        {
            "name": "Chrome Web Store",
            "url": "https://chrome.google.com/webstore",
            "description": "Uses Polymer with extensive shadow DOM"
        },
        {
            "name": "GitHub (logged out)",
            "url": "https://github.com",
            "description": "Some components use shadow DOM"
        }
    ]
    
    # Configure browser with shadow DOM enabled
    config = StealthConfig(
        level=StealthLevel.MAXIMUM,
        headless=False,  # Set to False to see the browser
        enable_shadow_dom_extraction=True,
        shadow_dom_max_depth=10,
        shadow_dom_element_limit=200,
        viewport_width=1920,
        viewport_height=1080
    )
    
    logger.info("=" * 60)
    logger.info("Shadow DOM Extraction Demo")
    logger.info("=" * 60)
    
    async with UltimateStealthBrowser(config) as browser:
        for site in test_sites:
            logger.info(f"\nTesting: {site['name']}")
            logger.info(f"URL: {site['url']}")
            logger.info(f"Description: {site['description']}")
            logger.info("-" * 40)
            
            try:
                # Extract elements
                result = await browser.extract_elements(site['url'])
                
                if result.success:
                    # Count shadow DOM elements
                    shadow_elements = [
                        e for e in result.elements 
                        if hasattr(e, 'is_in_shadow_dom') and e.is_in_shadow_dom
                    ]
                    regular_elements = [
                        e for e in result.elements 
                        if not (hasattr(e, 'is_in_shadow_dom') and e.is_in_shadow_dom)
                    ]
                    
                    logger.info(f"✓ Total elements found: {len(result.elements)}")
                    logger.info(f"  - Regular DOM elements: {len(regular_elements)}")
                    logger.info(f"  - Shadow DOM elements: {len(shadow_elements)}")
                    
                    if shadow_elements:
                        # Show some shadow DOM elements
                        logger.info("\n  Sample Shadow DOM elements:")
                        for i, elem in enumerate(shadow_elements[:5]):
                            depth = elem.shadow_dom_depth if hasattr(elem, 'shadow_dom_depth') else 0
                            host = elem.shadow_host_id if hasattr(elem, 'shadow_host_id') else 'unknown'
                            logger.info(f"    {i+1}. {elem.tag_name} - depth: {depth}, host: {host}")
                            if elem.text_content:
                                logger.info(f"       Text: {elem.text_content[:50]}...")
                    
                    # Show element type distribution
                    if shadow_elements:
                        shadow_tags = {}
                        for elem in shadow_elements:
                            tag = elem.tag_name
                            shadow_tags[tag] = shadow_tags.get(tag, 0) + 1
                        
                        logger.info("\n  Shadow DOM element types:")
                        for tag, count in sorted(shadow_tags.items(), key=lambda x: x[1], reverse=True)[:10]:
                            logger.info(f"    - {tag}: {count}")
                else:
                    logger.error(f"✗ Extraction failed: {result.errors}")
                    
            except Exception as e:
                logger.error(f"✗ Error testing {site['name']}: {e}")
                
            # Small delay between sites
            await asyncio.sleep(2)
    
    logger.info("\n" + "=" * 60)
    logger.info("Demo completed!")
    logger.info("=" * 60)


async def compare_with_without_shadow():
    """Compare extraction with and without shadow DOM"""
    
    test_url = "https://www.youtube.com"
    
    logger.info("=" * 60)
    logger.info("Comparing extraction WITH and WITHOUT shadow DOM")
    logger.info("=" * 60)
    
    # Test WITHOUT shadow DOM
    config_without = StealthConfig(
        level=StealthLevel.MAXIMUM,
        headless=True,
        enable_shadow_dom_extraction=False
    )
    
    async with UltimateStealthBrowser(config_without) as browser:
        result_without = await browser.extract_elements(test_url)
        count_without = len(result_without.elements) if result_without.success else 0
        logger.info(f"\nWithout Shadow DOM: {count_without} elements")
    
    # Test WITH shadow DOM
    config_with = StealthConfig(
        level=StealthLevel.MAXIMUM,
        headless=True,
        enable_shadow_dom_extraction=True,
        shadow_dom_max_depth=10,
        shadow_dom_element_limit=500
    )
    
    async with UltimateStealthBrowser(config_with) as browser:
        result_with = await browser.extract_elements(test_url)
        count_with = len(result_with.elements) if result_with.success else 0
        shadow_count = len([
            e for e in result_with.elements 
            if hasattr(e, 'is_in_shadow_dom') and e.is_in_shadow_dom
        ]) if result_with.success else 0
        
        logger.info(f"With Shadow DOM: {count_with} elements ({shadow_count} from shadow DOM)")
    
    if count_with > count_without:
        improvement = ((count_with - count_without) / count_without) * 100
        logger.info(f"\n✓ Shadow DOM extraction found {improvement:.1f}% more elements!")
    else:
        logger.info("\n✓ No additional shadow DOM elements found (site may not use shadow DOM)")
    
    logger.info("=" * 60)


async def main():
    """Run all demos"""
    
    # Run extraction demo
    await demo_shadow_dom_extraction()
    
    # Run comparison
    logger.info("\n\n")
    await compare_with_without_shadow()


if __name__ == "__main__":
    asyncio.run(main())