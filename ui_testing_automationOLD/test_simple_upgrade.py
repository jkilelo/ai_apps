#!/usr/bin/env python3
"""Simple test to verify upgraded extractors work."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from element_extractor_no_llm import ElementExtractorNoLLM

async def test():
    print("[TEST] Upgraded DOM Extractor")
    print("-" * 40)
    
    extractor = ElementExtractorNoLLM()
    
    try:
        # Test extraction with new features
        result = await extractor.extract_from_url("https://example.com", capture_screenshot=True)
        
        print(f"[OK] Extraction completed")
        print(f"[OK] Elements: {result['element_count']}")
        print(f"[OK] Screenshot: {len(result['screenshot']) if result['screenshot'] else 0} bytes")
        print(f"[OK] Time: {result['extraction_time']:.2f}s")
        
        # Check for enhanced data
        if result['elements']:
            elem = result['elements'][0]
            metadata = elem.metadata
            
            print("\n[ENHANCED DATA]")
            print(f"  Validation: {bool(metadata.get('validation'))}")
            print(f"  ARIA: {bool(metadata.get('aria'))}")
            print(f"  Parent XPath: {bool(metadata.get('parent_xpath'))}")
            print(f"  DOM Depth: {metadata.get('depth_in_dom', 0)}")
            print(f"  Clickable: {metadata.get('is_clickable', False)}")
            
            # Check if we have validation rules
            for e in result['elements']:
                if e.metadata.get('validation'):
                    print(f"\n[VALIDATION FOUND]")
                    print(f"  Element: {e.tag_name}")
                    print(f"  Type: {e.element_type}")
                    print(f"  Rules: {list(e.metadata['validation'].keys())}")
                    break
        
        print("\n[SUCCESS] Upgraded extractor works!")
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await extractor.cleanup()

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)