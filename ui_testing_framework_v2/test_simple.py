"""
Simple test for v2 architecture with stealth browser
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui_testing_framework_v2 import extract

def test_simple():
    """Test simple extraction with stealth browser"""
    print("Testing v2 architecture with robust stealth browser...")
    print("-" * 60)
    
    try:
        # Test extraction
        url = "https://example.com"
        print(f"Extracting from: {url}")
        
        elements = extract(url)
        
        print(f"[OK] Successfully extracted {len(elements)} elements")
        
        # Show first few elements
        print("\nFirst 3 elements:")
        for element in elements[:3]:
            print(f"  - {element.tag_name}: {element.selector}")
        
        # Show interactive elements
        interactive = [e for e in elements if e.is_interactive]
        print(f"\nInteractive elements: {len(interactive)}")
        
        print("\n[SUCCESS] V2 architecture working with stealth browser!")
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple()