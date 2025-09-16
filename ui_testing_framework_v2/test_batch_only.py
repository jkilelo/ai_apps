"""
Quick test for batch extraction fix
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui_testing_framework_v2 import extract_batch

def test_batch():
    """Test batch extraction with fix"""
    print("Testing batch extraction...")
    
    urls = [
        "https://example.com",
        "https://www.wikipedia.org",
        "https://httpbin.org"
    ]
    
    try:
        results = extract_batch(urls, parallel=True, max_workers=3)
        
        for url, elements in results.items():
            print(f"[OK] {url}: {len(elements)} elements")
        
        print(f"\n[SUCCESS] Batch extraction test passed!")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    test_batch()