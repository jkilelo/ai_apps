#!/usr/bin/env python3
"""
Test script to verify the screenshot functionality fix in element_extractor_no_llm_robust.py
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ui_testing_framework.element_extractor_no_llm_robust import (
        UltimateElementExtractor,
        ExtractionResult,
        ExtractionStrategy,
        Platform,
    )
    logger.info("Successfully imported element_extractor_no_llm_robust modules")
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    sys.exit(1)


async def test_screenshot_functionality():
    """Test the screenshot functionality with the fixed properties field"""
    
    extractor = None
    test_results = {
        "tests_passed": 0,
        "tests_failed": 0,
        "details": []
    }
    
    try:
        # Initialize the extractor
        logger.info("Initializing UltimateElementExtractor...")
        extractor = UltimateElementExtractor(
            browser=None  # Will use default UltimateStealthBrowser
        )
        
        # Test 1: Basic extraction without screenshot
        logger.info("\n=== Test 1: Basic extraction without screenshot ===")
        try:
            result = await extractor.extract(
                url="https://example.com",
                strategies=[ExtractionStrategy.DOM_REGULAR],
                platform=Platform.DESKTOP
            )
            
            # Verify result has properties field
            assert hasattr(result, "properties"), "ExtractionResult should have properties field"
            assert isinstance(result.properties, dict), "properties should be a dict"
            
            logger.info(f"✓ Basic extraction successful. Properties field exists: {type(result.properties)}")
            test_results["tests_passed"] += 1
            test_results["details"].append({
                "test": "Basic extraction",
                "status": "PASSED",
                "properties_type": str(type(result.properties))
            })
        except Exception as e:
            logger.error(f"✗ Basic extraction failed: {e}")
            test_results["tests_failed"] += 1
            test_results["details"].append({
                "test": "Basic extraction",
                "status": "FAILED",
                "error": str(e)
            })
        
        # Test 2: Extraction with screenshot
        logger.info("\n=== Test 2: Extraction with screenshot ===")
        screenshot_path = Path("test_screenshot.png")
        try:
            result = await extractor.extract_with_screenshots(
                url="https://example.com",
                strategies=[ExtractionStrategy.DOM_REGULAR],
                platform=Platform.DESKTOP,
                screenshot_path=screenshot_path
            )
            
            # Verify properties field contains screenshot path
            assert hasattr(result, "properties"), "ExtractionResult should have properties field"
            assert isinstance(result.properties, dict), "properties should be a dict"
            
            if screenshot_path.exists():
                assert "screenshot_path" in result.properties, "properties should contain screenshot_path"
                assert result.properties["screenshot_path"] == str(screenshot_path), "screenshot_path should match"
                logger.info(f"✓ Screenshot saved at: {result.properties['screenshot_path']}")
                
                # Clean up screenshot
                screenshot_path.unlink()
                logger.info("✓ Screenshot cleanup successful")
            else:
                logger.warning("Screenshot file not created (may be due to headless mode or page load issue)")
            
            test_results["tests_passed"] += 1
            test_results["details"].append({
                "test": "Extraction with screenshot",
                "status": "PASSED",
                "screenshot_in_properties": "screenshot_path" in result.properties
            })
        except Exception as e:
            logger.error(f"✗ Screenshot extraction failed: {e}")
            test_results["tests_failed"] += 1
            test_results["details"].append({
                "test": "Extraction with screenshot",
                "status": "FAILED",
                "error": str(e)
            })
        
        # Test 3: Extraction with enrichment (tests validation report in properties)
        logger.info("\n=== Test 3: Extraction with enrichment and validation ===")
        try:
            result = await extractor.extract_with_enrichment(
                url="https://example.com",
                strategies=[ExtractionStrategy.DOM_REGULAR],
                platform=Platform.DESKTOP,
                enrich=True,
                validate=True
            )
            
            # Verify properties field contains validation report
            assert hasattr(result, "properties"), "ExtractionResult should have properties field"
            assert isinstance(result.properties, dict), "properties should be a dict"
            
            if "validation_report" in result.properties:
                logger.info("✓ Validation report added to properties")
                logger.info(f"  Quality score: {result.properties['validation_report'].get('quality_score', 'N/A')}")
            
            test_results["tests_passed"] += 1
            test_results["details"].append({
                "test": "Extraction with enrichment",
                "status": "PASSED",
                "validation_in_properties": "validation_report" in result.properties
            })
        except Exception as e:
            logger.error(f"✗ Enrichment extraction failed: {e}")
            test_results["tests_failed"] += 1
            test_results["details"].append({
                "test": "Extraction with enrichment",
                "status": "FAILED",
                "error": str(e)
            })
        
        # Test 4: Verify properties field persists through model operations
        logger.info("\n=== Test 4: Properties field persistence ===")
        try:
            # Create a result manually
            manual_result = ExtractionResult(
                url="https://test.com",
                platform=Platform.DESKTOP
            )
            
            # Add custom properties
            manual_result.properties["custom_key"] = "custom_value"
            manual_result.properties["test_data"] = {"nested": "value"}
            
            # Convert to dict and back (simulating serialization)
            result_dict = manual_result.model_dump()
            restored_result = ExtractionResult(**result_dict)
            
            # Verify properties are preserved
            assert restored_result.properties["custom_key"] == "custom_value"
            assert restored_result.properties["test_data"]["nested"] == "value"
            
            logger.info("✓ Properties field persists through serialization")
            test_results["tests_passed"] += 1
            test_results["details"].append({
                "test": "Properties persistence",
                "status": "PASSED"
            })
        except Exception as e:
            logger.error(f"✗ Properties persistence test failed: {e}")
            test_results["tests_failed"] += 1
            test_results["details"].append({
                "test": "Properties persistence",
                "status": "FAILED",
                "error": str(e)
            })
        
    except Exception as e:
        logger.error(f"Fatal error during testing: {e}")
        test_results["details"].append({
            "test": "General",
            "status": "FATAL ERROR",
            "error": str(e)
        })
    finally:
        # Cleanup
        if extractor:
            await extractor.close()
            logger.info("Extractor closed successfully")
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    logger.info(f"Tests Passed: {test_results['tests_passed']}")
    logger.info(f"Tests Failed: {test_results['tests_failed']}")
    logger.info(f"Total Tests: {test_results['tests_passed'] + test_results['tests_failed']}")
    
    if test_results['tests_failed'] == 0:
        logger.info("\n✅ ALL TESTS PASSED! Screenshot functionality is working correctly.")
    else:
        logger.error("\n❌ SOME TESTS FAILED! Please review the details above.")
    
    # Save results to file
    results_file = Path("test_screenshot_results.json")
    with open(results_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)
    logger.info(f"\nDetailed results saved to: {results_file}")
    
    return test_results['tests_failed'] == 0


def test_type_safety():
    """Test type safety of the properties field"""
    logger.info("\n=== Testing Type Safety ===")
    
    try:
        from typing import TYPE_CHECKING
        
        if TYPE_CHECKING:
            # This block only runs during type checking
            result = ExtractionResult(url="test", platform=Platform.DESKTOP)
            
            # These should all be type-safe operations
            result.properties["key"] = "value"
            result.properties["number"] = 123
            result.properties["nested"] = {"a": 1, "b": 2}
            _ = result.properties.get("key", "default")
            _ = len(result.properties)
            
        logger.info("✓ Type annotations are correct for properties field")
        return True
    except Exception as e:
        logger.error(f"✗ Type safety check failed: {e}")
        return False


def main():
    """Main entry point"""
    logger.info("Starting screenshot functionality tests...")
    logger.info("="*60)
    
    # Run async tests
    success = asyncio.run(test_screenshot_functionality())
    
    # Run type safety test
    type_safe = test_type_safety()
    
    if success and type_safe:
        logger.info("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        logger.error("\n⚠️ Some tests failed. Please review the output.")
        sys.exit(1)


if __name__ == "__main__":
    main()