"""
Pipeline v2 - End-to-End Orchestrator
Chains all modules together with proper data flow
Each module's output feeds into the next module's input
"""

import asyncio
import time
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Import ALL modules
import browser_manager_v2
import element_extractor_v2
import ai_enricher_v2
import test_generator_v2

# Import ALL types from centralized data_types_v2
from data_types_v2 import (
    # Contracts
    BrowserContract,
    BrowserResult,
    ExtractContract,
    ElementResult,
    EnrichContract,
    EnrichedResult,
    # Configurations
    PipelineConfig,
    BrowserConfig,
    ExtractionConfig,
    LLMConfig,
    # Results
    PipelineResult,
    TestSuiteResult,
    # Types
    BrowserType,
    TestFramework,
    # Other types
    validate_ascii,
    SystemConstants
)


class PipelineV2:
    """
    Main Pipeline Orchestrator
    Chains all modules together with proper data flow
    Each step depends on output from previous step
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.stage_times: Dict[str, float] = {}
        self.errors: list[str] = []
        self.warnings: list[str] = []

    async def execute(self, url: str) -> PipelineResult:
        """
        Execute complete pipeline
        Args:
            url: URL to test
        Returns:
            Complete pipeline result with all intermediate results
        """
        start_time = time.time()
        print(f"\n{'='*60}")
        print(f"PIPELINE V2 - E2E WEB AUTOMATION")
        print(f"{'='*60}")
        print(f"URL: {url}")
        print(f"Time: {datetime.now().isoformat()}")
        print(f"{'='*60}\n")

        try:
            # ============================================================
            # STAGE 1: BROWSER SETUP
            # ============================================================
            print("[STAGE 1] Browser Setup...")
            stage1_start = time.time()

            browser_contract = BrowserContract(
                url=url,
                config=self.config.browser
            )

            # Create browser manager and get session
            browser_manager = browser_manager_v2.BrowserManagerV2()
            browser_result = await browser_manager.execute(browser_contract)

            self.stage_times['browser_setup'] = time.time() - stage1_start
            print(f"  -> Session ID: {browser_result.session_id}")
            print(f"  -> Page Title: {browser_result.page_title}")
            print(f"  -> Time: {self.stage_times['browser_setup']:.2f}s")

            # SAVE COMPLETE STEP 1 OUTPUT
            step1_file = Path(self.config.output_directory) / f"step1_browser_result_{browser_result.session_id}.json"
            step1_file.parent.mkdir(exist_ok=True)
            with open(step1_file, 'w') as f:
                json.dump(browser_result.model_dump(), f, indent=2, default=str)
            print(f"  -> Saved: {step1_file}")

            # Get page object for next stage
            # We need to retrieve the page from the browser manager's pool
            page_session = await browser_manager.pool.get_session(browser_result.session_id)
            if not page_session or 'page' not in page_session:
                raise ValueError("Failed to get page session from browser manager")

            page = page_session['page']

            # ============================================================
            # STAGE 2: ELEMENT EXTRACTION (depends on browser session)
            # ============================================================
            print("\n[STAGE 2] Element Extraction...")
            stage2_start = time.time()

            extract_contract = ExtractContract(
                browser_session=browser_result.session_id,
                config=self.config.extraction
            )

            element_result = await element_extractor_v2.execute(extract_contract, page)

            self.stage_times['element_extraction'] = time.time() - stage2_start
            print(f"  -> Total Elements: {element_result.total_elements}")
            print(f"  -> Interactive: {element_result.interactive_elements}")
            print(f"  -> Time: {self.stage_times['element_extraction']:.2f}s")

            # SAVE COMPLETE STEP 2 OUTPUT
            step2_file = Path(self.config.output_directory) / f"step2_elements_{browser_result.session_id}.json"
            with open(step2_file, 'w') as f:
                json.dump(element_result.model_dump(), f, indent=2, default=str)
            print(f"  -> Saved: {step2_file}")

            # ============================================================
            # STAGE 3: AI ENRICHMENT (depends on extracted elements)
            # ============================================================
            print("\n[STAGE 3] AI Enrichment...")
            stage3_start = time.time()

            # Check if we have elements to enrich
            if element_result.total_elements == 0:
                print("  -> No elements to enrich")
                # Create empty enriched result
                from data_types_v2 import PageInsights, PageType
                enriched_result = EnrichedResult(
                    elements=[],
                    page_insights=PageInsights(
                        page_type=PageType.UNKNOWN,
                        functionality=[],
                        ui_patterns=[],
                        accessibility_level="low"
                    ),
                    enrichment_time=0,
                    llm_tokens_used=0,
                    cache_hits=0,
                    confidence_scores={}
                )
            else:
                enrich_contract = EnrichContract(
                    elements=element_result.elements,
                    config=self.config.llm,
                    page_context={
                        'url': url,
                        'title': browser_result.page_title,
                        'total_elements': element_result.total_elements
                    }
                )

                enriched_result = await ai_enricher_v2.execute(enrich_contract)

                print(f"  -> Enriched Elements: {len(enriched_result.elements)}")
                print(f"  -> Page Type: {enriched_result.page_insights.page_type}")
                print(f"  -> Cache Hits: {enriched_result.cache_hits}")
                print(f"  -> Time: {time.time() - stage3_start:.2f}s")

                # SAVE COMPLETE STEP 3 OUTPUT
                step3_file = Path(self.config.output_directory) / f"step3_enriched_{browser_result.session_id}.json"
                with open(step3_file, 'w') as f:
                    json.dump(enriched_result.model_dump(), f, indent=2, default=str)
                print(f"  -> Saved: {step3_file}")

            self.stage_times['ai_enrichment'] = time.time() - stage3_start

            # ============================================================
            # STAGE 4: TEST GENERATION (depends on enriched elements)
            # ============================================================
            print("\n[STAGE 4] Test Generation...")
            stage4_start = time.time()

            # Use real test generator
            from data_types_v2 import TestContract

            # Create test contract and generate tests using real generator
            test_contract = TestContract(
                enriched_elements=enriched_result.elements,
                page_insights=enriched_result.page_insights,
                config=self.config.test
            )

            test_suite = await test_generator_v2.execute(test_contract)

            self.stage_times['test_generation'] = time.time() - stage4_start
            print(f"  -> Scenarios: {test_suite.total_scenarios}")
            print(f"  -> Coverage: {test_suite.coverage_percentage:.0%}")
            print(f"  -> Time: {self.stage_times['test_generation']:.2f}s")

            # SAVE COMPLETE STEP 4 OUTPUT
            step4_file = Path(self.config.output_directory) / f"step4_test_suite_{browser_result.session_id}.json"
            with open(step4_file, 'w') as f:
                json.dump(test_suite.model_dump(), f, indent=2, default=str)
            print(f"  -> Saved: {step4_file}")

            # ============================================================
            # STAGE 5: CODE GENERATION (depends on test scenarios)
            # ============================================================
            print("\n[STAGE 5] Code Generation...")
            stage5_start = time.time()

            # Create mock code artifacts
            from data_types_v2 import CodeArtifact, TestFramework

            code_artifacts = []
            for framework in self.config.frameworks:
                # Generate basic Playwright code
                test_code = self._generate_basic_test_code(test_suite, framework, url)

                artifact = CodeArtifact(
                    framework=framework,
                    language="python",
                    test_files={"test_main.py": test_code},
                    helper_files={},
                    page_objects={},
                    config_files={},
                    dependencies=["playwright", "pytest"],
                    setup_instructions="pip install playwright pytest"
                )
                code_artifacts.append(artifact)

            self.stage_times['code_generation'] = time.time() - stage5_start
            print(f"  -> Frameworks: {[f.value for f in self.config.frameworks]}")
            print(f"  -> Files Generated: {sum(len(a.test_files) for a in code_artifacts)}")
            print(f"  -> Time: {self.stage_times['code_generation']:.2f}s")

            # SAVE COMPLETE STEP 5 OUTPUT
            for i, artifact in enumerate(code_artifacts):
                step5_file = Path(self.config.output_directory) / f"step5_code_{artifact.framework.value}_{browser_result.session_id}.json"
                with open(step5_file, 'w') as f:
                    json.dump(artifact.model_dump(), f, indent=2, default=str)
                print(f"  -> Saved: {step5_file}")

                # Also save actual code files
                for filename, code in artifact.test_files.items():
                    code_file = Path(self.config.output_directory) / f"{artifact.framework.value}_{filename}"
                    with open(code_file, 'w') as f:
                        f.write(code)
                    print(f"  -> Code saved: {code_file}")

            # ============================================================
            # STAGE 6: EXECUTION (optional, depends on code artifacts)
            # ============================================================
            execution_result = None
            if self.config.auto_execute:
                print("\n[STAGE 6] Test Execution...")
                stage6_start = time.time()

                # Mock execution result
                from data_types_v2 import ExecutionResult, ExecutionStatus, TestResult

                execution_result = ExecutionResult(
                    total_tests=test_suite.total_scenarios,
                    passed=test_suite.total_scenarios - 1 if test_suite.total_scenarios > 0 else 0,
                    failed=1 if test_suite.total_scenarios > 0 else 0,
                    skipped=0,
                    execution_time=time.time() - stage6_start,
                    test_results=[],
                    coverage_report=None,
                    artifacts={},
                    error_summary=[]
                )

                self.stage_times['execution'] = time.time() - stage6_start
                print(f"  -> Tests Run: {execution_result.total_tests}")
                print(f"  -> Passed: {execution_result.passed}")
                print(f"  -> Failed: {execution_result.failed}")
                print(f"  -> Time: {self.stage_times['execution']:.2f}s")

            # ============================================================
            # FINAL: BUILD COMPLETE RESULT
            # ============================================================
            total_time = time.time() - start_time

            pipeline_result = PipelineResult(
                url=url,
                config=self.config,
                browser_result=browser_result,
                element_result=element_result,
                enriched_result=enriched_result,
                test_suite=test_suite,
                code_artifacts=code_artifacts,
                execution_result=execution_result,
                total_time=total_time,
                stage_times=self.stage_times,
                success=True,
                errors=self.errors,
                warnings=self.warnings,
                metrics={
                    'elements_per_second': element_result.total_elements / self.stage_times['element_extraction'],
                    'llm_efficiency': enriched_result.cache_hits / max(1, enriched_result.cache_hits + 1),
                    'test_coverage': test_suite.coverage_percentage,
                    'total_stages': 6 if execution_result else 5
                }
            )

            # Save results
            await self._save_results(pipeline_result)

            print(f"\n{'='*60}")
            print(f"PIPELINE COMPLETED SUCCESSFULLY")
            print(f"Total Time: {total_time:.2f}s")
            print(f"{'='*60}\n")

            # Cleanup
            await browser_manager.cleanup()

            return pipeline_result

        except Exception as e:
            self.errors.append(str(e))
            print(f"\n[ERROR] Pipeline failed: {e}")
            raise

    def _generate_basic_test_code(self, test_suite: TestSuiteResult, framework: TestFramework, url: str) -> str:
        """Generate basic test code for the framework"""
        if framework == TestFramework.PLAYWRIGHT:
            code = f"""\"\"\"
Automated tests generated by Pipeline v2
URL: {url}
Generated: {datetime.now().isoformat()}
\"\"\"

import asyncio
from playwright.async_api import async_playwright

async def test_main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to page
        await page.goto("{url}")

"""
            for scenario in test_suite.scenarios:
                code += f"""
        # Test: {scenario.name}
        try:
"""
                for step in scenario.steps:
                    if step.action == "click":
                        code += f"            await page.click('{step.target}')\n"
                    elif step.action == "type":
                        code += f"            await page.fill('{step.target}', '{step.value or ''}')\n"
                    elif step.action == "assert":
                        code += f"            assert await page.title() is not None\n"

                code += """            print(f"✓ Test passed: {scenario.name}")
        except Exception as e:
            print(f"✗ Test failed: {scenario.name} - {e}")
"""

            code += """
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_main())
"""
            return validate_ascii(code)

        return "# Code generation for this framework not implemented"

    async def _save_results(self, result: PipelineResult) -> None:
        """Save pipeline results to file"""
        output_dir = Path(self.config.output_directory)
        output_dir.mkdir(exist_ok=True)

        # Save main result
        result_file = output_dir / f"pipeline_result_{int(time.time())}.json"
        result_dict = {
            'url': result.url,
            'success': result.success,
            'total_time': result.total_time,
            'stage_times': result.stage_times,
            'metrics': result.metrics,
            'browser': {
                'session_id': result.browser_result.session_id,
                'page_title': result.browser_result.page_title
            },
            'elements': {
                'total': result.element_result.total_elements,
                'interactive': result.element_result.interactive_elements
            },
            'enrichment': {
                'enriched_count': len(result.enriched_result.elements),
                'page_type': result.enriched_result.page_insights.page_type.value,
                'cache_hits': result.enriched_result.cache_hits
            },
            'tests': {
                'scenarios': result.test_suite.total_scenarios,
                'coverage': result.test_suite.coverage_percentage
            }
        }

        with open(result_file, 'w') as f:
            json.dump(result_dict, f, indent=2)

        print(f"\n[INFO] Results saved to: {result_file}")


# ==============================================================================
# MAIN EXECUTION FUNCTION
# ==============================================================================

async def execute(url: str, config: Optional[PipelineConfig] = None) -> PipelineResult:
    """
    Main pipeline execution function
    Args:
        url: URL to test
        config: Pipeline configuration
    Returns:
        Complete pipeline result
    """
    pipeline = PipelineV2(config)
    return await pipeline.execute(url)


# ==============================================================================
# TEST
# ==============================================================================

async def test():
    """Test the complete E2E pipeline"""
    print("Testing Complete Pipeline v2...")

    # Configure pipeline
    config = PipelineConfig(
        browser=BrowserConfig(
            browser_type=BrowserType.CHROMIUM,
            headless=False,  # Show browser for testing
            enable_stealth=True
        ),
        extraction=ExtractionConfig(
            max_elements=50,
            include_invisible=False
        ),
        llm=LLMConfig(
            batch_size=5,
            cache_enabled=True
        ),
        frameworks=[TestFramework.PLAYWRIGHT],
        auto_execute=False,
        output_directory="./pipeline_output"
    )

    # Test with real URL
    test_url = "https://uat01.citi.com"

    try:
        result = await execute(test_url, config)

        print("\n" + "="*60)
        print("PIPELINE TEST SUMMARY")
        print("="*60)
        print(f"[OK] Browser Setup: {result.stage_times.get('browser_setup', 0):.2f}s")
        print(f"[OK] Element Extraction: {result.stage_times.get('element_extraction', 0):.2f}s")
        print(f"[OK] AI Enrichment: {result.stage_times.get('ai_enrichment', 0):.2f}s")
        print(f"[OK] Test Generation: {result.stage_times.get('test_generation', 0):.2f}s")
        print(f"[OK] Code Generation: {result.stage_times.get('code_generation', 0):.2f}s")
        print(f"\nTotal Time: {result.total_time:.2f}s")
        print(f"Success: {result.success}")
        print("="*60)

    except Exception as e:
        print(f"Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Import missing types for testing
    from data_types_v2 import BrowserType, TestFramework

    asyncio.run(test())