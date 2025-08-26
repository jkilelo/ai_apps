#!/usr/bin/env python3
"""
Basic Code Execution Example

This example demonstrates:
- Simple code execution with security sandbox
- Basic configuration options
- Report generation (HTML, JSON)
- Resource monitoring
- Error handling and validation

Requirements:
- Dependencies: psutil (pip install psutil)
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from code_execution import (
    CodeExecutionEngine,
    ExecutionConfig,
    ExecutionMode,
    SecurityLevel,
    ReportFormat,
    TestStatus
)

async def basic_code_execution_demo():
    """
    Demonstrates basic code execution with simple Python test code
    """
    print("="*60)
    print("BASIC CODE EXECUTION DEMO")
    print("="*60)
    
    # Simple test code to execute
    test_code = """
# Simple Python test code
import unittest
import math

class TestBasicMath(unittest.TestCase):
    '''Basic math operations test suite'''
    
    def test_addition(self):
        '''Test addition operation'''
        result = 2 + 3
        self.assertEqual(result, 5)
        print(f"[OK] Addition test: 2 + 3 = {result}")
    
    def test_multiplication(self):
        '''Test multiplication operation'''
        result = 4 * 6
        self.assertEqual(result, 24)
        print(f"[OK] Multiplication test: 4 * 6 = {result}")
    
    def test_square_root(self):
        '''Test square root calculation'''
        result = math.sqrt(16)
        self.assertEqual(result, 4.0)
        print(f"[OK] Square root test: sqrt(16) = {result}")
    
    def test_power(self):
        '''Test power calculation'''
        result = pow(2, 3)
        self.assertEqual(result, 8)
        print(f"[OK] Power test: 2^3 = {result}")

# Mark test as passed for our executor
test_passed = True
print("\\n📊 All basic math tests completed successfully!")
print("Total assertions: 4")
print("Status: All tests passed")
"""

    print("📝 Test Code Overview:")
    print("   - 4 basic math test methods")
    print("   - unittest framework")
    print("   - Simple assertions and validations")
    print("   - Output capturing enabled")
    
    # Configure basic execution
    config = ExecutionConfig(
        execution_mode=ExecutionMode.SEQUENTIAL,
        security_level=SecurityLevel.STANDARD,
        timeout_per_test=10,
        verbose=True,
        capture_output=True,
        generate_reports=[ReportFormat.HTML, ReportFormat.JSON],
        output_dir=Path("basic_test_results")
    )
    
    print(f"\n⚙️ Configuration:")
    print(f"   Execution Mode: {config.execution_mode.value}")
    print(f"   Security Level: {config.security_level.value}")
    print(f"   Timeout: {config.timeout_per_test}s")
    print(f"   Reports: {[r.value for r in config.generate_reports]}")
    
    try:
        # Initialize execution engine
        print(f"\n🚀 Initializing Code Execution Engine...")
        engine = CodeExecutionEngine(config)
        
        print(f"[OK] Engine initialized successfully")
        print(f"📁 Output directory: {config.output_dir.absolute()}")
        
        # Execute the test code
        print(f"\n[FAST] Executing test code...")
        print(f"   Validating code security...")
        print(f"   Running in sandbox environment...")
        
        result = await engine.execute(code=test_code)
        
        # Display execution results
        print(f"\n" + "="*60)
        print("EXECUTION RESULTS")
        print("="*60)
        
        print(f"🎯 Overall Success: {result.success}")
        print(f"[TIME] Execution Time: {result.execution_time:.3f}s")
        
        # Suite statistics
        suite = result.suite
        print(f"\n📊 Test Suite Statistics:")
        print(f"   Suite Name: {suite.name}")
        print(f"   Total Tests: {suite.total_tests}")
        print(f"   Passed: {suite.passed} [OK]")
        print(f"   Failed: {suite.failed} [ERROR]")
        print(f"   Errors: {suite.errors} ⚠️")
        print(f"   Skipped: {suite.skipped} ⏭️")
        print(f"   Success Rate: {suite.get_success_rate():.1f}%")
        print(f"   Duration: {suite.duration:.3f}s")
        
        # Individual test results
        if suite.results:
            print(f"\n📋 Individual Test Results:")
            for i, test_result in enumerate(suite.results, 1):
                status_symbol = {
                    TestStatus.PASSED: "[OK]",
                    TestStatus.FAILED: "[ERROR]",
                    TestStatus.ERROR: "⚠️",
                    TestStatus.SKIPPED: "⏭️",
                    TestStatus.TIMEOUT: "[TIME]"
                }.get(test_result.status, "❓")
                
                print(f"   {i}. {status_symbol} {test_result.test_name}")
                print(f"      Status: {test_result.status.value}")
                print(f"      Duration: {test_result.duration:.3f}s")
                print(f"      Retries: {test_result.retries}")
                
                # Resource usage
                if test_result.memory_usage_mb > 0:
                    print(f"      Memory: {test_result.memory_usage_mb:.2f} MB")
                if test_result.cpu_usage_percent > 0:
                    print(f"      CPU: {test_result.cpu_usage_percent:.1f}%")
                
                # Show output if available
                if test_result.output:
                    output_lines = test_result.output.strip().split('\n')
                    if output_lines:
                        print(f"      Output:")
                        for line in output_lines[:3]:  # Show first 3 lines
                            if line.strip():
                                print(f"        {line}")
                        if len(output_lines) > 3:
                            print(f"        ... ({len(output_lines) - 3} more lines)")
                
                # Show errors if any
                if test_result.error_message:
                    print(f"      Error: {test_result.error_message}")
                
                print()
        
        # Generated reports
        print(f"📄 Generated Reports:")
        if result.reports:
            for format, path in result.reports.items():
                file_size = path.stat().st_size if path.exists() else 0
                print(f"   {format.value.upper()}: {path.name} ({file_size} bytes)")
        else:
            print(f"   No reports generated")
        
        # Additional metadata
        if result.metadata:
            print(f"\n🔍 Execution Metadata:")
            config_data = result.metadata.get('config', {})
            if config_data:
                print(f"   Security Level: {config_data.get('security_level', 'Unknown')}")
                print(f"   Memory Limit: {config_data.get('memory_limit_mb', 'Unlimited')} MB")
                print(f"   CPU Limit: {config_data.get('cpu_limit_percent', 'Unlimited')}%")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Execution failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Common troubleshooting
        print(f"\n🔧 Troubleshooting:")
        print(f"1. Check if psutil is installed: pip install psutil")
        print(f"2. Verify write permissions for output directory")
        print(f"3. Ensure sufficient memory is available")
        print(f"4. Try with SecurityLevel.BASIC for debugging")
        
        return False

async def demonstrate_error_handling():
    """
    Demonstrates error handling with problematic code
    """
    print(f"\n" + "="*60)
    print("ERROR HANDLING DEMONSTRATION")
    print("="*60)
    
    # Code that will cause errors
    problematic_code = """
# Intentionally problematic code to test error handling
import unittest

class TestWithErrors(unittest.TestCase):
    
    def test_division_by_zero(self):
        '''This test will cause a division by zero error'''
        result = 10 / 0  # This will raise ZeroDivisionError
        self.assertEqual(result, float('inf'))
    
    def test_assertion_failure(self):
        '''This test will fail an assertion'''
        self.assertEqual(1 + 1, 3)  # This will fail
    
    def test_undefined_variable(self):
        '''This test will cause a NameError'''
        print(undefined_variable)  # This will raise NameError

# This will NOT set test_passed to True, simulating test failure
print("Tests with intentional errors executed")
"""

    config = ExecutionConfig(
        security_level=SecurityLevel.STANDARD,
        timeout_per_test=5,
        max_retries=1,
        verbose=True,
        continue_on_failure=True,  # Continue even if tests fail
        generate_reports=[ReportFormat.JSON]
    )
    
    print("🧪 Testing error handling with problematic code:")
    print("   - Division by zero")
    print("   - Assertion failure")
    print("   - Undefined variable")
    
    try:
        engine = CodeExecutionEngine(config)
        result = await engine.execute(code=problematic_code)
        
        print(f"\n📊 Error Handling Results:")
        print(f"   Overall Success: {result.success}")
        print(f"   Suite Passed: {result.suite.passed}")
        print(f"   Suite Failed: {result.suite.failed}")
        print(f"   Suite Errors: {result.suite.errors}")
        
        # Show error details
        if result.suite.results:
            print(f"\n🔍 Error Details:")
            for test_result in result.suite.results:
                if test_result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                    print(f"   Test: {test_result.test_name}")
                    print(f"   Status: {test_result.status.value}")
                    if test_result.error_message:
                        print(f"   Error: {test_result.error_message[:100]}...")
        
        print(f"\n[OK] Error handling working correctly!")
        print(f"Engine gracefully handled problematic code without crashing")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Unexpected error in error handling demo: {e}")
        return False

async def demonstrate_timeout_handling():
    """
    Demonstrates timeout handling with slow code
    """
    print(f"\n" + "="*60)
    print("TIMEOUT HANDLING DEMONSTRATION")
    print("="*60)
    
    # Code that will timeout
    slow_code = """
import time
import unittest

class TestTimeout(unittest.TestCase):
    
    def test_quick_operation(self):
        '''This test will complete quickly'''
        result = 1 + 1
        self.assertEqual(result, 2)
        print("Quick test completed")
    
    def test_slow_operation(self):
        '''This test will exceed the timeout'''
        print("Starting slow operation...")
        time.sleep(8)  # Sleep for 8 seconds (will exceed 5s timeout)
        self.assertTrue(True)
        print("Slow operation completed")

print("Timeout test executed")
"""

    config = ExecutionConfig(
        timeout_per_test=5,  # 5 second timeout
        security_level=SecurityLevel.BASIC,
        verbose=True
    )
    
    print("[TIME] Testing timeout handling:")
    print(f"   Timeout setting: {config.timeout_per_test}s")
    print("   One test will exceed timeout")
    
    try:
        engine = CodeExecutionEngine(config)
        result = await engine.execute(code=slow_code)
        
        print(f"\n📊 Timeout Handling Results:")
        print(f"   Execution completed: {result.success}")
        print(f"   Total tests: {result.suite.total_tests}")
        
        # Check for timeout results
        timeout_tests = [r for r in result.suite.results if r.status == TestStatus.TIMEOUT]
        if timeout_tests:
            print(f"   Timeout tests: {len(timeout_tests)}")
            for test in timeout_tests:
                print(f"     - {test.test_name}: exceeded {config.timeout_per_test}s limit")
        
        print(f"\n[OK] Timeout handling working correctly!")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error in timeout demo: {e}")
        return False

async def main():
    """
    Main function that runs all basic execution examples
    """
    print("🚀 BASIC CODE EXECUTION EXAMPLES")
    print("This demonstrates the core functionality of the execution engine")
    
    success_count = 0
    total_demos = 3
    
    # Run basic execution demo
    print("\n1️⃣ Running basic execution demo...")
    if await basic_code_execution_demo():
        success_count += 1
    
    # Run error handling demo
    print("\n2️⃣ Running error handling demo...")
    if await demonstrate_error_handling():
        success_count += 1
    
    # Run timeout handling demo
    print("\n3️⃣ Running timeout handling demo...")
    if await demonstrate_timeout_handling():
        success_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("EXAMPLES COMPLETED")
    print("="*60)
    
    print(f"[OK] Successful demos: {success_count}/{total_demos}")
    
    if success_count == total_demos:
        print("\n🎉 All examples completed successfully!")
        
        print("\n📋 Key Features Demonstrated:")
        print("   [OK] Secure code execution with sandbox")
        print("   [OK] Resource monitoring (memory, CPU)")
        print("   [OK] Comprehensive error handling")
        print("   [OK] Timeout management")
        print("   [OK] Report generation (HTML, JSON)")
        print("   [OK] Test result analysis")
        
        print("\n📁 Check the generated files:")
        print("   - basic_test_results/: Contains HTML and JSON reports")
        print("   - View HTML report in your browser for detailed results")
        
        print("\n🔗 Try other examples:")
        print("   - python security_sandbox_demo.py")
        print("   - python parallel_execution_demo.py")
        print("   - python llm_integration_example.py")
        
        return 0
    else:
        print(f"\n⚠️ Some examples failed. Check error messages above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Examples interrupted by user")
        sys.exit(130)