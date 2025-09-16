#!/usr/bin/env python3
"""
Fixed test for Shadow DOM extraction using a proper HTML file
"""

import asyncio
import logging
import os
from pathlib import Path
from browser import UltimateStealthBrowser, StealthConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_shadow_dom_extraction():
    """Test shadow DOM extraction with a proper HTML file"""
    
    # Get the path to the test HTML file
    test_file = Path(__file__).parent / "test_shadow_dom_page.html"
    test_url = f"file:///{test_file.absolute()}".replace("\\", "/")
    
    logger.info("="*60)
    logger.info("Shadow DOM Extraction Test - Fixed Version")
    logger.info("="*60)
    logger.info(f"Test URL: {test_url}")
    
    # Test with Shadow DOM DISABLED first
    logger.info("\n--- Testing WITHOUT Shadow DOM extraction ---")
    config_without = StealthConfig(
        enable_shadow_dom_extraction=False,
        headless=True,
        stealth_level="basic"
    )
    
    browser_without = UltimateStealthBrowser(config_without)
    try:
        await browser_without.initialize()
        await browser_without.page.goto(test_url)
        await asyncio.sleep(0.5)  # Let JavaScript execute
        
        # Extract elements
        all_elements = []
        for strategy in browser_without.extraction_strategies:
            elements = await strategy.extract(browser_without.page)
            all_elements.extend(elements)
        
        logger.info(f"Without Shadow DOM: Found {len(all_elements)} elements")
        for elem in all_elements[:5]:
            logger.info(f"  - {elem.tag_name}: {elem.text_content[:30] if elem.text_content else 'no text'}")
    finally:
        await browser_without.cleanup()
    
    # Test with Shadow DOM ENABLED
    logger.info("\n--- Testing WITH Shadow DOM extraction ---")
    config_with = StealthConfig(
        enable_shadow_dom_extraction=True,
        shadow_dom_max_depth=5,
        shadow_dom_element_limit=200,
        headless=True,
        stealth_level="basic"
    )
    
    browser_with = UltimateStealthBrowser(config_with)
    try:
        await browser_with.initialize()
        await browser_with.page.goto(test_url)
        await asyncio.sleep(0.5)  # Let JavaScript execute
        
        # Verify shadow roots exist on the page
        verification = await browser_with.page.evaluate("""
            () => {
                const results = {
                    shadowHosts: [],
                    shadowElementCounts: {}
                };
                
                // Find all elements with shadow roots
                document.querySelectorAll('*').forEach(el => {
                    if (el.shadowRoot) {
                        const id = el.id || el.tagName.toLowerCase();
                        results.shadowHosts.push(id);
                        
                        // Count interactive elements in this shadow root
                        const interactiveCount = el.shadowRoot.querySelectorAll(
                            'button, input, textarea, select, a'
                        ).length;
                        results.shadowElementCounts[id] = interactiveCount;
                    }
                });
                
                return results;
            }
        """)
        
        logger.info(f"Page verification:")
        logger.info(f"  Shadow hosts found: {verification['shadowHosts']}")
        logger.info(f"  Shadow element counts: {verification['shadowElementCounts']}")
        
        # Extract elements from all strategies
        all_elements = []
        shadow_elements = []
        regular_elements = []
        
        for strategy in browser_with.extraction_strategies:
            strategy_name = strategy.__class__.__name__
            elements = await strategy.extract(browser_with.page)
            
            logger.info(f"\n  {strategy_name}: Found {len(elements)} elements")
            
            for elem in elements:
                all_elements.append(elem)
                if hasattr(elem, 'is_in_shadow_dom') and elem.is_in_shadow_dom:
                    shadow_elements.append(elem)
                else:
                    regular_elements.append(elem)
        
        logger.info(f"\nWith Shadow DOM enabled:")
        logger.info(f"  Total elements: {len(all_elements)}")
        logger.info(f"  Regular DOM elements: {len(regular_elements)}")
        logger.info(f"  Shadow DOM elements: {len(shadow_elements)}")
        
        # List shadow elements with details
        if shadow_elements:
            logger.info("\nShadow DOM elements found:")
            # Group by depth
            by_depth = {}
            for elem in shadow_elements:
                depth = elem.shadow_dom_depth if hasattr(elem, 'shadow_dom_depth') else 0
                if depth not in by_depth:
                    by_depth[depth] = []
                by_depth[depth].append(elem)
            
            for depth in sorted(by_depth.keys()):
                logger.info(f"\n  Depth {depth}: {len(by_depth[depth])} elements")
                for elem in by_depth[depth][:3]:  # Show first 3 at each depth
                    host = elem.shadow_host_id if hasattr(elem, 'shadow_host_id') else 'unknown'
                    text = elem.text_content[:20] if elem.text_content else elem.id or 'no text'
                    logger.info(f"    - {elem.tag_name} (host: {host}): {text}")
        else:
            logger.warning("  ⚠️ No shadow DOM elements found!")
        
        # Compare counts
        logger.info("\n" + "="*60)
        if shadow_elements:
            improvement = len(all_elements) - len(regular_elements)
            logger.info(f"✅ SUCCESS: Shadow DOM extraction found {improvement} additional elements!")
            logger.info(f"✅ Shadow DOM extraction is working correctly!")
        else:
            logger.error("❌ FAILURE: No shadow DOM elements were extracted!")
            logger.error("The ShadowDOMExtractionStrategy may not be working correctly.")
        
    finally:
        await browser_with.cleanup()
    
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(test_shadow_dom_extraction())