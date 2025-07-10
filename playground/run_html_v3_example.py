#!/usr/bin/env python3
"""
Example script showing how to run html_v3_examples programmatically
"""

import asyncio
import json
from html_v3_examples import (
    create_data_quality_chain,
    create_job_application_chain,
    create_insurance_claim_chain,
    create_support_ticket_chain,
    DatabaseType, ExperienceLevel, Department
)

async def run_data_quality_example():
    """Run the data quality check example"""
    print("=== Data Quality Check Example ===\n")
    
    # Create the chain
    chain = create_data_quality_chain()
    
    # Step 1: Data source selection
    print("Step 1: Data Source Selection")
    step1_html = chain.generate_form_html("step_1")
    print(f"Generated form with {len(step1_html)} characters")
    
    step1_data = {
        "database_type": DatabaseType.POSTGRESQL.value,
        "connection_string": "postgresql://user:pass@localhost/testdb",
        "table_name": "customers",
        "sample_size": "1000"
    }
    
    result1 = await chain.process_step("step_1", step1_data, {})
    print(f"Response: {result1['next_step_id']}")
    print(f"Discovered columns: {len(result1['chain_state']['step_step_1_response']['columns'])}")
    
    # Step 2: Quality checks
    print("\nStep 2: Quality Check Configuration")
    columns = result1['chain_state']['step_step_1_response']['columns']
    
    step2_data = {
        "database_type": DatabaseType.POSTGRESQL.value,
        "table_name": "customers",
        "columns_to_check": [col["name"] for col in columns[:3]],
        "check_nulls": True,
        "check_duplicates": True,
        "check_patterns": False,
        "check_outliers": False
    }
    
    result2 = await chain.process_step("step_2", step2_data, result1['chain_state'])
    quality_score = result2['chain_state']['step_step_2_response']['quality_score']
    print(f"Quality Score: {quality_score}")
    
    # Step 3: Actions
    print("\nStep 3: Quality Actions")
    step3_data = {
        "table_name": "customers",
        "quality_score": quality_score,
        "generate_report": True,
        "create_cleaned_table": True,
        "cleaned_table_name": "customers_cleaned",
        "add_constraints": False,
        "schedule_monitoring": True,
        "monitoring_frequency": "daily"
    }
    
    result3 = await chain.process_step("step_3", step3_data, result2['chain_state'])
    print(f"Completed: {result3['completed']}")
    print(f"Actions taken: {len(result3['final_data']['step_step_3_response']['actions_completed'])}")


async def run_job_application_example():
    """Run the job application example showing conditional routing"""
    print("\n\n=== Job Application Example ===\n")
    
    chain = create_job_application_chain()
    
    # Test Engineering path
    print("Testing Engineering Department Path:")
    eng_data = {
        "full_name": "Jane Developer",
        "email": "jane@example.com",
        "phone": "+1-555-1234",
        "experience_level": ExperienceLevel.SENIOR.value,
        "department": Department.ENGINEERING.value,
        "years_experience": "10",
        "resume_text": "Senior software engineer with 10 years experience..."
    }
    
    result = await chain.process_step("basic_info", eng_data, {})
    print(f"Next step: {result['next_step_id']} (should be 'tech_assessment')")
    print("Senior-level fields injected:", "leadership_experience" in result['next_form_html'])
    
    # Test Sales path
    print("\nTesting Sales Department Path:")
    sales_data = {
        "full_name": "John Seller",
        "email": "john@example.com",
        "phone": "+1-555-5678",
        "experience_level": ExperienceLevel.MID.value,
        "department": Department.SALES.value,
        "years_experience": "5",
        "resume_text": "Sales professional..."
    }
    
    result = await chain.process_step("basic_info", sales_data, {})
    print(f"Next step: {result['next_step_id']} (should be 'sales_assessment')")


def main():
    """Run the examples"""
    print("HTML v3 Examples - Programmatic Demo\n")
    
    # Run async examples
    asyncio.run(run_data_quality_example())
    asyncio.run(run_job_application_example())
    
    print("\n\nTo see the full interactive experience, visit http://localhost:8037")


if __name__ == "__main__":
    main()