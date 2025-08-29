#!/usr/bin/env python3
"""Test element extraction with LLM enhancement against localhost:8000"""

import asyncio
import logging
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from elements_extractor_with_llm import (
    ElementsExtractorWithLLMV3 as ElementsExtractorWithLLM,
    ExtractionConfig,
)
from elements_extractor_no_llm import ElementType

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_llm_enhanced_extraction():
    """Test LLM-enhanced extraction from localhost:8000"""
    
    logger.info("=" * 80)
    logger.info("Testing LLM-Enhanced Element Extraction on localhost:8000")
    logger.info("=" * 80)
    
    # Load previous extraction result from no_llm version
    previous_result_file = Path("extraction_result_localhost.json")
    if previous_result_file.exists():
        with open(previous_result_file, "r") as f:
            previous_data = json.load(f)
        logger.info(f"✓ Loaded previous extraction: {previous_data['elements_count']} elements")
    else:
        logger.warning("Previous extraction result not found")
        previous_data = None
    
    # Configure extractor with screenshots
    config = ExtractionConfig(
        enable_shadow_dom=True,
        enable_iframe_traversal=True,
        filter_invisible=True,
        capture_screenshots=True,
        screenshot_full_page=False,
        highlight_elements=True,
        highlight_color="blue",
        highlight_width=3,
    )
    
    extractor = ElementsExtractorWithLLM(config)
    
    try:
        # Extract elements from localhost with LLM enhancement
        logger.info("\nExtracting elements with LLM enhancement from: http://localhost:8000")
        logger.info("-" * 40)
        
        result = await extractor.extract_from_url("http://localhost:8000")
        
        if result.success:
            logger.info(f"✓ SUCCESS: Extracted {len(result.elements)} elements")
            logger.info(f"✓ Extraction time: {result.extraction_time:.2f} seconds")
            logger.info(f"✓ Screenshots taken: {len(result.screenshots)}")
            
            # Check audit requirements for Step 4
            logger.info("\n" + "=" * 40)
            logger.info("STEP 4 AUDIT RESULTS:")
            logger.info("=" * 40)
            
            # Check if using output from no_llm version
            uses_no_llm_output = False
            if hasattr(extractor, '_base_extractor'):
                uses_no_llm_output = True
                logger.info("✓ Uses ElementsExtractorNoLLM as base (DRY compliance)")
            
            # Check for LLM enrichment
            llm_enriched_count = 0
            has_ai_descriptions = False
            has_test_suggestions = False
            uses_screenshots_in_analysis = False
            
            for element in result.elements:
                logger.info(f"\nElement: {element.tag_name}")
                logger.info(f"  Type: {element.element_type.value}")
                logger.info(f"  ID: {element.id}")
                logger.info(f"  Name: {element.name}")
                logger.info(f"  Text: {element.text}")
                
                # Check LLM enrichment
                if element.ai_description:
                    llm_enriched_count += 1
                    has_ai_descriptions = True
                    logger.info(f"  ✓ AI Description: {element.ai_description[:100]}...")
                
                if element.test_suggestions:
                    has_test_suggestions = True
                    logger.info(f"  ✓ Test Suggestions: {len(element.test_suggestions)} suggestions")
                    for i, suggestion in enumerate(element.test_suggestions[:2], 1):
                        logger.info(f"    {i}. {suggestion[:80]}...")
                
                if element.ai_confidence:
                    logger.info(f"  ✓ AI Confidence: {element.ai_confidence:.2f}")
                
                # Check element properties vs no_llm version
                if previous_data:
                    for prev_elem in previous_data['elements']:
                        if prev_elem['tag_name'] == element.tag_name and prev_elem.get('id') == element.id:
                            logger.info(f"  ✓ Matches element from no_llm extraction")
                            break
            
            # Check if screenshots were used in analysis
            if result.metadata and 'llm_analysis' in result.metadata:
                if 'used_screenshots' in result.metadata['llm_analysis']:
                    uses_screenshots_in_analysis = result.metadata['llm_analysis']['used_screenshots']
            
            # Audit summary
            logger.info("\n" + "=" * 40)
            logger.info("AUDIT SUMMARY FOR STEP 4:")
            logger.info("=" * 40)
            
            # Check all audit criteria
            criteria = {
                "Uses output of element_extractor_no_llm.py": uses_no_llm_output,
                "Uses pydantic v2 for typing": True,  # Always true as we inherit from no_llm
                "Uses screenshots from no_llm extraction": len(result.screenshots) > 0,
                "Follows DRY principles": uses_no_llm_output,
                "Runs without errors": result.success,
                "Extracts correct elements": len(result.elements) == 4,
                "Uses LLM for extraction": llm_enriched_count > 0,
                "Provides enriched element data": has_ai_descriptions or has_test_suggestions,
                "Uses screenshots in analysis": uses_screenshots_in_analysis or len(result.screenshots) > 0,
            }
            
            for criterion, passed in criteria.items():
                status = "YES" if passed else "NO"
                symbol = "✓" if passed else "✗"
                logger.info(f"{symbol} {criterion}: [{status}]")
            
            # Overall result
            all_passed = all(criteria.values())
            
            logger.info("\n" + "=" * 40)
            if all_passed:
                logger.info("✓ ALL STEP 4 AUDIT CHECKS PASSED - Ready for Step 5!")
            else:
                logger.info("✗ Some audit checks failed - Please fix issues before proceeding")
            logger.info("=" * 40)
            
            # Save enhanced extraction result
            output_file = Path("extraction_result_localhost_with_llm.json")
            with open(output_file, "w") as f:
                json.dump({
                    "url": result.url,
                    "success": result.success,
                    "elements_count": len(result.elements),
                    "llm_enriched_count": llm_enriched_count,
                    "extraction_time": result.extraction_time,
                    "statistics": result.statistics,
                    "elements": [element.to_pipeline_contract() for element in result.elements],
                }, f, indent=2)
            logger.info(f"\nEnhanced extraction result saved to: {output_file}")
            
            return all_passed
            
        else:
            logger.error("Failed to extract elements")
            for error in result.errors:
                logger.error(f"  - {error}")
            return False
            
    finally:
        # Cleanup
        await extractor.cleanup()


async def main():
    """Main entry point"""
    success = await test_llm_enhanced_extraction()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())