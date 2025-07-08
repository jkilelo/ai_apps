"""
Example of how to integrate MongoDB tracking with app executions
"""
import asyncio
from datetime import datetime
import json

# Add the ai_apps directory to Python path
import sys
sys.path.append('/var/www/ai_apps')

from apps.common.services.execution_tracker import get_execution_tracker
from apps.common.database import ExecutionStatus, StepStatus


async def example_workflow_execution():
    """Example of tracking a complete workflow execution"""
    
    # Get the execution tracker
    tracker = await get_execution_tracker()
    
    # Simulate a UI Web Auto Testing workflow
    print("Starting UI Web Auto Testing workflow...")
    
    # Track the main execution
    async with tracker.track_execution(
        app_id=2,
        app_name="ui_web_auto_testing",
        user_id="demo_user",
        metadata={
            "source": "example_script",
            "environment": "development"
        }
    ) as execution_id:
        
        print(f"Created execution: {execution_id}")
        
        # Step 1: Element Extraction
        print("\nStep 1: Extracting web elements...")
        async with tracker.track_step(
            execution_id=execution_id,
            step_id=1,
            step_name="element_extraction_using_python_playwright",
            input_data={"web_page_url": "https://example.com"}
        ) as set_output:
            
            # Simulate element extraction
            await asyncio.sleep(2)  # Simulate processing time
            
            # Set the output
            extracted_elements = [
                {
                    "id": "elem_1",
                    "type": "button",
                    "selector": "#submit-btn",
                    "text": "Submit"
                },
                {
                    "id": "elem_2",
                    "type": "input",
                    "selector": "#email-input",
                    "placeholder": "Email"
                }
            ]
            
            set_output({
                "extracted_elements": extracted_elements,
                "metadata": {
                    "total_elements": len(extracted_elements),
                    "pages_crawled": 1
                }
            })
            
            print(f"  - Extracted {len(extracted_elements)} elements")
        
        # Step 2: Generate Test Cases
        print("\nStep 2: Generating test cases...")
        async with tracker.track_step(
            execution_id=execution_id,
            step_id=2,
            step_name="generate_test_cases_using_llm",
            input_data={"extracted_elements": extracted_elements}
        ) as set_output:
            
            # Simulate test generation
            await asyncio.sleep(1)
            
            test_cases = [
                {
                    "id": "test_1",
                    "name": "Test submit button click",
                    "type": "positive",
                    "steps": ["Navigate to page", "Click submit button", "Verify action"]
                },
                {
                    "id": "test_2",
                    "name": "Test email validation",
                    "type": "negative",
                    "steps": ["Enter invalid email", "Submit form", "Verify error"]
                }
            ]
            
            set_output({
                "test_cases": test_cases,
                "metadata": {
                    "total_tests": len(test_cases),
                    "positive_tests": 1,
                    "negative_tests": 1
                }
            })
            
            print(f"  - Generated {len(test_cases)} test cases")
        
        # Step 3: Execute Test Cases
        print("\nStep 3: Executing test cases...")
        async with tracker.track_step(
            execution_id=execution_id,
            step_id=3,
            step_name="execute_test_cases",
            input_data={"test_cases": test_cases}
        ) as set_output:
            
            # Simulate test execution
            await asyncio.sleep(1.5)
            
            test_results = [
                {
                    "test_id": "test_1",
                    "test_name": "Test submit button click",
                    "status": "passed",
                    "duration": 0.5
                },
                {
                    "test_id": "test_2",
                    "test_name": "Test email validation",
                    "status": "passed",
                    "duration": 0.3
                }
            ]
            
            set_output({
                "test_results": test_results,
                "summary": {
                    "total": len(test_results),
                    "passed": 2,
                    "failed": 0,
                    "pass_rate": 100.0
                }
            })
            
            print(f"  - Executed {len(test_results)} tests (100% pass rate)")
        
        print(f"\nWorkflow completed successfully!")
    
    # Retrieve and display execution details
    print("\n" + "="*50)
    print("EXECUTION DETAILS")
    print("="*50)
    
    details = await tracker.get_execution_details(execution_id)
    
    print(f"\nExecution ID: {details['execution']['execution_id']}")
    print(f"Status: {details['execution']['status']}")
    print(f"Duration: {details['execution']['duration_ms']}ms")
    
    print("\nSteps:")
    for step in details['steps']:
        print(f"  - Step {step['step_id']}: {step['step_name']}")
        print(f"    Status: {step['status']}")
        print(f"    Duration: {step['duration_ms']}ms")
        if step.get('output'):
            print(f"    Output: {json.dumps(step['output'], indent=6)[:200]}...")


async def example_failed_execution():
    """Example of tracking a failed execution"""
    
    tracker = await get_execution_tracker()
    
    print("\n" + "="*50)
    print("SIMULATING FAILED EXECUTION")
    print("="*50)
    
    try:
        async with tracker.track_execution(
            app_id=2,
            app_name="ui_web_auto_testing",
            user_id="demo_user"
        ) as execution_id:
            
            print(f"\nCreated execution: {execution_id}")
            
            # Simulate a failing step
            async with tracker.track_step(
                execution_id=execution_id,
                step_id=1,
                step_name="element_extraction_using_python_playwright",
                input_data={"web_page_url": "https://invalid-url-that-fails.com"}
            ) as set_output:
                
                await asyncio.sleep(0.5)
                
                # Simulate an error
                raise Exception("Failed to connect to URL: Connection timeout")
                
    except Exception as e:
        print(f"\nExecution failed as expected: {e}")
    
    # Check the failed execution
    details = await tracker.get_execution_details(execution_id)
    print(f"\nFailed execution status: {details['execution']['status']}")
    print(f"Error: {details['execution']['error']}")


async def example_execution_history():
    """Example of retrieving execution history"""
    
    tracker = await get_execution_tracker()
    
    print("\n" + "="*50)
    print("EXECUTION HISTORY")
    print("="*50)
    
    history = await tracker.get_execution_history(
        user_id="demo_user",
        app_id=2,
        limit=5
    )
    
    print(f"\nFound {len(history)} recent executions:")
    
    for i, item in enumerate(history, 1):
        execution = item['execution']
        steps = item['steps']
        
        print(f"\n{i}. Execution {execution['execution_id'][:8]}...")
        print(f"   Status: {execution['status']}")
        print(f"   Started: {execution['started_at']}")
        print(f"   Duration: {execution.get('duration_ms', 'N/A')}ms")
        print(f"   Steps: {len(steps)}")


async def main():
    """Run all examples"""
    
    # Example 1: Successful workflow execution
    await example_workflow_execution()
    
    # Example 2: Failed execution
    await example_failed_execution()
    
    # Example 3: Query execution history
    await example_execution_history()
    
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())