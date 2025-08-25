"""
Test browser integration with platform utils
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent  # ai_apps level
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Use absolute imports
from simple_apps_v2.shared_modules.ui_web_auto_testing_v2.browser import BrowserService

async def test_browser_with_platform_utils():
    """Test browser service with platform utils integration"""
    
    print("Testing Browser Service with Platform Utils Integration")
    print("-" * 60)
    
    try:
        # Create browser service
        browser = BrowserService()
        print("[OK] BrowserService created")
        
        # Start the browser
        await browser.start()
        print("[OK] Browser started successfully")
        
        # Get a page and navigate
        page = await browser.get_page("https://example.com")
        print("[OK] Successfully navigated to https://example.com")
        
        # Take a screenshot to verify it works
        screenshot = await browser.screenshot(page)
        if screenshot:
            print("[OK] Screenshot taken successfully")
        
        # Get page title
        title = await browser.evaluate(page, "document.title")
        print(f"[OK] Page title: {title}")
        
        # Stop the browser
        await browser.stop()
        print("[OK] Browser stopped successfully")
        
        print("\n" + "=" * 60)
        print("SUCCESS: All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_browser_with_platform_utils())
    exit(0 if success else 1)