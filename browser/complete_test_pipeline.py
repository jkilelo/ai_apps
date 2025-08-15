"""
Complete Test Pipeline: Generate → Execute → Report
====================================================
This script demonstrates the complete workflow:
1. Generate test code dynamically for any website
2. Execute the generated tests
3. Generate comprehensive reports

This is the ultimate demonstration of the framework's capabilities.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from browser.dynamic_test_code_generator import (
    DynamicCodeGenConfig,
    DynamicTestCodeGenerator
)
from browser.test_executor import (
    ExecutionConfig,
    TestExecutor
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CompleteTestPipeline:
    """Orchestrates the complete test pipeline from generation to execution."""
    
    def __init__(self, 
                 test_cases_file: str,
                 extraction_file: str = None,
                 base_url: str = None):
        """
        Initialize the pipeline.
        
        Args:
            test_cases_file: Path to test cases JSON
            extraction_file: Optional path to extraction data
            base_url: Optional base URL override
        """
        self.test_cases_file = test_cases_file
        self.extraction_file = extraction_file
        self.base_url = base_url
        self.generation_output_dir = "pipeline_generated_tests"
        self.execution_output_dir = "pipeline_execution_results"
        
    async def run_complete_pipeline(self) -> Dict:
        """Run the complete pipeline from generation to execution."""
        
        print("\n" + "="*80)
        print("COMPLETE TEST PIPELINE: GENERATE -> EXECUTE -> REPORT")
        print("="*80)
        
        pipeline_results = {
            "timestamp": datetime.now().isoformat(),
            "test_cases_file": self.test_cases_file,
            "extraction_file": self.extraction_file,
            "generation": {},
            "execution": {},
            "success": False
        }
        
        try:
            # ========================================
            # PHASE 1: GENERATE TEST CODE
            # ========================================
            print("\n" + "-"*60)
            print("PHASE 1: GENERATING TEST CODE WITH LLM")
            print("-"*60)
            
            generation_results = await self._generate_test_code()
            pipeline_results["generation"] = generation_results
            
            if not generation_results.get("success"):
                logger.error("Code generation failed")
                return pipeline_results
            
            print(f"\n[OK] Generated {len(generation_results.get('generated_files', []))} files")
            print(f"   LLM Calls: {generation_results.get('llm_calls', 0)}")
            
            # ========================================
            # PHASE 2: EXECUTE GENERATED TESTS
            # ========================================
            print("\n" + "-"*60)
            print("PHASE 2: EXECUTING GENERATED TESTS")
            print("-"*60)
            
            # Wait a moment for files to be written
            await asyncio.sleep(2)
            
            execution_results = await self._execute_tests()
            pipeline_results["execution"] = execution_results
            
            if execution_results.get("success"):
                print("\n[OK] All tests passed successfully!")
            else:
                print(f"\n[WARNING] Some tests failed")
            
            # ========================================
            # PHASE 3: GENERATE FINAL REPORT
            # ========================================
            print("\n" + "-"*60)
            print("PHASE 3: GENERATING FINAL REPORT")
            print("-"*60)
            
            self._generate_final_report(pipeline_results)
            
            pipeline_results["success"] = (
                generation_results.get("success") and 
                execution_results.get("results", {}).get("failed", 1) == 0
            )
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            pipeline_results["error"] = str(e)
            import traceback
            traceback.print_exc()
        
        return pipeline_results
    
    async def _generate_test_code(self) -> Dict:
        """Generate test code using the dynamic generator."""
        
        # Configure generation
        gen_config = DynamicCodeGenConfig(
            llm_provider="gemini",
            llm_model="gemini-2.5-flash-lite",
            llm_temperature=0.1,
            
            # Enable key strategies for quality
            enable_pal=True,
            enable_chain_of_thought=True,
            enable_constitutional_ai=True,
            enable_reflexion=True,
            enable_few_shot=True,
            
            # Disable others for speed
            enable_tree_of_thoughts=False,
            enable_react=False,
            enable_meta_prompting=False,
            enable_scratchpad=False,
            enable_debate=False,
            
            # Single sample for speed
            self_consistency_samples=1,
            
            output_dir=self.generation_output_dir
        )
        
        # Generate code
        generator = DynamicTestCodeGenerator(gen_config)
        
        logger.info("Generating test code...")
        results = await generator.generate_from_test_cases(
            self.test_cases_file,
            self.extraction_file
        )
        
        return results
    
    async def _execute_tests(self) -> Dict:
        """Execute the generated tests."""
        
        # Configure execution
        exec_config = ExecutionConfig(
            test_dir=self.generation_output_dir,
            execution_mode="all",
            browser="chromium",
            headless=False,  # Show browser for demo
            parallel_workers=1,
            max_retries=1,
            timeout_per_test=60,
            
            # Override base URL if provided
            base_url=self.base_url,
            
            # Enable reporting
            generate_html_report=True,
            generate_json_report=True,
            capture_screenshots=True,
            capture_videos=False,
            
            # Output settings
            output_dir=self.execution_output_dir,
            
            # Auto setup
            auto_install_deps=True,
            validate_before_run=True
        )
        
        # Execute tests
        executor = TestExecutor(exec_config)
        
        logger.info("Executing tests...")
        results = await executor.execute()
        
        return results
    
    def _generate_final_report(self, pipeline_results: Dict):
        """Generate a final comprehensive report."""
        
        report_file = Path(self.execution_output_dir) / f"pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        # Create comprehensive report
        report = {
            "pipeline_execution": pipeline_results,
            "summary": {
                "total_files_generated": len(pipeline_results["generation"].get("generated_files", [])),
                "llm_calls": pipeline_results["generation"].get("llm_calls", 0),
                "total_tests": pipeline_results["execution"].get("results", {}).get("total", 0),
                "tests_passed": pipeline_results["execution"].get("results", {}).get("passed", 0),
                "tests_failed": pipeline_results["execution"].get("results", {}).get("failed", 0),
                "execution_time": pipeline_results["execution"].get("results", {}).get("execution_time", 0),
                "overall_success": pipeline_results["success"]
            }
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Final report saved to: {report_file}")
        
        # Print summary
        print("\n" + "="*80)
        print("PIPELINE SUMMARY")
        print("="*80)
        print(f"Files Generated: {report['summary']['total_files_generated']}")
        print(f"LLM Calls: {report['summary']['llm_calls']}")
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Tests Passed: {report['summary']['tests_passed']}")
        print(f"Tests Failed: {report['summary']['tests_failed']}")
        print(f"Execution Time: {report['summary']['execution_time']:.2f}s")
        print(f"Overall Success: {'[YES]' if report['summary']['overall_success'] else '[NO]'}")
        print("="*80)


async def demo_pipeline():
    """Demonstrate the complete pipeline with test data."""
    
    # Check for test files
    test_cases = "test_results_github/20250814_160251_github_com_tests.json"
    extraction = "test_results_github/20250814_160251_github_com_extraction.json"
    
    if not Path(test_cases).exists():
        print(f"ERROR: Test cases file not found: {test_cases}")
        print("Please run the test extraction first to generate test cases.")
        return
    
    # Run pipeline
    pipeline = CompleteTestPipeline(
        test_cases_file=test_cases,
        extraction_file=extraction,
        base_url="https://github.com"  # Override if needed
    )
    
    results = await pipeline.run_complete_pipeline()
    
    if results["success"]:
        print("\n[SUCCESS] PIPELINE COMPLETED SUCCESSFULLY!")
        print("The framework has:")
        print("1. Generated test code dynamically using LLM")
        print("2. Executed the generated tests")
        print("3. Generated comprehensive reports")
        print("\nThis proves the framework can handle the complete testing lifecycle!")
    else:
        print("\n[WARNING] Pipeline completed with some issues")
        print("Check the reports for details")
    
    return results


async def run_custom_pipeline(test_cases_file: str, 
                            extraction_file: str = None,
                            base_url: str = None):
    """
    Run pipeline with custom test cases.
    
    Args:
        test_cases_file: Path to your test cases JSON
        extraction_file: Optional path to extraction data
        base_url: Optional base URL for testing
    """
    pipeline = CompleteTestPipeline(
        test_cases_file=test_cases_file,
        extraction_file=extraction_file,
        base_url=base_url
    )
    
    return await pipeline.run_complete_pipeline()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete Test Pipeline: Generate → Execute → Report")
    parser.add_argument("--test-cases", help="Path to test cases JSON file")
    parser.add_argument("--extraction", help="Path to extraction data JSON file")
    parser.add_argument("--base-url", help="Base URL for testing")
    parser.add_argument("--demo", action="store_true", help="Run demo with GitHub test data")
    
    args = parser.parse_args()
    
    if args.demo:
        # Run demo
        results = asyncio.run(demo_pipeline())
    elif args.test_cases:
        # Run with custom test cases
        results = asyncio.run(run_custom_pipeline(
            args.test_cases,
            args.extraction,
            args.base_url
        ))
    else:
        print("Usage:")
        print("  Demo mode: python complete_test_pipeline.py --demo")
        print("  Custom: python complete_test_pipeline.py --test-cases <file> [--extraction <file>] [--base-url <url>]")
        sys.exit(1)