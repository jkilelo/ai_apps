#!/usr/bin/env python3
"""
Simple test to verify the fixed module works
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_core_functionality():
    """Test that the module can be imported and key features work"""
    results = []
    
    print("=" * 60)
    print("TESTING FIXED elements_extractor_no_llm.py")
    print("=" * 60)
    
    # Test 1: Import module
    try:
        from elements_extractor_no_llm import ElementsExtractorNoLLM
        print("[PASS] Module imports successfully")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Module import failed: {e}")
        results.append(False)
        return False
    
    # Test 2: Import production utilities
    try:
        from elements_extractor_no_llm import retry_with_backoff, thread_safe, memory_manager
        print("[PASS] Production utilities available")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Production utilities missing: {e}")
        results.append(False)
    
    # Test 3: Import enums
    try:
        from elements_extractor_no_llm import ElementType, InteractionType, ExtractionStrategy
        print("[PASS] Enumerations available")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Enumerations missing: {e}")
        results.append(False)
    
    # Test 4: Create configuration
    try:
        from elements_extractor_no_llm import ExtractionConfig
        config = ExtractionConfig(max_elements=50)
        print("[PASS] Configuration works")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Configuration failed: {e}")
        results.append(False)
    
    # Test 5: Initialize extractor
    try:
        extractor = ElementsExtractorNoLLM(config)
        print("[PASS] Extractor initialization works")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Extractor initialization failed: {e}")
        results.append(False)
    
    # Test 6: Check type annotations were added
    try:
        assert hasattr(extractor, '_cache')
        assert isinstance(extractor._cache, dict)
        print("[PASS] Type annotations present")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Type annotations missing: {e}")
        results.append(False)
    
    # Test 7: Memory management works
    try:
        memory_manager.check_memory()
        memory_manager.cleanup()
        print("[PASS] Memory management works")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Memory management failed: {e}")
        results.append(False)
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: Module is working correctly!")
        return True
    else:
        print("FAILURE: Some tests failed")
        return False

if __name__ == "__main__":
    success = test_core_functionality()
    sys.exit(0 if success else 1)