"""
Comprehensive E2E Test Runner for Web Automation Pipeline
Senior QA Engineer Pattern: Test Orchestration and Reporting
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import asyncio
import signal
from typing import Dict, List, Optional

class E2ETestRunner:
    """Test runner with comprehensive reporting and process management"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.frontend_dir = self.project_root.parent / "simple_apps_original" / "frontend"
        self.backend_dir = self.project_root / "backend" / "web_automation"
        self.test_dir = self.project_root / "e2e_tests"
        self.results_dir = self.test_dir / "test-results"
        self.processes: List[subprocess.Popen] = []
        self.test_report: Dict = {
            "start_time": None,
            "end_time": None,
            "duration": None,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        
    def setup_environment(self):
        """Setup test environment"""
        print("\n" + "="*60)
        print("[SETUP] Preparing E2E Test Environment")
        print("="*60)
        
        # Create results directory
        self.results_dir.mkdir(parents=True, exist_ok=True)
        (self.results_dir / "screenshots").mkdir(exist_ok=True)
        (self.results_dir / "failures").mkdir(exist_ok=True)
        
        # Check dependencies
        self._check_dependencies()
        
    def _check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("\n[CHECK] Verifying dependencies...")
        
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            print(f"  - Node.js: {result.stdout.strip()}")
        except FileNotFoundError:
            print("  [ERROR] Node.js not found. Please install Node.js")
            sys.exit(1)
            
        # Check Python
        print(f"  - Python: {sys.version.split()[0]}")
        
        # Check if frontend dependencies are installed
        if not (self.frontend_dir / "node_modules").exists():
            print("  [INFO] Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=self.frontend_dir, check=True)
            
        # Check if Playwright is installed
        if not (self.test_dir / "node_modules").exists():
            print("  [INFO] Installing Playwright...")
            subprocess.run(["npm", "install"], cwd=self.test_dir, check=True)
            subprocess.run(["npx", "playwright", "install"], cwd=self.test_dir, check=True)
            
    def start_backend(self) -> subprocess.Popen:
        """Start the backend server"""
        print("\n[BACKEND] Starting backend server on port 5175...")
        
        # Set environment variables
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)
        
        # Start backend
        process = subprocess.Popen(
            [sys.executable, "startup.py"],
            cwd=self.backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for backend to be ready
        print("  Waiting for backend to be ready...")
        for i in range(30):
            try:
                import requests
                response = requests.get("http://localhost:5175/api/ui/health")
                if response.status_code == 200:
                    print("  [SUCCESS] Backend is ready!")
                    break
            except:
                time.sleep(2)
        else:
            print("  [ERROR] Backend failed to start")
            process.terminate()
            sys.exit(1)
            
        self.processes.append(process)
        return process
        
    def start_frontend(self) -> subprocess.Popen:
        """Start the frontend dev server"""
        print("\n[FRONTEND] Starting frontend on port 3000...")
        
        # Start frontend
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=self.frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for frontend to be ready
        print("  Waiting for frontend to be ready...")
        for i in range(30):
            try:
                import requests
                response = requests.get("http://localhost:3000")
                if response.status_code == 200:
                    print("  [SUCCESS] Frontend is ready!")
                    break
            except:
                time.sleep(2)
        else:
            print("  [ERROR] Frontend failed to start")
            process.terminate()
            sys.exit(1)
            
        self.processes.append(process)
        return process
        
    def run_tests(self, test_type: str = "all") -> int:
        """Run Playwright tests"""
        print("\n" + "="*60)
        print(f"[TESTS] Running {test_type} E2E tests")
        print("="*60)
        
        self.test_report["start_time"] = datetime.now().isoformat()
        
        # Determine test command
        if test_type == "smoke":
            cmd = ["npm", "run", "test:smoke"]
        elif test_type == "api":
            cmd = ["npm", "run", "test:api"]
        elif test_type == "mobile":
            cmd = ["npm", "run", "test:mobile"]
        else:
            cmd = ["npm", "run", "test"]
            
        # Run tests
        result = subprocess.run(
            cmd,
            cwd=self.test_dir,
            capture_output=True,
            text=True
        )
        
        self.test_report["end_time"] = datetime.now().isoformat()
        
        # Parse results
        self._parse_test_results(result)
        
        return result.returncode
        
    def _parse_test_results(self, result):
        """Parse test results from Playwright output"""
        output = result.stdout + result.stderr
        
        # Look for test summary
        if "passed" in output:
            import re
            
            # Extract test counts
            passed_match = re.search(r"(\d+) passed", output)
            failed_match = re.search(r"(\d+) failed", output)
            skipped_match = re.search(r"(\d+) skipped", output)
            
            if passed_match:
                self.test_report["passed"] = int(passed_match.group(1))
            if failed_match:
                self.test_report["failed"] = int(failed_match.group(1))
            if skipped_match:
                self.test_report["skipped"] = int(skipped_match.group(1))
                
        # Extract errors
        if "Error:" in output:
            errors = output.split("Error:")
            for error in errors[1:]:
                self.test_report["errors"].append(error.strip()[:200])
                
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("[REPORT] Test Execution Summary")
        print("="*60)
        
        total = self.test_report["passed"] + self.test_report["failed"] + self.test_report["skipped"]
        
        print(f"\nTotal Tests: {total}")
        print(f"  - Passed: {self.test_report['passed']} ✓")
        print(f"  - Failed: {self.test_report['failed']} ✗")
        print(f"  - Skipped: {self.test_report['skipped']} -")
        
        if total > 0:
            pass_rate = (self.test_report['passed'] / total) * 100
            print(f"\nPass Rate: {pass_rate:.1f}%")
            
        if self.test_report["errors"]:
            print("\n[ERRORS]")
            for i, error in enumerate(self.test_report["errors"][:5], 1):
                print(f"  {i}. {error}")
                
        # Save report to file
        report_file = self.results_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(self.test_report, f, indent=2)
        print(f"\nDetailed report saved to: {report_file}")
        
        # Show HTML report
        print("\nTo view HTML report, run:")
        print(f"  cd {self.test_dir} && npm run report")
        
    def cleanup(self):
        """Cleanup processes"""
        print("\n[CLEANUP] Stopping services...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                
        print("  Services stopped.")
        
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print("\n[INTERRUPT] Stopping tests...")
        self.cleanup()
        sys.exit(0)
        
    def run(self, test_type: str = "all", skip_setup: bool = False):
        """Main test execution flow"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Setup
            if not skip_setup:
                self.setup_environment()
                self.start_backend()
                self.start_frontend()
                
            # Run tests
            print("\n[INFO] Services are ready. Starting tests in 5 seconds...")
            time.sleep(5)
            
            exit_code = self.run_tests(test_type)
            
            # Generate report
            self.generate_report()
            
            # Return exit code
            return exit_code
            
        finally:
            # Cleanup
            self.cleanup()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run E2E tests for Web Automation Pipeline")
    parser.add_argument(
        "--type",
        choices=["all", "smoke", "api", "mobile"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="Skip service setup (assume they're already running)"
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run tests in headed mode (show browser)"
    )
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     Web Automation Pipeline - E2E Test Suite              ║
    ║     Senior QA Engineer Edition                            ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    runner = E2ETestRunner()
    
    # Override test command if headed mode
    if args.headed:
        os.environ["HEADED"] = "true"
        
    exit_code = runner.run(test_type=args.type, skip_setup=args.skip_setup)
    
    # Exit with test result code
    sys.exit(exit_code)


if __name__ == "__main__":
    main()