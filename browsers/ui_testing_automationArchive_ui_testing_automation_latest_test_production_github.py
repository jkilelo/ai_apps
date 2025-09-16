#!/usr/bin/env python3
"""
Production End-to-End Test with GitHub.com
==========================================
This test runs the complete pipeline with real LLM calls,
saving audit trails at each step.

Author: Production Test Engineer
Date: 2025-08-27
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import uuid

# Add path for imports
sys.path.insert(0, r'C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ui_testing_automation')

# Import the integrated pipeline
from pipeline_integration import IntegratedTestPipeline, PipelineConfig
from elements_extractor_no_llm import ExtractedElement, ElementType, InteractionType

async def run_production_test():
    """Run production end-to-end test with GitHub.com"""
    
    # Create audit directory
    audit_dir = Path("./production_audit")
    audit_dir.mkdir(exist_ok=True)
    
    # Create session ID for this test run
    session_id = f"github_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    session_dir = audit_dir / session_id
    session_dir.mkdir(exist_ok=True)
    
    print("[PRODUCTION TEST] Starting end-to-end test with GitHub.com")
    print("=" * 80)
    print(f"Session ID: {session_id}")
    print(f"Audit Directory: {session_dir}")
    print(f"Target URL: https://github.com")
    print(f"Mode: PRODUCTION (Real LLM calls)")
    print("=" * 80)
    
    # Initialize pipeline with production configuration
    from test_generation_with_llm import TestCategory, TestFramework
    from code_generation_with_llm import TestFramework as CodeTestFramework, BrowserFramework, CodePattern
    from code_execution import ExecutionMode
    
    config = PipelineConfig(
        max_elements=20,  # Focus on key elements
        enable_screenshots=True,
        test_categories=[TestCategory.FUNCTIONAL, TestCategory.SECURITY, TestCategory.ACCESSIBILITY],
        test_frameworks=[TestFramework.PLAYWRIGHT],
        max_scenarios_per_category=2,  # 2 scenarios per category = 6 total
        timeout_per_test=60,
        enable_retry=True,
        max_retries=2,
        enable_metrics=True,
        enable_health_checks=True
    )
    
    pipeline = IntegratedTestPipeline(config)
    
    # Stage 1: Run the complete pipeline
    print("\n[STAGE 1] Running integrated pipeline")
    print("-" * 40)
    
    try:
        # Run pipeline with GitHub.com
        result = await pipeline.run_pipeline(
            url="https://github.com",
            custom_elements=None  # Let it extract from the actual page
        )
        
        # Save pipeline result
        pipeline_result_file = session_dir / "1_pipeline_result.json"
        with open(pipeline_result_file, 'w') as f:
            json.dump({
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "url": "https://github.com",
                "success": result.success,
                "stage_results": result.stage_results,
                "metrics": result.metrics,
                "errors": result.errors
            }, f, indent=2, default=str)
        print(f"[OK] Pipeline result saved to: {pipeline_result_file}")
        
        # Stage 2: Save element extraction details
        print("\n[STAGE 2] Saving element extraction audit")
        print("-" * 40)
        
        if "element_extraction" in result.stage_results:
            extraction_data = result.stage_results["element_extraction"]
            extraction_file = session_dir / "2_extracted_elements.json"
            
            # Process extraction result
            elements_data = []
            if extraction_data and hasattr(extraction_data, 'elements'):
                for elem in extraction_data.elements[:20]:  # Save top 20 elements
                    elements_data.append({
                        "selector": elem.selector,
                        "tag_name": elem.tag_name,
                        "element_type": elem.element_type.value if hasattr(elem.element_type, 'value') else str(elem.element_type),
                        "text": elem.text[:100] if elem.text else None,
                        "attributes": elem.attributes,
                        "confidence": elem.confidence,
                        "is_clickable": elem.is_clickable,
                        "is_visible": elem.is_visible
                    })
            
            with open(extraction_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_elements": len(extraction_data.elements) if extraction_data and hasattr(extraction_data, 'elements') else 0,
                    "elements": elements_data,
                    "extraction_time": extraction_data.extraction_time if extraction_data and hasattr(extraction_data, 'extraction_time') else 0
                }, f, indent=2)
            print(f"[OK] Extracted elements saved: {len(elements_data)} elements")
            
            # Save screenshots if available
            if extraction_data and hasattr(extraction_data, 'screenshots') and extraction_data.screenshots:
                screenshots_dir = session_dir / "screenshots"
                screenshots_dir.mkdir(exist_ok=True)
                saved_screenshots = extraction_data.save_screenshots(screenshots_dir)
                print(f"[OK] Screenshots saved: {len(saved_screenshots)} files")
        
        # Stage 3: Save test generation audit
        print("\n[STAGE 3] Saving test generation audit")
        print("-" * 40)
        
        if "test_generation" in result.stage_results:
            test_gen_data = result.stage_results["test_generation"]
            test_gen_file = session_dir / "3_generated_tests.json"
            
            test_scenarios = []
            if test_gen_data and hasattr(test_gen_data, 'test_suites'):
                for suite in test_gen_data.test_suites:
                    for scenario in suite.scenarios:
                        test_scenarios.append({
                            "name": scenario.name,
                            "category": scenario.category,
                            "priority": scenario.priority,
                            "confidence": scenario.confidence_score,
                            "steps": [
                                {"keyword": step.keyword, "text": step.text}
                                for step in scenario.steps
                            ],
                            "test_data": scenario.test_data
                        })
            
            with open(test_gen_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_scenarios": len(test_scenarios),
                    "generation_time": test_gen_data.generation_time if test_gen_data and hasattr(test_gen_data, 'generation_time') else 0,
                    "scenarios": test_scenarios,
                    "strategies_used": test_gen_data.strategies_used if test_gen_data and hasattr(test_gen_data, 'strategies_used') else []
                }, f, indent=2)
            print(f"[OK] Test scenarios saved: {len(test_scenarios)} scenarios")
        
        # Stage 4: Save code generation audit
        print("\n[STAGE 4] Saving code generation audit")
        print("-" * 40)
        
        if "code_generation" in result.stage_results:
            code_gen_data = result.stage_results["code_generation"]
            code_gen_file = session_dir / "4_generated_code.py"
            
            if code_gen_data and hasattr(code_gen_data, 'code'):
                with open(code_gen_file, 'w') as f:
                    f.write(code_gen_data.code)
                print(f"[OK] Generated Python Playwright code saved: {len(code_gen_data.code)} characters")
                
                # Save metadata
                code_metadata_file = session_dir / "4_code_metadata.json"
                with open(code_metadata_file, 'w') as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "framework": code_gen_data.framework if hasattr(code_gen_data, 'framework') else "playwright",
                        "code_length": len(code_gen_data.code),
                        "generation_time": code_gen_data.generation_time if hasattr(code_gen_data, 'generation_time') else 0,
                        "includes_pom": "PageObject" in code_gen_data.code,
                        "includes_pytest": "pytest" in code_gen_data.code or "def test_" in code_gen_data.code
                    }, f, indent=2)
        
        # Stage 5: Save execution audit
        print("\n[STAGE 5] Saving execution audit")
        print("-" * 40)
        
        if "code_execution" in result.stage_results:
            exec_data = result.stage_results["code_execution"]
            exec_file = session_dir / "5_execution_results.json"
            
            execution_results = {
                "timestamp": datetime.now().isoformat(),
                "execution_success": exec_data.success if hasattr(exec_data, 'success') else False,
                "tests_run": exec_data.tests_run if hasattr(exec_data, 'tests_run') else 0,
                "tests_passed": exec_data.tests_passed if hasattr(exec_data, 'tests_passed') else 0,
                "tests_failed": exec_data.tests_failed if hasattr(exec_data, 'tests_failed') else 0,
                "execution_time": exec_data.execution_time if hasattr(exec_data, 'execution_time') else 0,
                "output": exec_data.output[:5000] if hasattr(exec_data, 'output') else None,
                "errors": exec_data.errors if hasattr(exec_data, 'errors') else []
            }
            
            with open(exec_file, 'w') as f:
                json.dump(execution_results, f, indent=2)
            print(f"[OK] Execution results saved")
        
        # Generate final audit report
        print("\n[STAGE 6] Generating final audit report")
        print("-" * 40)
        
        report = []
        report.append("# Production Test Audit Report")
        report.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Session ID**: {session_id}")
        report.append(f"**Target URL**: https://github.com")
        report.append(f"**Pipeline Success**: {result.success}")
        report.append("")
        report.append("## Summary")
        report.append(f"- Total Pipeline Time: {result.metrics.get('total_time', 0):.2f} seconds")
        report.append(f"- Elements Extracted: {result.metrics.get('elements_extracted', 0)}")
        report.append(f"- Test Scenarios Generated: {result.metrics.get('test_scenarios_generated', 0)}")
        report.append(f"- Code Generated: {'Yes' if 'code_generation' in result.stage_results else 'No'}")
        report.append(f"- Tests Executed: {'Yes' if 'code_execution' in result.stage_results else 'No'}")
        report.append("")
        
        report.append("## Stage Results")
        for stage, data in result.stage_results.items():
            report.append(f"### {stage.replace('_', ' ').title()}")
            if data:
                if hasattr(data, '__dict__'):
                    for key, value in data.__dict__.items():
                        if not key.startswith('_'):
                            if isinstance(value, (str, int, float, bool)):
                                report.append(f"- {key}: {value}")
                            elif isinstance(value, list):
                                report.append(f"- {key}: {len(value)} items")
            report.append("")
        
        if result.errors:
            report.append("## Errors")
            for error in result.errors:
                report.append(f"- {error}")
            report.append("")
        
        report.append("## Files Generated")
        report.append(f"1. Pipeline Result: `{pipeline_result_file.name}`")
        report.append(f"2. Extracted Elements: `2_extracted_elements.json`")
        report.append(f"3. Generated Tests: `3_generated_tests.json`")
        report.append(f"4. Generated Code: `4_generated_code.py`")
        report.append(f"5. Execution Results: `5_execution_results.json`")
        
        # Save report
        report_file = session_dir / "AUDIT_REPORT.md"
        with open(report_file, 'w') as f:
            f.write('\n'.join(report))
        print(f"[OK] Audit report saved to: {report_file}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("[PRODUCTION TEST COMPLETE]")
        print(f"Session ID: {session_id}")
        print(f"Audit Directory: {session_dir}")
        print(f"Pipeline Success: {result.success}")
        print(f"Total Time: {result.metrics.get('total_time', 0):.2f} seconds")
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"\n[ERROR] Production test failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Save error report
        error_file = session_dir / "ERROR_REPORT.txt"
        with open(error_file, 'w') as f:
            f.write(f"Error: {e}\n\n")
            f.write(traceback.format_exc())
        
        return None

if __name__ == "__main__":
    print("[INFO] Starting production test with GitHub.com")
    print("[INFO] This will use REAL LLM calls and may take 30-60 seconds")
    print()
    
    result = asyncio.run(run_production_test())
    
    if result and result.success:
        print("\n[SUCCESS] Production test completed successfully!")
        sys.exit(0)
    else:
        print("\n[FAILURE] Production test failed. Check audit logs for details.")
        sys.exit(1)