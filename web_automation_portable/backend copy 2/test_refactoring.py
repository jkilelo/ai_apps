#!/usr/bin/env python3
"""
Test script to verify DRY refactoring changes
"""

import sys
import traceback

def test_imports():
    """Test all critical imports after refactoring"""
    print("Testing DRY Refactoring Results")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: ElementType from data_types
    try:
        from data_types import ElementType
        assert ElementType.BUTTON.value == "button"
        assert ElementType.LINK.value == "link"
        assert ElementType.TEXT_INPUT.value == "text_input"
        print("[PASS] ElementType imported from data_types")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] ElementType import: {e}")
        tests_failed += 1
    
    # Test 2: browser.py imports
    try:
        from browser import ExtractionResult, ElementData
        print("[PASS] browser.py imports (ExtractionResult, ElementData)")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] browser.py imports: {e}")
        tests_failed += 1
    
    # Test 3: elements_extractor_no_llm.py imports
    try:
        from elements_extractor_no_llm import ExtractionConfig, ExtractionResult
        print("[PASS] elements_extractor_no_llm.py imports")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] elements_extractor_no_llm.py imports: {e}")
        tests_failed += 1
    
    # Test 4: Cross-module compatibility
    try:
        from elements_extractor_with_llm import ElementLLMAnalyzer
        from test_generation_with_llm import generate_tests
        print("[PASS] Cross-module imports working")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Cross-module imports: {e}")
        tests_failed += 1
    
    # Test 5: Verify no duplicate definitions
    try:
        # Check that ElementType is the same object from different imports
        from browser import ElementType as BrowserElementType
        from data_types import ElementType as DataTypesElementType
        assert BrowserElementType is DataTypesElementType
        print("[PASS] ElementType is single source (no duplicates)")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] ElementType consistency: {e}")
        tests_failed += 1
    
    # Test 6: Test instantiation of configs
    try:
        from data_types import DOMExtractionConfig, BrowserExtractionConfig
        dom_config = DOMExtractionConfig()
        browser_config = BrowserExtractionConfig()
        print("[PASS] Config classes instantiate correctly")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Config instantiation: {e}")
        tests_failed += 1
    
    # Test 7: Check that old imports still work (backward compatibility)
    try:
        from elements_extractor_no_llm import ExtractionConfig
        from browser import ExtractionResult
        print("[PASS] Backward compatibility maintained")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Backward compatibility: {e}")
        tests_failed += 1
    
    print("=" * 60)
    print(f"Results: {tests_passed} passed, {tests_failed} failed")
    
    if tests_failed == 0:
        print("\n[SUCCESS] ALL TESTS PASSED - DRY refactoring successful!")
    else:
        print(f"\n[WARNING] {tests_failed} tests failed - review needed")
    
    return tests_failed == 0

def test_functionality():
    """Test basic functionality with refactored code"""
    print("\nFunctional Testing")
    print("=" * 60)
    
    try:
        from elements_extractor_no_llm import ElementsExtractorNoLLM
        from data_types import DOMExtractionConfig
        
        # Create extractor with config
        config = DOMExtractionConfig()
        extractor = ElementsExtractorNoLLM(config)
        print("[PASS] ElementsExtractorNoLLM initialized with DOMExtractionConfig")
        
        # Test ElementType usage
        from data_types import ElementType
        button_type = ElementType.BUTTON
        print(f"[PASS] ElementType.BUTTON = {button_type.value}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Functional test: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import_success = test_imports()
    functional_success = test_functionality()
    
    print("\n" + "=" * 60)
    if import_success and functional_success:
        print("[SUCCESS] DRY REFACTORING VERIFICATION COMPLETE - ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("[WARNING] Some tests failed - review the refactoring")
        sys.exit(1)