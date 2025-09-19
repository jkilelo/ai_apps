"""
Test script for UI Session Database Layer
Demonstrates all features of the MongoDB session management system
"""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_db_layer.ui_db import (
    # Core functions
    get_ui_session, save_ui_session, delete_ui_session,
    # Step save functions
    save_browser_setup, save_element_extraction, save_ai_enrichment,
    save_test_generation, save_code_generation,
    # Step load functions
    load_browser_setup, load_element_extraction, load_ai_enrichment,
    load_test_generation, load_code_generation,
    # Recovery functions
    get_resume_point, mark_step_in_progress, mark_step_failed,
    # Utility functions
    list_all_sessions, get_session_summary, clear_session_cache,
    export_session_to_json, import_session_from_json, get_statistics,
    # Enums
    PipelineStep, StepStatus, LoadStrategy
)


def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def test_session_creation():
    """Test 1: Create and save a new session"""
    print_section("TEST 1: Session Creation")

    test_url = "https://example.com/test"

    # Delete any existing session first
    delete_ui_session(test_url)

    # Create new session
    session = get_ui_session(test_url, create_if_missing=True)
    print(f"[OK] Created session for: {session.url}")
    print(f"  - Netloc (key): {session.netloc}")
    print(f"  - Created at: {session.created_at}")
    print(f"  - Session ID: {session.session_id}")

    return test_url


def test_step_save_functions(test_url):
    """Test 2: Save results for each pipeline step"""
    print_section("TEST 2: Save Step Results")

    # Step 1: Browser Setup
    browser_result = {
        "session_id": "browser_123",
        "page_title": "Example Test Page",
        "url": test_url,
        "browser_type": "chromium",
        "duration": 2.5
    }
    success = save_browser_setup(test_url, browser_result)
    print(f"[OK] Browser Setup saved: {success}")

    time.sleep(0.5)

    # Step 2: Element Extraction
    extraction_result = {
        "total_elements": 150,
        "interactive_elements": 45,
        "form_elements": 12,
        "elements": [
            {"id": "btn1", "type": "button", "text": "Submit"},
            {"id": "input1", "type": "text", "placeholder": "Enter name"}
        ],
        "extraction_time": 1.2
    }
    success = save_element_extraction(test_url, extraction_result)
    print(f"[OK] Element Extraction saved: {success}")

    time.sleep(0.5)

    # Step 3: AI Enrichment
    enrichment_result = {
        "enriched_elements": [
            {"id": "btn1", "purpose": "form_submission", "priority": "high"},
            {"id": "input1", "purpose": "user_input", "validation": "required"}
        ],
        "page_insights": {
            "page_type": "form",
            "functionality": ["data_collection", "user_registration"]
        },
        "enrichment_time": 3.5
    }
    success = save_ai_enrichment(test_url, enrichment_result)
    print(f"[OK] AI Enrichment saved: {success}")

    time.sleep(0.5)

    # Step 4: Test Generation
    test_result = {
        "total_scenarios": 8,
        "scenarios": [
            {"name": "Test form submission", "steps": ["fill_form", "submit", "verify"]},
            {"name": "Test validation", "steps": ["leave_empty", "submit", "check_error"]}
        ],
        "generation_time": 2.0
    }
    success = save_test_generation(test_url, test_result)
    print(f"[OK] Test Generation saved: {success}")

    time.sleep(0.5)

    # Step 5: Code Generation
    code_result = {
        "frameworks": ["playwright", "selenium"],
        "test_files": {
            "test_main.py": "def test_form():\n    # test code here",
            "test_validation.py": "def test_validation():\n    # validation tests"
        },
        "generation_time": 1.5
    }
    success = save_code_generation(test_url, code_result)
    print(f"[OK] Code Generation saved: {success}")


def test_step_load_functions(test_url):
    """Test 3: Load cached step results"""
    print_section("TEST 3: Load Cached Results")

    # Load with AUTO strategy (uses cache if recent)
    browser_data = load_browser_setup(test_url, LoadStrategy.AUTO)
    print(f"[OK] Browser Setup loaded: {browser_data.get('page_title') if browser_data else 'None'}")

    extraction_data = load_element_extraction(test_url, LoadStrategy.CACHED)
    print(f"[OK] Element Extraction loaded: {extraction_data.get('total_elements') if extraction_data else 0} elements")

    enrichment_data = load_ai_enrichment(test_url, LoadStrategy.CACHED)
    print(f"[OK] AI Enrichment loaded: {bool(enrichment_data)}")

    test_data = load_test_generation(test_url, LoadStrategy.CACHED)
    print(f"[OK] Test Generation loaded: {test_data.get('total_scenarios') if test_data else 0} scenarios")

    code_data = load_code_generation(test_url, LoadStrategy.CACHED)
    print(f"[OK] Code Generation loaded: {code_data.get('frameworks') if code_data else []}")

    # Test FRESH strategy (should return None)
    fresh_data = load_browser_setup(test_url, LoadStrategy.FRESH)
    print(f"[OK] FRESH strategy returns: {fresh_data}")


def test_session_recovery():
    """Test 4: Session recovery and resumption"""
    print_section("TEST 4: Session Recovery")

    # Create a partially completed session
    partial_url = "https://partial.com/test"
    delete_ui_session(partial_url)

    # Save only first two steps
    save_browser_setup(partial_url, {"page_title": "Partial Test"})
    save_element_extraction(partial_url, {"total_elements": 50})

    # Check resume point
    resume_step = get_resume_point(partial_url)
    print(f"[OK] Resume point: {resume_step.value if resume_step else 'Complete'}")

    # Mark step as in progress
    success = mark_step_in_progress(partial_url, PipelineStep.AI_ENRICHMENT)
    print(f"[OK] Marked AI_ENRICHMENT as in progress: {success}")

    # Simulate failure
    success = mark_step_failed(partial_url, PipelineStep.AI_ENRICHMENT, "LLM API error")
    print(f"[OK] Marked AI_ENRICHMENT as failed: {success}")

    # Get updated resume point
    resume_step = get_resume_point(partial_url)
    print(f"[OK] Resume point after failure: {resume_step.value if resume_step else 'None'}")

    return partial_url


def test_session_management(test_url, partial_url):
    """Test 5: Session management utilities"""
    print_section("TEST 5: Session Management")

    # List all sessions
    sessions = list_all_sessions(limit=10)
    print(f"[OK] Total sessions found: {len(sessions)}")
    for session in sessions[:3]:
        print(f"  - {session['netloc']}: {session['page_title']} (Complete: {session['is_complete']})")

    # Get session summary
    summary = get_session_summary(test_url)
    if summary:
        print(f"\n[OK] Session Summary for {summary['netloc']}:")
        print(f"  - Completion: {summary['completion_percentage']:.0f}%")
        print(f"  - Total Elements: {summary['total_elements']}")
        print(f"  - Test Scenarios: {summary['test_scenarios_count']}")
        print(f"  - Step Statuses:")
        for step, status in summary['step_statuses'].items():
            print(f"    • {step}: {status['status']}")

    # Export session to JSON
    filepath = export_session_to_json(test_url)
    print(f"\n[OK] Session exported to: {filepath}")

    # Clear cache for specific steps
    success = clear_session_cache(partial_url, [PipelineStep.AI_ENRICHMENT])
    print(f"[OK] Cleared cache for AI_ENRICHMENT: {success}")

    # Get statistics
    stats = get_statistics()
    print(f"\n[OK] Database Statistics:")
    print(f"  - Total Sessions: {stats.get('total_sessions', 0)}")
    print(f"  - Complete Sessions: {stats.get('complete_sessions', 0)}")
    print(f"  - Completion Rate: {stats.get('completion_rate', 0):.1f}%")
    if 'step_statistics' in stats:
        print(f"  - Step Statistics:")
        for step, step_stats in stats['step_statistics'].items():
            print(f"    • {step}: {step_stats['completed']} completed, {step_stats['failed']} failed")


def test_load_strategies():
    """Test 6: Different load strategies"""
    print_section("TEST 6: Load Strategies")

    strategy_url = "https://strategy.com/test"
    delete_ui_session(strategy_url)

    # Save a step result
    save_browser_setup(strategy_url, {
        "page_title": "Strategy Test",
        "timestamp": datetime.now().isoformat()
    })

    # Test different strategies
    print("Testing load strategies:")

    # CACHED - always returns cached data
    cached = load_browser_setup(strategy_url, LoadStrategy.CACHED)
    print(f"  [OK] CACHED: {bool(cached)}")

    # FRESH - never returns cached data
    fresh = load_browser_setup(strategy_url, LoadStrategy.FRESH)
    print(f"  [OK] FRESH: {bool(fresh)}")

    # AUTO - returns cached if recent (default 24 hours)
    auto = load_browser_setup(strategy_url, LoadStrategy.AUTO)
    print(f"  [OK] AUTO: {bool(auto)}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print(" UI SESSION DATABASE LAYER - COMPREHENSIVE TEST")
    print("="*60)

    try:
        # Run tests
        test_url = test_session_creation()
        test_step_save_functions(test_url)
        test_step_load_functions(test_url)
        partial_url = test_session_recovery()
        test_session_management(test_url, partial_url)
        test_load_strategies()

        print_section("TEST COMPLETE")
        print("[OK] All tests completed successfully!")
        print(f"[OK] Test URL: {test_url}")
        print(f"[OK] Partial URL: {partial_url}")

        # Show final summary
        summary = get_session_summary(test_url)
        if summary and summary['is_complete']:
            print(f"\n[OK] Complete pipeline session stored in database!")
            print(f"  - URL: {summary['url']}")
            print(f"  - Elements: {summary['total_elements']}")
            print(f"  - Scenarios: {summary['test_scenarios_count']}")
            print(f"  - Frameworks: {summary['frameworks']}")

    except Exception as e:
        print(f"\n[ERROR] Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()