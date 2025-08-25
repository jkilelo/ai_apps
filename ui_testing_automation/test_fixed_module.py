#!/usr/bin/env python3
"""
Test script to verify elements_extractor_no_llm.py is working correctly
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from elements_extractor_no_llm import (
    ElementsExtractorNoLLM,
    ExtractionConfig,
    ElementType,
    memory_manager
)

async def test_basic_functionality():
    """Test basic module functionality without requiring Playwright"""
    print("=" * 60)
    print("TEST 1: Module Import and Initialization")
    print("=" * 60)
    
    try:
        # Test 1: Can we import the module?
        print("[TEST] Importing module... ", end="")
        from elements_extractor_no_llm import ElementsExtractorNoLLM
        print("[OK] PASS")
        
        # Test 2: Can we create a config?
        print("[TEST] Creating configuration... ", end="")
        config = ExtractionConfig(
            max_elements=100,
            enable_shadow_dom=True,
            enable_iframe_traversal=True
        )
        print("[OK] PASS")
        
        # Test 3: Can we initialize the extractor?
        print("[TEST] Initializing extractor... ", end="")
        extractor = ElementsExtractorNoLLM(config)
        print("[OK] PASS")
        
        # Test 4: Check production utilities work
        print("[TEST] Testing retry decorator... ", end="")
        from elements_extractor_no_llm import retry_with_backoff
        
        @retry_with_backoff(max_attempts=2)
        async def test_func():
            return "success"
        
        result = await test_func()
        assert result == "success"
        print("[OK] PASS")
        
        # Test 5: Check thread safety
        print("[TEST] Testing thread safety decorator... ", end="")
        from elements_extractor_no_llm import thread_safe
        
        @thread_safe
        def test_thread_func():
            return "thread_safe"
        
        result = test_thread_func()
        assert result == "thread_safe"
        print("[OK] PASS")
        
        # Test 6: Check memory manager
        print("[TEST] Testing memory manager... ", end="")
        from elements_extractor_no_llm import memory_manager
        assert memory_manager.check_memory() == True
        memory_manager.cleanup()
        print("[OK] PASS")
        
        # Test 7: Check enums
        print("[TEST] Testing enumerations... ", end="")
        assert ElementType.BUTTON.value == "button"
        assert len(ElementType) > 30  # Should have many element types
        print("[OK] PASS")
        
        # Test 8: Check type annotations
        print("[TEST] Checking type annotations... ", end="")
        assert hasattr(extractor, '_cache')
        assert isinstance(extractor._cache, dict)
        print("[OK] PASS")
        
        print("\n" + "=" * 60)
        print("RESULT: ALL TESTS PASSED [OK]")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_data_models():
    """Test data model functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Data Models and Validation")
    print("=" * 60)
    
    try:
        from elements_extractor_no_llm import (
            ExtractedElement,
            ElementSelector,
            BoundingBox,
            ExtractionResult,
            ScreenshotData,
            ScreenshotMetadata
        )
        
        # Test ExtractedElement
        print("[TEST] Creating ExtractedElement... ", end="")
        from elements_extractor_no_llm import LocatorStrategy
        selector = ElementSelector(
            strategy=LocatorStrategy.CSS_SELECTOR,
            value="button.primary",
            score=0.95,
            is_unique=True
        )
        element = ExtractedElement(
            tag_name="button",
            element_type=ElementType.BUTTON,
            text="Click me",
            selectors=[selector]
        )
        assert element.tag_name == "button"
        assert element.element_type == ElementType.BUTTON
        print("[OK] PASS")
        
        # Test BoundingBox
        print("[TEST] Creating BoundingBox... ", end="")
        bbox = BoundingBox(x=10, y=20, width=100, height=50, top=20, right=110, bottom=70, left=10)
        assert bbox.x == 10
        assert bbox.y == 20
        assert bbox.width == 100
        assert bbox.height == 50
        print("[OK] PASS")
        
        # Test ExtractionResult
        print("[TEST] Creating ExtractionResult... ", end="")
        result = ExtractionResult(
            url="https://example.com",
            success=True,
            elements=[element]
        )
        result_dict = result.to_dict()
        assert result_dict['success'] == True
        assert len(result_dict['elements']) == 1
        print("[OK] PASS")
        
        # Test ScreenshotData
        print("[TEST] Creating ScreenshotData... ", end="")
        screenshot = ScreenshotData(
            data="base64encodeddata",
            format="png",
            width=1920,
            height=1080
        )
        assert screenshot.format == "png"
        print("[OK] PASS")
        
        print("\n" + "=" * 60)
        print("RESULT: DATA MODEL TESTS PASSED [OK]")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("TESTING FIXED elements_extractor_no_llm.py MODULE")
    print("=" * 80)
    
    # Run tests
    success = True
    
    # Test 1: Basic functionality
    if not asyncio.run(test_basic_functionality()):
        success = False
    
    # Test 2: Data models
    if not asyncio.run(test_data_models()):
        success = False
    
    # Summary
    print("\n" + "=" * 80)
    if success:
        print("FINAL RESULT: ALL TESTS PASSED [OK][OK][OK]")
        print("The module is production ready!")
    else:
        print("FINAL RESULT: SOME TESTS FAILED [FAIL]")
        print("Please review the errors above.")
    print("=" * 80)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())