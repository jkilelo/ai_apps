"""
Comprehensive Test Executor for Dynamically Generated Tests
============================================================
This framework executes the dynamically generated test code with:
- Automatic dependency installation
- Environment setup and validation
- Multiple execution modes (all, specific, parallel)
- Real-time progress tracking
- Comprehensive reporting (HTML, JSON, Allure)
- Screenshot and video capture on failure
- Retry logic for flaky tests
- Performance metrics collection
- Cross-browser support
- CI/CD integration ready

Author: AI Test Framework
Date: 2025
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import platform
import tempfile
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class ExecutionConfig:
    """Configuration for test execution."""
    
    # Test Directory
    test_dir: str = "dynamic_generated_tests"
    
    # Execution Settings
    execution_mode: str = "all"  # all, specific, parallel, smoke, regression
    specific_tests: List[str] = field(default_factory=list)
    parallel_workers: int = 4
    max_retries: int = 2
    retry_delay: int = 2  # seconds
    timeout_per_test: int = 120  # seconds
    
    # Browser Settings
    browser: str = "chromium"  # chromium, firefox, webkit
    headless: bool = False
    slow_mo: int = 0  # milliseconds
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # Environment Settings
    base_url: Optional[str] = None
    env_file: str = ".env.test"
    use_existing_env: bool = True
    
    # Reporting Settings
    generate_html_report: bool = True
    generate_json_report: bool = True
    generate_allure_report: bool = False
    capture_screenshots: bool = True
    capture_videos: bool = False
    capture_traces: bool = False
    
    # Output Settings
    output_dir: str = "test_execution_results"
    keep_temp_files: bool = False
    
    # CI/CD Settings
    ci_mode: bool = False
    fail_fast: bool = False
    continue_on_failure: bool = True
    
    # Performance Settings
    collect_metrics: bool = True
    performance_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "page_load_time": 5.0,  # seconds
        "api_response_time": 2.0,  # seconds
        "test_execution_time": 60.0  # seconds
    })
    
    # Validation Settings
    validate_before_run: bool = True
    auto_install_deps: bool = True
    check_browser_installed: bool = True


# ============================================================================
# DEPENDENCY MANAGER
# ============================================================================

class DependencyManager:
    """Manages test dependencies and environment setup."""
    
    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.test_dir = Path(config.test_dir)
        
    def validate_environment(self) -> Tuple[bool, List[str]]:
        """Validate the test environment is ready."""
        issues = []
        
        # Check test directory exists
        if not self.test_dir.exists():
            issues.append(f"Test directory not found: {self.test_dir}")
            return False, issues
        
        # Check for key files
        required_files = ["conftest.py", "requirements.txt"]
        for file in required_files:
            if not (self.test_dir / file).exists():
                issues.append(f"Required file missing: {file}")
        
        # Check for test files
        test_files = list((self.test_dir / "tests").glob("test_*.py")) if (self.test_dir / "tests").exists() else []
        if not test_files:
            issues.append("No test files found in tests/ directory")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            issues.append(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        
        return len(issues) == 0, issues
    
    def install_dependencies(self) -> bool:
        """Install required dependencies from requirements.txt."""
        requirements_file = self.test_dir / "requirements.txt"
        
        if not requirements_file.exists():
            logger.warning("No requirements.txt found, skipping dependency installation")
            return True
        
        try:
            logger.info("Installing dependencies...")
            
            # Upgrade pip first
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         capture_output=True, text=True, check=True)
            
            # Install requirements
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Dependencies installed successfully")
            
            # Install Playwright browsers if needed
            if "playwright" in requirements_file.read_text().lower():
                self._install_playwright_browsers()
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
    
    def _install_playwright_browsers(self) -> bool:
        """Install Playwright browsers."""
        try:
            logger.info(f"Installing Playwright {self.config.browser} browser...")
            
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", self.config.browser],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Playwright {self.config.browser} installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Playwright browsers: {e}")
            return False
    
    def setup_environment(self) -> Dict[str, str]:
        """Setup environment variables for test execution."""
        env = os.environ.copy()
        
        # Load from .env.test file if exists
        env_file = self.test_dir / self.config.env_file
        if env_file.exists():
            logger.info(f"Loading environment from {env_file}")
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env[key.strip()] = value.strip()
        
        # Override with config settings
        if self.config.base_url:
            env['BASE_URL'] = self.config.base_url
        
        env['HEADLESS'] = str(self.config.headless).lower()
        env['BROWSER'] = self.config.browser
        env['SLOW_MO'] = str(self.config.slow_mo)
        env['VIEWPORT_WIDTH'] = str(self.config.viewport_width)
        env['VIEWPORT_HEIGHT'] = str(self.config.viewport_height)
        env['SCREENSHOT_ON_FAILURE'] = str(self.config.capture_screenshots).lower()
        env['RECORD_VIDEO'] = str(self.config.capture_videos).lower()
        env['PARALLEL_WORKERS'] = str(self.config.parallel_workers)
        env['DEFAULT_TIMEOUT'] = str(self.config.timeout_per_test * 1000)  # Convert to ms
        
        return env


# ============================================================================
# TEST RUNNER
# ============================================================================

class TestRunner:
    """Runs the generated tests with various execution modes."""
    
    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.test_dir = Path(config.test_dir)
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
        self.metrics = {}
        
    def get_test_files(self) -> List[Path]:
        """Get list of test files to execute."""
        test_dir = self.test_dir / "tests"
        
        if self.config.execution_mode == "specific" and self.config.specific_tests:
            # Run specific test files
            test_files = []
            for test_name in self.config.specific_tests:
                if not test_name.endswith('.py'):
                    test_name += '.py'
                test_file = test_dir / test_name
                if test_file.exists():
                    test_files.append(test_file)
                else:
                    logger.warning(f"Test file not found: {test_file}")
            return test_files
        
        elif self.config.execution_mode == "smoke":
            # Run only critical/smoke tests
            return list(test_dir.glob("test_critical*.py")) + list(test_dir.glob("test_smoke*.py"))
        
        elif self.config.execution_mode == "regression":
            # Run all non-smoke tests
            all_tests = list(test_dir.glob("test_*.py"))
            return [t for t in all_tests if 'smoke' not in t.name and 'critical' not in t.name]
        
        else:  # all
            # Run all test files
            return list(test_dir.glob("test_*.py"))
    
    def build_pytest_command(self, test_files: List[Path], env: Dict[str, str]) -> List[str]:
        """Build pytest command with appropriate options."""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test files
        for test_file in test_files:
            cmd.append(str(test_file))
        
        # Verbosity
        cmd.extend(["-v", "--tb=short"])
        
        # Parallel execution
        if self.config.execution_mode == "parallel" and self.config.parallel_workers > 1:
            cmd.extend(["-n", str(self.config.parallel_workers)])
        
        # Retry failed tests
        if self.config.max_retries > 0:
            cmd.extend(["--reruns", str(self.config.max_retries)])
            cmd.extend(["--reruns-delay", str(self.config.retry_delay)])
        
        # Fail fast
        if self.config.fail_fast:
            cmd.append("-x")
        
        # Continue on failure
        if self.config.continue_on_failure:
            cmd.append("--continue-on-collection-errors")
        
        # HTML Report
        if self.config.generate_html_report:
            report_file = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            cmd.extend(["--html", str(report_file), "--self-contained-html"])
        
        # JSON Report
        if self.config.generate_json_report:
            json_report = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            cmd.extend(["--json-report", "--json-report-file", str(json_report)])
        
        # Allure Report
        if self.config.generate_allure_report:
            allure_dir = self.output_dir / "allure-results"
            allure_dir.mkdir(exist_ok=True)
            cmd.extend(["--alluredir", str(allure_dir)])
        
        # Capture output
        if self.config.ci_mode:
            cmd.extend(["--capture=no", "-s"])
        
        # Timeout
        cmd.extend(["--timeout", str(self.config.timeout_per_test)])
        
        # Markers for specific test types
        if self.config.execution_mode == "smoke":
            cmd.extend(["-m", "smoke or critical"])
        
        return cmd
    
    async def execute_tests(self, env: Dict[str, str]) -> Dict[str, Any]:
        """Execute the tests and collect results."""
        test_files = self.get_test_files()
        
        if not test_files:
            logger.error("No test files found to execute")
            return {
                "success": False,
                "error": "No test files found",
                "test_count": 0
            }
        
        logger.info(f"Found {len(test_files)} test file(s) to execute")
        
        # Build pytest command
        cmd = self.build_pytest_command(test_files, env)
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        # Create temporary directory for test artifacts
        temp_dir = self.output_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        # Execute tests
        start_time = time.time()
        
        try:
            # Change to test directory for execution
            original_dir = os.getcwd()
            os.chdir(self.test_dir)
            
            # Run pytest
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                universal_newlines=True
            )
            
            # Stream output in real-time
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())
                    output_lines.append(line)
            
            process.wait()
            
            # Change back to original directory
            os.chdir(original_dir)
            
            execution_time = time.time() - start_time
            
            # Parse results
            output = ''.join(output_lines)
            results = self._parse_pytest_output(output)
            results['execution_time'] = execution_time
            results['exit_code'] = process.returncode
            results['success'] = process.returncode == 0
            
            # Collect artifacts
            self._collect_artifacts(temp_dir)
            
            # Store metrics
            if self.config.collect_metrics:
                self.metrics = self._collect_metrics(results, execution_time)
            
            return results
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
        finally:
            # Cleanup temp directory if not keeping
            if not self.config.keep_temp_files and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest output for results."""
        results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0,
            "test_details": []
        }
        
        # Parse summary line (e.g., "5 passed, 2 failed, 1 skipped")
        import re
        
        # Look for passed tests
        passed_match = re.search(r'(\d+) passed', output)
        if passed_match:
            results['passed'] = int(passed_match.group(1))
        
        # Look for failed tests
        failed_match = re.search(r'(\d+) failed', output)
        if failed_match:
            results['failed'] = int(failed_match.group(1))
        
        # Look for skipped tests
        skipped_match = re.search(r'(\d+) skipped', output)
        if skipped_match:
            results['skipped'] = int(skipped_match.group(1))
        
        # Look for errors
        error_match = re.search(r'(\d+) error', output)
        if error_match:
            results['errors'] = int(error_match.group(1))
        
        results['total'] = results['passed'] + results['failed'] + results['skipped'] + results['errors']
        
        # Extract individual test results
        test_pattern = re.compile(r'(test_\w+\.py::\w+::\w+)\s+(PASSED|FAILED|SKIPPED|ERROR)')
        for match in test_pattern.finditer(output):
            results['test_details'].append({
                'name': match.group(1),
                'status': match.group(2)
            })
        
        return results
    
    def _collect_artifacts(self, temp_dir: Path):
        """Collect test artifacts (screenshots, videos, etc.)."""
        artifacts_dir = self.output_dir / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)
        
        # Collect screenshots
        if self.config.capture_screenshots:
            screenshot_dir = artifacts_dir / "screenshots"
            screenshot_dir.mkdir(exist_ok=True)
            
            for screenshot in Path(self.test_dir).glob("**/*.png"):
                if screenshot.stat().st_mtime > time.time() - 3600:  # Created in last hour
                    shutil.copy2(screenshot, screenshot_dir / screenshot.name)
        
        # Collect videos
        if self.config.capture_videos:
            video_dir = artifacts_dir / "videos"
            video_dir.mkdir(exist_ok=True)
            
            for video in Path(self.test_dir).glob("**/*.webm"):
                if video.stat().st_mtime > time.time() - 3600:
                    shutil.copy2(video, video_dir / video.name)
    
    def _collect_metrics(self, results: Dict[str, Any], execution_time: float) -> Dict[str, Any]:
        """Collect performance metrics."""
        metrics = {
            "execution_time": execution_time,
            "tests_per_second": results['total'] / execution_time if execution_time > 0 else 0,
            "pass_rate": (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0,
            "failure_rate": (results['failed'] / results['total'] * 100) if results['total'] > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check against thresholds
        if execution_time > self.config.performance_thresholds.get('test_execution_time', 60):
            logger.warning(f"Tests took {execution_time:.2f}s, exceeding threshold of {self.config.performance_thresholds['test_execution_time']}s")
        
        return metrics


# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generates comprehensive test reports."""
    
    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.output_dir = Path(config.output_dir)
    
    def generate_summary_report(self, results: Dict[str, Any], metrics: Dict[str, Any]) -> Path:
        """Generate a comprehensive summary report."""
        report_file = self.output_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        summary = {
            "execution_date": datetime.now().isoformat(),
            "configuration": {
                "test_directory": self.config.test_dir,
                "execution_mode": self.config.execution_mode,
                "browser": self.config.browser,
                "headless": self.config.headless,
                "parallel_workers": self.config.parallel_workers
            },
            "results": results,
            "metrics": metrics,
            "environment": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": platform.platform(),
                "processor": platform.processor()
            }
        }
        
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Summary report saved to: {report_file}")
        return report_file
    
    def generate_markdown_report(self, results: Dict[str, Any], metrics: Dict[str, Any]) -> Path:
        """Generate a markdown report for easy reading."""
        report_file = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        content = f"""# Test Execution Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Tests**: {results.get('total', 0)}
- **Passed**: {results.get('passed', 0)} ✅
- **Failed**: {results.get('failed', 0)} ❌
- **Skipped**: {results.get('skipped', 0)} ⏭️
- **Errors**: {results.get('errors', 0)} 🔥
- **Success Rate**: {metrics.get('pass_rate', 0):.1f}%

## Execution Details

- **Execution Time**: {metrics.get('execution_time', 0):.2f} seconds
- **Tests per Second**: {metrics.get('tests_per_second', 0):.2f}
- **Browser**: {self.config.browser}
- **Mode**: {self.config.execution_mode}
- **Parallel Workers**: {self.config.parallel_workers}

## Test Results

| Test Name | Status |
|-----------|--------|
"""
        
        for test in results.get('test_details', []):
            status_emoji = {
                'PASSED': '✅',
                'FAILED': '❌',
                'SKIPPED': '⏭️',
                'ERROR': '🔥'
            }.get(test['status'], '❓')
            content += f"| {test['name']} | {test['status']} {status_emoji} |\n"
        
        content += f"""

## Configuration

- **Test Directory**: {self.config.test_dir}
- **Output Directory**: {self.config.output_dir}
- **Headless**: {self.config.headless}
- **Retries**: {self.config.max_retries}
- **Timeout per Test**: {self.config.timeout_per_test}s

## Artifacts

- **Screenshots**: {self.config.capture_screenshots}
- **Videos**: {self.config.capture_videos}
- **HTML Report**: {self.config.generate_html_report}
- **JSON Report**: {self.config.generate_json_report}

---

*Report generated by Test Executor Framework*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Markdown report saved to: {report_file}")
        return report_file


# ============================================================================
# MAIN EXECUTOR
# ============================================================================

class TestExecutor:
    """Main test executor that orchestrates the entire execution flow."""
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()
        self.dependency_manager = DependencyManager(self.config)
        self.test_runner = TestRunner(self.config)
        self.report_generator = ReportGenerator(self.config)
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the complete test flow."""
        logger.info("="*60)
        logger.info("TEST EXECUTION FRAMEWORK")
        logger.info("="*60)
        
        execution_result = {
            "success": False,
            "start_time": datetime.now().isoformat(),
            "results": {},
            "metrics": {},
            "reports": []
        }
        
        try:
            # Step 1: Validate environment
            if self.config.validate_before_run:
                logger.info("Step 1: Validating environment...")
                valid, issues = self.dependency_manager.validate_environment()
                
                if not valid:
                    logger.error("Environment validation failed:")
                    for issue in issues:
                        logger.error(f"  - {issue}")
                    
                    if not self.config.auto_install_deps:
                        execution_result["error"] = "Environment validation failed"
                        return execution_result
            
            # Step 2: Install dependencies
            if self.config.auto_install_deps:
                logger.info("Step 2: Installing dependencies...")
                if not self.dependency_manager.install_dependencies():
                    execution_result["error"] = "Failed to install dependencies"
                    return execution_result
            
            # Step 3: Setup environment
            logger.info("Step 3: Setting up environment...")
            env = self.dependency_manager.setup_environment()
            
            # Step 4: Execute tests
            logger.info("Step 4: Executing tests...")
            logger.info(f"  Mode: {self.config.execution_mode}")
            logger.info(f"  Browser: {self.config.browser}")
            logger.info(f"  Headless: {self.config.headless}")
            
            results = await self.test_runner.execute_tests(env)
            execution_result["results"] = results
            
            # Step 5: Collect metrics
            if self.config.collect_metrics:
                logger.info("Step 5: Collecting metrics...")
                execution_result["metrics"] = self.test_runner.metrics
            
            # Step 6: Generate reports
            logger.info("Step 6: Generating reports...")
            
            # Summary report
            summary_report = self.report_generator.generate_summary_report(
                results, 
                execution_result["metrics"]
            )
            execution_result["reports"].append(str(summary_report))
            
            # Markdown report
            md_report = self.report_generator.generate_markdown_report(
                results,
                execution_result["metrics"]
            )
            execution_result["reports"].append(str(md_report))
            
            # Set success based on test results
            execution_result["success"] = results.get("success", False)
            execution_result["end_time"] = datetime.now().isoformat()
            
            # Print summary
            self._print_summary(results, execution_result["metrics"])
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            traceback.print_exc()
            execution_result["error"] = str(e)
        
        return execution_result
    
    def _print_summary(self, results: Dict[str, Any], metrics: Dict[str, Any]):
        """Print execution summary to console."""
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        
        total = results.get('total', 0)
        passed = results.get('passed', 0)
        failed = results.get('failed', 0)
        skipped = results.get('skipped', 0)
        errors = results.get('errors', 0)
        
        print(f"Total Tests: {total}")
        print(f"  Passed:  {passed} ({passed/total*100:.1f}%)" if total > 0 else "  Passed:  0")
        print(f"  Failed:  {failed} ({failed/total*100:.1f}%)" if total > 0 else "  Failed:  0")
        print(f"  Skipped: {skipped}")
        print(f"  Errors:  {errors}")
        
        print(f"\nExecution Time: {metrics.get('execution_time', 0):.2f} seconds")
        print(f"Tests per Second: {metrics.get('tests_per_second', 0):.2f}")
        
        if results.get('success'):
            print("\n✅ ALL TESTS PASSED!")
        else:
            print("\n❌ SOME TESTS FAILED")
        
        print("\nReports saved to:", self.config.output_dir)
        print("="*60)


# ============================================================================
# CLI INTERFACE
# ============================================================================

async def run_tests(
    test_dir: str = "dynamic_generated_tests",
    mode: str = "all",
    browser: str = "chromium",
    headless: bool = False,
    parallel: int = 1,
    **kwargs
) -> Dict[str, Any]:
    """
    Run tests with specified configuration.
    
    Args:
        test_dir: Directory containing generated tests
        mode: Execution mode (all, specific, parallel, smoke, regression)
        browser: Browser to use (chromium, firefox, webkit)
        headless: Run in headless mode
        parallel: Number of parallel workers
        **kwargs: Additional configuration options
    
    Returns:
        Execution results dictionary
    """
    config = ExecutionConfig(
        test_dir=test_dir,
        execution_mode="parallel" if parallel > 1 else mode,
        browser=browser,
        headless=headless,
        parallel_workers=parallel,
        **kwargs
    )
    
    executor = TestExecutor(config)
    return await executor.execute()


def main():
    """Main entry point for CLI execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Execute dynamically generated tests")
    parser.add_argument("test_dir", nargs="?", default="dynamic_generated_tests",
                       help="Directory containing generated tests")
    parser.add_argument("--mode", choices=["all", "specific", "parallel", "smoke", "regression"],
                       default="all", help="Execution mode")
    parser.add_argument("--browser", choices=["chromium", "firefox", "webkit"],
                       default="chromium", help="Browser to use")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--parallel", type=int, default=1, help="Number of parallel workers")
    parser.add_argument("--retries", type=int, default=2, help="Number of retries for failed tests")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout per test in seconds")
    parser.add_argument("--no-install", action="store_true", help="Skip dependency installation")
    parser.add_argument("--output", default="test_execution_results", help="Output directory")
    parser.add_argument("--base-url", help="Override base URL for tests")
    parser.add_argument("--ci", action="store_true", help="CI mode (no interactive output)")
    
    args = parser.parse_args()
    
    # Build configuration
    config = ExecutionConfig(
        test_dir=args.test_dir,
        execution_mode=args.mode,
        browser=args.browser,
        headless=args.headless,
        parallel_workers=args.parallel,
        max_retries=args.retries,
        timeout_per_test=args.timeout,
        auto_install_deps=not args.no_install,
        output_dir=args.output,
        base_url=args.base_url,
        ci_mode=args.ci
    )
    
    # Run executor
    executor = TestExecutor(config)
    results = asyncio.run(executor.execute())
    
    # Exit with appropriate code
    sys.exit(0 if results.get("success") else 1)


if __name__ == "__main__":
    main()