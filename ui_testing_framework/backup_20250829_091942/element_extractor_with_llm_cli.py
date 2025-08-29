#!/usr/bin/env python3
"""
ELEMENT EXTRACTOR WITH LLM - CLI Enhanced Version
================================================
LLM-enhanced element extraction with CLI support and Pydantic v2 contracts.
Loads output from element_extractor_no_llm and enriches with AI analysis.
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

from utils import format_url_for_filename, save_json, load_json, validate_pydantic_output

from pydantic import BaseModel, Field, ConfigDict
from elements_extractor_with_llm import (
    ElementsExtractorWithLLMV3,
    ExtractionConfig,
    PageAnalysis
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ElementWithLLMOutput(BaseModel):
    """Output contract for element extraction with LLM enhancement"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    url: str = Field(..., description="URL that was extracted")
    formatted_url: str = Field(..., description="URL-encoded version for file naming")
    success: bool = Field(..., description="Whether extraction succeeded")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # From no_llm extraction
    base_elements_count: int = Field(..., description="Number of base elements")
    base_elements: List[Dict[str, Any]] = Field(..., description="Base elements from no_llm")
    screenshots_used: int = Field(..., description="Number of screenshots used")
    
    # LLM enrichment
    page_type: str = Field(..., description="Type of page detected")
    framework_detected: Optional[str] = Field(None, description="Framework detected")
    enriched_elements: List[Dict[str, Any]] = Field(..., description="Elements with LLM enrichment")
    llm_insights: Dict[str, Any] = Field(default_factory=dict, description="LLM analysis insights")
    qa_test_plan: Dict[str, List[str]] = Field(default_factory=dict, description="QA test plan")
    test_scenarios: List[str] = Field(default_factory=list, description="Generated test scenarios")
    
    processing_time: float = Field(..., description="Total processing time")
    llm_processing_time: float = Field(..., description="LLM processing time")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    
    def save_to_file(self, filepath: Path) -> None:
        """Save output to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved LLM-enhanced output to: {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'ElementWithLLMOutput':
        """Load output from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)


async def enhance_with_llm(input_file: Path = None, url: str = None, output_dir: Path = None) -> ElementWithLLMOutput:
    """
    Enhance elements with LLM analysis
    
    Args:
        input_file: Path to no_llm elements JSON file
        url: URL to extract from (if input_file not provided)
        output_dir: Directory to save output (defaults to current dir)
    
    Returns:
        ElementWithLLMOutput with LLM-enhanced results
    """
    if output_dir is None:
        output_dir = Path.cwd()
    
    # Load input from no_llm extraction if provided
    base_elements = []
    screenshots_count = 0
    
    if input_file and input_file.exists():
        logger.info(f"Loading base extraction from: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            base_data = json.load(f)
        
        url = base_data.get('url', url)
        base_elements = base_data.get('elements', [])
        screenshots_count = len(base_data.get('screenshots', []))
        logger.info(f"Loaded {len(base_elements)} elements from no_llm extraction")
    
    if not url:
        raise ValueError("URL must be provided either directly or in input file")
    
    # Initialize extractor
    config = ExtractionConfig(
        enable_shadow_dom=True,
        enable_iframe_traversal=True,
        filter_invisible=True,
        capture_screenshots=True
    )
    
    extractor = ElementsExtractorWithLLMV3(config)
    
    try:
        start_time = datetime.now()
        
        # Extract and analyze with LLM
        logger.info(f"Enhancing elements from: {url}")
        result = await extractor.extract_and_analyze(url)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Convert enriched elements to dict format
        enriched_data = []
        for element in result.enriched_elements:
            elem_dict = {
                "base_element": element.base_element,
                "llm_analysis": element.llm_analysis,
                "test_scenarios": element.test_scenarios,
                "qa_categories": [cat.value if hasattr(cat, 'value') else str(cat) 
                                 for cat in element.qa_categories],
                "confidence_score": element.confidence_score
            }
            enriched_data.append(elem_dict)
        
        # Generate test scenarios for QA
        qa_result = await extractor.extract_for_qa(url)
        test_scenarios = []
        if qa_result:
            _, scenarios = qa_result
            test_scenarios = scenarios[:10]  # Top 10 scenarios
        
        # Create output with new naming convention
        formatted_url = format_url_for_filename(url)
        output = ElementWithLLMOutput(
            url=url,
            formatted_url=formatted_url,
            success=True,
            base_elements_count=len(base_elements) if base_elements else result.total_elements,
            base_elements=base_elements if base_elements else [],
            screenshots_used=screenshots_count,
            page_type=result.page_type,
            framework_detected=result.framework_detected,
            enriched_elements=enriched_data,
            llm_insights=result.llm_insights,
            qa_test_plan=result.qa_test_plan,
            test_scenarios=test_scenarios,
            processing_time=processing_time,
            llm_processing_time=processing_time * 0.8,  # Estimate
            errors=[]
        )
        
        # Save to file
        output_file = output_dir / f"{formatted_url}_with_llm_elements.json"
        output.save_to_file(output_file)
        
        logger.info(f"✓ LLM enhancement completed: {len(enriched_data)} enriched elements")
        return output
        
    except Exception as e:
        logger.error(f"LLM enhancement failed: {e}")
        formatted_url = format_url_for_filename(url) if url else "unknown"
        output = ElementWithLLMOutput(
            url=url or "unknown",
            formatted_url=formatted_url,
            success=False,
            base_elements_count=len(base_elements),
            base_elements=base_elements,
            screenshots_used=screenshots_count,
            page_type="unknown",
            enriched_elements=[],
            processing_time=0,
            llm_processing_time=0,
            errors=[str(e)]
        )
        return output


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Enhance extracted elements with LLM analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Direct URL extraction with LLM
  python element_extractor_with_llm.py --url http://localhost:8000
  
  # Load from no_llm output
  python element_extractor_with_llm.py --input http%3A%2F%2Flocalhost%3A8000_no_llm_elements.json
  
  # Both (uses input file, URL as fallback)
  python element_extractor_with_llm.py --input output.json --url http://localhost:8000
        """
    )
    
    parser.add_argument(
        '--input',
        type=Path,
        help='Path to no_llm elements JSON file'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        help='URL to extract elements from (fallback if not in input file)'
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
    
    # Validate arguments
    if not args.input and not args.url:
        parser.error("Either --input or --url must be provided")
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create output directory if needed
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run enhancement
    try:
        output = asyncio.run(enhance_with_llm(
            input_file=args.input,
            url=args.url,
            output_dir=args.output_dir
        ))
        
        # Print summary
        print("\n" + "=" * 60)
        print("LLM ENHANCEMENT SUMMARY")
        print("=" * 60)
        print(f"URL: {output.url}")
        print(f"Success: {output.success}")
        print(f"Page Type: {output.page_type}")
        print(f"Framework: {output.framework_detected or 'None'}")
        print(f"Base Elements: {output.base_elements_count}")
        print(f"Enriched Elements: {len(output.enriched_elements)}")
        print(f"Test Scenarios: {len(output.test_scenarios)}")
        print(f"Processing Time: {output.processing_time:.2f}s")
        print(f"Output: {output.formatted_url}_with_llm_elements.json")
        
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