#!/usr/bin/env python3
"""
Minimal Baseline Test with Live Monitoring
==========================================
Tests framework with single username field while monitoring LLM responses.

Author: QA Automation Engineer
Date: 2025-08-27
"""

import asyncio
import json
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import subprocess

# Add path for imports
sys.path.insert(0, r'C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ui_testing_automation')

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('minimal_test.log'),
        logging.StreamHandler()
    ]
)

# Import framework components
from elements_extractor_no_llm import ElementsExtractorNoLLM, ExtractionConfig, ExtractedElement
from test_generation_with_llm import WorldClassTestGenerator, TestCategory, TestFramework
from code_generation_with_llm import CodeGenerationWithLLM
from base.llm import call_default_llm

logger = logging.getLogger(__name__)

class MinimalBaselineTest:
    """Minimal baseline test with live monitoring"""
    
    def __init__(self):
        self.test_url = "http://localhost:8888/minimal.html"
        self.results_dir = Path("./minimal_baseline_results")
        self.results_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.session_dir = self.results_dir / f"session_{self.timestamp}"
        self.session_dir.mkdir(exist_ok=True)
        
        logger.info(f"[INIT] Session directory: {self.session_dir}")
    
    async def extract_single_element(self) -> Dict[str, Any]:
        """Extract just the username field"""
        logger.info("[STAGE 1] Starting element extraction")
        logger.info(f"[URL] {self.test_url}")
        
        start_time = time.time()
        
        config = ExtractionConfig(
            max_elements=10,  # Very limited
            enable_screenshots=True,
            capture_screenshots=True,
            enable_stealth=False,
            timeout_seconds=30
        )
        
        extractor = ElementsExtractorNoLLM(config)
        
        try:
            logger.info("[EXTRACT] Initializing browser...")
            result = await extractor.extract_from_url(self.test_url)
            
            elapsed = time.time() - start_time
            logger.info(f"[EXTRACT] Completed in {elapsed:.2f}s")
            logger.info(f"[EXTRACT] Found {len(result.elements)} elements")
            
            # Find the username input
            username_elem = None
            for elem in result.elements:
                logger.info(f"  - Element: {elem.tag_name} #{elem.id} type={elem.element_type.value}")
                if elem.id == "username":
                    username_elem = elem
                    logger.info(f"[FOUND] Username field: {elem.selector}")
            
            # Save extraction results
            extraction_data = {
                "url": self.test_url,
                "extraction_time": elapsed,
                "total_elements": len(result.elements),
                "username_field": {
                    "found": username_elem is not None,
                    "selector": username_elem.selector if username_elem else None,
                    "id": username_elem.id if username_elem else None,
                    "type": username_elem.element_type.value if username_elem else None
                } if username_elem else None,
                "all_elements": [
                    {
                        "tag": elem.tag_name,
                        "id": elem.id,
                        "type": elem.element_type.value,
                        "text": elem.text[:50] if elem.text else None
                    } for elem in result.elements
                ]
            }
            
            # Save results
            with open(self.session_dir / "1_extraction.json", 'w') as f:
                json.dump(extraction_data, f, indent=2)
            
            await extractor.cleanup()
            
            if username_elem:
                return {"success": True, "element": username_elem, "all_elements": result.elements}
            else:
                logger.error("[ERROR] Username field not found!")
                return {"success": False, "error": "Username field not found"}
                
        except Exception as e:
            logger.error(f"[ERROR] Extraction failed: {e}")
            await extractor.cleanup()
            return {"success": False, "error": str(e)}
    
    async def test_llm_generation(self, element: Any) -> Dict[str, Any]:
        """Test LLM generation with live monitoring"""
        logger.info("[STAGE 2] Starting LLM test generation")
        logger.info("[LLM] This will use REAL LLM - monitoring responses...")
        
        start_time = time.time()
        
        # First, test direct LLM call
        logger.info("[LLM TEST] Testing direct LLM call first...")
        
        try:
            # Simple test message
            messages = [
                {"role": "system", "content": "You are a QA test generator. Be concise."},
                {"role": "user", "content": "Generate exactly 3 test cases for a username input field. Format as numbered list."}
            ]
            
            logger.info("[LLM] Sending test request...")
            llm_start = time.time()
            
            response = call_default_llm(messages)
            
            llm_time = time.time() - llm_start
            logger.info(f"[LLM] Response received in {llm_time:.2f}s")
            
            # Fix: LLMResponse is an object, need to access .content property
            response_content = response.content if hasattr(response, 'content') else str(response)
            logger.info(f"[LLM] Response length: {len(response_content)} characters")
            logger.info("[LLM] Response preview:")
            logger.info(response_content[:500] if len(response_content) > 500 else response_content)
            
            # Save LLM response
            with open(self.session_dir / "2_llm_test_response.txt", 'w') as f:
                f.write(f"Time: {llm_time:.2f}s\n\n")
                f.write(response_content)
            
        except Exception as e:
            logger.error(f"[LLM ERROR] Direct call failed: {e}")
        
        # Now test with WorldClassTestGenerator
        logger.info("[TEST GEN] Using WorldClassTestGenerator...")
        
        generator = WorldClassTestGenerator()
        
        try:
            # Create a minimal list with just the username element
            elements = [element]
            
            logger.info(f"[TEST GEN] Generating scenarios for 1 element")
            logger.info(f"[TEST GEN] Element: {element.selector} (type={element.element_type.value})")
            
            gen_start = time.time()
            
            # Generate with minimal configuration
            result = await generator.generate_from_elements(
                elements=elements,
                url=self.test_url,
                test_categories=[TestCategory.FUNCTIONAL],  # Just functional
                frameworks=[TestFramework.PLAYWRIGHT],
                enable_mcp=False,
                enable_self_healing=False
            )
            
            gen_time = time.time() - gen_start
            logger.info(f"[TEST GEN] Completed in {gen_time:.2f}s")
            logger.info(f"[TEST GEN] Generated {result.total_scenarios} scenarios")
            
            # Log scenarios
            for suite in result.test_suites:
                logger.info(f"[SUITE] {suite.name}")
                for scenario in suite.scenarios:
                    logger.info(f"  [SCENARIO] {scenario.name}")
                    logger.info(f"    Priority: {scenario.priority}")
                    logger.info(f"    Confidence: {scenario.confidence_score}")
                    logger.info(f"    Steps: {len(scenario.steps)}")
                    for i, step in enumerate(scenario.steps[:3], 1):
                        logger.info(f"      {i}. {step.keyword} {step.text}")
            
            # Save generation results
            generation_data = {
                "generation_time": gen_time,
                "total_scenarios": result.total_scenarios,
                "strategies_used": result.strategies_used,
                "scenarios": [
                    {
                        "name": scenario.name,
                        "category": scenario.category,
                        "priority": scenario.priority,
                        "confidence": scenario.confidence_score,
                        "steps": [
                            {"keyword": step.keyword, "text": step.text}
                            for step in scenario.steps
                        ]
                    }
                    for suite in result.test_suites
                    for scenario in suite.scenarios
                ]
            }
            
            with open(self.session_dir / "3_test_generation.json", 'w') as f:
                json.dump(generation_data, f, indent=2)
            
            return {"success": True, "result": result, "time": gen_time}
            
        except Exception as e:
            logger.error(f"[TEST GEN ERROR] Generation failed: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def test_code_generation(self, test_result: Any) -> Dict[str, Any]:
        """Test code generation with monitoring"""
        logger.info("[STAGE 3] Starting code generation")
        
        generator = CodeGenerationWithLLM()
        start_time = time.time()
        
        try:
            logger.info("[CODE GEN] Generating Python Playwright code...")
            
            # Take first test suite
            test_suite = test_result.test_suites[0]
            logger.info(f"[CODE GEN] Using suite: {test_suite.name}")
            logger.info(f"[CODE GEN] Scenarios: {len(test_suite.scenarios)}")
            
            code_result = await generator.generate_from_test_suite(
                test_suite=test_suite,
                framework="playwright",
                base_url=self.test_url
            )
            
            gen_time = time.time() - start_time
            logger.info(f"[CODE GEN] Completed in {gen_time:.2f}s")
            
            # Analyze generated code
            lines = code_result.code.split('\n')
            logger.info(f"[CODE GEN] Generated {len(lines)} lines of code")
            
            # Check code quality
            has_imports = any('import' in line for line in lines)
            has_class = any('class' in line for line in lines)
            has_async = any('async def' in line for line in lines)
            has_test = any('test_' in line for line in lines)
            has_assert = any('assert' in line or 'expect' in line for line in lines)
            
            logger.info("[CODE QUALITY]")
            logger.info(f"  - Has imports: {has_imports}")
            logger.info(f"  - Has class: {has_class}")
            logger.info(f"  - Has async: {has_async}")
            logger.info(f"  - Has test functions: {has_test}")
            logger.info(f"  - Has assertions: {has_assert}")
            
            # Save code
            code_file = self.session_dir / "4_generated_code.py"
            with open(code_file, 'w') as f:
                f.write(code_result.code)
            
            logger.info(f"[CODE GEN] Code saved to {code_file}")
            
            # Show first 20 lines
            logger.info("[CODE PREVIEW] First 20 lines:")
            for i, line in enumerate(lines[:20], 1):
                logger.info(f"  {i:3}: {line}")
            
            return {"success": True, "code": code_result.code, "time": gen_time}
            
        except Exception as e:
            logger.error(f"[CODE GEN ERROR] Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_minimal_test(self):
        """Run the minimal baseline test with proper circuit breakers"""
        logger.info("=" * 70)
        logger.info("MINIMAL BASELINE TEST - SINGLE USERNAME FIELD")
        logger.info("=" * 70)
        logger.info(f"URL: {self.test_url}")
        logger.info(f"Session: {self.session_dir}")
        logger.info("CIRCUIT BREAKER: Enabled - Any stage failure terminates workflow")
        logger.info("=" * 70)
        
        total_start = time.time()
        failed_stage = None
        
        try:
            # Stage 1: Extract element (CIRCUIT BREAKER)
            logger.info("[CIRCUIT BREAKER] Stage 1: Element Extraction")
            extraction = await self.extract_single_element()
            if not extraction["success"]:
                failed_stage = "extraction"
                error_msg = f"[CIRCUIT BREAKER TRIGGERED] Stage 1 FAILED: {extraction.get('error', 'Unknown error')}"
                logger.error(error_msg)
                logger.error("[TERMINATION] Workflow terminated due to extraction failure")
                
                # Save failure report
                failure_report = {
                    "timestamp": datetime.now().isoformat(),
                    "failed_stage": failed_stage,
                    "error": extraction.get('error', 'Unknown error'),
                    "total_time": time.time() - total_start,
                    "circuit_breaker_triggered": True
                }
                with open(self.session_dir / "FAILURE_REPORT.json", 'w') as f:
                    json.dump(failure_report, f, indent=2)
                
                return False
            
            logger.info("[CIRCUIT BREAKER] Stage 1 PASSED - Proceeding to Stage 2")
            
            # Stage 2: Generate tests (CIRCUIT BREAKER)
            logger.info("[CIRCUIT BREAKER] Stage 2: Test Generation")
            test_gen = await self.test_llm_generation(extraction["element"])
            if not test_gen["success"]:
                failed_stage = "test_generation"
                error_msg = f"[CIRCUIT BREAKER TRIGGERED] Stage 2 FAILED: {test_gen.get('error', 'Unknown error')}"
                logger.error(error_msg)
                logger.error("[TERMINATION] Workflow terminated due to test generation failure")
                
                # Save failure report
                failure_report = {
                    "timestamp": datetime.now().isoformat(),
                    "failed_stage": failed_stage,
                    "error": test_gen.get('error', 'Unknown error'),
                    "total_time": time.time() - total_start,
                    "circuit_breaker_triggered": True,
                    "completed_stages": ["extraction"]
                }
                with open(self.session_dir / "FAILURE_REPORT.json", 'w') as f:
                    json.dump(failure_report, f, indent=2)
                
                return False
            
            logger.info("[CIRCUIT BREAKER] Stage 2 PASSED - Proceeding to Stage 3")
            
            # Stage 3: Generate code (CIRCUIT BREAKER)
            logger.info("[CIRCUIT BREAKER] Stage 3: Code Generation")
            code_gen = await self.test_code_generation(test_gen["result"])
            if not code_gen["success"]:
                failed_stage = "code_generation"
                error_msg = f"[CIRCUIT BREAKER TRIGGERED] Stage 3 FAILED: {code_gen.get('error', 'Unknown error')}"
                logger.error(error_msg)
                logger.error("[TERMINATION] Workflow terminated due to code generation failure")
                
                # Save failure report
                failure_report = {
                    "timestamp": datetime.now().isoformat(),
                    "failed_stage": failed_stage,
                    "error": code_gen.get('error', 'Unknown error'),
                    "total_time": time.time() - total_start,
                    "circuit_breaker_triggered": True,
                    "completed_stages": ["extraction", "test_generation"]
                }
                with open(self.session_dir / "FAILURE_REPORT.json", 'w') as f:
                    json.dump(failure_report, f, indent=2)
                
                return False
            
            logger.info("[CIRCUIT BREAKER] Stage 3 PASSED - All stages completed successfully")
            
        except Exception as e:
            logger.error(f"[CIRCUIT BREAKER TRIGGERED] Unexpected error in stage: {e}")
            logger.error("[TERMINATION] Workflow terminated due to unexpected exception")
            
            # Save critical failure report
            failure_report = {
                "timestamp": datetime.now().isoformat(),
                "failed_stage": failed_stage or "unknown",
                "error": str(e),
                "error_type": "unexpected_exception",
                "total_time": time.time() - total_start,
                "circuit_breaker_triggered": True
            }
            with open(self.session_dir / "CRITICAL_FAILURE_REPORT.json", 'w') as f:
                json.dump(failure_report, f, indent=2)
            
            return False
        
        total_time = time.time() - total_start
        
        # Create success summary report
        logger.info("\n" + "=" * 70)
        logger.info("MINIMAL BASELINE TEST SUMMARY - ALL STAGES PASSED")
        logger.info("=" * 70)
        logger.info(f"Total Time: {total_time:.2f}s")
        logger.info(f"Extraction: {extraction.get('time', 'N/A')}s")
        logger.info(f"Test Generation: {test_gen.get('time', 'N/A')}s")
        logger.info(f"Code Generation: {code_gen.get('time', 'N/A')}s")
        logger.info("CIRCUIT BREAKER: No failures - Workflow completed successfully")
        logger.info("=" * 70)
        
        # Save comprehensive success summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_time": total_time,
            "circuit_breaker_triggered": False,
            "all_stages_passed": True,
            "stages": {
                "extraction": {
                    "success": extraction["success"], 
                    "time": extraction.get("time"),
                    "elements_found": len(extraction.get("all_elements", []))
                },
                "test_generation": {
                    "success": test_gen["success"], 
                    "time": test_gen.get("time"),
                    "scenarios_generated": test_gen["result"].total_scenarios if "result" in test_gen else 0
                },
                "code_generation": {
                    "success": code_gen["success"], 
                    "time": code_gen.get("time"),
                    "code_lines": len(code_gen.get("code", "").split('\n')) if "code" in code_gen else 0
                }
            },
            "session_dir": str(self.session_dir)
        }
        
        with open(self.session_dir / "SUCCESS_SUMMARY.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"[SUCCESS] All results saved to {self.session_dir}")
        return True

async def main():
    """Main entry point with server management"""
    
    # Start server
    logger.info("[SERVER] Starting HTTP server...")
    python_path = r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.venv\Scripts\python.exe"
    server_process = subprocess.Popen(
        [python_path, "test_baseline/server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    await asyncio.sleep(2)  # Wait for server
    
    try:
        # Run test
        tester = MinimalBaselineTest()
        success = await tester.run_minimal_test()
        
        if success:
            logger.info("[SUCCESS] Minimal baseline test completed!")
            return 0
        else:
            logger.error("[FAILURE] Test failed")
            return 1
            
    finally:
        # Stop server
        logger.info("[SERVER] Stopping...")
        server_process.terminate()
        await asyncio.sleep(1)

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))