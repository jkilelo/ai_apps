#!/usr/bin/env python3
"""
Consolidated Test Suite for UI Testing Framework
Combines all essential tests in one clean file
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Import modules to test
from step3_code_generator import (
    PythonTestCodeGenerator, TestCodeConfig, TestFramework, 
    BrowserFramework, GherkinParser, StepMapper
)
from step4_test_executor import (
    TestExecutor, ExecutionConfig, ExecutionMode,
    ReportFormat, TestStatus, TestResult
)

# ============================================================================
# STEP 3: CODE GENERATOR TESTS
# ============================================================================

class TestCodeGenerator:
    """Essential tests for Python code generation"""
    
    @pytest.fixture
    def sample_gherkin(self):
        return """
        Feature: User Login
          Scenario: Successful login
            Given the user is on login page
            When the user enters "test@example.com" in email field
            And the user enters "password123" in password field
            And the user clicks "Login" button
            Then the user should see dashboard
        """
    
    @pytest.fixture
    def sample_elements(self):
        return [
            {"tag_name": "input", "element_id": "email", "element_type": "email"},
            {"tag_name": "input", "element_id": "password", "element_type": "password"},
            {"tag_name": "button", "text_content": "Login", "is_clickable": True}
        ]
    
    def test_gherkin_parsing(self, sample_gherkin):
        """Test Gherkin content parsing"""
        parser = GherkinParser()
        feature = parser.parse_feature_content(sample_gherkin)
        
        assert feature is not None
        assert feature.name == "User Login"
        assert len(feature.scenarios) == 1
        assert len(feature.scenarios[0].steps) == 5
    
    def test_step_mapping(self):
        """Test step to action mapping"""
        mapper = StepMapper(BrowserFramework.PLAYWRIGHT)
        
        # Test navigation
        from step3_code_generator import GherkinStep
        step = GherkinStep("Given", 'user navigates to "https://example.com"', ["https://example.com"])
        action, params = mapper.map_step_to_action(step)
        assert action == "navigate_to"
        assert params == ["https://example.com"]
        
        # Test click
        step = GherkinStep("When", 'user clicks "Login" button', ["Login"])
        action, params = mapper.map_step_to_action(step)
        assert action == "click_element"
    
    def test_code_generation(self, sample_gherkin, sample_elements):
        """Test complete code generation"""
        config = TestCodeConfig(
            test_framework=TestFramework.PYTEST,
            browser_framework=BrowserFramework.PLAYWRIGHT
        )
        generator = PythonTestCodeGenerator(config)
        
        # Parse and generate
        feature = generator.parser.parse_feature_content(sample_gherkin)
        code = generator._generate_test_file(feature)
        
        # Verify code structure
        assert "import pytest" in code
        assert "class TestUserLogin" in code
        assert "async def test_successful_login" in code
        
        # Verify syntax
        try:
            compile(code, '<string>', 'exec')
            syntax_valid = True
        except SyntaxError:
            syntax_valid = False
        assert syntax_valid, "Generated code has syntax errors"
    
    def test_page_object_generation(self, sample_elements):
        """Test Page Object Model generation"""
        config = TestCodeConfig(generate_page_objects=True)
        generator = PythonTestCodeGenerator(config)
        
        from step3_code_generator import GherkinFeature
        feature = GherkinFeature("Login Page", "", [])
        
        page_object = generator._generate_page_object(feature, sample_elements)
        
        assert "class LoginPagePage(BasePage):" in page_object
        assert "email" in page_object
        assert "password" in page_object

# ============================================================================
# STEP 4: TEST EXECUTOR TESTS
# ============================================================================

class TestExecutor:
    """Essential tests for test execution engine"""
    
    @pytest.fixture
    def temp_test_dir(self):
        """Create temporary test directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "tests"
            test_dir.mkdir()
            
            # Create sample test file
            test_file = test_dir / "test_sample.py"
            test_file.write_text('''
import pytest

def test_pass():
    assert True

def test_fail():
    assert False
''')
            yield test_dir
    
    @pytest.fixture
    def execution_config(self, temp_test_dir):
        """Test execution configuration"""
        return ExecutionConfig(
            test_dir=temp_test_dir,
            output_dir=temp_test_dir / "results",
            execution_mode=ExecutionMode.SEQUENTIAL,
            timeout_per_test=10
        )
    
    def test_test_discovery(self, temp_test_dir, execution_config):
        """Test discovering test files"""
        from step4_test_executor import TestDiscovery
        
        discovery = TestDiscovery(execution_config)
        test_files = discovery.discover_tests()
        
        assert len(test_files) == 1
        assert "test_sample.py" in str(test_files[0])
    
    @pytest.mark.asyncio
    async def test_sequential_execution(self, execution_config):
        """Test sequential test execution"""
        from step4_test_executor import TestRunner
        
        runner = TestRunner(execution_config)
        
        with patch.object(runner, '_run_single_test_file', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = TestResult(
                test_name="test",
                test_file="test.py",
                status=TestStatus.PASSED,
                duration=1.0,
                start_time=datetime.now(),
                end_time=datetime.now()
            )
            
            test_files = [Path("test1.py"), Path("test2.py")]
            suite = await runner.execute_tests(test_files)
            
            assert mock_run.call_count == 2
            assert suite.total_tests == 2
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test parallel test execution"""
        config = ExecutionConfig(
            execution_mode=ExecutionMode.PARALLEL,
            parallel_workers=4
        )
        from step4_test_executor import TestRunner
        runner = TestRunner(config)
        
        # Mock execution
        async def mock_run(test_file):
            await asyncio.sleep(0.01)
            return TestResult(
                test_name=test_file.stem,
                test_file=str(test_file),
                status=TestStatus.PASSED,
                duration=0.01,
                start_time=datetime.now(),
                end_time=datetime.now()
            )
        
        with patch.object(runner, '_run_single_test_file', side_effect=mock_run):
            test_files = [Path(f"test{i}.py") for i in range(8)]
            
            start = asyncio.get_event_loop().time()
            await runner.execute_tests(test_files)
            duration = asyncio.get_event_loop().time() - start
            
            # Should be faster than sequential (8 * 0.01 = 0.08s)
            assert duration < 0.05  # With 4 workers, should take ~0.02s
    
    def test_report_generation(self, execution_config):
        """Test report generation"""
        from step4_test_executor import ReportGenerator, TestSuite
        
        suite = TestSuite(
            name="Test Suite",
            test_files=[Path("test.py")],
            total_tests=2,
            passed=1,
            failed=1,
            skipped=0,
            errors=0,
            duration=1.5
        )
        
        results = [
            TestResult("test_pass", "test.py", TestStatus.PASSED, 0.5, datetime.now(), datetime.now()),
            TestResult("test_fail", "test.py", TestStatus.FAILED, 1.0, datetime.now(), datetime.now())
        ]
        
        reporter = ReportGenerator(execution_config)
        
        # Test JSON report
        json_path = reporter._generate_json_report(suite, results)
        assert json_path.exists()
        
        with open(json_path) as f:
            data = json.load(f)
        assert data["suite"]["total_tests"] == 2
        assert data["suite"]["passed"] == 1

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for the complete pipeline"""
    
    @pytest.mark.asyncio
    async def test_pipeline_flow(self):
        """Test data flow through pipeline"""
        # This is a conceptual test - in real use, each step feeds the next
        
        # Step 1 output: elements
        elements = [
            {"tag_name": "button", "text_content": "Submit"}
        ]
        
        # Step 2 output: Gherkin
        gherkin = "Feature: Test\n  Scenario: Click button\n    When user clicks Submit"
        
        # Step 3: Generate code from Gherkin
        config = TestCodeConfig()
        generator = PythonTestCodeGenerator(config)
        feature = generator.parser.parse_feature_content(gherkin)
        assert feature is not None
        
        # Step 4: Would execute the generated tests
        exec_config = ExecutionConfig()
        executor = TestExecutor(exec_config)
        assert executor is not None

# ============================================================================
# TEST RUNNER
# ============================================================================

def run_tests(category=None):
    """Run tests with optional category filter"""
    args = [__file__, "-v", "--tb=short"]
    
    if category == "unit":
        args.extend(["-k", "not Integration"])
    elif category == "integration":
        args.extend(["-k", "Integration"])
    
    return pytest.main(args)

if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("🧪 UI Testing Framework - Test Suite")
    print("="*60)
    
    # Check for category argument
    category = None
    if len(sys.argv) > 1 and "--category" in sys.argv:
        idx = sys.argv.index("--category")
        if idx + 1 < len(sys.argv):
            category = sys.argv[idx + 1]
    
    exit_code = run_tests(category)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")
    
    sys.exit(exit_code)