"""
Example usage of the Web Automation SDK
"""

import asyncio
import json
from datetime import datetime
from web_automation_framework import (
    WebAutomationSDK, 
    WorkflowConfig, 
    ExecutionConfig,
    TestType
)

async def example_basic_workflow():
    """Example: Basic workflow execution"""
    print("=== Basic Workflow Example ===\n")
    
    async with WebAutomationSDK() as sdk:
        # Configure the workflow
        config = WorkflowConfig(
            target_url="https://example.com",
            test_name="Basic Example Test",
            description="Testing example.com with default settings",
            profile="qa_tester"
        )
        
        # Run the complete workflow
        print("Starting workflow...")
        results = await sdk.run_complete_workflow(config)
        
        # Display results
        print(f"\nTest Results:")
        print(f"- Success Rate: {results['metrics']['success_rate']:.1f}%")
        print(f"- Total Tests: {results['test_execution']['total_tests']}")
        print(f"- Passed: {results['test_execution']['passed_tests']}")
        print(f"- Failed: {results['test_execution']['failed_tests']}")
        print(f"- Execution Time: {results['test_execution']['execution_time']:.2f}s")
        
        return results

async def example_step_by_step():
    """Example: Step-by-step workflow execution with monitoring"""
    print("\n=== Step-by-Step Workflow Example ===\n")
    
    sdk = WebAutomationSDK()
    
    try:
        # Step 1: Target Setup
        print("Step 1: Setting up target and extracting elements...")
        config = WorkflowConfig(
            target_url="https://example.com",
            test_name="Step-by-Step Example",
            profile="qa_tester",
            include_accessibility=True
        )
        
        session = await sdk.start_workflow(config)
        print(f"Session created: {session.session_id}")
        
        # Wait for element extraction to complete
        step1_result = await sdk.wait_for_step_completion(session.session_id, 1)
        print(f"✓ Element extraction completed: {step1_result.message}")
        
        # Get session status to see extracted elements
        status = await sdk.get_workflow_status(session.session_id)
        element_count = len(status.elements_data.get('elements', []))
        print(f"  Found {element_count} elements")
        
        # Step 2: Workflow Builder
        print("\nStep 2: Building test workflow...")
        await sdk.build_workflow(
            session.session_id, 
            test_types=["functional", "accessibility"]
        )
        
        step2_result = await sdk.wait_for_step_completion(session.session_id, 2)
        print(f"✓ Test generation completed: {step2_result.message}")
        
        # Check generated tests
        status = await sdk.get_workflow_status(session.session_id)
        test_count = len(status.workflow_data.get('test_cases', []))
        print(f"  Generated {test_count} test cases")
        
        # Step 3: Test Execution
        print("\nStep 3: Executing tests...")
        execution_config = ExecutionConfig(
            execution_mode="parallel",
            capture_screenshots=True,
            max_retries=2
        )
        
        await sdk.execute_tests(session.session_id, execution_config)
        
        # Monitor execution progress
        while True:
            step3_status = await sdk.get_step_status(session.session_id, 3)
            if step3_status.status == "completed":
                print(f"✓ Test execution completed: {step3_status.message}")
                break
            elif step3_status.status == "failed":
                print(f"✗ Test execution failed: {step3_status.message}")
                break
            else:
                print(f"  Status: {step3_status.status}")
                await asyncio.sleep(2)
        
        # Step 4: Results & Report
        print("\nStep 4: Generating report...")
        results = await sdk.get_results(session.session_id, format="json")
        
        print(f"✓ Report generated successfully")
        print(f"\nFinal Results:")
        print(f"- Success Rate: {results['metrics']['success_rate']:.1f}%")
        print(f"- Coverage Score: {results['metrics']['coverage_score']:.1f}%")
        print(f"- Accessibility Score: {results['metrics']['accessibility_compliance']:.1f}%")
        
        # Save results to file
        with open(f"results_{session.session_id}.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to: results_{session.session_id}.json")
        
        return results
        
    finally:
        await sdk.close()

async def example_cross_browser_testing():
    """Example: Cross-browser testing"""
    print("\n=== Cross-Browser Testing Example ===\n")
    
    async with WebAutomationSDK() as sdk:
        config = WorkflowConfig(
            target_url="https://example.com",
            test_name="Cross-Browser Test Suite"
        )
        
        execution_config = ExecutionConfig(
            cross_browser=True,
            browsers=["chrome", "firefox", "edge"],
            execution_mode="parallel"
        )
        
        print("Running tests across multiple browsers...")
        results = await sdk.run_complete_workflow(
            config=config,
            execution_config=execution_config
        )
        
        # Display browser-specific results
        if "browser_results" in results:
            print("\nBrowser Compatibility Results:")
            for browser, result in results["browser_results"].items():
                status = "✓ PASS" if result["passed"] else "✗ FAIL"
                print(f"- {browser}: {status}")
        
        return results

async def example_parallel_workflows():
    """Example: Running multiple workflows in parallel"""
    print("\n=== Parallel Workflows Example ===\n")
    
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net"
    ]
    
    async with WebAutomationSDK() as sdk:
        # Create tasks for parallel execution
        tasks = []
        for url in urls:
            config = WorkflowConfig(
                target_url=url,
                test_name=f"Test for {url}"
            )
            task = sdk.run_quick_test(url, test_name=f"Quick test of {url}")
            tasks.append(task)
        
        print(f"Running {len(urls)} workflows in parallel...")
        start_time = datetime.now()
        
        # Execute all workflows in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Display summary
        print(f"\nCompleted in {duration:.2f} seconds")
        print("\nResults Summary:")
        for i, (url, result) in enumerate(zip(urls, results)):
            if isinstance(result, Exception):
                print(f"- {url}: ✗ ERROR - {str(result)}")
            else:
                success_rate = result['metrics']['success_rate']
                print(f"- {url}: {success_rate:.1f}% success rate")
        
        return results

async def example_custom_element_extraction():
    """Example: Custom element extraction and test generation"""
    print("\n=== Custom Element Extraction Example ===\n")
    
    async with WebAutomationSDK() as sdk:
        # Extract elements only (without full workflow)
        print("Extracting elements from target page...")
        elements = await sdk.extract_elements(
            url="https://example.com",
            profile="developer"
        )
        
        print(f"Found {len(elements)} elements")
        
        # Show element types
        element_types = {}
        for element in elements:
            elem_type = element.get('type', 'unknown')
            element_types[elem_type] = element_types.get(elem_type, 0) + 1
        
        print("\nElement breakdown:")
        for elem_type, count in element_types.items():
            print(f"- {elem_type}: {count}")
        
        # Generate tests from extracted elements
        print("\nGenerating custom test cases...")
        test_data = await sdk.generate_tests(
            elements=elements,
            test_type="functional"
        )
        
        print(f"Generated {len(test_data['test_cases'])} test cases")
        
        # Display some test names
        print("\nSample test cases:")
        for test in test_data['test_cases'][:5]:
            print(f"- {test['name']}")
        
        return test_data

async def example_error_handling():
    """Example: Proper error handling"""
    print("\n=== Error Handling Example ===\n")
    
    async with WebAutomationSDK() as sdk:
        # Example 1: Handle invalid URL
        try:
            config = WorkflowConfig(
                target_url="not-a-valid-url",
                test_name="Invalid URL Test"
            )
            await sdk.run_complete_workflow(config)
        except Exception as e:
            print(f"Expected error for invalid URL: {e}")
        
        # Example 2: Handle timeout
        try:
            config = WorkflowConfig(
                target_url="https://example.com",
                test_name="Timeout Test"
            )
            session = await sdk.start_workflow(config)
            
            # Use very short timeout
            await sdk.wait_for_step_completion(
                session.session_id, 
                step=1, 
                timeout=1  # 1 second timeout
            )
        except TimeoutError as e:
            print(f"Expected timeout error: {e}")
        
        # Example 3: Handle missing session
        try:
            await sdk.get_workflow_status("non-existent-session-id")
        except Exception as e:
            print(f"Expected error for missing session: {e}")

async def main():
    """Run all examples"""
    examples = [
        example_basic_workflow,
        example_step_by_step,
        example_cross_browser_testing,
        example_parallel_workflows,
        example_custom_element_extraction,
        example_error_handling
    ]
    
    for example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\nError in {example_func.__name__}: {e}")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())