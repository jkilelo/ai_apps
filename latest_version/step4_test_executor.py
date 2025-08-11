#!/usr/bin/env python3
"""
Test Executor Engine - Step 4 of UI Testing Framework
Executes generated Python test code with comprehensive reporting and analysis

Following CODER Strategy:
- Single file implementation
- No code duplication
- Comprehensive error handling
- Production-ready features
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CODER STRATEGIC PLANNING
# ============================================================================
"""
Strategic Analysis:
1. Approach 1: Simple subprocess execution
   - Pros: Easy to implement, isolated execution
   - Cons: Limited control, harder to collect metrics
   
2. Approach 2: Dynamic import and execution
   - Pros: Full control, detailed metrics, in-process
   - Cons: Risk of test pollution, complex cleanup
   
3. Approach 3: Hybrid with pytest programmatic API
   - Pros: Best of both worlds, full pytest features
   - Cons: Requires pytest as dependency

Selected Approach: Hybrid (Approach 3)
- Use pytest programmatic API for execution
- Subprocess fallback for isolation
- Rich reporting and metrics collection
"""

# ============================================================================
# DATA MODELS
# ============================================================================

class TestStatus(str, Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"

class ExecutionMode(str, Enum):
    """Test execution mode"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"

class ReportFormat(str, Enum):
    """Report output format"""
    JSON = "json"
    HTML = "html"
    JUNIT = "junit"
    MARKDOWN = "markdown"
    ALLURE = "allure"

@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    test_file: str
    status: TestStatus
    duration: float
    start_time: datetime
    end_time: datetime
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    assertions: int = 0
    retries: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "test_name": self.test_name,
            "test_file": self.test_file,
            "status": self.status.value,
            "duration": self.duration,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "screenshots": self.screenshots,
            "logs": self.logs,
            "assertions": self.assertions,
            "retries": self.retries
        }

@dataclass
class TestSuite:
    """Test suite information"""
    name: str
    test_files: List[Path]
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0
    
    def get_pass_rate(self) -> float:
        """Calculate pass rate"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100

@dataclass
class ExecutionConfig:
    """Test execution configuration"""
    test_dir: Path = Path("./generated_tests")
    output_dir: Path = Path("./test_results")
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    parallel_workers: int = 4
    timeout_per_test: int = 60  # seconds
    retry_failed_tests: bool = True
    max_retries: int = 2
    capture_screenshots: bool = True
    capture_video: bool = False
    generate_reports: List[ReportFormat] = field(
        default_factory=lambda: [ReportFormat.JSON, ReportFormat.HTML]
    )
    browser_options: Dict[str, Any] = field(default_factory=dict)
    environment: str = "test"
    headless: bool = False
    slow_mo: int = 0  # milliseconds
    
    # CI/CD settings
    ci_mode: bool = False
    fail_fast: bool = False
    continue_on_failure: bool = True
    
    # Reporting settings
    verbose: bool = True
    quiet: bool = False
    show_progress: bool = True

# ============================================================================
# TEST DISCOVERY
# ============================================================================

class TestDiscovery:
    """Discover and analyze test files"""
    
    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.test_files: List[Path] = []
        self.test_methods: Dict[Path, List[str]] = {}
    
    def discover_tests(self) -> List[Path]:
        """Discover all test files in directory"""
        logger.info(f"Discovering tests in: {self.config.test_dir}")
        
        if not self.config.test_dir.exists():
            logger.warning(f"Test directory does not exist: {self.config.test_dir}")
            return []
        
        # Find all test files
        test_patterns = ["test_*.py", "*_test.py"]
        
        for pattern in test_patterns:
            for file in self.config.test_dir.rglob(pattern):
                # Only include files that start with "test_" (more strict)
                if file.name.startswith("test_") and file.name.endswith(".py"):
                    self.test_files.append(file)
        
        # Remove duplicates
        self.test_files = list(set(self.test_files))
        
        logger.info(f"Discovered {len(self.test_files)} test files")
        
        # Analyze each file
        for test_file in self.test_files:
            self._analyze_test_file(test_file)
        
        return self.test_files
    
    def _analyze_test_file(self, test_file: Path):
        """Analyze a test file to find test methods"""
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Find test methods (simple regex approach)
            import re
            
            # Find async def test_* or def test_*
            test_pattern = r'(?:async\s+)?def\s+(test_\w+)\s*\('
            matches = re.findall(test_pattern, content)
            
            self.test_methods[test_file] = matches
            
            logger.debug(f"Found {len(matches)} tests in {test_file.name}")
            
        except Exception as e:
            logger.error(f"Failed to analyze {test_file}: {e}")
    
    def get_total_test_count(self) -> int:
        """Get total number of tests"""
        return sum(len(methods) for methods in self.test_methods.values())
    
    def get_test_list(self) -> List[Tuple[Path, str]]:
        """Get list of all tests as (file, method) tuples"""
        tests = []
        for test_file, methods in self.test_methods.items():
            for method in methods:
                tests.append((test_file, method))
        return tests

# ============================================================================
# TEST RUNNER
# ============================================================================

class TestRunner:
    """Core test execution engine"""
    
    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.results: List[TestResult] = []
        self.suite = TestSuite(
            name="UI Test Suite",
            test_files=[]
        )
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute_tests(self, test_files: Optional[List[Path]] = None) -> TestSuite:
        """Execute all tests and return results"""
        self.start_time = datetime.now()
        logger.info(f"Starting test execution at {self.start_time}")
        
        # Discover tests if not provided
        if test_files is None:
            discovery = TestDiscovery(self.config)
            test_files = discovery.discover_tests()
        
        self.suite.test_files = test_files
        self.suite.total_tests = len(test_files)
        
        if not test_files:
            logger.warning("No test files found")
            return self.suite
        
        # Execute based on mode
        if self.config.execution_mode == ExecutionMode.PARALLEL:
            await self._execute_parallel(test_files)
        else:
            await self._execute_sequential(test_files)
        
        self.end_time = datetime.now()
        self.suite.duration = (self.end_time - self.start_time).total_seconds()
        
        # Update suite statistics
        self._update_suite_stats()
        
        logger.info(f"Test execution completed in {self.suite.duration:.2f}s")
        logger.info(f"Passed: {self.suite.passed}/{self.suite.total_tests}")
        
        return self.suite
    
    async def _execute_sequential(self, test_files: List[Path]):
        """Execute tests sequentially"""
        for i, test_file in enumerate(test_files, 1):
            if self.config.show_progress:
                logger.info(f"[{i}/{len(test_files)}] Running: {test_file.name}")
            
            result = await self._run_single_test_file(test_file)
            self.results.append(result)
            
            # Fail fast if configured
            if self.config.fail_fast and result.status == TestStatus.FAILED:
                logger.warning("Failing fast due to test failure")
                break
    
    async def _execute_parallel(self, test_files: List[Path]):
        """Execute tests in parallel"""
        logger.info(f"Running tests in parallel with {self.config.parallel_workers} workers")
        
        # Create tasks for parallel execution
        semaphore = asyncio.Semaphore(self.config.parallel_workers)
        
        async def run_with_semaphore(test_file: Path) -> TestResult:
            async with semaphore:
                return await self._run_single_test_file(test_file)
        
        # Execute all tests in parallel
        tasks = [run_with_semaphore(test_file) for test_file in test_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Test execution failed: {result}")
            else:
                self.results.append(result)
    
    async def _run_single_test_file(self, test_file: Path) -> TestResult:
        """Run a single test file"""
        start_time = datetime.now()
        
        # Check if file exists
        if not test_file.exists():
            return TestResult(
                test_name=test_file.name,
                test_file=str(test_file),
                status=TestStatus.ERROR,
                duration=0.0,
                start_time=start_time,
                end_time=datetime.now(),
                error_message=f"Test file not found: {test_file}"
            )
        
        # Determine test framework
        try:
            content = test_file.read_text()
            if "pytest" in content:
                result = await self._run_pytest(test_file)
            else:
                result = await self._run_python_unittest(test_file)
        except Exception as e:
            result = TestResult(
                test_name=test_file.name,
                test_file=str(test_file),
                status=TestStatus.ERROR,
                duration=0.0,
                start_time=start_time,
                end_time=datetime.now(),
                error_message=f"Error reading test file: {e}"
            )
        
        end_time = datetime.now()
        result.duration = (end_time - start_time).total_seconds()
        result.start_time = start_time
        result.end_time = end_time
        
        # Retry if failed and configured
        if result.status == TestStatus.FAILED and self.config.retry_failed_tests:
            for retry in range(self.config.max_retries):
                logger.info(f"Retrying {test_file.name} (attempt {retry + 1}/{self.config.max_retries})")
                result = await self._run_pytest(test_file)
                result.retries = retry + 1
                
                if result.status == TestStatus.PASSED:
                    break
        
        return result
    
    async def _run_pytest(self, test_file: Path) -> TestResult:
        """Run test using pytest"""
        result = TestResult(
            test_name=test_file.stem,
            test_file=str(test_file),
            status=TestStatus.PENDING,
            duration=0.0,
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        try:
            # Build pytest command
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_file),
                "-v" if self.config.verbose else "-q",
                f"--timeout={self.config.timeout_per_test}",
                "--tb=short",
                f"--junit-xml={self.config.output_dir / f'{test_file.stem}_junit.xml'}",
                "--capture=no" if not self.config.quiet else "--capture=yes"
            ]
            
            # Add headless option for browser tests
            if self.config.headless:
                cmd.extend(["--headed" if not self.config.headless else "--headless"])
            
            # Run pytest
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.timeout_per_test
                )
            except asyncio.TimeoutError:
                process.kill()
                result.status = TestStatus.TIMEOUT
                result.error_message = f"Test timed out after {self.config.timeout_per_test}s"
                return result
            
            # Parse output
            output = stdout.decode() if stdout else ""
            errors = stderr.decode() if stderr else ""
            
            result.logs = output.split('\n') if output else []
            
            # Determine status from return code
            if process.returncode == 0:
                result.status = TestStatus.PASSED
            elif process.returncode == 1:
                result.status = TestStatus.FAILED
                result.error_message = self._extract_error_message(output, errors)
                result.stack_trace = self._extract_stack_trace(output, errors)
            else:
                result.status = TestStatus.ERROR
                result.error_message = f"Process exited with code {process.returncode}"
            
            # Parse JUnit XML for detailed results
            junit_file = self.config.output_dir / f'{test_file.stem}_junit.xml'
            if junit_file.exists():
                self._parse_junit_results(result, junit_file)
            
            # Collect screenshots
            if self.config.capture_screenshots:
                result.screenshots = self._collect_screenshots(test_file.stem)
            
        except Exception as e:
            result.status = TestStatus.ERROR
            result.error_message = str(e)
            result.stack_trace = traceback.format_exc()
            logger.error(f"Failed to run {test_file}: {e}")
        
        return result
    
    async def _run_python_unittest(self, test_file: Path) -> TestResult:
        """Run test using unittest"""
        # Similar to pytest but with unittest runner
        result = TestResult(
            test_name=test_file.stem,
            test_file=str(test_file),
            status=TestStatus.PENDING,
            duration=0.0,
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        try:
            cmd = [
                sys.executable,
                str(test_file)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result.status = TestStatus.PASSED
            else:
                result.status = TestStatus.FAILED
                result.error_message = stderr.decode() if stderr else ""
        
        except Exception as e:
            result.status = TestStatus.ERROR
            result.error_message = str(e)
        
        return result
    
    def _extract_error_message(self, stdout: str, stderr: str) -> str:
        """Extract error message from output"""
        # Look for assertion errors or exceptions
        lines = (stdout + stderr).split('\n')
        
        for i, line in enumerate(lines):
            if 'AssertionError' in line or 'Exception' in line or 'Error' in line:
                # Return this line and the next few for context
                return '\n'.join(lines[i:min(i+3, len(lines))])
        
        return stderr[:500] if stderr else "Test failed"
    
    def _extract_stack_trace(self, stdout: str, stderr: str) -> str:
        """Extract stack trace from output"""
        output = stdout + stderr
        
        # Look for traceback
        if 'Traceback' in output:
            start = output.index('Traceback')
            # Find the end of traceback (usually an empty line or next test)
            lines = output[start:].split('\n')
            
            for i, line in enumerate(lines):
                if i > 0 and (not line.strip() or line.startswith('=')):
                    return '\n'.join(lines[:i])
            
            return '\n'.join(lines[:20])  # Limit to 20 lines
        
        return ""
    
    def _parse_junit_results(self, result: TestResult, junit_file: Path):
        """Parse JUnit XML for detailed results"""
        try:
            tree = ET.parse(junit_file)
            root = tree.getroot()
            
            # Parse test suite
            for testsuite in root.findall('testsuite'):
                result.assertions = int(testsuite.get('tests', 0))
                
                # Parse test cases
                for testcase in testsuite.findall('testcase'):
                    # Check for failures
                    failure = testcase.find('failure')
                    if failure is not None:
                        result.error_message = failure.get('message', '')
                        result.stack_trace = failure.text or ''
                    
                    # Check for errors
                    error = testcase.find('error')
                    if error is not None:
                        result.status = TestStatus.ERROR
                        result.error_message = error.get('message', '')
                        result.stack_trace = error.text or ''
        
        except Exception as e:
            logger.warning(f"Failed to parse JUnit XML: {e}")
    
    def _collect_screenshots(self, test_name: str) -> List[str]:
        """Collect screenshots for a test"""
        screenshots = []
        
        screenshot_dir = Path("screenshots")
        if screenshot_dir.exists():
            # Look for screenshots with test name
            for screenshot in screenshot_dir.glob(f"*{test_name}*.png"):
                screenshots.append(str(screenshot))
        
        return screenshots
    
    def _update_suite_stats(self):
        """Update suite statistics from results"""
        for result in self.results:
            if result.status == TestStatus.PASSED:
                self.suite.passed += 1
            elif result.status == TestStatus.FAILED:
                self.suite.failed += 1
            elif result.status == TestStatus.SKIPPED:
                self.suite.skipped += 1
            elif result.status in [TestStatus.ERROR, TestStatus.TIMEOUT]:
                self.suite.errors += 1

# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generate test execution reports"""
    
    def __init__(self, config: ExecutionConfig):
        self.config = config
    
    def generate_reports(
        self,
        suite: TestSuite,
        results: List[TestResult]
    ) -> Dict[str, Path]:
        """Generate all configured reports"""
        generated_reports = {}
        
        for format in self.config.generate_reports:
            if format == ReportFormat.JSON:
                report_path = self._generate_json_report(suite, results)
                generated_reports["json"] = report_path
            
            elif format == ReportFormat.HTML:
                report_path = self._generate_html_report(suite, results)
                generated_reports["html"] = report_path
            
            elif format == ReportFormat.MARKDOWN:
                report_path = self._generate_markdown_report(suite, results)
                generated_reports["markdown"] = report_path
            
            elif format == ReportFormat.JUNIT:
                report_path = self._generate_junit_report(suite, results)
                generated_reports["junit"] = report_path
        
        return generated_reports
    
    def _generate_json_report(
        self,
        suite: TestSuite,
        results: List[TestResult]
    ) -> Path:
        """Generate JSON report"""
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.config.output_dir / "test_report.json"
        
        report_data = {
            "suite": {
                "name": suite.name,
                "total_tests": suite.total_tests,
                "passed": suite.passed,
                "failed": suite.failed,
                "skipped": suite.skipped,
                "errors": suite.errors,
                "duration": suite.duration,
                "pass_rate": suite.get_pass_rate()
            },
            "execution": {
                "mode": self.config.execution_mode.value,
                "parallel_workers": self.config.parallel_workers,
                "environment": self.config.environment,
                "timestamp": datetime.now().isoformat()
            },
            "results": [result.to_dict() for result in results]
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"JSON report saved to: {report_path}")
        return report_path
    
    def _generate_html_report(
        self,
        suite: TestSuite,
        results: List[TestResult]
    ) -> Path:
        """Generate HTML report"""
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.config.output_dir / "test_report.html"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Execution Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #333; color: white; padding: 20px; }}
        .summary {{ margin: 20px 0; padding: 15px; background: #f5f5f5; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .skipped {{ color: orange; }}
        .error {{ color: darkred; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background: #f2f2f2; }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #f0f0f0;
            border-radius: 5px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #45a049);
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Test Execution Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <p><strong>Total Tests:</strong> {suite.total_tests}</p>
        <p><strong>Duration:</strong> {suite.duration:.2f} seconds</p>
        <p><strong>Pass Rate:</strong> {suite.get_pass_rate():.1f}%</p>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {suite.get_pass_rate()}%"></div>
        </div>
        
        <p>
            <span class="passed">✅ Passed: {suite.passed}</span> |
            <span class="failed">❌ Failed: {suite.failed}</span> |
            <span class="skipped">⏭️ Skipped: {suite.skipped}</span> |
            <span class="error">⚠️ Errors: {suite.errors}</span>
        </p>
    </div>
    
    <h2>📝 Test Results</h2>
    <table>
        <tr>
            <th>Test Name</th>
            <th>Status</th>
            <th>Duration (s)</th>
            <th>Error Message</th>
            <th>Retries</th>
        </tr>
"""
        
        for result in results:
            status_class = result.status.value
            status_icon = {
                TestStatus.PASSED: "✅",
                TestStatus.FAILED: "❌",
                TestStatus.SKIPPED: "⏭️",
                TestStatus.ERROR: "⚠️",
                TestStatus.TIMEOUT: "⏱️"
            }.get(result.status, "❓")
            
            html_content += f"""
        <tr>
            <td>{result.test_name}</td>
            <td class="{status_class}">{status_icon} {result.status.value}</td>
            <td>{result.duration:.2f}</td>
            <td>{result.error_message or '-'}</td>
            <td>{result.retries}</td>
        </tr>
"""
        
        html_content += """
    </table>
    
    <div style="margin-top: 40px; padding: 20px; background: #f9f9f9;">
        <p style="text-align: center; color: #666;">
            Generated by UI Testing Framework - Test Executor Engine
        </p>
    </div>
</body>
</html>
"""
        
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML report saved to: {report_path}")
        return report_path
    
    def _generate_markdown_report(
        self,
        suite: TestSuite,
        results: List[TestResult]
    ) -> Path:
        """Generate Markdown report"""
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.config.output_dir / "test_report.md"
        
        md_content = f"""# Test Execution Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Tests:** {suite.total_tests}
- **Passed:** {suite.passed} ✅
- **Failed:** {suite.failed} ❌
- **Skipped:** {suite.skipped} ⏭️
- **Errors:** {suite.errors} ⚠️
- **Duration:** {suite.duration:.2f} seconds
- **Pass Rate:** {suite.get_pass_rate():.1f}%

## Test Results

| Test Name | Status | Duration (s) | Error Message | Retries |
|-----------|--------|--------------|---------------|---------|
"""
        
        for result in results:
            error_msg = (result.error_message[:50] + "...") if result.error_message and len(result.error_message) > 50 else (result.error_message or "-")
            md_content += f"| {result.test_name} | {result.status.value} | {result.duration:.2f} | {error_msg} | {result.retries} |\n"
        
        # Add failed test details
        failed_tests = [r for r in results if r.status == TestStatus.FAILED]
        if failed_tests:
            md_content += "\n## Failed Test Details\n\n"
            
            for result in failed_tests:
                md_content += f"### {result.test_name}\n\n"
                if result.error_message:
                    md_content += f"**Error:** {result.error_message}\n\n"
                if result.stack_trace:
                    md_content += f"```\n{result.stack_trace}\n```\n\n"
        
        with open(report_path, 'w') as f:
            f.write(md_content)
        
        logger.info(f"Markdown report saved to: {report_path}")
        return report_path
    
    def _generate_junit_report(
        self,
        suite: TestSuite,
        results: List[TestResult]
    ) -> Path:
        """Generate JUnit XML report"""
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.config.output_dir / "junit_report.xml"
        
        # Create root element
        testsuites = ET.Element('testsuites')
        testsuite = ET.SubElement(
            testsuites,
            'testsuite',
            name=suite.name,
            tests=str(suite.total_tests),
            failures=str(suite.failed),
            errors=str(suite.errors),
            skipped=str(suite.skipped),
            time=str(suite.duration)
        )
        
        # Add test cases
        for result in results:
            testcase = ET.SubElement(
                testsuite,
                'testcase',
                name=result.test_name,
                classname=result.test_file,
                time=str(result.duration)
            )
            
            if result.status == TestStatus.FAILED:
                failure = ET.SubElement(
                    testcase,
                    'failure',
                    message=result.error_message or "Test failed"
                )
                if result.stack_trace:
                    failure.text = result.stack_trace
            
            elif result.status == TestStatus.ERROR:
                error = ET.SubElement(
                    testcase,
                    'error',
                    message=result.error_message or "Test error"
                )
                if result.stack_trace:
                    error.text = result.stack_trace
            
            elif result.status == TestStatus.SKIPPED:
                ET.SubElement(testcase, 'skipped')
        
        # Write XML
        tree = ET.ElementTree(testsuites)
        tree.write(report_path, encoding='utf-8', xml_declaration=True)
        
        logger.info(f"JUnit report saved to: {report_path}")
        return report_path

# ============================================================================
# CI/CD INTEGRATION
# ============================================================================

class CICDIntegration:
    """CI/CD integration utilities"""
    
    @staticmethod
    def detect_ci_environment() -> Optional[str]:
        """Detect CI/CD environment"""
        if os.getenv('GITHUB_ACTIONS'):
            return "github_actions"
        elif os.getenv('GITLAB_CI'):
            return "gitlab"
        elif os.getenv('JENKINS_URL'):
            return "jenkins"
        elif os.getenv('CIRCLECI'):
            return "circleci"
        elif os.getenv('TRAVIS'):
            return "travis"
        elif os.getenv('AZURE_PIPELINES'):
            return "azure_devops"
        return None
    
    @staticmethod
    def set_github_output(name: str, value: str):
        """Set GitHub Actions output"""
        if os.getenv('GITHUB_OUTPUT'):
            with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                f.write(f"{name}={value}\n")
    
    @staticmethod
    def create_github_summary(suite: TestSuite, results: List[TestResult]):
        """Create GitHub Actions job summary"""
        if not os.getenv('GITHUB_STEP_SUMMARY'):
            return
        
        summary = f"""# Test Execution Summary

## Results
- ✅ Passed: {suite.passed}/{suite.total_tests}
- ❌ Failed: {suite.failed}
- ⏭️ Skipped: {suite.skipped}
- ⚠️ Errors: {suite.errors}
- ⏱️ Duration: {suite.duration:.2f}s
- 📊 Pass Rate: {suite.get_pass_rate():.1f}%

## Failed Tests
"""
        
        for result in results:
            if result.status == TestStatus.FAILED:
                summary += f"- {result.test_name}: {result.error_message}\n"
        
        with open(os.getenv('GITHUB_STEP_SUMMARY'), 'w') as f:
            f.write(summary)
    
    @staticmethod
    def exit_with_code(suite: TestSuite) -> int:
        """Get appropriate exit code for CI/CD"""
        if suite.failed > 0 or suite.errors > 0:
            return 1
        return 0

# ============================================================================
# MAIN EXECUTOR
# ============================================================================

class TestExecutor:
    """Main test executor orchestrator"""
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()
        self.runner = TestRunner(self.config)
        self.reporter = ReportGenerator(self.config)
        self.ci_cd = CICDIntegration()
        
        # Detect CI environment
        ci_env = self.ci_cd.detect_ci_environment()
        if ci_env:
            logger.info(f"Detected CI environment: {ci_env}")
            self.config.ci_mode = True
            self.config.headless = True  # Force headless in CI
    
    async def execute(self, step3_output):
        """Execute tests from Step 3 contract and return Step 4 contract.
        
        Args:
            step3_output: CodeGeneration contract from Step 3
            
        Returns:
            ExecutionResult: Contract-compliant output
        """
        from data_contracts import ExecutionResult, TestResult, TestStatus, CodeGeneration
        from datetime import datetime
        import time
        
        # Validate input is correct contract type
        if not isinstance(step3_output, CodeGeneration):
            raise TypeError(f"Expected CodeGeneration, got {type(step3_output).__name__}")
        
        start_time = time.time()
        success = True
        error_message = None
        results = []
        test_files = []
        
        try:
            # Save generated files to disk
            for gen_file in step3_output.files:
                gen_file.save()
                if gen_file.file_type.value == "test":
                    test_files.append(gen_file.path)
            
            # Use internal execution method
            exec_result = await self._execute_internal(test_files=test_files)
            
            # Convert results to contract format
            if 'results' in exec_result:
                for test_res in exec_result['results']:
                    status_map = {
                        'passed': TestStatus.PASSED,
                        'failed': TestStatus.FAILED,
                        'skipped': TestStatus.SKIPPED,
                        'error': TestStatus.ERROR
                    }
                    
                    results.append(TestResult(
                        test_name=test_res.get('test_name', 'unknown'),
                        test_file=Path(test_res.get('test_file', '')),
                        status=status_map.get(test_res.get('status', 'error'), TestStatus.ERROR),
                        duration=test_res.get('duration', 0.0),
                        error_message=test_res.get('error_message'),
                        stack_trace=test_res.get('stack_trace'),
                        screenshots=test_res.get('screenshots', []),
                        logs=test_res.get('logs', []),
                        retries=test_res.get('retries', 0)
                    ))
            
            # Get summary
            summary = exec_result.get('suite', {})
            
        except Exception as e:
            success = False
            error_message = str(e)
            logger.error(f"Test execution failed: {e}")
            summary = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
        
        # Return contract
        return ExecutionResult(
            test_files=test_files,
            timestamp=datetime.now().isoformat(),
            success=success,
            results=results,
            summary={
                "total": summary.get("total", 0),
                "passed": summary.get("passed", 0),
                "failed": summary.get("failed", 0),
                "skipped": summary.get("skipped", 0)
            },
            reports=exec_result.get('reports', {}) if 'exec_result' in locals() else {},
            metadata={
                "executor_version": "1.0.0",
                "execution_mode": self.config.execution_mode.value,
                "ci_mode": self.config.ci_mode
            },
            error_message=error_message,
            execution_time=time.time() - start_time,
            environment=self.config.environment
        )
    
    async def _execute_internal(
        self,
        test_dir: Optional[Path] = None,
        test_files: Optional[List[Path]] = None
    ) -> Dict[str, Any]:
        """
        Execute tests and generate reports
        
        Args:
            test_dir: Directory containing tests
            test_files: Specific test files to run
        
        Returns:
            Execution results dictionary
        """
        
        try:
            if test_dir:
                self.config.test_dir = test_dir
            
            logger.info("=" * 60)
            logger.info("🚀 Test Executor Engine - Starting")
            logger.info("=" * 60)
            
            # Execute tests
            suite = await self.runner.execute_tests(test_files)
            
            # Generate reports
            reports = self.reporter.generate_reports(suite, self.runner.results)
            
            # CI/CD integration
            if self.config.ci_mode:
                self._handle_ci_integration(suite, self.runner.results)
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            # Return error result
            return {
                "suite": {
                    "name": "Error",
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 1,
                    "error_message": str(e)
                },
                "results": [],
                "reports": {},
                "exit_code": 1
            }
        
        # Prepare results
        execution_results = {
            "suite": {
                "name": suite.name,
                "total": suite.total_tests,
                "passed": suite.passed,
                "failed": suite.failed,
                "skipped": suite.skipped,
                "errors": suite.errors,
                "duration": suite.duration,
                "pass_rate": suite.get_pass_rate()
            },
            "reports": {k: str(v) for k, v in reports.items()},
            "results": [r.to_dict() for r in self.runner.results],
            "exit_code": self.ci_cd.exit_with_code(suite)
        }
        
        # Print summary
        self._print_summary(suite)
        
        return execution_results
    
    def _handle_ci_integration(self, suite: TestSuite, results: List[TestResult]):
        """Handle CI/CD specific features"""
        # GitHub Actions
        if os.getenv('GITHUB_ACTIONS'):
            self.ci_cd.set_github_output('test_passed', str(suite.passed))
            self.ci_cd.set_github_output('test_failed', str(suite.failed))
            self.ci_cd.set_github_output('pass_rate', str(suite.get_pass_rate()))
            self.ci_cd.create_github_summary(suite, results)
    
    def _print_summary(self, suite: TestSuite):
        """Print execution summary"""
        print("\n" + "=" * 60)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {suite.total_tests}")
        print(f"✅ Passed: {suite.passed}")
        print(f"❌ Failed: {suite.failed}")
        print(f"⏭️ Skipped: {suite.skipped}")
        print(f"⚠️ Errors: {suite.errors}")
        print(f"⏱️ Duration: {suite.duration:.2f} seconds")
        print(f"📈 Pass Rate: {suite.get_pass_rate():.1f}%")
        print("=" * 60)

# ============================================================================
# CLI INTERFACE
# ============================================================================

async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test Executor Engine - Execute generated test code"
    )
    
    parser.add_argument(
        "test_dir",
        nargs="?",
        default="./generated_tests",
        help="Directory containing test files"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout per test in seconds"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browsers in headless mode"
    )
    
    parser.add_argument(
        "--retry",
        type=int,
        default=2,
        help="Number of retries for failed tests"
    )
    
    parser.add_argument(
        "--output",
        default="./test_results",
        help="Output directory for reports"
    )
    
    parser.add_argument(
        "--format",
        nargs="+",
        choices=["json", "html", "markdown", "junit"],
        default=["json", "html"],
        help="Report formats to generate"
    )
    
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first failure"
    )
    
    args = parser.parse_args()
    
    # Create configuration
    config = ExecutionConfig(
        test_dir=Path(args.test_dir),
        output_dir=Path(args.output),
        execution_mode=ExecutionMode.PARALLEL if args.parallel else ExecutionMode.SEQUENTIAL,
        parallel_workers=args.workers,
        timeout_per_test=args.timeout,
        headless=args.headless,
        max_retries=args.retry,
        fail_fast=args.fail_fast,
        generate_reports=[ReportFormat(f) for f in args.format]
    )
    
    # Execute tests
    executor = TestExecutor(config)
    results = await executor.execute()
    
    # Exit with appropriate code
    sys.exit(results["exit_code"])

if __name__ == "__main__":
    asyncio.run(main())