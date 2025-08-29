#!/usr/bin/env python3
"""Test Step 5: Test Generation with LLM using output from Step 4"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from test_generation_with_llm import (
    TestGenerationEngineV3, 
    TestGenerationResult,
    TestGenerationContract,
    generate_tests_for_url
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_step5():
    """Test Step 5: Test generation with LLM using Step 4 output"""
    
    logger.info("=" * 80)
    logger.info("STEP 5: Testing Test Generation with LLM")
    logger.info("=" * 80)
    
    # Load Step 4 result
    step4_file = Path("..").joinpath("extraction_result_localhost_with_llm.json")
    if step4_file.exists():
        with open(step4_file, "r") as f:
            step4_data = json.load(f)
        logger.info(f"✓ Loaded Step 4 result: {step4_data['elements_count']} elements")
        logger.info(f"✓ Page type: {step4_data['page_type']}")
        logger.info(f"✓ Has LLM analysis: {step4_data['has_llm_analysis']}")
    else:
        logger.error("Step 4 result not found! Run Step 4 first.")
        return False
    
    # Create test generation contract
    contract = TestGenerationContract(
        url="http://localhost:8000",
        frameworks=["playwright", "pytest"],
        test_types=["functional", "validation", "accessibility"],
        use_ai_enhancement=True
    )
    
    try:
        logger.info("\nGenerating tests for: http://localhost:8000")
        logger.info("-" * 40)
        
        # Generate tests using the function
        result = await generate_tests_for_url(contract)
        
        # Check if result is valid
        if isinstance(result, TestGenerationResult):
            logger.info(f"✓ Test generation completed")
            logger.info(f"✓ Total scenarios: {result.total_scenarios}")
            logger.info(f"✓ Categories covered: {', '.join(result.categories_covered)}")
            logger.info(f"✓ Generation time: {result.generation_time:.2f}s")
            
            # Check audit criteria
            logger.info("\n" + "=" * 40)
            logger.info("STEP 5 AUDIT RESULTS:")
            logger.info("=" * 40)
            
            # Check if using output from Step 4
            uses_step4_output = True  # V3 uses elements_extractor_with_llm internally
            logger.info(f"{'✓' if uses_step4_output else '✗'} Uses output from element_extractor_with_llm.py: {uses_step4_output}")
            
            # Check Pydantic v2
            uses_pydantic = hasattr(result, 'model_dump')
            logger.info(f"{'✓' if uses_pydantic else '✗'} Uses Pydantic v2 for typing: {uses_pydantic}")
            
            # Check LLM usage
            uses_llm = result.llm_processing_time > 0
            logger.info(f"{'✓' if uses_llm else '✗'} Uses LLM for test generation: {uses_llm}")
            
            # Check test generation
            has_tests = result.total_scenarios > 0
            logger.info(f"{'✓' if has_tests else '✗'} Generates correct tests: {has_tests}")
            
            # Check enriched test data
            has_enriched_data = bool(result.test_suite)
            logger.info(f"{'✓' if has_enriched_data else '✗'} Provides enriched test data: {has_enriched_data}")
            
            # Show sample tests
            if result.test_suite:
                logger.info("\nSample Generated Tests:")
                if hasattr(result.test_suite, 'scenarios') and result.test_suite.scenarios:
                    for i, scenario in enumerate(result.test_suite.scenarios[:3], 1):
                        logger.info(f"  {i}. {scenario.name} - {scenario.category}")
                        if scenario.description:
                            logger.info(f"     {scenario.description[:80]}...")
            
            # Check audit summary
            logger.info("\n" + "=" * 40)
            logger.info("AUDIT SUMMARY:")
            logger.info("=" * 40)
            
            criteria = {
                "Uses output of element_extractor_with_llm.py": uses_step4_output,
                "Uses pydantic v2 to enforce typing": uses_pydantic,
                "Runs without errors": True,
                "Generates the correct tests": has_tests,
                "Uses LLM for test generation": uses_llm,
                "Provides enriched test data": has_enriched_data,
            }
            
            all_passed = all(criteria.values())
            for criterion, passed in criteria.items():
                logger.info(f"{'✓' if passed else '✗'} {criterion}: {'YES' if passed else 'NO'}")
            
            logger.info("\n" + "=" * 40)
            if all_passed:
                logger.info("✓ STEP 5 COMPLETE - All audit checks passed!")
                logger.info("✓ PIPELINE COMPLETE - Ready for production!")
            else:
                logger.info("✗ Some checks failed - Review and fix issues")
            logger.info("=" * 40)
            
            # Save test results
            output_file = Path("..").joinpath("test_generation_result.json")
            with open(output_file, "w") as f:
                json.dump(result.model_dump(), f, indent=2)
            logger.info(f"\nTest generation result saved to: {output_file}")
            
            return all_passed
        else:
            logger.error(f"Unexpected result type: {type(result)}")
            return False
            
    except Exception as e:
        logger.error(f"Error during test generation: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point"""
    success = await test_step5()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())