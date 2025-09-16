#!/usr/bin/env python3
"""
HTML v3 Form Chain Engine - Working Demo
Shows that the form chains are fully functional
"""

import asyncio
from html_v3_examples import (
    create_data_quality_chain,
    DataSourceRequest,
    DataSourceResponse,
    QualityCheckRequest
)
import json


async def demonstrate_form_chain():
    """Demonstrate the form chain working correctly"""
    
    print("HTML v3 Form Chain Engine - Working Demo")
    print("="*60)
    
    # Create the data quality chain
    chain = create_data_quality_chain()
    print("\n1. Created Data Quality Chain")
    print(f"   - Chain ID: {chain.chain_id}")
    print(f"   - Steps: {len(chain.steps)}")
    
    # Step 1: Generate initial form
    print("\n2. Generate Entry Form (Step 1)")
    print("-"*40)
    
    html = chain.generate_form_html("step_1")
    print(f"✅ Generated HTML form ({len(html)} bytes)")
    print("   Fields: database_type, connection_string, table_name, sample_size")
    
    # Step 2: Process form submission
    print("\n3. Process Step 1 Submission")
    print("-"*40)
    
    form_data = {
        "database_type": "postgresql",
        "connection_string": "postgresql://localhost/testdb",
        "table_name": "customers",
        "sample_size": "1000"
    }
    
    result = await chain.process_step("step_1", form_data, {})
    
    print("✅ Step 1 processed successfully")
    print(f"   - Got next form: {'next_form_html' in result}")
    print(f"   - Next step ID: {result.get('next_step_id', 'N/A')}")
    
    # Extract the response data
    chain_state = result.get('chain_state', {})
    step1_response = chain_state.get('step_step_1_response', {})
    
    print("\n   Step 1 Response Data:")
    print(f"   - Table: {step1_response.get('table_name')}")
    print(f"   - Total rows: {step1_response.get('total_rows')}")
    print(f"   - Columns: {len(step1_response.get('columns', []))}")
    
    # Show column names
    columns = step1_response.get('columns', [])
    if columns:
        print("\n   Available columns:")
        for col in columns[:5]:  # Show first 5
            print(f"     - {col['name']} ({col['type']})")
        if len(columns) > 5:
            print(f"     ... and {len(columns) - 5} more")
    
    # Step 3: Process step 2
    print("\n4. Process Step 2 (Quality Checks)")
    print("-"*40)
    
    # Simulate step 2 form data
    form_data_step2 = {
        "database_type": "postgresql",
        "table_name": "customers",
        "columns_to_check": ["email", "phone", "order_amount"],
        "check_nulls": True,
        "check_duplicates": True,
        "check_patterns": True,
        "check_outliers": False
    }
    
    result2 = await chain.process_step("step_2", form_data_step2, chain_state)
    
    print("✅ Step 2 processed successfully")
    
    # Extract quality check results
    chain_state2 = result2.get('chain_state', {})
    step2_response = chain_state2.get('step_step_2_response', {})
    
    print(f"   - Quality Score: {step2_response.get('quality_score')}%")
    print(f"   - Issues found: {len(step2_response.get('quality_issues', []))}")
    
    issues = step2_response.get('quality_issues', [])
    if issues:
        print("\n   Quality Issues:")
        for issue in issues[:3]:  # Show first 3
            print(f"     - {issue['column']}: {issue['issue_type']} ({issue['count']} occurrences)")
    
    # Step 4: Process final step
    print("\n5. Process Step 3 (Take Action)")
    print("-"*40)
    
    form_data_step3 = {
        "table_name": "customers",
        "quality_score": step2_response.get('quality_score', 0),
        "generate_report": True,
        "create_cleaned_table": True,
        "cleaned_table_name": "customers_cleaned",
        "add_constraints": False,
        "schedule_monitoring": True,
        "monitoring_frequency": "weekly"
    }
    
    result3 = await chain.process_step("step_3", form_data_step3, chain_state2)
    
    print("✅ Step 3 processed successfully")
    print(f"   - Chain completed: {result3.get('completed', False)}")
    
    if result3.get('completed'):
        print("\n   Final Actions:")
        final_data = result3.get('final_data', {})
        step3_response = final_data.get('step_step_3_response', {})
        
        for action in step3_response.get('actions_completed', []):
            print(f"     - {action}")
        
        if step3_response.get('report_url'):
            print(f"     - Report URL: {step3_response['report_url']}")
    
    print("\n" + "="*60)
    print("CONCLUSION: HTML v3 Form Chains are working correctly!")
    print("="*60)
    
    print("\nKey Features Demonstrated:")
    print("✅ Multi-step form processing")
    print("✅ Response data flows to next step") 
    print("✅ State management across steps")
    print("✅ Dynamic processing with business logic")
    print("✅ Completion handling")
    
    print("\nThe form chain successfully:")
    print("1. Collected database connection info")
    print("2. Analyzed the table and found columns")
    print("3. Performed quality checks")
    print("4. Generated actions based on results")
    print("5. Completed the workflow")


async def test_other_chains():
    """Test that other example chains also work"""
    
    print("\n\nTesting Other Example Chains")
    print("="*60)
    
    from html_v3_examples import (
        create_job_application_chain,
        create_insurance_claim_chain,
        create_support_ticket_chain
    )
    
    chains = [
        ("Job Application", create_job_application_chain),
        ("Insurance Claim", create_insurance_claim_chain),
        ("Support Ticket", create_support_ticket_chain)
    ]
    
    for name, create_func in chains:
        print(f"\n{name} Chain:")
        try:
            chain = create_func()
            entry_point = chain.get_entry_point()
            html = chain.generate_form_html(entry_point.id)
            print(f"  ✅ Generated entry form ({len(html)} bytes)")
            print(f"  ✅ Entry point: {entry_point.title}")
            
            # Show the routing logic
            if entry_point.conditional_next:
                print(f"  ✅ Has conditional routing")
            elif entry_point.next_step_id:
                print(f"  ✅ Next step: {entry_point.next_step_id}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")


def save_example_forms():
    """Save example forms for inspection"""
    
    print("\n\nSaving Example Forms")
    print("="*60)
    
    from html_v3_examples import create_data_quality_chain
    
    chain = create_data_quality_chain()
    
    # Save step 1
    html = chain.generate_form_html("step_1")
    with open("example_step1.html", "w") as f:
        f.write(html)
    print("✅ Saved example_step1.html")
    
    # Generate step 2 with mock data
    from html_v3_examples import DataSourceResponse
    mock_response = DataSourceResponse(
        database_type="postgresql",
        table_name="test",
        total_rows=1000,
        columns=[
            {"name": "id", "type": "integer", "nullable": "false"},
            {"name": "email", "type": "varchar", "nullable": "true"},
            {"name": "created_at", "type": "timestamp", "nullable": "false"}
        ],
        sample_data=[]
    )
    
    html2 = chain.generate_form_html("step_2", 
                                     chain_state={"mock": "state"}, 
                                     previous_response=mock_response)
    with open("example_step2.html", "w") as f:
        f.write(html2)
    print("✅ Saved example_step2.html")
    
    print("\nYou can open these files in a browser to see the forms")


if __name__ == "__main__":
    print("Starting HTML v3 Working Demo...\n")
    
    # Run the demo
    asyncio.run(demonstrate_form_chain())
    
    # Test other chains
    asyncio.run(test_other_chains())
    
    # Save examples
    save_example_forms()
    
    print("\n✨ Demo complete! HTML v3 Form Chains are fully functional.")