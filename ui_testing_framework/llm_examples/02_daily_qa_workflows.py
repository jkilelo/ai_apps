#!/usr/bin/env python3
"""
Daily QA Workflow Examples
=========================

This example demonstrates real-world QA workflows that happen daily:
- Morning standup test coverage analysis
- Bug triage and analysis  
- Sprint planning test estimation
- Code review test gap identification
- Production incident response

Run directly: python 02_daily_qa_workflows.py
"""

import sys
from pathlib import Path

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import query_llm, StrategyType
import json
from datetime import datetime


def morning_standup_analysis():
    """Generate test coverage analysis for morning standup."""
    print("☀️ MORNING STANDUP - TEST COVERAGE ANALYSIS")
    print("=" * 55)
    
    # Simulate a feature being discussed in standup
    feature_description = """
    New Feature: Social Media Login Integration
    
    Details:
    - Users can now log in with Google, Facebook, or Twitter
    - Existing account linking functionality
    - Profile data synchronization from social platforms
    - New privacy settings for social data usage
    - Mobile app integration included
    
    Status: Ready for QA testing
    """
    
    messages = [{
        "role": "user",
        "content": f"""
        Feature being discussed in standup:
        {feature_description}
        
        Provide a quick test coverage analysis for standup discussion:
        1. What should be tested (priority areas)
        2. What might be missed (blind spots)
        3. Risk areas requiring extra attention
        4. Estimated testing effort (hours)
        
        Keep it concise for standup - 2-3 bullet points per section.
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.CHAIN_OF_THOUGHT, max_tokens=600)
    print(response.content)
    print("\n" + "=" * 55 + "\n")
    return response.content


def bug_triage_analysis():
    """Rapid bug analysis for triage meeting."""
    print("🐛 BUG TRIAGE - RAPID ANALYSIS")
    print("=" * 35)
    
    # Simulate bugs reported overnight
    bugs = [
        {
            "id": "BUG-1234",
            "title": "Cart total shows $0 after applying 100% discount code",
            "description": "When users apply discount code 'HOLIDAY100' for 100% off, cart total becomes $0 but checkout button is disabled",
            "reporter": "Customer Support",
            "environment": "Production"
        },
        {
            "id": "BUG-1235", 
            "title": "Profile image upload fails for files over 2MB",
            "description": "Users report profile image upload shows 'success' message but image doesn't appear. Happens with files larger than 2MB",
            "reporter": "QA Team",
            "environment": "Staging"
        },
        {
            "id": "BUG-1236",
            "title": "Password reset emails not being sent",
            "description": "Multiple users report not receiving password reset emails. Email service logs show 'delivery failed' errors",
            "reporter": "Customer Support", 
            "environment": "Production"
        }
    ]
    
    for bug in bugs:
        messages = [{
            "role": "user",
            "content": f"""
            Bug Report: {bug['title']}
            ID: {bug['id']}
            Description: {bug['description']}
            Environment: {bug['environment']}
            
            Provide rapid triage analysis:
            1. Severity (Critical/High/Medium/Low) with reasoning
            2. Likely root cause
            3. User impact assessment
            4. Quick verification test
            5. Recommended priority
            
            Be concise - 1-2 sentences per point for triage meeting.
            """
        }]
        
        response = query_llm(messages, strategy=StrategyType.REACT, max_tokens=400)
        print(f"🔍 Analysis for {bug['id']}:")
        print(response.content)
        print("-" * 50)
    
    print("=" * 35 + "\n")
    return bugs


def sprint_planning_estimation():
    """Generate testing effort estimates for sprint planning."""
    print("📋 SPRINT PLANNING - TESTING EFFORT ESTIMATION")
    print("=" * 50)
    
    # Simulate user stories for upcoming sprint
    user_stories = [
        "As a user, I want to filter products by price range so I can find items within my budget",
        "As a user, I want to save items to my wishlist so I can purchase them later", 
        "As a user, I want to share product links on social media so I can get opinions from friends",
        "As an admin, I want to export customer data to CSV so I can analyze purchase patterns",
        "As a user, I want to receive email notifications for price drops on wishlist items",
        "As a user, I want to compare up to 3 products side-by-side so I can make informed decisions"
    ]
    
    messages = [{
        "role": "user",
        "content": f"""
        User Stories for Sprint Planning:
        {chr(10).join([f'{i+1}. {story}' for i, story in enumerate(user_stories)])}
        
        Estimate testing effort for each story:
        - Number of test cases needed
        - Testing complexity (Simple/Medium/Complex)
        - Estimated testing hours
        - Key risk factors
        - Dependencies on other stories
        
        Format as a table for easy sprint planning discussion.
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.LEAST_TO_MOST, max_tokens=800)
    print(response.content)
    print("\n" + "=" * 50 + "\n")
    return response.content


def code_review_test_gaps():
    """Identify test coverage gaps during code review."""
    print("👀 CODE REVIEW - TEST COVERAGE GAP ANALYSIS")
    print("=" * 50)
    
    # Simulate code changes from a pull request
    code_changes = """
    Pull Request #456: Enhanced Payment Processing
    
    Changes Made:
    - Added retry logic for failed payment attempts (3 retries with exponential backoff)
    - Increased payment gateway timeout from 30s to 60s
    - Added fallback to secondary payment processor if primary fails
    - Implemented payment fraud detection scoring
    - Added support for new payment method: Buy Now Pay Later (BNPL)
    - Enhanced logging for payment failure scenarios
    - Added database cleanup for abandoned payment sessions
    
    Files Changed:
    - payment_processor.py (125 lines added, 45 modified)
    - fraud_detection.py (78 lines added)
    - payment_gateway.py (34 lines modified)
    - database_cleanup.py (67 lines added)
    """
    
    messages = [{
        "role": "user",
        "content": f"""
        Code Review - Payment Processing Changes:
        {code_changes}
        
        Identify test coverage gaps:
        1. Untested scenarios that could break in production
        2. Edge cases that need specific test coverage
        3. Integration points requiring testing
        4. Performance test considerations
        5. Security test requirements
        
        Priority order by risk level (High/Medium/Low).
        Suggest specific test scenarios for each gap.
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.TREE_OF_THOUGHTS, max_tokens=900)
    print(response.content)
    print("\n" + "=" * 50 + "\n")
    return response.content


def production_incident_response():
    """Generate emergency test plan for production issues."""
    print("🚨 PRODUCTION INCIDENT - EMERGENCY TEST PLAN")
    print("=" * 50)
    
    # Simulate production incident
    incident = """
    PRODUCTION INCIDENT: Payment Gateway Intermittent Failures
    
    Incident Details:
    - Started: 2 hours ago
    - Symptoms: 15% of payment attempts return 500 errors
    - Impact: ~200 failed transactions, $50,000 potential lost revenue
    - User Reports: "Payment failed, please try again" messages
    - Monitoring: Payment success rate dropped from 98% to 83%
    - Initial Investigation: Primary payment gateway showing high latency
    
    Proposed Fix: 
    - Route traffic to secondary payment gateway
    - Reduce timeout from 60s to 30s to fail faster
    - Implement circuit breaker pattern
    """
    
    messages = [{
        "role": "user",
        "content": f"""
        Production Incident Response:
        {incident}
        
        Create emergency test plan with 3 phases:
        
        Phase 1: Immediate Smoke Tests (5 minutes)
        - Critical path verification
        - Basic functionality check
        
        Phase 2: Critical Flow Tests (15 minutes)  
        - End-to-end payment flows
        - Error handling verification
        
        Phase 3: Regression Tests (30 minutes)
        - Related system verification
        - Performance validation
        
        Focus on preventing further customer impact.
        Include specific test steps and success criteria.
        """
    }]
    
    response = query_llm(messages, strategy=StrategyType.CHAIN_OF_THOUGHT, temperature=0.1)
    print(response.content)
    print("\n" + "=" * 50 + "\n")
    return response.content


def save_workflow_results(results, filename):
    """Save workflow results to file."""
    output_file = Path(__file__).parent / filename
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "workflow_type": "Daily QA Workflows",
        "scenarios_covered": list(results.keys()),
        "results": results,
        "usage": "Real-world QA scenarios for daily use"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Workflow results saved to: {output_file}")


def main():
    """Run all daily QA workflow examples."""
    print("🔄 DAILY QA WORKFLOW EXAMPLES")
    print("=============================")
    print("Simulating real-world QA scenarios that happen every day...")
    print()
    
    results = {}
    
    try:
        # Run daily workflow scenarios
        results["standup_analysis"] = morning_standup_analysis()
        results["bug_triage"] = bug_triage_analysis()
        results["sprint_estimation"] = sprint_planning_estimation()
        results["code_review_gaps"] = code_review_test_gaps()
        results["incident_response"] = production_incident_response()
        
        # Save results
        save_workflow_results(results, "daily_qa_workflows_results.json")
        
        print("✅ SUCCESS: All daily QA workflows completed!")
        print(f"📊 Processed {len(results)} workflow scenarios")
        print("💡 These examples show how LLM can accelerate daily QA tasks")
        print("📁 Check daily_qa_workflows_results.json for complete analysis")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()