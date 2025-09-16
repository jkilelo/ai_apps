#!/usr/bin/env python3
"""
Batch Processing Examples
========================

This example demonstrates processing multiple QA tasks in batches:
- Batch test case generation for multiple features
- Parallel processing with async operations
- Bulk test data generation
- Mass bug analysis
- Sprint planning for multiple epics

Run directly: python 05_batch_processing.py
"""

import sys
from pathlib import Path
import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import query_llm, aquery_llm, StrategyType


def batch_feature_testing():
    """Generate test cases for multiple features in batch."""
    print("📦 BATCH FEATURE TEST GENERATION")
    print("=" * 35)
    
    # Multiple features to test
    features = [
        {
            "name": "User Registration",
            "description": "Allow users to create new accounts with email verification",
            "priority": "high"
        },
        {
            "name": "Password Reset",
            "description": "Enable users to reset forgotten passwords via email",
            "priority": "high"
        },
        {
            "name": "Profile Management",
            "description": "Users can update profile information, avatar, and preferences",
            "priority": "medium"
        },
        {
            "name": "Two-Factor Authentication",
            "description": "Add SMS and authenticator app based 2FA for enhanced security",
            "priority": "high"
        },
        {
            "name": "Social Media Login",
            "description": "Integration with Google, Facebook, and Twitter for quick login",
            "priority": "medium"
        },
        {
            "name": "Account Deletion",
            "description": "Allow users to permanently delete their accounts with data cleanup",
            "priority": "low"
        }
    ]
    
    results = {}
    total_start = time.time()
    
    for i, feature in enumerate(features, 1):
        print(f"Processing feature {i}/{len(features)}: {feature['name']}")
        
        messages = [{
            "role": "user",
            "content": f"""
            Generate comprehensive test cases for this feature:
            
            Feature: {feature['name']}
            Description: {feature['description']}
            Priority: {feature['priority']}
            
            Include:
            - Functional test cases
            - Edge cases and boundary conditions
            - Error handling scenarios
            - Security considerations
            - Performance aspects
            
            Format as numbered list with Given-When-Then structure.
            """
        }]
        
        start_time = time.time()
        response = query_llm(messages, strategy=StrategyType.CHAIN_OF_THOUGHT)
        execution_time = time.time() - start_time
        
        results[feature['name']] = {
            "description": feature['description'],
            "priority": feature['priority'],
            "test_cases": response.content,
            "generation_time": execution_time
        }
        
        print(f"  ✅ Generated in {execution_time:.2f}s")
    
    total_time = time.time() - total_start
    
    print(f"\n📊 Batch Summary:")
    print(f"  Features processed: {len(features)}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average per feature: {total_time/len(features):.2f}s")
    print("\n" + "=" * 35 + "\n")
    
    return results


async def parallel_test_generation():
    """Generate test cases in parallel using async operations."""
    print("⚡ PARALLEL TEST CASE GENERATION")
    print("=" * 35)
    
    # Test scenarios to process in parallel
    scenarios = [
        "Login form validation with email and password",
        "Shopping cart add/remove/update operations",
        "Payment processing with multiple payment methods",
        "User profile update with image upload",
        "Search functionality with filters and sorting",
        "Mobile responsive design testing",
        "API rate limiting and throttling",
        "Database performance under load"
    ]
    
    async def generate_single_test(scenario):
        """Generate test cases for a single scenario."""
        messages = [{
            "role": "user",
            "content": f"""
            Generate test cases for: {scenario}
            
            Include positive, negative, and edge cases.
            Keep it concise but comprehensive.
            """
        }]
        
        start_time = time.time()
        response = await aquery_llm(messages, strategy=StrategyType.TREE_OF_THOUGHTS)
        execution_time = time.time() - start_time
        
        return {
            "scenario": scenario,
            "test_cases": response.content,
            "generation_time": execution_time
        }
    
    print(f"Starting parallel generation for {len(scenarios)} scenarios...")
    total_start = time.time()
    
    # Execute all scenarios in parallel
    tasks = [generate_single_test(scenario) for scenario in scenarios]
    results = await asyncio.gather(*tasks)
    
    total_time = time.time() - total_start
    
    print(f"\n📊 Parallel Execution Summary:")
    print(f"  Scenarios processed: {len(scenarios)}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average per scenario: {total_time/len(scenarios):.2f}s")
    print(f"  Time saved vs sequential: ~{(len(scenarios)*3-total_time):.1f}s")
    
    for result in results:
        print(f"  ✅ {result['scenario']} - {result['generation_time']:.2f}s")
    
    print("\n" + "=" * 35 + "\n")
    
    return {result["scenario"]: result for result in results}


def bulk_test_data_generation():
    """Generate large amounts of test data for different scenarios."""
    print("🔢 BULK TEST DATA GENERATION")
    print("=" * 30)
    
    data_requests = [
        {
            "type": "User Registration Data",
            "requirements": """
            Generate 25 sets of test data for user registration:
            - 15 valid user profiles (name, email, password, phone)
            - 10 invalid profiles covering different validation errors
            Include realistic names, diverse email domains, and varied phone formats
            """
        },
        {
            "type": "E-commerce Product Data", 
            "requirements": """
            Generate 20 product entries for testing:
            - Product names, descriptions, prices, categories
            - Mix of physical and digital products
            - Include edge cases (very long names, special characters, extreme prices)
            """
        },
        {
            "type": "Financial Transaction Data",
            "requirements": """
            Generate 30 financial transaction test cases:
            - Different currencies and amounts
            - Various transaction types (payment, refund, transfer)
            - Include boundary conditions (minimum/maximum amounts)
            - Add some invalid transaction scenarios
            """
        },
        {
            "type": "API Request Payloads",
            "requirements": """
            Generate 20 JSON payloads for API testing:
            - User management operations (create, update, delete)
            - Include valid and invalid JSON structures
            - Test different data types and field combinations
            """
        }
    ]
    
    results = {}
    
    for data_request in data_requests:
        print(f"Generating {data_request['type']}...")
        
        messages = [{
            "role": "user",
            "content": data_request['requirements']
        }]
        
        start_time = time.time()
        response = query_llm(messages, strategy=StrategyType.SELF_CONSISTENCY)
        execution_time = time.time() - start_time
        
        results[data_request['type']] = {
            "data": response.content,
            "generation_time": execution_time
        }
        
        print(f"  ✅ Generated in {execution_time:.2f}s")
    
    print("\n" + "=" * 30 + "\n")
    return results


def mass_bug_analysis():
    """Analyze multiple bug reports in batch."""
    print("🐛 MASS BUG ANALYSIS")
    print("=" * 20)
    
    # Simulate a batch of bug reports
    bug_reports = [
        {
            "id": "BUG-001",
            "title": "Search returns no results for valid queries",
            "description": "Users report that searching for existing products sometimes returns zero results",
            "severity": "high",
            "environment": "production"
        },
        {
            "id": "BUG-002", 
            "title": "Mobile app crashes on profile update",
            "description": "iOS app consistently crashes when users try to update profile picture",
            "severity": "critical",
            "environment": "production"
        },
        {
            "id": "BUG-003",
            "title": "Checkout process hangs on payment",
            "description": "Payment processing shows loading spinner indefinitely, no error message",
            "severity": "critical", 
            "environment": "production"
        },
        {
            "id": "BUG-004",
            "title": "Email notifications have broken formatting",
            "description": "HTML emails show raw HTML code instead of formatted content",
            "severity": "medium",
            "environment": "staging"
        },
        {
            "id": "BUG-005",
            "title": "CSV export downloads empty file",
            "description": "Admin dashboard CSV export functionality returns zero-byte files",
            "severity": "medium",
            "environment": "production"
        }
    ]
    
    results = {}
    
    for bug in bug_reports:
        print(f"Analyzing {bug['id']}: {bug['title'][:50]}...")
        
        messages = [{
            "role": "user",
            "content": f"""
            Analyze this bug report:
            
            ID: {bug['id']}
            Title: {bug['title']}
            Description: {bug['description']}
            Severity: {bug['severity']}
            Environment: {bug['environment']}
            
            Provide:
            1. Root cause analysis (possible causes)
            2. Impact assessment 
            3. Reproduction steps
            4. Testing strategy to verify fix
            5. Prevention recommendations
            
            Be specific and actionable.
            """
        }]
        
        start_time = time.time()
        response = query_llm(messages, strategy=StrategyType.REACT)
        execution_time = time.time() - start_time
        
        results[bug['id']] = {
            "bug_info": bug,
            "analysis": response.content,
            "analysis_time": execution_time
        }
        
        print(f"  ✅ Analyzed in {execution_time:.2f}s")
    
    print("\n" + "=" * 20 + "\n")
    return results


def sprint_planning_batch():
    """Process multiple epics for sprint planning."""
    print("📋 SPRINT PLANNING - MULTIPLE EPICS")
    print("=" * 37)
    
    epics = [
        {
            "name": "User Authentication Overhaul",
            "stories": [
                "Implement OAuth 2.0 login",
                "Add biometric authentication",
                "Create password strength meter",
                "Build account lockout protection",
                "Add login attempt monitoring"
            ]
        },
        {
            "name": "Mobile App Performance",
            "stories": [
                "Optimize image loading and caching",
                "Implement lazy loading for lists", 
                "Reduce app startup time",
                "Add offline mode support",
                "Optimize database queries"
            ]
        },
        {
            "name": "Payment System Enhancement",
            "stories": [
                "Add Apple Pay and Google Pay",
                "Implement subscription billing",
                "Build refund processing system",
                "Add multi-currency support",
                "Create payment analytics dashboard"
            ]
        }
    ]
    
    results = {}
    
    for epic in epics:
        print(f"Planning epic: {epic['name']}")
        
        stories_text = "\n".join([f"- {story}" for story in epic['stories']])
        
        messages = [{
            "role": "user",
            "content": f"""
            Sprint planning analysis for epic: {epic['name']}
            
            User Stories:
            {stories_text}
            
            Provide:
            1. Testing effort estimation (hours per story)
            2. Story complexity assessment (Simple/Medium/Complex)
            3. Testing dependencies and risks
            4. Recommended story ordering
            5. QA resource requirements
            6. Definition of Done criteria
            
            Format as a sprint planning summary.
            """
        }]
        
        start_time = time.time()
        response = query_llm(messages, strategy=StrategyType.LEAST_TO_MOST)
        execution_time = time.time() - start_time
        
        results[epic['name']] = {
            "stories": epic['stories'],
            "planning_analysis": response.content,
            "analysis_time": execution_time
        }
        
        print(f"  ✅ Planned in {execution_time:.2f}s")
    
    print("\n" + "=" * 37 + "\n")
    return results


def threaded_batch_processing():
    """Use threading for CPU-bound batch operations."""
    print("🧵 THREADED BATCH PROCESSING")
    print("=" * 30)
    
    # Different types of test analysis to run in parallel
    analysis_tasks = [
        {
            "name": "Security Test Review",
            "content": "Review security test coverage for authentication, authorization, input validation, and data encryption across web and mobile applications"
        },
        {
            "name": "Performance Test Planning", 
            "content": "Create comprehensive performance testing strategy for API endpoints, database queries, and front-end rendering under various load conditions"
        },
        {
            "name": "Accessibility Testing Guide",
            "content": "Generate accessibility testing checklist covering WCAG 2.1 guidelines, screen reader compatibility, and keyboard navigation testing"
        },
        {
            "name": "Cross-Browser Compatibility",
            "content": "Develop cross-browser testing matrix for Chrome, Firefox, Safari, Edge covering desktop and mobile viewports with different OS combinations"
        }
    ]
    
    def process_analysis_task(task):
        """Process a single analysis task."""
        messages = [{
            "role": "user",
            "content": f"""
            Create a comprehensive {task['name']} document:
            {task['content']}
            
            Include:
            - Detailed checklist items
            - Tools and techniques
            - Common pitfalls to avoid
            - Success criteria
            - Reporting format
            """
        }]
        
        start_time = time.time()
        response = query_llm(messages, strategy=StrategyType.GENERATED_KNOWLEDGE)
        execution_time = time.time() - start_time
        
        return {
            "task_name": task['name'],
            "result": response.content,
            "execution_time": execution_time
        }
    
    # Use ThreadPoolExecutor for parallel processing
    print(f"Processing {len(analysis_tasks)} analysis tasks in parallel...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_analysis_task, analysis_tasks))
    
    total_time = time.time() - start_time
    
    print(f"\n📊 Threaded Processing Summary:")
    print(f"  Tasks completed: {len(results)}")
    print(f"  Total time: {total_time:.2f}s")
    
    for result in results:
        print(f"  ✅ {result['task_name']} - {result['execution_time']:.2f}s")
    
    print("\n" + "=" * 30 + "\n")
    
    return {result["task_name"]: result for result in results}


def save_batch_results(all_results, filename):
    """Save all batch processing results to file."""
    output_file = Path(__file__).parent / filename
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "batch_operations": list(all_results.keys()),
        "total_operations": sum(len(results) if isinstance(results, dict) else 1 
                              for results in all_results.values()),
        "results": all_results,
        "summary": "Comprehensive batch processing examples for QA automation"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"📁 Batch results saved to: {output_file}")


async def main():
    """Run all batch processing examples."""
    print("📦 BATCH PROCESSING EXAMPLES")
    print("============================")
    print("Demonstrating efficient batch processing for QA tasks...")
    print()
    
    all_results = {}
    
    try:
        # Sequential batch processing
        all_results["batch_features"] = batch_feature_testing()
        
        # Parallel async processing
        all_results["parallel_tests"] = await parallel_test_generation()
        
        # Bulk data generation
        all_results["bulk_data"] = bulk_test_data_generation()
        
        # Mass analysis
        all_results["bug_analysis"] = mass_bug_analysis()
        
        # Sprint planning
        all_results["sprint_planning"] = sprint_planning_batch()
        
        # Threaded processing
        all_results["threaded_analysis"] = threaded_batch_processing()
        
        # Save all results
        save_batch_results(all_results, "batch_processing_results.json")
        
        print("✅ SUCCESS: All batch processing examples completed!")
        print(f"📊 Completed {len(all_results)} different batch operations")
        print("⚡ Demonstrated sequential, parallel, and threaded processing")
        print("📁 Check batch_processing_results.json for complete results")
        print()
        print("Batch Operations Summary:")
        print("  📦 Feature Testing - Sequential batch processing")
        print("  ⚡ Parallel Tests - Async concurrent generation")
        print("  🔢 Bulk Data - Large-scale test data creation")
        print("  🐛 Bug Analysis - Mass bug report analysis")
        print("  📋 Sprint Planning - Multiple epic analysis")
        print("  🧵 Threaded Analysis - CPU-bound parallel processing")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())