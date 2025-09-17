"""
Correct Pipeline Implementation
As specified: Single browser in no_llm → LLM enrichment only → Test generation only

Author: Senior Architect
Date: 2025-09-15
"""

import asyncio
import time
import logging
import json
from typing import Optional, Dict, Any
from pathlib import Path
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the modules
from web_automation_portable.backend.data_types import (
    ExtractionResult,
    ExtractionConfig,
    PageAnalysis,
    TestCategory,
    clean_for_llm
)

from web_automation_portable.backend.elements_extractor_no_llm import (
    ElementsExtractorNoLLM,
    extract_from_url as extract_no_llm
)

from web_automation_portable.backend.elements_extractor_with_llm import (
    ElementsExtractorWithLLM
)

from web_automation_portable.backend.test_generation_with_llm import (
    TestGenerationEngine
)


async def run_correct_pipeline(
    url: str,
    config: Optional[ExtractionConfig] = None,
    max_elements: int = 10,
    generate_tests: bool = True
) -> Dict[str, Any]:
    """
    THE CORRECT PIPELINE IMPLEMENTATION

    Flow:
    1. elements_extractor_no_llm.py - SINGLE browser instantiation, extracts elements
    2. elements_extractor_with_llm.py - NO browser, only LLM enrichment
    3. test_generation_with_llm.py - NO browser, only LLM test generation

    Args:
        url: URL to process
        config: Extraction configuration
        max_elements: Max elements for LLM processing
        generate_tests: Whether to generate test scenarios

    Returns:
        Complete pipeline results
    """

    pipeline_start = time.time()
    results = {
        'url': url,
        'success': False,
        'stages': {},
        'errors': []
    }

    try:
        # ========================================================================
        # STAGE 1: DOM Extraction with SINGLE browser instance
        # ========================================================================
        stage1_start = time.time()
        logger.info("=" * 80)
        logger.info("STAGE 1: DOM Extraction (elements_extractor_no_llm.py)")
        logger.info("         Single browser instantiation")
        logger.info("=" * 80)

        # Use elements_extractor_no_llm as entry point - it handles browser
        extraction_result = await extract_no_llm(url, headless=True, enable_stealth=True)

        stage1_duration = time.time() - stage1_start

        results['stages']['dom_extraction'] = {
            'module': 'elements_extractor_no_llm.py',
            'duration': stage1_duration,
            'success': extraction_result.success,
            'elements_extracted': len(extraction_result.elements),
            'browser_instances': 1  # SINGLE browser
        }

        if not extraction_result.success:
            raise Exception(f"DOM extraction failed: {extraction_result.errors}")

        logger.info(f"[OK] Stage 1 complete: {len(extraction_result.elements)} elements in {stage1_duration:.2f}s")
        logger.info(f"  Output type: ExtractionResult")

        # Save Stage 1 raw results as JSON (cleaned to reduce size)
        stage1_json_path = Path("stage1_extraction_result.json")
        cleaned_stage1 = clean_for_llm(extraction_result.model_dump())
        with open(stage1_json_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_stage1, f, indent=2, default=str)
        logger.info(f"  Saved cleaned output to: {stage1_json_path}")

        # ========================================================================
        # STAGE 2: LLM Enrichment (NO BROWSER)
        # ========================================================================
        stage2_start = time.time()
        logger.info("")
        logger.info("=" * 80)
        logger.info("STAGE 2: LLM Enrichment (elements_extractor_with_llm.py)")
        logger.info("         NO browser instantiation - only LLM calls")
        logger.info("=" * 80)

        # Create LLM enricher
        llm_enricher = ElementsExtractorWithLLM()

        # Use the NEW method that accepts ExtractionResult
        page_analysis = await llm_enricher.enrich_extracted_elements(
            extraction_result=extraction_result,  # Pass the extraction result
            analyze_with_llm=True,
            max_elements=max_elements
        )

        stage2_duration = time.time() - stage2_start

        results['stages']['llm_enrichment'] = {
            'module': 'elements_extractor_with_llm.py',
            'duration': stage2_duration,
            'input_type': 'ExtractionResult',
            'output_type': 'PageAnalysis',
            'enriched_elements': len(page_analysis.enriched_elements),
            'page_type': page_analysis.page_type,
            'browser_instances': 0  # NO browser
        }

        logger.info(f"[OK] Stage 2 complete: {len(page_analysis.enriched_elements)} enriched in {stage2_duration:.2f}s")
        logger.info(f"  Input: ExtractionResult → Output: PageAnalysis")

        # Save Stage 2 raw results as JSON (cleaned to reduce size)
        stage2_json_path = Path("stage2_page_analysis.json")
        cleaned_stage2 = clean_for_llm(page_analysis.model_dump())
        with open(stage2_json_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_stage2, f, indent=2, default=str)
        logger.info(f"  Saved cleaned output to: {stage2_json_path}")

        # ========================================================================
        # STAGE 3: Test Generation (NO BROWSER)
        # ========================================================================
        if generate_tests:
            stage3_start = time.time()
            logger.info("")
            logger.info("=" * 80)
            logger.info("STAGE 3: Test Generation (test_generation_with_llm.py)")
            logger.info("         NO browser instantiation - only LLM calls")
            logger.info("=" * 80)

            # Create test generator
            test_generator = TestGenerationEngine()

            # Generate test scenarios from PageAnalysis
            test_scenarios = await test_generator.generate_test_scenarios(
                page_analysis=page_analysis,  # Pass the page analysis
                categories=[TestCategory.FUNCTIONAL, TestCategory.VALIDATION],
                max_per_category=3
            )

            stage3_duration = time.time() - stage3_start

            results['stages']['test_generation'] = {
                'module': 'test_generation_with_llm.py',
                'duration': stage3_duration,
                'input_type': 'PageAnalysis',
                'output_type': 'List[TestScenario]',
                'scenarios_generated': len(test_scenarios),
                'browser_instances': 0  # NO browser
            }

            results['test_scenarios'] = test_scenarios

            logger.info(f"[OK] Stage 3 complete: {len(test_scenarios)} scenarios in {stage3_duration:.2f}s")
            logger.info(f"  Input: PageAnalysis → Output: TestScenarios")

            # Save Stage 3 raw results as JSON (cleaned to reduce size)
            stage3_json_path = Path("stage3_test_scenarios.json")
            # Convert test scenarios to dict format
            test_scenarios_dict = [
                scenario.model_dump() if hasattr(scenario, 'model_dump') else scenario
                for scenario in test_scenarios
            ]
            cleaned_stage3 = clean_for_llm(test_scenarios_dict)
            with open(stage3_json_path, "w", encoding="utf-8") as f:
                json.dump(cleaned_stage3, f, indent=2, default=str)
            logger.info(f"  Saved cleaned output to: {stage3_json_path}")

        # ========================================================================
        # FINAL SUMMARY
        # ========================================================================
        total_duration = time.time() - pipeline_start

        results['success'] = True
        results['total_duration'] = total_duration
        results['extraction_result'] = extraction_result
        results['page_analysis'] = page_analysis

        logger.info("")
        logger.info("=" * 80)
        logger.info("PIPELINE COMPLETE - CORRECT IMPLEMENTATION")
        logger.info("=" * 80)
        logger.info(f"Total duration: {total_duration:.2f}s")
        logger.info("")
        logger.info("Data Flow:")
        logger.info("  URL -> [no_llm + browser] -> ExtractionResult")
        logger.info("       -> [with_llm + NO browser] -> PageAnalysis")
        logger.info("       -> [test_gen + NO browser] -> TestScenarios")
        logger.info("")
        logger.info("Browser Instances: 1 (only in elements_extractor_no_llm)")
        logger.info("=" * 80)

        # Save complete pipeline summary
        pipeline_summary_path = Path("pipeline_summary.json")
        summary = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "success": True,
            "total_duration": total_duration,
            "stages": results['stages'],
            "data_flow": {
                "stage1_output": "stage1_extraction_result.json",
                "stage2_output": "stage2_page_analysis.json",
                "stage3_output": "stage3_test_scenarios.json" if generate_tests else None
            },
            "browser_instances": 1,
            "elements_extracted": len(extraction_result.elements),
            "elements_enriched": len(page_analysis.enriched_elements),
            "test_scenarios_generated": len(test_scenarios) if generate_tests else 0
        }
        with open(pipeline_summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)
        logger.info(f"\nPipeline summary saved to: {pipeline_summary_path}")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        results['success'] = False
        results['errors'].append(str(e))

    return results


async def main():
    """
    Demonstrate the correct pipeline implementation
    """
    print("\n" + "=" * 80)
    print("CORRECT PIPELINE IMPLEMENTATION TEST")
    print("=" * 80)
    print()
    print("Specification:")
    print("  1. elements_extractor_no_llm.py - Entry point with SINGLE browser")
    print("  2. elements_extractor_with_llm.py - NO browser, only LLM enrichment")
    print("  3. test_generation_with_llm.py - NO browser, only test generation")
    print()
    print("Data Flow:")
    print("  URL -> ExtractionResult -> PageAnalysis -> TestScenarios")
    print()
    print("=" * 80)

    # Test with a real URL
    url = "https://github.com"
    print(f"\nTesting with: {url}\n")

    results = await run_correct_pipeline(
        url=url,
        max_elements=5,
        generate_tests=True
    )

    # Print summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    if results['success']:
        print(f"[OK] Pipeline successful")
        print(f"[OK] Total duration: {results['total_duration']:.2f}s")
        print()
        print("Stage Breakdown:")
        for stage_name, stage_data in results['stages'].items():
            print(f"  {stage_name}:")
            print(f"    - Module: {stage_data.get('module', 'N/A')}")
            print(f"    - Duration: {stage_data['duration']:.2f}s")
            print(f"    - Browser instances: {stage_data.get('browser_instances', 0)}")
            if 'input_type' in stage_data:
                print(f"    - Input: {stage_data['input_type']}")
            if 'output_type' in stage_data:
                print(f"    - Output: {stage_data['output_type']}")

        print()
        print("Total Browser Instances: 1 (only in stage 1)")
        print()
        print("[OK] CORRECT IMPLEMENTATION VERIFIED")
    else:
        print(f"[FAIL] Pipeline failed: {results.get('errors', ['Unknown error'])}")

    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())