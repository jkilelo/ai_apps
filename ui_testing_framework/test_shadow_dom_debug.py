#!/usr/bin/env python3
"""
Debug test to understand what's happening with Shadow DOM extraction
"""

import asyncio
import logging
from browser import UltimateStealthBrowser, StealthConfig

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def debug_shadow_dom():
    """Debug shadow DOM extraction to see what's actually happening"""
    
    # Create config with Shadow DOM enabled
    config = StealthConfig(
        enable_shadow_dom_extraction=True,
        shadow_dom_max_depth=5,
        shadow_dom_element_limit=100,
        headless=True,
        stealth_level="basic"
    )
    
    browser = UltimateStealthBrowser(config)
    
    try:
        await browser.initialize()
        
        # Create test page with known shadow DOM structure
        test_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Shadow DOM Test</title></head>
        <body>
            <h1>Regular DOM Content</h1>
            <button id="regular-button">Regular Button</button>
            <div id="shadow-host-1">This will have shadow DOM</div>
            <div id="shadow-host-2">Another shadow host</div>
            
            <script>
                // Create shadow DOM on first host
                const host1 = document.getElementById('shadow-host-1');
                const shadow1 = host1.attachShadow({mode: 'open'});
                shadow1.innerHTML = `
                    <style>button { background: blue; color: white; }</style>
                    <button id="shadow-button-1">Shadow Button 1</button>
                    <input type="text" id="shadow-input" placeholder="Shadow Input" />
                    <a href="#" id="shadow-link">Shadow Link</a>
                `;
                
                // Create shadow DOM on second host
                const host2 = document.getElementById('shadow-host-2');
                const shadow2 = host2.attachShadow({mode: 'open'});
                shadow2.innerHTML = `
                    <button id="shadow-button-2">Shadow Button 2</button>
                    <div id="nested-host">Nested Shadow Host</div>
                `;
                
                // Create nested shadow DOM
                const nestedHost = shadow2.getElementById('nested-host');
                const nestedShadow = nestedHost.attachShadow({mode: 'open'});
                nestedShadow.innerHTML = `
                    <button id="nested-shadow-button">Nested Shadow Button</button>
                `;
                
                console.log('Shadow DOMs created successfully');
                console.log('Host 1 has shadow:', !!host1.shadowRoot);
                console.log('Host 2 has shadow:', !!host2.shadowRoot);
            </script>
        </body>
        </html>
        """
        
        # Navigate to test page
        await browser.page.goto(f"data:text/html,{test_html}")
        
        # Wait a moment for JavaScript to execute
        await asyncio.sleep(0.5)
        
        # Verify shadow roots exist via JavaScript
        shadow_check = await browser.page.evaluate("""
            () => {
                const host1 = document.getElementById('shadow-host-1');
                const host2 = document.getElementById('shadow-host-2');
                
                return {
                    host1_has_shadow: !!host1.shadowRoot,
                    host2_has_shadow: !!host2.shadowRoot,
                    host1_shadow_mode: host1.shadowRoot ? host1.shadowRoot.mode : null,
                    host2_shadow_mode: host2.shadowRoot ? host2.shadowRoot.mode : null,
                    shadow1_button_count: host1.shadowRoot ? 
                        host1.shadowRoot.querySelectorAll('button').length : 0,
                    shadow2_button_count: host2.shadowRoot ? 
                        host2.shadowRoot.querySelectorAll('button').length : 0
                };
            }
        """)
        
        logger.info(f"Shadow DOM verification: {shadow_check}")
        
        # Now test extraction
        logger.info("\n" + "="*60)
        logger.info("Testing element extraction...")
        logger.info("="*60)
        
        # Extract elements from each strategy
        for i, strategy in enumerate(browser.extraction_strategies):
            strategy_name = strategy.__class__.__name__
            logger.info(f"\nStrategy {i+1}: {strategy_name}")
            
            elements = await strategy.extract(browser.page)
            logger.info(f"  Found {len(elements)} elements")
            
            # Analyze elements
            regular_elements = []
            shadow_elements = []
            
            for elem in elements:
                if hasattr(elem, 'is_in_shadow_dom') and elem.is_in_shadow_dom:
                    shadow_elements.append(elem)
                else:
                    regular_elements.append(elem)
            
            logger.info(f"  - Regular DOM: {len(regular_elements)} elements")
            logger.info(f"  - Shadow DOM: {len(shadow_elements)} elements")
            
            # List regular elements
            if regular_elements:
                logger.info("  Regular elements found:")
                for elem in regular_elements[:5]:
                    logger.info(f"    - {elem.tag_name}: {elem.text_content[:30] if elem.text_content else 'no text'}")
            
            # List shadow elements with details
            if shadow_elements:
                logger.info("  Shadow elements found:")
                for elem in shadow_elements:
                    logger.info(f"    - {elem.tag_name} (depth={elem.shadow_dom_depth}, host={elem.shadow_host_id}): {elem.text_content[:30] if elem.text_content else 'no text'}")
            else:
                logger.warning("  ⚠️  No shadow DOM elements found!")
        
        # Manual shadow DOM check
        logger.info("\n" + "="*60)
        logger.info("Manual shadow DOM element check...")
        logger.info("="*60)
        
        manual_check = await browser.page.evaluate("""
            () => {
                const results = [];
                
                // Check shadow host 1
                const host1 = document.getElementById('shadow-host-1');
                if (host1.shadowRoot) {
                    const buttons = host1.shadowRoot.querySelectorAll('button');
                    buttons.forEach(btn => {
                        results.push({
                            tag: 'button',
                            text: btn.textContent,
                            id: btn.id,
                            in_shadow: true,
                            host: 'shadow-host-1'
                        });
                    });
                }
                
                // Check shadow host 2
                const host2 = document.getElementById('shadow-host-2');
                if (host2.shadowRoot) {
                    const buttons = host2.shadowRoot.querySelectorAll('button');
                    buttons.forEach(btn => {
                        results.push({
                            tag: 'button',
                            text: btn.textContent,
                            id: btn.id,
                            in_shadow: true,
                            host: 'shadow-host-2'
                        });
                    });
                    
                    // Check nested shadow
                    const nestedHost = host2.shadowRoot.getElementById('nested-host');
                    if (nestedHost && nestedHost.shadowRoot) {
                        const nestedButtons = nestedHost.shadowRoot.querySelectorAll('button');
                        nestedButtons.forEach(btn => {
                            results.push({
                                tag: 'button',
                                text: btn.textContent,
                                id: btn.id,
                                in_shadow: true,
                                host: 'nested-host',
                                nested: true
                            });
                        });
                    }
                }
                
                return results;
            }
        """)
        
        logger.info(f"Manual check found {len(manual_check)} shadow elements:")
        for elem in manual_check:
            logger.info(f"  - {elem}")
        
    finally:
        await browser.cleanup()
        
    logger.info("\n" + "="*60)
    logger.info("Debug test completed")
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(debug_shadow_dom())