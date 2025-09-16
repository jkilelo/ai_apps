#!/usr/bin/env python3
"""
END-TO-END PIPELINE TEST V3
============================
Tests the complete flow:
1. elements_extractor_with_llm_v3.py -> Extract elements from URL
2. test_generation_with_llm_v3.py -> Generate test scenarios
3. code_generation_with_llm_v3.py -> Generate executable code
4. code_execution_v3.py -> Execute the generated code

NO fallbacks - must work 100% or fail
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import all V3 modules
from elements_extractor_with_llm_v3 import extract_and_analyze
from test_generation_with_llm_v3 import (
    generate_tests_for_url,
    TestGenerationContract,
    TestCategory
)
from code_generation_with_llm_v3 import (
    generate_code_for_url,
    TestFramework,
    BrowserFramework,
    CodePattern
)
from code_execution_v3 import (
    execute_generated_code,
    ExecutionConfig,
    ExecutionMode,
    SecurityLevel,
    ReportFormat
)

async def run_end_to_end_pipeline(url: str = "https://example.com"):
    """
    Run the complete end-to-end pipeline
    """
    print("="*70)
    print("END-TO-END PIPELINE V3 TEST")
    print("="*70)
    print(f"Target URL: {url}")
    print()
    
    pipeline_start = datetime.now()
    results = {
        "url": url,
        "steps": {},
        "success": False,
        "errors": []
    }
    
    try:
        # ======================================================================
        # STEP 1: ELEMENT EXTRACTION WITH LLM
        # ======================================================================
        print("[STEP 1] Element Extraction with LLM V3")
        print("-" * 40)
        
        step1_start = datetime.now()
        print(f"[INFO] Extracting elements from: {url}")
        
        # Extract and analyze page elements
        page_analysis = await extract_and_analyze(url)
        
        step1_duration = (datetime.now() - step1_start).total_seconds()
        
        print(f"[OK] Extraction completed in {step1_duration:.2f}s")
        print(f"     Elements found: {page_analysis.total_elements}")
        print(f"     Interactive elements: {page_analysis.interactive_elements}")
        print(f"     Page type: {page_analysis.page_type}")
        
        # Verify we have elements
        if not page_analysis.enriched_elements or page_analysis.total_elements == 0:
            raise ValueError("No elements extracted from page")
        
        results["steps"]["element_extraction"] = {
            "success": True,
            "duration": step1_duration,
            "elements_count": page_analysis.total_elements,
            "page_type": page_analysis.page_type
        }
        
        # ======================================================================
        # STEP 2: TEST GENERATION WITH LLM
        # ======================================================================
        print()
        print("[STEP 2] Test Generation with LLM V3")
        print("-" * 40)
        
        step2_start = datetime.now()
        print(f"[INFO] Generating test scenarios...")
        
        # Generate test scenarios
        test_contract = TestGenerationContract(
            url=url,
            max_scenarios_per_category=1,  # Keep it simple for demo
            test_categories=[
                TestCategory.FUNCTIONAL,
                TestCategory.VALIDATION
            ]
        )
        
        test_result = await generate_tests_for_url(test_contract)
        
        step2_duration = (datetime.now() - step2_start).total_seconds()
        
        # Verify we have scenarios
        if not test_result.test_suite or not test_result.test_suite.scenarios:
            raise ValueError("No test scenarios generated")
        
        print(f"[OK] Test generation completed in {step2_duration:.2f}s")
        print(f"     Scenarios generated: {len(test_result.test_suite.scenarios)}")
        print(f"     Categories covered: {test_result.categories_covered}")
        
        # Show generated scenarios
        print(f"\n     Generated Scenarios:")
        for i, scenario in enumerate(test_result.test_suite.scenarios, 1):
            print(f"     {i}. {scenario.name} ({scenario.category})")
            print(f"        Steps: {len(scenario.steps)}")
        
        results["steps"]["test_generation"] = {
            "success": True,
            "duration": step2_duration,
            "scenarios_count": len(test_result.test_suite.scenarios),
            "categories": test_result.categories_covered
        }
        
        # ======================================================================
        # STEP 3: CODE GENERATION WITH LLM
        # ======================================================================
        print()
        print("[STEP 3] Code Generation with LLM V3")
        print("-" * 40)
        
        step3_start = datetime.now()
        print(f"[INFO] Generating executable test code...")
        
        # Generate code from test scenarios
        code_result = await generate_code_for_url(
            url=url,
            test_framework=TestFramework.PYTEST,
            browser_framework=BrowserFramework.PLAYWRIGHT,
            code_pattern=CodePattern.DIRECT
        )
        
        step3_duration = (datetime.now() - step3_start).total_seconds()
        
        # Debug: Check what we got
        print(f"[DEBUG] code_result.success: {code_result.success}")
        print(f"[DEBUG] code_result.generated_code type: {type(code_result.generated_code)}")
        print(f"[DEBUG] code_result.generated_code has 'code' field: {hasattr(code_result.generated_code, 'code')}")
        if hasattr(code_result.generated_code, 'code'):
            print(f"[DEBUG] code_result.generated_code.code is None: {code_result.generated_code.code is None}")
            if code_result.generated_code.code:
                print(f"[DEBUG] code_result.generated_code.code length: {len(code_result.generated_code.code)}")
        
        # Verify code was generated
        if not code_result.success or not code_result.generated_code.code:
            raise ValueError(f"Code generation failed: {code_result.errors}")
        
        print(f"[OK] Code generation completed in {step3_duration:.2f}s")
        print(f"     Lines of code: {code_result.metrics.lines_of_code}")
        print(f"     Methods generated: {code_result.metrics.methods_count}")
        print(f"     Safety score: {code_result.metrics.safety_score:.2f}")
        print(f"     Syntax valid: {code_result.syntax_valid}")
        
        if code_result.safety_violations:
            print(f"[WARN] Safety violations: {len(code_result.safety_violations)}")
            for v in code_result.safety_violations[:3]:
                print(f"       - {v.violation_type}: {v.description}")
        
        # Get the generated code
        generated_code = code_result.generated_code.to_file_content()
        
        # Save generated code for inspection
        code_file = Path("pipeline_generated_code.py")
        code_file.write_text(generated_code)
        print(f"\n     Generated code saved to: {code_file}")
        
        results["steps"]["code_generation"] = {
            "success": True,
            "duration": step3_duration,
            "lines_of_code": code_result.metrics.lines_of_code,
            "safety_score": code_result.metrics.safety_score,
            "syntax_valid": code_result.syntax_valid
        }
        
        # ======================================================================
        # STEP 4: CODE EXECUTION
        # ======================================================================
        print()
        print("[STEP 4] Code Execution V3")
        print("-" * 40)
        
        step4_start = datetime.now()
        print(f"[INFO] Executing generated test code...")
        
        # Configure execution
        exec_config = ExecutionConfig(
            execution_mode=ExecutionMode.SEQUENTIAL,
            security_level=SecurityLevel.BASIC,  # Use BASIC for generated code
            timeout_per_test=30,
            capture_output=True,
            report_formats=[ReportFormat.JSON, ReportFormat.HTML]
        )
        
        # Execute the generated code
        exec_result = await execute_generated_code(
            code=generated_code,
            config=exec_config,
            test_name="pipeline_generated_test"
        )
        
        step4_duration = (datetime.now() - step4_start).total_seconds()
        
        print(f"[OK] Execution completed in {step4_duration:.2f}s")
        print(f"     Tests executed: {exec_result.total_tests}")
        print(f"     Passed: {exec_result.passed}")
        print(f"     Failed: {exec_result.failed}")
        print(f"     Errors: {exec_result.errors}")
        print(f"     Success: {exec_result.success}")
        
        if exec_result.security_violations:
            print(f"[WARN] Security violations during execution:")
            for violation in exec_result.security_violations:
                print(f"       - {violation}")
        
        # Show test details
        if exec_result.test_results:
            print(f"\n     Execution Details:")
            for test in exec_result.test_results:
                print(f"     - {test.test_name}: {test.status} ({test.duration:.3f}s)")
                if test.error_message:
                    print(f"       Error: {test.error_message[:100]}...")
        
        results["steps"]["code_execution"] = {
            "success": exec_result.success,
            "duration": step4_duration,
            "tests_executed": exec_result.total_tests,
            "passed": exec_result.passed,
            "failed": exec_result.failed,
            "errors": exec_result.errors
        }
        
        # ======================================================================
        # PIPELINE SUMMARY
        # ======================================================================
        pipeline_duration = (datetime.now() - pipeline_start).total_seconds()
        
        print()
        print("="*70)
        print("PIPELINE SUMMARY")
        print("="*70)
        
        # Check overall success
        all_steps_passed = all(
            step_result.get("success", False) 
            for step_result in results["steps"].values()
        )
        
        results["success"] = all_steps_passed
        results["total_duration"] = pipeline_duration
        
        print(f"Overall Success: {all_steps_passed}")
        print(f"Total Duration: {pipeline_duration:.2f}s")
        print()
        
        print("Step Results:")
        for step_name, step_result in results["steps"].items():
            status = "[OK]" if step_result["success"] else "[FAIL]"
            print(f"  {status} {step_name}: {step_result['duration']:.2f}s")
        
        # Save pipeline results
        results_file = Path(f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        results_file.write_text(json.dumps(results, indent=2, default=str))
        print(f"\nPipeline results saved to: {results_file}")
        
        if all_steps_passed:
            print()
            print("="*70)
            print("[SUCCESS] END-TO-END PIPELINE V3 WORKING PERFECTLY!")
            print("="*70)
            print()
            print("The complete flow works seamlessly:")
            print("  1. Element extraction with LLM analysis")
            print("  2. Test scenario generation from elements")
            print("  3. Executable code generation from scenarios")
            print("  4. Secure execution of generated code")
            print()
            print("All V3 modules integrated successfully with NO fallbacks!")
            return 0
        else:
            print()
            print("[FAILURE] Pipeline had issues")
            return 1
            
    except Exception as e:
        print()
        print(f"[ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        
        results["success"] = False
        results["errors"].append(str(e))
        
        # Save error results
        results_file = Path(f"pipeline_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        results_file.write_text(json.dumps(results, indent=2, default=str))
        print(f"\nError details saved to: {results_file}")
        
        return 1

async def main():
    """Main entry point"""
    # Test with a simple URL
    return await run_end_to_end_pipeline("https://example.com")

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))