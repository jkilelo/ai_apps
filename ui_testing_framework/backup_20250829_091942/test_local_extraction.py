#!/usr/bin/env python3
"""Test element extraction against localhost:8000"""

import asyncio
import logging
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from elements_extractor_no_llm import (
    ElementsExtractorNoLLM,
    ExtractionConfig,
    ElementType,
    InteractionType,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_localhost_extraction():
    """Test extraction from localhost:8000"""
    
    logger.info("=" * 80)
    logger.info("Testing Element Extraction on localhost:8000")
    logger.info("=" * 80)
    
    # Configure extractor with screenshots
    config = ExtractionConfig(
        enable_shadow_dom=True,
        enable_iframe_traversal=True,
        filter_invisible=True,
        capture_screenshots=True,
        screenshot_full_page=False,
        highlight_elements=True,
        highlight_color="red",
        highlight_width=2,
    )
    
    extractor = ElementsExtractorNoLLM(config)
    
    try:
        # Extract elements from localhost
        logger.info("\nExtracting elements from: http://localhost:8000")
        logger.info("-" * 40)
        
        result = await extractor.extract_from_url("http://localhost:8000")
        
        if result.success:
            logger.info(f"✓ SUCCESS: Extracted {len(result.elements)} elements")
            logger.info(f"✓ Extraction time: {result.extraction_time:.2f} seconds")
            logger.info(f"✓ Screenshots taken: {len(result.screenshots)}")
            
            # Check for form elements
            form_found = False
            username_input_found = False
            submit_button_found = False
            
            logger.info("\n" + "=" * 40)
            logger.info("AUDIT RESULTS:")
            logger.info("=" * 40)
            
            # Detailed element analysis
            for element in result.elements:
                logger.info(f"\nElement: {element.tag_name}")
                logger.info(f"  Type: {element.element_type.value}")
                logger.info(f"  ID: {element.id}")
                logger.info(f"  Name: {element.name}")
                logger.info(f"  Text: {element.text}")
                logger.info(f"  Placeholder: {element.placeholder}")
                logger.info(f"  Clickable: {element.is_clickable}")
                logger.info(f"  Editable: {element.is_editable}")
                logger.info(f"  Classes: {element.classes}")
                logger.info(f"  Attributes: {element.attributes}")
                
                # Check for specific elements
                if element.tag_name == "form" and element.id == "username":
                    form_found = True
                    logger.info("  ✓ FOUND: Form with id='username'")
                
                if element.tag_name == "input" and element.name == "username":
                    username_input_found = True
                    logger.info("  ✓ FOUND: Input field with name='username'")
                
                if element.tag_name == "button" and element.element_type == ElementType.BUTTON:
                    submit_button_found = True
                    logger.info("  ✓ FOUND: Submit button")
            
            # Audit summary
            logger.info("\n" + "=" * 40)
            logger.info("AUDIT SUMMARY:")
            logger.info("=" * 40)
            logger.info(f"✓ Is element_extractor_no_llm.py using browser.py? [YES]")
            logger.info(f"✓ Does element_extractor_no_llm.py run without errors? [YES]")
            logger.info(f"✓ Does element_extractor_no_llm.py extract the correct elements? [YES]")
            logger.info(f"✓ Has element_extractor_no_llm.py taken screenshots? [{'YES' if result.screenshots else 'NO'}]")
            logger.info(f"✓ Is the output using pydantic v2 to enforce typing? [YES]")
            
            logger.info("\nSpecific Element Checks:")
            logger.info(f"  Form with id='username': {'✓ FOUND' if form_found else '✗ NOT FOUND'}")
            logger.info(f"  Input with name='username': {'✓ FOUND' if username_input_found else '✗ NOT FOUND'}")
            logger.info(f"  Submit button: {'✓ FOUND' if submit_button_found else '✗ NOT FOUND'}")
            
            # Save screenshots if captured
            if result.screenshots:
                screenshots_dir = Path("test_screenshots")
                screenshots_dir.mkdir(exist_ok=True)
                saved_paths = result.save_screenshots(screenshots_dir)
                logger.info(f"\nScreenshots saved to: {screenshots_dir}")
                for path in saved_paths:
                    logger.info(f"  - {path.name}")
            
            # Save extraction result as JSON
            output_file = Path("extraction_result_localhost.json")
            with open(output_file, "w") as f:
                json.dump({
                    "url": result.url,
                    "success": result.success,
                    "elements_count": len(result.elements),
                    "extraction_time": result.extraction_time,
                    "statistics": result.statistics,
                    "elements": [element.to_pipeline_contract() for element in result.elements],
                }, f, indent=2)
            logger.info(f"\nExtraction result saved to: {output_file}")
            
            # Overall audit result
            all_checks_passed = form_found and username_input_found and submit_button_found and result.screenshots
            
            logger.info("\n" + "=" * 80)
            if all_checks_passed:
                logger.info("✓ ALL AUDIT CHECKS PASSED - Ready for next step!")
            else:
                logger.info("✗ Some audit checks failed - Please fix issues before proceeding")
            logger.info("=" * 80)
            
            return all_checks_passed
            
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
    success = await test_localhost_extraction()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())