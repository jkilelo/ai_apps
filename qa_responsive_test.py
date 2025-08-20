"""
Senior QA Engineer - Comprehensive Responsive Testing
Focus: Canvas content area, Y-overflow, viewport utilization
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

async def test_responsive_layout():
    """Test actual viewport usage and overflow issues"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    viewports = [
        {"name": "Mobile", "width": 375, "height": 667},  # iPhone SE
        {"name": "Tablet", "width": 768, "height": 1024},  # iPad
        {"name": "Laptop", "width": 1366, "height": 768},  # Common laptop
        {"name": "Desktop", "width": 1920, "height": 1080}, # Full HD
    ]
    
    pages_to_test = [
        {"name": "Home", "url": "http://localhost:3000"},
        {"name": "DataProfiling", "url": "http://localhost:3000/data-profiling"},
        {"name": "WebAutomation", "url": "http://localhost:3000/web-automation"},
    ]
    
    print("\n" + "="*60)
    print("RESPONSIVE LAYOUT TESTING - SENIOR QA ANALYSIS")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        for viewport in viewports:
            print(f"\n{viewport['name']} ({viewport['width']}x{viewport['height']})")
            print("-" * 40)
            
            context = await browser.new_context(
                viewport={'width': viewport['width'], 'height': viewport['height']}
            )
            page = await context.new_page()
            
            for page_info in pages_to_test:
                await page.goto(page_info['url'], wait_until="networkidle")
                await page.wait_for_timeout(1000)
                
                # Measure actual content vs viewport
                measurements = await page.evaluate("""
                    () => {
                        const body = document.body;
                        const html = document.documentElement;
                        const nav = document.querySelector('nav');
                        const mainContent = document.querySelector('main') || document.querySelector('[role="main"]') || document.querySelector('.min-h-screen');
                        
                        // Get viewport dimensions
                        const viewportHeight = window.innerHeight;
                        const viewportWidth = window.innerWidth;
                        
                        // Get actual content dimensions
                        const scrollHeight = Math.max(
                            body.scrollHeight, body.offsetHeight,
                            html.clientHeight, html.scrollHeight, html.offsetHeight
                        );
                        const scrollWidth = Math.max(
                            body.scrollWidth, body.offsetWidth,
                            html.clientWidth, html.scrollWidth, html.offsetWidth
                        );
                        
                        // Check for overflow
                        const hasYOverflow = scrollHeight > viewportHeight;
                        const hasXOverflow = scrollWidth > viewportWidth;
                        
                        // Calculate wasted space
                        const navHeight = nav ? nav.offsetHeight : 0;
                        const availableContentHeight = viewportHeight - navHeight;
                        
                        // Get main content area dimensions
                        const mainRect = mainContent ? mainContent.getBoundingClientRect() : null;
                        
                        return {
                            viewport: { width: viewportWidth, height: viewportHeight },
                            content: { width: scrollWidth, height: scrollHeight },
                            overflow: { x: hasXOverflow, y: hasYOverflow },
                            navHeight: navHeight,
                            availableContentHeight: availableContentHeight,
                            contentUsage: scrollHeight > 0 ? (viewportHeight / scrollHeight * 100).toFixed(1) : 100,
                            mainContentDimensions: mainRect ? {
                                width: mainRect.width,
                                height: mainRect.height,
                                top: mainRect.top
                            } : null,
                            pixelsOverflow: {
                                y: Math.max(0, scrollHeight - viewportHeight),
                                x: Math.max(0, scrollWidth - viewportWidth)
                            }
                        };
                    }
                """)
                
                # Print analysis
                print(f"\n  {page_info['name']}:")
                print(f"    Nav Height: {measurements['navHeight']}px ({(measurements['navHeight']/viewport['height']*100):.1f}% of viewport)")
                print(f"    Content Height: {measurements['content']['height']}px")
                print(f"    Viewport Usage: {measurements['contentUsage']}%")
                
                if measurements['overflow']['y']:
                    print(f"    WARNING: Y-OVERFLOW: {measurements['pixelsOverflow']['y']}px overflow!")
                else:
                    print(f"    OK: No Y-overflow")
                    
                if measurements['overflow']['x']:
                    print(f"    WARNING: X-OVERFLOW: {measurements['pixelsOverflow']['x']}px overflow!")
                else:
                    print(f"    OK: No X-overflow")
                
                # Take screenshot for visual inspection
                screenshot_name = f"qa_{viewport['name']}_{page_info['name']}_{timestamp}.png"
                await page.screenshot(path=screenshot_name, full_page=False)
                
                # Check specific issues for mobile
                if viewport['width'] < 768:
                    # Check if content is cut off
                    visible_content = await page.evaluate("""
                        () => {
                            const elements = document.querySelectorAll('h1, h2, h3, p, button, a');
                            let cutOffElements = 0;
                            elements.forEach(el => {
                                const rect = el.getBoundingClientRect();
                                if (rect.bottom > window.innerHeight && rect.top < window.innerHeight) {
                                    cutOffElements++;
                                }
                            });
                            return cutOffElements;
                        }
                    """)
                    
                    if visible_content > 0:
                        print(f"    WARNING: {visible_content} elements cut off at viewport bottom")
            
            await context.close()
        
        await browser.close()
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS:")
    print("1. Reduce navigation height to max 48px on mobile, 56px on desktop")
    print("2. Use vh units for main content areas")
    print("3. Implement collapsible sidebars on mobile")
    print("4. Reduce padding/margins by 30-50%")
    print("5. Use scroll containers for overflow content")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_responsive_layout())