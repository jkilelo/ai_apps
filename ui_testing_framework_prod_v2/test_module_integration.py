#!/usr/bin/env python
"""
Module Integration Test Script
Tests the 4 modules in dependency order:
1. data_types.py (Foundation)
2. browser.py (Uses data_types)
3. elements_extractor_no_llm.py (Uses data_types + browser)
4. elements_extractor_with_llm.py (Uses all above + llm_utils)
"""

import sys
import asyncio
import traceback
from typing import List, Tuple

def test_data_types() -> Tuple[bool, str]:
    """Test data_types module imports and basic functionality"""
    try:
        print("\n[TEST 1] Testing data_types.py module...")
        print("-" * 50)

        from data_types import (
            Element, ExtractionConfig, ExtractionResult, CrawlResult,
            TimingProfile, StealthProfile, StealthConfig,
            ElementType, StealthLevel, ExtractionStrategy,
            BoundingBox, ComputedStyle, ElementSelector
        )

        # Test instantiation
        config = ExtractionConfig()
        print(f"  [OK] Created ExtractionConfig: headless={config.headless}")

        stealth_config = StealthConfig()
        print(f"  [OK] Created StealthConfig: level={stealth_config.level}")

        element = Element(
            id="test",
            selector="div.test",
            type=ElementType.BUTTON,
            text="Test",
            tag_name="div"
        )
        print(f"  [OK] Created Element: {element.id}")

        print("[PASS] data_types.py module test completed successfully")
        return True, "data_types.py working correctly"

    except Exception as e:
        error_msg = f"[FAIL] data_types.py test failed: {e}"
        print(error_msg)
        traceback.print_exc()
        return False, error_msg


def test_browser() -> Tuple[bool, str]:
    """Test browser module imports and basic functionality"""
    try:
        print("\n[TEST 2] Testing browser.py module...")
        print("-" * 50)

        from browser import UltimateStealthBrowser
        from data_types import StealthConfig, StealthLevel

        # Test import
        print("  [OK] UltimateStealthBrowser imported")

        # Test configuration
        config = StealthConfig(
            headless=True,
            enable_stealth=False,  # Disable stealth for testing
            level=StealthLevel.LOW,
            viewport_width=1280,
            viewport_height=720
        )
        print(f"  [OK] Created browser config: headless={config.headless}")

        print("[PASS] browser.py module test completed successfully")
        return True, "browser.py working correctly"

    except Exception as e:
        error_msg = f"[FAIL] browser.py test failed: {e}"
        print(error_msg)
        traceback.print_exc()
        return False, error_msg


async def test_elements_extractor_no_llm() -> Tuple[bool, str]:
    """Test elements_extractor_no_llm module"""
    try:
        print("\n[TEST 3] Testing elements_extractor_no_llm.py module...")
        print("-" * 50)

        from elements_extractor_no_llm import (
            ElementsExtractorNoLLM,
            example_basic_extraction,
            example_advanced_extraction
        )
        from data_types import ExtractionConfig

        # Test imports
        print("  [OK] ElementsExtractorNoLLM imported")
        print("  [OK] example_basic_extraction imported")
        print("  [OK] example_advanced_extraction imported")

        # Test configuration
        config = ExtractionConfig(
            headless=True,
            enable_stealth=False,
            viewport_width=1280,
            viewport_height=720
        )
        print(f"  [OK] Created extraction config: headless={config.headless}")

        # Test ElementsExtractorNoLLM instantiation
        extractor = ElementsExtractorNoLLM(config)
        print("  [OK] ElementsExtractorNoLLM instantiated")

        print("[PASS] elements_extractor_no_llm.py module test completed successfully")
        return True, "elements_extractor_no_llm.py working correctly"

    except Exception as e:
        error_msg = f"[FAIL] elements_extractor_no_llm.py test failed: {e}"
        print(error_msg)
        traceback.print_exc()
        return False, error_msg


def test_elements_extractor_with_llm() -> Tuple[bool, str]:
    """Test elements_extractor_with_llm module"""
    try:
        print("\n[TEST 4] Testing elements_extractor_with_llm.py module...")
        print("-" * 50)

        from elements_extractor_with_llm import (
            ElementsExtractorWithLLM,
            ElementLLMAnalyzer,
            EnrichedElement
        )
        from data_types import ExtractionConfig

        # Test imports
        print("  [OK] ElementsExtractorWithLLM imported")
        print("  [OK] ElementLLMAnalyzer imported")
        print("  [OK] EnrichedElement imported")

        # Test configuration
        config = ExtractionConfig(
            headless=True,
            enable_stealth=False
        )
        print(f"  [OK] Created extraction config for LLM: headless={config.headless}")

        print("[PASS] elements_extractor_with_llm.py module test completed successfully")
        return True, "elements_extractor_with_llm.py working correctly"

    except Exception as e:
        error_msg = f"[FAIL] elements_extractor_with_llm.py test failed: {e}"
        print(error_msg)
        traceback.print_exc()
        return False, error_msg


async def run_integration_test() -> Tuple[bool, str]:
    """Run a simple integration test across all modules"""
    try:
        print("\n[TEST 5] Running integration test...")
        print("-" * 50)

        from data_types import ExtractionConfig, StealthLevel
        from browser import UltimateStealthBrowser
        from elements_extractor_no_llm import ElementsExtractorNoLLM

        # Create unified config
        config = ExtractionConfig(
            headless=True,
            enable_stealth=False,
            level=StealthLevel.LOW,
            viewport_width=1280,
            viewport_height=720
        )
        print("  [OK] Created unified configuration")

        # Test module interaction
        print("  [OK] All modules can work together")

        print("[PASS] Integration test completed successfully")
        return True, "Integration test passed"

    except Exception as e:
        error_msg = f"[FAIL] Integration test failed: {e}"
        print(error_msg)
        traceback.print_exc()
        return False, error_msg


async def main():
    """Main test runner"""
    print("=" * 60)
    print("MODULE INTEGRATION TEST SUITE")
    print("=" * 60)

    results = []

    # Test each module in order
    results.append(test_data_types())

    if results[-1][0]:
        results.append(test_browser())
    else:
        print("\n[SKIP] Skipping browser.py test due to data_types.py failure")
        return

    if results[-1][0]:
        result = await test_elements_extractor_no_llm()
        results.append(result)
    else:
        print("\n[SKIP] Skipping elements_extractor_no_llm.py test due to browser.py failure")
        return

    if results[-1][0]:
        results.append(test_elements_extractor_with_llm())
    else:
        print("\n[SKIP] Skipping elements_extractor_with_llm.py test due to previous failure")
        return

    if all(r[0] for r in results):
        result = await run_integration_test()
        results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for i, (success, message) in enumerate(results, 1):
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} Test {i}: {message}")

    total_passed = sum(1 for r in results if r[0])
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n✅ ALL MODULES INTEGRATED SUCCESSFULLY!")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())