"""
Test script for the new v2 architecture
Tests all major functionality with real websites
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui_testing_framework_v2 import (
    extract,
    extract_batch,
    query,
    stats,
    profiles,
    compare,
    get,  # Alias test
    find,  # Alias test
    info  # Alias test
)


def test_simple_extraction():
    """Test basic extraction"""
    print("\n=== Testing Simple Extraction ===")
    
    # Test with a simple website
    elements = extract("https://example.com")
    print(f"Extracted {len(elements)} elements from example.com")
    
    # Show first few elements
    for element in elements[:3]:
        print(f"  - {element.tag_name}: {element.selector}")
    
    return len(elements) > 0


def test_profile_extraction():
    """Test extraction with different profiles"""
    print("\n=== Testing Profile-Based Extraction ===")
    
    url = "https://www.google.com"
    
    # Test different profiles
    for profile_name in ["qa", "interactive", "general"]:
        elements = extract(url, profile=profile_name)
        print(f"Profile '{profile_name}': {len(elements)} elements")
        
        # Show interactive elements for each profile
        interactive = [e for e in elements if e.is_interactive]
        print(f"  Interactive elements: {len(interactive)}")
    
    return True


def test_batch_extraction():
    """Test batch extraction"""
    print("\n=== Testing Batch Extraction ===")
    
    urls = [
        "https://example.com",
        "https://www.wikipedia.org",
        "https://httpbin.org"
    ]
    
    results = extract_batch(urls, parallel=True, max_workers=3)
    
    for url, elements in results.items():
        print(f"{url}: {len(elements)} elements")
    
    return len(results) == len(urls)


def test_query_functionality():
    """Test querying historical data"""
    print("\n=== Testing Query Functionality ===")
    
    # Query by element type
    buttons = query(element_type="button", limit=10)
    print(f"Found {len(buttons)} button records in history")
    
    # Query by URL
    example_data = query(url="https://example.com", limit=10)
    print(f"Found {len(example_data)} extraction records for example.com")
    
    # Query highly interactive elements
    interactive = query(min_score=0.7, limit=10)
    print(f"Found {len(interactive)} highly interactive elements")
    
    return True


def test_stats_and_profiles():
    """Test statistics and profile listing"""
    print("\n=== Testing Stats and Profiles ===")
    
    # Get system stats
    system_stats = stats()
    print("System Statistics:")
    print(f"  Storage: {json.dumps(system_stats.get('storage', {}), indent=2)}")
    print(f"  Cache: {json.dumps(system_stats.get('cache', {}), indent=2)}")
    
    # List profiles
    available_profiles = profiles()
    print(f"Available profiles: {', '.join(available_profiles)}")
    
    return len(available_profiles) > 0


def test_comparison():
    """Test profile comparison"""
    print("\n=== Testing Profile Comparison ===")
    
    url = "https://example.com"
    
    # Compare general vs interactive profiles
    diff = compare(url, "general", "interactive")
    
    print(f"Comparison for {url}:")
    print(f"  General profile: {diff['profile1_count']} elements")
    print(f"  Interactive profile: {diff['profile2_count']} elements")
    print(f"  Common elements: {diff['common']}")
    print(f"  Unique to general: {diff['unique_to_profile1']}")
    print(f"  Unique to interactive: {diff['unique_to_profile2']}")
    
    return True


def test_aliases():
    """Test API aliases"""
    print("\n=== Testing API Aliases ===")
    
    # Test 'get' alias for extract
    elements = get("https://example.com")
    print(f"'get' alias: {len(elements)} elements")
    
    # Test 'find' alias for query
    results = find(element_type="link", limit=5)
    print(f"'find' alias: {len(results)} results")
    
    # Test 'info' alias for stats
    system_info = info()
    print(f"'info' alias: Got system info with {len(system_info)} categories")
    
    return True


def test_caching():
    """Test caching functionality"""
    print("\n=== Testing Caching ===")
    
    url = "https://example.com"
    
    # First extraction (will cache)
    import time
    start = time.time()
    elements1 = extract(url, cache=True)
    time1 = time.time() - start
    print(f"First extraction: {len(elements1)} elements in {time1:.2f}s")
    
    # Second extraction (should use cache)
    start = time.time()
    elements2 = extract(url, cache=True)
    time2 = time.time() - start
    print(f"Cached extraction: {len(elements2)} elements in {time2:.2f}s")
    
    # Should be much faster
    print(f"Cache speedup: {time1/time2:.1f}x faster")
    
    return len(elements1) == len(elements2)


def test_interactive_only():
    """Test interactive-only filtering"""
    print("\n=== Testing Interactive-Only Filter ===")
    
    url = "https://www.google.com"
    
    # Get all elements
    all_elements = extract(url)
    print(f"All elements: {len(all_elements)}")
    
    # Get only interactive elements
    interactive = extract(url, interactive_only=True)
    print(f"Interactive only: {len(interactive)}")
    
    # Verify all are interactive
    all_interactive = all(e.is_interactive for e in interactive)
    print(f"All elements interactive: {all_interactive}")
    
    return all_interactive


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("UI Testing Framework v2 - Architecture Test Suite")
    print("=" * 60)
    
    tests = [
        ("Simple Extraction", test_simple_extraction),
        ("Profile Extraction", test_profile_extraction),
        ("Batch Extraction", test_batch_extraction),
        ("Query Functionality", test_query_functionality),
        ("Stats and Profiles", test_stats_and_profiles),
        ("Profile Comparison", test_comparison),
        ("API Aliases", test_aliases),
        ("Caching", test_caching),
        ("Interactive Only", test_interactive_only)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, "PASSED" if result else "FAILED"))
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append((name, "ERROR"))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for name, status in results:
        symbol = "[OK]" if status == "PASSED" else "[FAIL]"
        print(f"{symbol} {name}: {status}")
    
    passed = sum(1 for _, status in results if status == "PASSED")
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    # Run all tests
    success = run_all_tests()
    
    if success:
        print("\n[OK] All tests passed! The v2 architecture is working correctly.")
    else:
        print("\n[ERROR] Some tests failed. Please review the output above.")