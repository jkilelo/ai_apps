"""
Wrapper for element extractor to handle Windows async issues
"""

import asyncio
import sys
import json
from typing import Dict, Any
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Set Windows event loop policy BEFORE importing anything async
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from apps.ui_web_auto_testing_v2.element_extractor import extract_elements_from_url

async def extract_with_proper_loop(url: str, headless: bool = True, analyze: bool = True) -> Dict[str, Any]:
    """
    Extract elements with proper event loop handling for Windows
    """
    try:
        # Create a new event loop for this extraction
        loop = asyncio.get_event_loop()
        
        # Run the extraction
        result = await extract_elements_from_url(
            url=url,
            headless=headless,
            analyze=analyze
        )
        
        return result
        
    except Exception as e:
        # Log the actual error
        print(f"Error in extraction: {e}")
        print(f"Error type: {type(e)}")
        
        # Return error response
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "total_elements": 0,
            "elements": [],
            "elements_by_category": {}
        }

def run_extraction_sync(url: str, headless: bool = True, analyze: bool = True) -> Dict[str, Any]:
    """
    Synchronous wrapper for extraction
    """
    try:
        # Create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the async function
        result = loop.run_until_complete(
            extract_with_proper_loop(url, headless, analyze)
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "total_elements": 0,
            "elements": [],
            "elements_by_category": {}
        }
    finally:
        loop.close()

if __name__ == "__main__":
    # Test the wrapper
    test_url = "https://example.com"
    print(f"Testing extraction for {test_url}...")
    
    result = run_extraction_sync(test_url, headless=True, analyze=False)
    
    if result.get("success") == False:
        print(f"Error: {result.get('error')}")
    else:
        print(f"Extracted {result.get('total_elements', 0)} elements")
        if 'elements_by_category' in result:
            for cat, items in result['elements_by_category'].items():
                print(f"  {cat}: {len(items)} elements")