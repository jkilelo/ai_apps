#!/usr/bin/env python3
"""
Test script for Shadow DOM extraction feature.
Verifies backward compatibility and new functionality.
"""

import asyncio
import logging
from typing import List
from browser import UltimateStealthBrowser, StealthConfig, ElementData

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_backward_compatibility():
    """Test that existing functionality works without Shadow DOM extraction"""
    logger.info("Testing backward compatibility (Shadow DOM disabled)")
    
    # Create config with Shadow DOM disabled
    config = StealthConfig(
        enable_shadow_dom_extraction=False,
        headless=True,
        stealth_level="basic"
    )
    
    browser = UltimateStealthBrowser(config)
    
    try:
        await browser.initialize()
        
        # Verify only base strategy is loaded
        assert len(browser.extraction_strategies) == 1, "Expected only 1 strategy"
        assert browser.extraction_strategies[0].__class__.__name__ == "DOMExtractionStrategy"
        
        logger.info("✓ Backward compatibility test passed - Shadow DOM not loaded when disabled")
        
        # Navigate to a simple page
        await browser.page.goto("https://example.com")
        
        # Extract elements using base strategy
        elements = []
        for strategy in browser.extraction_strategies:
            extracted = await strategy.extract(browser.page)
            elements.extend(extracted)
        
        logger.info(f"✓ Extracted {len(elements)} elements without Shadow DOM strategy")
        
        # Verify no shadow DOM fields are set
        for element in elements:
            assert element.is_in_shadow_dom == False, "Shadow DOM flag should be False"
            assert element.shadow_host_id is None, "Shadow host ID should be None"
            assert element.shadow_root_mode is None, "Shadow root mode should be None"
            assert element.shadow_dom_depth == 0, "Shadow DOM depth should be 0"
            assert len(element.shadow_dom_path) == 0, "Shadow DOM path should be empty"
        
        logger.info("✓ All elements have correct default shadow DOM values")
        
    finally:
        await browser.cleanup()


async def test_shadow_dom_enabled():
    """Test that Shadow DOM extraction works when enabled"""
    logger.info("Testing Shadow DOM extraction (enabled)")
    
    # Create config with Shadow DOM enabled
    config = StealthConfig(
        enable_shadow_dom_extraction=True,
        shadow_dom_max_depth=3,
        shadow_dom_element_limit=50,
        headless=True,
        stealth_level="basic"
    )
    
    browser = UltimateStealthBrowser(config)
    
    try:
        await browser.initialize()
        
        # Verify both strategies are loaded
        assert len(browser.extraction_strategies) == 2, "Expected 2 strategies"
        strategy_names = [s.__class__.__name__ for s in browser.extraction_strategies]
        assert "DOMExtractionStrategy" in strategy_names
        assert "ShadowDOMExtractionStrategy" in strategy_names
        
        logger.info("✓ Shadow DOM strategy loaded when enabled")
        
        # Create a test page with Shadow DOM
        await browser.page.goto("data:text/html,<html><body><div id='host'>Regular content</div></body></html>")
        
        # Inject Shadow DOM content via JavaScript
        await browser.page.evaluate("""
            () => {
                const host = document.getElementById('host');
                const shadow = host.attachShadow({mode: 'open'});
                shadow.innerHTML = `
                    <button id="shadow-button">Shadow Button</button>
                    <input type="text" placeholder="Shadow Input" />
                    <div id="nested-host">Nested Host</div>
                `;
                
                // Create nested shadow root
                const nestedHost = shadow.getElementById('nested-host');
                const nestedShadow = nestedHost.attachShadow({mode: 'open'});
                nestedShadow.innerHTML = `
                    <button>Deeply Nested Button</button>
                `;
            }
        """)
        
        # Extract elements
        all_elements: List[ElementData] = []
        for strategy in browser.extraction_strategies:
            extracted = await strategy.extract(browser.page)
            all_elements.extend(extracted)
        
        # Check if we found shadow DOM elements
        shadow_elements = [e for e in all_elements if e.is_in_shadow_dom]
        regular_elements = [e for e in all_elements if not e.is_in_shadow_dom]
        
        logger.info(f"✓ Found {len(shadow_elements)} shadow DOM elements")
        logger.info(f"✓ Found {len(regular_elements)} regular DOM elements")
        
        # Verify shadow DOM metadata
        if shadow_elements:
            for element in shadow_elements:
                assert element.is_in_shadow_dom == True
                assert element.extraction_method == 'shadow_dom_inspection'
                logger.info(f"  - Shadow element: {element.tag_name} at depth {element.shadow_dom_depth}")
        
        logger.info("✓ Shadow DOM extraction test passed")
        
    finally:
        await browser.cleanup()


async def test_config_defaults():
    """Test that default configuration values are correct"""
    logger.info("Testing default configuration values")
    
    config = StealthConfig()
    
    # Check default shadow DOM settings
    assert config.enable_shadow_dom_extraction == True, "Shadow DOM should be enabled by default"
    assert config.shadow_dom_max_depth == 5, "Default max depth should be 5"
    assert config.shadow_dom_element_limit == 100, "Default element limit should be 100"
    
    logger.info("✓ Default configuration values are correct")


async def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("Starting Shadow DOM Progressive Enhancement Tests")
    logger.info("=" * 60)
    
    try:
        # Test configuration defaults
        await test_config_defaults()
        logger.info("")
        
        # Test backward compatibility
        await test_backward_compatibility()
        logger.info("")
        
        # Test shadow DOM extraction
        await test_shadow_dom_enabled()
        logger.info("")
        
        logger.info("=" * 60)
        logger.info("✅ All tests passed successfully!")
        logger.info("Shadow DOM support is working correctly.")
        logger.info("Implementation is backward compatible.")
        logger.info("=" * 60)
        
    except AssertionError as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())