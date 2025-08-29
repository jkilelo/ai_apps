#!/usr/bin/env python3
"""
ELEMENT EXTRACTOR NO LLM - CLI Enhanced Version
==============================================
Pure DOM-based element extraction with CLI support and Pydantic v2 contracts.
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import format_url_for_filename, save_json, validate_pydantic_output

from pydantic import BaseModel, Field, ConfigDict
from elements_extractor_no_llm import (
    ElementsExtractorNoLLM,
    ExtractionConfig,
    ExtractionResult,
    ExtractedElement,
    ElementType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ElementExtractionOutput(BaseModel):
    """Output contract for element extraction without LLM"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    url: str = Field(..., description="URL that was extracted")
    formatted_url: str = Field(..., description="URL-encoded version for file naming")
    success: bool = Field(..., description="Whether extraction succeeded")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    elements_count: int = Field(..., description="Number of elements extracted")
    elements: List[Dict[str, Any]] = Field(..., description="Extracted elements")
    screenshots: List[Dict[str, Any]] = Field(default_factory=list, description="Screenshots taken")
    extraction_time: float = Field(..., description="Time taken for extraction")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    
    def save_to_file(self, filepath: Path) -> None:
        """Save output to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved extraction output to: {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'ElementExtractionOutput':
        """Load output from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)


async def extract_elements(url: str, output_dir: Path = None) -> ElementExtractionOutput:
    """
    Extract elements from URL without LLM
    
    Args:
        url: URL to extract from
        output_dir: Directory to save output (defaults to current dir)
    
    Returns:
        ElementExtractionOutput with extraction results
    """
    if output_dir is None:
        output_dir = Path.cwd()
    
    # Configure extraction
    config = ExtractionConfig(
        enable_shadow_dom=True,
        enable_iframe_traversal=True,
        filter_invisible=True,
        capture_screenshots=True,
        screenshot_full_page=False,
        highlight_elements=True,
        highlight_color="red",
        highlight_width=2,
        max_elements=100
    )
    
    # Initialize extractor
    extractor = ElementsExtractorNoLLM(config)
    
    try:
        logger.info(f"Extracting elements from: {url}")
        
        # Extract elements
        result = await extractor.extract_from_url(url)
        
        # Create output contract with new naming convention
        formatted_url = format_url_for_filename(url)
        
        # Convert elements to dict format
        elements_data = []
        for element in result.elements:
            elem_dict = {
                "selector": element.selector,
                "element_type": element.element_type.value if hasattr(element.element_type, 'value') else str(element.element_type),
                "tag_name": element.tag_name,
                "text": element.text,
                "value": element.value,
                "placeholder": element.placeholder,
                "id": element.id,
                "name": element.name,
                "classes": element.classes,
                "attributes": element.attributes,
                "is_clickable": element.is_clickable,
                "is_editable": element.is_editable,
                "is_visible": element.is_visible,
                "is_enabled": element.is_enabled,
                "parent_selector": element.parent_selector,
                "child_count": element.child_count,
                "ai_description": None,  # No LLM
                "test_suggestions": [],  # No LLM
                "importance_score": element.importance_score if hasattr(element, 'importance_score') else 0.5
            }
            elements_data.append(elem_dict)
        
        # Convert screenshots to dict format
        screenshots_data = []
        for screenshot in result.screenshots:
            screenshot_dict = {
                "format": getattr(screenshot, 'format', 'png'),
                "width": getattr(screenshot, 'width', 0),
                "height": getattr(screenshot, 'height', 0),
                "full_page": getattr(screenshot, 'full_page', False),
                "timestamp": getattr(screenshot, 'timestamp', datetime.now().isoformat()),
                "data_size": len(screenshot.data) if hasattr(screenshot, 'data') and screenshot.data else 0
            }
            screenshots_data.append(screenshot_dict)
        
        # Create output
        output = ElementExtractionOutput(
            url=url,
            formatted_url=formatted_url,
            success=result.success,
            elements_count=len(result.elements),
            elements=elements_data,
            screenshots=screenshots_data,
            extraction_time=result.extraction_time,
            errors=result.errors
        )
        
        # Save to file
        output_file = output_dir / f"{formatted_url}_no_llm_elements.json"
        output.save_to_file(output_file)
        
        # Also save raw result for compatibility
        raw_file = output_dir / f"extraction_result_{formatted_url}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump({
                "url": url,
                "success": result.success,
                "elements_count": len(result.elements),
                "extraction_time": result.extraction_time,
                "statistics": result.statistics,
                "elements": elements_data
            }, f, indent=2)
        
        logger.info(f"✓ Extraction completed: {len(result.elements)} elements")
        return output
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        output = ElementExtractionOutput(
            url=url,
            formatted_url=format_url_for_filename(url),
            success=False,
            elements_count=0,
            elements=[],
            extraction_time=0,
            errors=[str(e)]
        )
        return output
    
    finally:
        # Cleanup
        await extractor.cleanup()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Extract elements from a webpage without LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python element_extractor_no_llm.py --url http://localhost:8000
  python element_extractor_no_llm.py --url https://example.com --output-dir ./results
        """
    )
    
    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='URL to extract elements from'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path.cwd(),
        help='Directory to save output files (default: current directory)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create output directory if needed
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run extraction
    try:
        output = asyncio.run(extract_elements(args.url, args.output_dir))
        
        # Print summary
        print("\n" + "=" * 60)
        print("EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"URL: {output.url}")
        print(f"Success: {output.success}")
        print(f"Elements: {output.elements_count}")
        print(f"Screenshots: {len(output.screenshots)}")
        print(f"Time: {output.extraction_time:.2f}s")
        print(f"Output: {output.formatted_url}_no_llm_elements.json")
        
        if output.errors:
            print(f"Errors: {', '.join(output.errors)}")
        
        print("=" * 60)
        
        # Exit with appropriate code
        sys.exit(0 if output.success else 1)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()