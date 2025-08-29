#!/usr/bin/env python3
"""
TEST GENERATION WITH LLM - CLI Enhanced Version
==============================================
Generate comprehensive test suites from LLM-enhanced elements.
Loads output from element_extractor_with_llm and generates tests.
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
from test_generation_with_llm import (
    TestGenerationEngineV3,
    TestGenerationContract,
    TestGenerationResult,
    generate_tests_for_url
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestGenerationOutput(BaseModel):
    """Output contract for test generation with LLM"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    url: str = Field(..., description="URL that tests were generated for")
    formatted_url: str = Field(..., description="Clean filename version")
    success: bool = Field(..., description="Whether generation succeeded")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Input tracking
    elements_count: int = Field(..., description="Number of input elements")
    page_type: str = Field(..., description="Type of page")
    framework_detected: Optional[str] = Field(None, description="Framework detected")
    
    # Generated tests
    total_scenarios: int = Field(..., description="Total test scenarios generated")
    categories_covered: List[str] = Field(..., description="Test categories covered")
    test_suite: Dict[str, Any] = Field(..., description="Generated test suite")
    test_scenarios: List[Dict[str, Any]] = Field(..., description="Test scenarios")
    test_code: Dict[str, List[str]] = Field(default_factory=dict, description="Generated test code by framework")
    
    # Metadata
    generation_time: float = Field(..., description="Total generation time")
    llm_processing_time: float = Field(..., description="LLM processing time")
    strategies_used: List[str] = Field(..., description="Prompt strategies used")
    errors: List[str] = Field(default_factory=list, description="Any errors")
    
    def save_to_file(self, filepath: Path) -> None:
        """Save output to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved test generation output to: {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'TestGenerationOutput':
        """Load output from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)


async def generate_tests(input_file: Path = None, url: str = None, output_dir: Path = None) -> TestGenerationOutput:
    """
    Generate tests from LLM-enhanced elements
    
    Args:
        input_file: Path to with_llm elements JSON file
        url: URL to generate tests for (if input_file not provided)
        output_dir: Directory to save output (defaults to current dir)
    
    Returns:
        TestGenerationOutput with generated tests
    """
    if output_dir is None:
        output_dir = Path.cwd()
    
    # Load input from with_llm extraction
    page_type = "unknown"
    framework = None
    elements_count = 0
    
    if input_file and input_file.exists():
        logger.info(f"Loading LLM-enhanced extraction from: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            llm_data = json.load(f)
        
        url = llm_data.get('url', url)
        page_type = llm_data.get('page_type', 'unknown')
        framework = llm_data.get('framework_detected')
        elements_count = llm_data.get('base_elements_count', 0)
        logger.info(f"Loaded {elements_count} elements, page type: {page_type}")
    
    if not url:
        raise ValueError("URL must be provided either directly or in input file")
    
    try:
        start_time = datetime.now()
        
        # Create test generation contract
        contract = TestGenerationContract(
            url=url,
            frameworks=["playwright", "pytest", "selenium"],
            test_types=["functional", "validation", "accessibility", "security"],
            use_ai_enhancement=True
        )
        
        # Generate tests
        logger.info(f"Generating tests for: {url}")
        result = await generate_tests_for_url(contract)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Extract test scenarios
        test_scenarios = []
        test_code = {}
        
        if result.test_suite and hasattr(result.test_suite, 'scenarios'):
            for scenario in result.test_suite.scenarios:
                scenario_dict = {
                    "name": scenario.name,
                    "category": scenario.category,
                    "description": scenario.description,
                    "priority": getattr(scenario, 'priority', 'medium'),
                    "steps": getattr(scenario, 'steps', [])
                }
                test_scenarios.append(scenario_dict)
            
            # Extract generated code if available
            if hasattr(result.test_suite, 'playwright_tests'):
                test_code['playwright'] = result.test_suite.playwright_tests
            if hasattr(result.test_suite, 'pytest_tests'):
                test_code['pytest'] = result.test_suite.pytest_tests
        
        # Create output
        formatted_url = format_url_for_filename(url)
        output = TestGenerationOutput(
            url=url,
            formatted_url=formatted_url,
            success=True,
            elements_count=elements_count,
            page_type=page_type or result.page_analysis.page_type,
            framework_detected=framework or result.page_analysis.framework_detected,
            total_scenarios=result.total_scenarios,
            categories_covered=result.categories_covered,
            test_suite=result.test_suite.model_dump() if hasattr(result.test_suite, 'model_dump') else {},
            test_scenarios=test_scenarios,
            test_code=test_code,
            generation_time=result.generation_time,
            llm_processing_time=result.llm_processing_time,
            strategies_used=result.strategies_used,
            errors=[]
        )
        
        # Save to file
        output_file = output_dir / f"{formatted_url}_with_llm_tests.json"
        output.save_to_file(output_file)
        
        # Also save test code as separate files if generated
        for framework, tests in test_code.items():
            if tests:
                code_file = output_dir / f"{formatted_url}_tests_{framework}.py"
                with open(code_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(tests))
                logger.info(f"Saved {framework} test code to: {code_file}")
        
        logger.info(f"✓ Test generation completed: {result.total_scenarios} scenarios")
        return output
        
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        formatted_url = format_url_for_filename(url) if url else "unknown"
        output = TestGenerationOutput(
            url=url or "unknown",
            formatted_url=formatted_url,
            success=False,
            elements_count=elements_count,
            page_type=page_type,
            framework_detected=framework,
            total_scenarios=0,
            categories_covered=[],
            test_suite={},
            test_scenarios=[],
            generation_time=0,
            llm_processing_time=0,
            strategies_used=[],
            errors=[str(e)]
        )
        return output


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive test suites with LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate tests from with_llm output
  python test_generation_with_llm.py --input localhost_8000_with_llm_elements.json
  
  # Direct URL test generation
  python test_generation_with_llm.py --url http://localhost:8000
  
  # Specify output directory
  python test_generation_with_llm.py --input output.json --output-dir ./tests
        """
    )
    
    parser.add_argument(
        '--input',
        type=Path,
        help='Path to with_llm elements JSON file'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        help='URL to generate tests for (fallback if not in input file)'
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
    
    # Run generation
    try:
        output = asyncio.run(generate_tests(
            input_file=args.input,
            url=args.url,
            output_dir=args.output_dir
        ))
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST GENERATION SUMMARY")
        print("=" * 60)
        print(f"URL: {output.url}")
        print(f"Success: {output.success}")
        print(f"Page Type: {output.page_type}")
        print(f"Framework: {output.framework_detected or 'None'}")
        print(f"Input Elements: {output.elements_count}")
        print(f"Test Scenarios: {output.total_scenarios}")
        print(f"Categories: {', '.join(output.categories_covered)}")
        print(f"Generation Time: {output.generation_time:.2f}s")
        print(f"Output: {output.formatted_url}_with_llm_tests.json")
        
        if output.test_code:
            print(f"Test Code: {', '.join(output.test_code.keys())} frameworks")
        
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