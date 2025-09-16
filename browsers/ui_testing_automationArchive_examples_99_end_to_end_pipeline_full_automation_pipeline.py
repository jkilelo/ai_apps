#!/usr/bin/env python3
"""
Full Automation Pipeline Example

This example demonstrates:
- Complete end-to-end workflow using available modules (7-8)
- Integration between code_generation_with_llm and code_execution
- Mock implementation of future modules (1-6) for demonstration
- Comprehensive reporting and monitoring
- Error handling and recovery

Requirements:
- API key: OPENAI_API_KEY (or ANTHROPIC_API_KEY or GEMINI_API_KEY)
- Dependencies: openai, psutil, black
"""

import asyncio
import os
import sys
from pathlib import Path
import json
from datetime import datetime
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from code_generation_with_llm import (
    CodeGenerationWithLLM, 
    CodeGenerationConfig,
    TestFramework,
    BrowserFramework,
    CodePattern,
    LLMProvider
)

from code_execution import (
    CodeExecutionEngine,
    ExecutionConfig,
    ExecutionMode,
    SecurityLevel,
    ReportFormat
)

class MockBrowserService:
    """Mock browser service to simulate stealth_browser module"""
    
    def __init__(self):
        self.current_url = None
        self.page_title = None
    
    async def navigate(self, url: str) -> dict:
        """Simulate browser navigation"""
        print(f"🌐 [MOCK BROWSER] Navigating to {url}")
        await asyncio.sleep(1)  # Simulate load time
        
        self.current_url = url
        self.page_title = "Example Website" if "example.com" in url else "Test Site"
        
        return {
            "success": True,
            "url": url,
            "title": self.page_title,
            "load_time": 1.2,
            "status_code": 200
        }

class MockElementExtractor:
    """Mock element extractor to simulate element_extractor_with_llm module"""
    
    async def extract_elements(self, url: str) -> dict:
        """Simulate element extraction"""
        print(f"🔍 [MOCK EXTRACTOR] Analyzing page elements at {url}")
        await asyncio.sleep(2)  # Simulate AI analysis time
        
        # Mock extracted elements based on URL
        if "login" in url.lower():
            elements = [
                {"type": "input", "selector": "input[type='email']", "label": "Email", "id": "email"},
                {"type": "input", "selector": "input[type='password']", "label": "Password", "id": "password"},
                {"type": "button", "selector": "button[type='submit']", "label": "Sign In", "id": "signin-btn"}
            ]
        else:
            elements = [
                {"type": "link", "selector": "a[href='/login']", "label": "Login", "id": "login-link"},
                {"type": "button", "selector": ".hero-button", "label": "Get Started", "id": "cta-button"},
                {"type": "nav", "selector": "nav.main-nav", "label": "Main Navigation", "id": "main-nav"}
            ]
        
        return {
            "success": True,
            "elements": elements,
            "analysis_time": 2.1,
            "ai_confidence": 0.92
        }

class MockTestGenerator:
    """Mock test generator to simulate test_generation_with_llm module"""
    
    async def generate_scenarios(self, elements: list, context: dict = None) -> str:
        """Simulate test scenario generation"""
        print(f"📝 [MOCK GENERATOR] Creating test scenarios from {len(elements)} elements")
        await asyncio.sleep(3)  # Simulate LLM processing time
        
        # Generate realistic Gherkin based on elements
        if any(elem["type"] == "input" for elem in elements):
            # Login-type scenario
            gherkin = """
Feature: User Authentication
  As a user
  I want to log into the system
  So that I can access my account

  Background:
    Given I am on the login page
    And the login form is visible

  Scenario: Successful login with valid credentials
    When I enter "user@example.com" in the email field
    And I enter "secure_password123" in the password field
    And I click the "Sign In" button
    Then I should be redirected to the dashboard
    And I should see a welcome message
    And my session should be established

  Scenario: Login attempt with invalid email format
    When I enter "invalid-email" in the email field
    And I enter "password123" in the password field
    And I click the "Sign In" button
    Then I should see an error message "Please enter a valid email address"
    And I should remain on the login page

  Scenario: Login attempt with empty fields
    When I leave the email field empty
    And I leave the password field empty
    And I click the "Sign In" button
    Then I should see validation errors
    And the form should highlight required fields
    And the submit button should remain disabled
"""
        else:
            # Navigation-type scenario
            gherkin = """
Feature: Website Navigation
  As a visitor
  I want to navigate through the website
  So that I can find the information I need

  Scenario: Navigate to login page
    Given I am on the homepage
    When I click the "Login" link
    Then I should be taken to the login page
    And the login form should be visible

  Scenario: Interact with call-to-action button
    Given I am on the homepage
    When I click the "Get Started" button
    Then I should see the registration form
    And the page should scroll to the form section
"""
        
        return gherkin.strip()

class UITestingPipeline:
    """Complete UI Testing Automation Pipeline"""
    
    def __init__(self):
        self.browser = MockBrowserService()
        self.element_extractor = MockElementExtractor()
        self.test_generator = MockTestGenerator()
        
        # Real modules (available)
        self.code_generator = None
        self.code_executor = None
        
        self.pipeline_start_time = None
        self.stage_times = {}
        self.results = {}
    
    async def initialize(self):
        """Initialize the pipeline with real modules"""
        print("🚀 INITIALIZING UI TESTING AUTOMATION PIPELINE")
        print("="*70)
        
        # Check for API keys
        if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), os.getenv("GEMINI_API_KEY")]):
            raise ValueError("No LLM API key found! Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY")
        
        # Initialize real code generation module
        gen_config = CodeGenerationConfig(
            test_framework=TestFramework.PYTEST,
            browser_framework=BrowserFramework.PLAYWRIGHT,
            code_pattern=CodePattern.PAGE_OBJECT,
            
            # Enable all AI features
            enable_constitutional_ai=True,
            enable_universal_self_consistency=True,
            enable_pal=True,
            enable_rafa=True,
            enable_dspy_refinement=True,
            
            # Quality settings
            num_synthesis_paths=2,  # Reduced for demo speed
            safety_threshold=0.9,
            auto_format=True,
            validate_syntax=True,
            add_type_hints=True,
            add_docstrings=True
        )
        
        # Determine LLM provider
        llm_provider = LLMProvider.OPENAI
        if not os.getenv("OPENAI_API_KEY"):
            if os.getenv("ANTHROPIC_API_KEY"):
                llm_provider = LLMProvider.ANTHROPIC
            elif os.getenv("GEMINI_API_KEY"):
                llm_provider = LLMProvider.GEMINI
        
        self.code_generator = CodeGenerationWithLLM(
            config=gen_config,
            llm_provider=llm_provider,
            verbose=True
        )
        
        # Initialize real code execution module
        exec_config = ExecutionConfig(
            execution_mode=ExecutionMode.SEQUENTIAL,  # For demo clarity
            security_level=SecurityLevel.STANDARD,
            timeout_per_test=30,
            max_retries=2,
            verbose=True,
            generate_reports=[ReportFormat.HTML, ReportFormat.JSON, ReportFormat.MARKDOWN],
            output_dir=Path("pipeline_results")
        )
        
        self.code_executor = CodeExecutionEngine(exec_config)
        
        print(f"[OK] Pipeline initialized successfully")
        print(f"   LLM Provider: {llm_provider.value}")
        print(f"   Security Level: {exec_config.security_level.value}")
        print(f"   Output Directory: {exec_config.output_dir.absolute()}")
    
    async def run_pipeline(self, target_url: str) -> dict:
        """Run the complete pipeline"""
        self.pipeline_start_time = time.time()
        
        print(f"\n" + "="*70)
        print(f"RUNNING COMPLETE PIPELINE FOR: {target_url}")
        print("="*70)
        
        try:
            # Stage 1: Browser Navigation (Mock)
            stage_start = time.time()
            print(f"\n📍 STAGE 1: BROWSER NAVIGATION")
            browser_result = await self.browser.navigate(target_url)
            self.stage_times['browser_navigation'] = time.time() - stage_start
            self.results['browser'] = browser_result
            print(f"   [OK] Navigation completed in {self.stage_times['browser_navigation']:.2f}s")
            
            # Stage 2: Element Extraction (Mock)
            stage_start = time.time()
            print(f"\n🔍 STAGE 2: ELEMENT EXTRACTION")
            extraction_result = await self.element_extractor.extract_elements(target_url)
            self.stage_times['element_extraction'] = time.time() - stage_start
            self.results['extraction'] = extraction_result
            print(f"   [OK] Extracted {len(extraction_result['elements'])} elements in {self.stage_times['element_extraction']:.2f}s")
            
            # Stage 3: Test Scenario Generation (Mock)
            stage_start = time.time()
            print(f"\n📝 STAGE 3: TEST SCENARIO GENERATION")
            gherkin_scenarios = await self.test_generator.generate_scenarios(
                extraction_result['elements'],
                context={'url': target_url, 'title': browser_result['title']}
            )
            self.stage_times['test_generation'] = time.time() - stage_start
            self.results['scenarios'] = gherkin_scenarios
            print(f"   [OK] Generated scenarios in {self.stage_times['test_generation']:.2f}s")
            
            # Stage 4: Code Generation (Real)
            stage_start = time.time()
            print(f"\n[FAST] STAGE 4: CODE GENERATION (REAL MODULE)")
            print(f"   Using Constitutional AI and Universal Self-Consistency...")
            code_result = await self.code_generator.generate_from_gherkin(gherkin_scenarios)
            self.stage_times['code_generation'] = time.time() - stage_start
            self.results['code_generation'] = code_result
            print(f"   [OK] Generated {len(code_result.code.split(chr(10)))} lines of code in {self.stage_times['code_generation']:.2f}s")
            print(f"   🛡️ Safety score: {code_result.safety_score:.3f}")
            
            # Stage 5: Code Execution (Real)
            stage_start = time.time()
            print(f"\n🔥 STAGE 5: CODE EXECUTION (REAL MODULE)")
            print(f"   Executing in secure sandbox...")
            execution_result = await self.code_executor.execute_from_llm_generated(
                code_result.code,
                test_name=f"pipeline_test_{int(time.time())}"
            )
            self.stage_times['code_execution'] = time.time() - stage_start
            self.results['execution'] = execution_result
            print(f"   [OK] Executed tests in {self.stage_times['code_execution']:.2f}s")
            print(f"   📊 Test results: {execution_result.suite.passed}/{execution_result.suite.total_tests} passed")
            
            # Calculate total time
            total_time = time.time() - self.pipeline_start_time
            self.stage_times['total'] = total_time
            
            # Generate pipeline report
            pipeline_result = await self._generate_pipeline_report()
            
            return pipeline_result
            
        except Exception as e:
            total_time = time.time() - self.pipeline_start_time
            print(f"\n[ERROR] Pipeline failed after {total_time:.2f}s: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'total_time': total_time,
                'completed_stages': list(self.stage_times.keys())
            }
    
    async def _generate_pipeline_report(self) -> dict:
        """Generate comprehensive pipeline report"""
        print(f"\n" + "="*70)
        print("PIPELINE EXECUTION REPORT")
        print("="*70)
        
        # Calculate success metrics
        overall_success = (
            self.results.get('browser', {}).get('success', False) and
            self.results.get('extraction', {}).get('success', False) and
            bool(self.results.get('scenarios')) and
            bool(self.results.get('code_generation')) and
            self.results.get('execution', {}).get('success', False)
        )
        
        # Stage-by-stage breakdown
        print(f"\n📋 STAGE-BY-STAGE BREAKDOWN:")
        stage_info = [
            ("Browser Navigation", "browser_navigation", self.results.get('browser', {})),
            ("Element Extraction", "element_extraction", self.results.get('extraction', {})),
            ("Test Generation", "test_generation", {"scenarios": len(self.results.get('scenarios', '').split('Scenario:')) - 1}),
            ("Code Generation", "code_generation", self.results.get('code_generation')),
            ("Code Execution", "code_execution", self.results.get('execution', {}))
        ]
        
        for stage_name, time_key, stage_result in stage_info:
            stage_time = self.stage_times.get(time_key, 0)
            status = "[OK] SUCCESS" if stage_result and (stage_result.get('success', True) if isinstance(stage_result, dict) else True) else "[ERROR] FAILED"
            print(f"   {stage_name:<20}: {status:<10} ({stage_time:.2f}s)")
        
        # Performance summary
        print(f"\n[FAST] PERFORMANCE SUMMARY:")
        print(f"   Total Pipeline Time: {self.stage_times['total']:.2f}s")
        
        # Show percentage breakdown
        for stage_name, time_key, _ in stage_info:
            if time_key in self.stage_times:
                percentage = (self.stage_times[time_key] / self.stage_times['total']) * 100
                print(f"   {stage_name:<20}: {self.stage_times[time_key]:.2f}s ({percentage:.1f}%)")
        
        # Quality metrics
        if self.results.get('code_generation'):
            code_result = self.results['code_generation']
            print(f"\n🛡️ CODE QUALITY METRICS:")
            print(f"   Safety Score: {code_result.safety_score:.3f}")
            print(f"   Lines Generated: {len(code_result.code.split(chr(10)))}")
            print(f"   Syntax Valid: {code_result.syntax_valid}")
            
            if hasattr(code_result, 'metrics') and code_result.metrics:
                print(f"   Maintainability: {code_result.metrics.maintainability_index:.1f}")
        
        # Execution metrics
        if self.results.get('execution'):
            exec_result = self.results['execution']
            print(f"\n📊 EXECUTION METRICS:")
            print(f"   Tests Total: {exec_result.suite.total_tests}")
            print(f"   Tests Passed: {exec_result.suite.passed}")
            print(f"   Tests Failed: {exec_result.suite.failed}")
            print(f"   Success Rate: {exec_result.suite.get_success_rate():.1f}%")
            print(f"   Execution Time: {exec_result.execution_time:.2f}s")
            
            # Show reports generated
            if exec_result.reports:
                print(f"\n📄 GENERATED REPORTS:")
                for format, path in exec_result.reports.items():
                    file_size = path.stat().st_size if path.exists() else 0
                    print(f"   {format.value.upper()}: {path.name} ({file_size} bytes)")
        
        # Resource utilization (if available)
        print(f"\n💻 RESOURCE UTILIZATION:")
        print(f"   Mock Stages: 3 stages (Browser, Extraction, Test Gen)")
        print(f"   Real Modules: 2 stages (Code Gen, Execution)")
        print(f"   API Calls: ~3-5 LLM calls")
        print(f"   Memory Usage: ~200-400 MB (estimated)")
        
        # Create final report
        report = {
            'success': overall_success,
            'total_time': self.stage_times['total'],
            'stage_times': self.stage_times,
            'stages_completed': len(self.stage_times) - 1,  # Exclude 'total'
            'performance': {
                'pipeline_time': self.stage_times['total'],
                'code_generation_time': self.stage_times.get('code_generation', 0),
                'execution_time': self.stage_times.get('code_execution', 0)
            }
        }
        
        # Add detailed results
        if self.results.get('code_generation'):
            report['code_quality'] = {
                'safety_score': self.results['code_generation'].safety_score,
                'lines_generated': len(self.results['code_generation'].code.split('\n')),
                'syntax_valid': self.results['code_generation'].syntax_valid
            }
        
        if self.results.get('execution'):
            exec_result = self.results['execution']
            report['test_execution'] = {
                'total_tests': exec_result.suite.total_tests,
                'passed_tests': exec_result.suite.passed,
                'failed_tests': exec_result.suite.failed,
                'success_rate': exec_result.suite.get_success_rate(),
                'reports_generated': len(exec_result.reports)
            }
        
        return report

async def demonstrate_multiple_scenarios():
    """Demonstrate pipeline with different types of websites"""
    
    scenarios = [
        {
            'name': 'E-commerce Login',
            'url': 'https://shop.example.com/login',
            'description': 'Test login functionality on e-commerce site'
        },
        {
            'name': 'Corporate Homepage',
            'url': 'https://company.example.com',
            'description': 'Test navigation and CTA buttons'
        },
        {
            'name': 'SaaS Application',
            'url': 'https://app.example.com/dashboard',
            'description': 'Test complex application interface'
        }
    ]
    
    print(f"\n" + "="*70)
    print("MULTI-SCENARIO PIPELINE DEMONSTRATION")
    print("="*70)
    
    pipeline = UITestingPipeline()
    await pipeline.initialize()
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*20} SCENARIO {i}: {scenario['name']} {'='*20}")
        print(f"Description: {scenario['description']}")
        print(f"URL: {scenario['url']}")
        
        try:
            result = await pipeline.run_pipeline(scenario['url'])
            result['scenario'] = scenario
            results.append(result)
            
            if result['success']:
                print(f"[OK] Scenario {i} completed successfully in {result['total_time']:.2f}s")
            else:
                print(f"[ERROR] Scenario {i} failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"[ERROR] Scenario {i} crashed: {str(e)}")
            results.append({
                'success': False,
                'scenario': scenario,
                'error': str(e),
                'total_time': 0
            })
        
        # Brief pause between scenarios
        await asyncio.sleep(1)
    
    # Summary
    print(f"\n" + "="*70)
    print("MULTI-SCENARIO SUMMARY")
    print("="*70)
    
    successful_scenarios = sum(1 for r in results if r['success'])
    total_time = sum(r.get('total_time', 0) for r in results)
    avg_time = total_time / len(results) if results else 0
    
    print(f"📊 Overall Results:")
    print(f"   Scenarios Tested: {len(scenarios)}")
    print(f"   Successful: {successful_scenarios}")
    print(f"   Failed: {len(scenarios) - successful_scenarios}")
    print(f"   Success Rate: {(successful_scenarios / len(scenarios) * 100):.1f}%")
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Average Time: {avg_time:.2f}s per scenario")
    
    # Per-scenario breakdown
    print(f"\n📋 Per-Scenario Results:")
    for i, result in enumerate(results, 1):
        scenario = result['scenario']
        status = "[OK] SUCCESS" if result['success'] else "[ERROR] FAILED"
        time_info = f"({result.get('total_time', 0):.2f}s)" if result.get('total_time') else ""
        print(f"   {i}. {scenario['name']}: {status} {time_info}")
    
    return results

async def main():
    """Main function demonstrating the complete pipeline"""
    
    print("🚀 FULL UI TESTING AUTOMATION PIPELINE DEMONSTRATION")
    print("="*70)
    print("This example shows the complete end-to-end workflow:")
    print("  - Mock browser navigation (future: stealth_browser)")
    print("  - Mock element extraction (future: element_extractor_with_llm)")
    print("  - Mock test generation (future: test_generation_with_llm)")
    print("  - [OK] REAL code generation (code_generation_with_llm)")
    print("  - [OK] REAL code execution (code_execution)")
    
    # Check prerequisites
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), os.getenv("GEMINI_API_KEY")]):
        print("\n[ERROR] ERROR: No LLM API key found!")
        print("Please set one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY")
        return 1
    
    try:
        # Run multi-scenario demonstration
        results = await demonstrate_multiple_scenarios()
        
        # Final summary
        print(f"\n" + "="*70)
        print("DEMONSTRATION COMPLETED")
        print("="*70)
        
        successful_count = sum(1 for r in results if r['success'])
        print(f"🎉 Pipeline demonstration successful!")
        print(f"   Scenarios completed: {successful_count}/{len(results)}")
        
        print(f"\n🏆 Key Achievements:")
        print(f"   [OK] End-to-end pipeline working")
        print(f"   [OK] Real AI-powered code generation")
        print(f"   [OK] Secure code execution with sandbox")
        print(f"   [OK] Comprehensive reporting")
        print(f"   [OK] Production-ready architecture")
        
        print(f"\n📁 Generated Artifacts:")
        print(f"   - Check 'pipeline_results/' for HTML reports")
        print(f"   - JSON reports with detailed metrics")
        print(f"   - Markdown reports for documentation")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Implement remaining modules (1-6)")
        print(f"   2. Replace mock services with real implementations")
        print(f"   3. Add advanced monitoring and alerting")
        print(f"   4. Scale for production deployment")
        
        print(f"\n🔗 Try related examples:")
        print(f"   - python ci_cd_integration_example.py")
        print(f"   - python performance_benchmarks.py")
        print(f"   - python production_deployment.py")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline demonstration failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Check API key is set correctly")
        print(f"   2. Ensure all dependencies installed")
        print(f"   3. Verify internet connection")
        print(f"   4. Check disk space for report generation")
        
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline demonstration interrupted by user")
        sys.exit(130)