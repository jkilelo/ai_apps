#!/usr/bin/env python3
"""
Simple test of LLM-enhanced browser extraction
"""

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ultimate_stealth_browser_llm_enhanced import UltimateStealthBrowserLLMEnhanced
from ultimate_stealth_browser import StealthConfig, StealthLevel

async def test_simple():
    """Test simple extraction"""
    
    config = StealthConfig(
        level=StealthLevel.MAXIMUM,
        headless=False
    )
    
    test_sites = [
        ("https://example.com", "Example"),
        ("https://www.google.com", "Google"),
    ]
    
    async with UltimateStealthBrowserLLMEnhanced(config) as browser:
        for url, name in test_sites:
            print(f"\nTesting {name} ({url})...")
            
            try:
                page_structure = await browser.extract_elements_for_llm(url)
                
                # Count elements
                total = sum(len(elems) for elems in page_structure.elements_by_category.values())
                
                print(f"Success! Extracted {total} elements")
                print(f"  Page Type: {page_structure.page_type}")
                print(f"  Business Purpose: {page_structure.business_purpose}")
                print(f"  User Journeys: {len(page_structure.user_journeys)}")
                print(f"  Categories: {list(page_structure.elements_by_category.keys())}")
                
                # Save result
                output_file = f"llm_test_{name.lower()}.json"
                with open(output_file, 'w') as f:
                    json.dump(page_structure.model_dump(), f, indent=2, default=str)
                print(f"  Saved to: {output_file}")
                
            except Exception as e:
                print(f"Failed: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple())