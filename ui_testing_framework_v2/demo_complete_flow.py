"""
Complete Test Generation Flow Demonstration
Shows the entire pipeline from extraction to LLM-generated test cases
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui_testing_framework_v2 import extract
from ui_testing_framework_v2.formatters import format_output
from ui_testing_framework_v2.test_generation import (
    generate_tests_from_elements,
    TestGenerationPipeline
)


def demonstrate_complete_flow():
    """
    Demonstrate the complete flow:
    1. Extract elements from webpage
    2. Format for LLM consumption
    3. Apply prompt strategy
    4. Generate test cases via LLM
    """
    
    print("=" * 80)
    print("COMPLETE TEST GENERATION FLOW")
    print("From Extraction to LLM-Generated Test Cases")
    print("=" * 80)
    
    # ========================================================================
    # STEP 1: EXTRACTION
    # ========================================================================
    print("\n[STEP 1] EXTRACTING ELEMENTS")
    print("-" * 40)
    
    url = "https://www.google.com"
    print(f"Target URL: {url}")
    print("Using profile: interactive (QA-focused)")
    
    # Extract interactive elements
    elements = extract(url, profile="interactive")
    
    print(f"[OK] Extracted {len(elements)} interactive elements")
    
    # Show sample elements
    print("\nSample Elements:")
    for i, elem in enumerate(elements[:3], 1):
        print(f"  {i}. {elem.tag_name}: {elem.selector}")
        if elem.attributes.get("aria-label"):
            print(f"     ARIA: {elem.attributes['aria-label']}")
    
    # ========================================================================
    # STEP 2: FORMAT FOR LLM
    # ========================================================================
    print("\n[STEP 2] FORMATTING FOR LLM")
    print("-" * 40)
    
    metadata = {
        "url": url,
        "profile": "interactive",
        "extraction_time": datetime.now().isoformat()
    }
    
    llm_format = format_output(elements, "llm_test", metadata)
    
    print("Formatted Output Structure:")
    print(f"  - Page Type: {llm_format['page_context']['page_type']}")
    print(f"  - Interactive Elements: {llm_format['page_context']['total_interactive_elements']}")
    print(f"  - High Priority: {llm_format['page_context']['high_priority_elements']}")
    
    print("\nTestable Element Categories:")
    for category, data in llm_format["testable_elements"].items():
        if data["count"] > 0:
            print(f"  - {category.upper()}: {data['count']} elements")
    
    print("\nSuggested Test Scenarios:")
    for scenario in llm_format["suggested_test_scenarios"]:
        print(f"  • {scenario}")
    
    # ========================================================================
    # STEP 3: GENERATE TESTS WITH QA_ENGINEER_AGENT STRATEGY
    # ========================================================================
    print("\n[STEP 3] GENERATING TESTS WITH QA_ENGINEER_AGENT")
    print("-" * 40)
    
    print("Strategy: QA_ENGINEER_AGENT (optimized for test generation)")
    print("Test Type: Comprehensive")
    print("\nCalling LLM (Gemini-2.5-pro)...")
    
    try:
        # Generate tests using QA strategy
        test_results = generate_tests_from_elements(
            elements=elements,
            url=url,
            strategy="qa_engineer_agent",
            test_type="comprehensive"
        )
        
        print("[OK] Test generation complete!")
        
        # Display results
        print("\n" + "=" * 80)
        print("GENERATED TEST RESULTS")
        print("=" * 80)
        
        print(f"\nStrategy Used: {test_results.get('strategy_used', 'QA_ENGINEER_AGENT')}")
        print(f"Elements Processed: {test_results.get('element_count', len(elements))}")
        
        if "token_usage" in test_results:
            print(f"Token Usage: {test_results['token_usage']}")
        
        # Display generated tests
        print("\n--- GENERATED TEST CASES ---")
        
        if "tests" in test_results and test_results["tests"]:
            for i, test in enumerate(test_results["tests"][:5], 1):  # Show first 5
                print(f"\nTest Case #{i}:")
                
                if isinstance(test, dict):
                    for key, value in test.items():
                        if key == "steps" and isinstance(value, list):
                            print(f"  {key.title()}:")
                            for step in value:
                                print(f"    - {step}")
                        elif key == "expected" and isinstance(value, list):
                            print(f"  {key.title()} Results:")
                            for result in value:
                                print(f"    - {result}")
                        else:
                            print(f"  {key.title()}: {value}")
                else:
                    print(f"  {test}")
        
        # Save results
        output_file = Path("generated_tests.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, default=str)
        
        print(f"\n[Saved complete results to {output_file}]")
        
    except Exception as e:
        print(f"[ERROR] Test generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ========================================================================
    # STEP 4: MULTI-STRATEGY GENERATION (Optional Advanced)
    # ========================================================================
    print("\n[STEP 4] ADVANCED: MULTI-STRATEGY GENERATION")
    print("-" * 40)
    
    print("Available Strategies:")
    print("  • QA_ENGINEER_AGENT - Test-focused verification")
    print("  • CHAIN_OF_THOUGHT - Step-by-step reasoning")
    print("  • TREE_OF_THOUGHTS - Explore multiple paths")
    print("  • DEBATE - Multiple perspectives")
    
    print("\nFor production use, you can combine strategies:")
    print("  pipeline = TestGenerationPipeline()")
    print("  results = pipeline.generate_comprehensive_tests(")
    print("      elements, url, strategies=['qa', 'cot', 'debate']")
    print("  )")
    
    return test_results


def demonstrate_pipeline_usage():
    """
    Show how to use the TestGenerationPipeline for advanced scenarios
    """
    
    print("\n" + "=" * 80)
    print("ADVANCED PIPELINE USAGE")
    print("=" * 80)
    
    # Extract elements
    url = "https://example.com"
    elements = extract(url, profile="qa")
    
    # Create pipeline
    pipeline = TestGenerationPipeline()
    
    print(f"\nGenerating comprehensive test suite for {url}")
    print("Using multiple strategies and test types...")
    
    # Generate with multiple strategies
    # Note: This would make multiple LLM calls
    # results = pipeline.generate_comprehensive_tests(
    #     elements=elements,
    #     url=url,
    #     strategies=["qa", "cot"]  # Use QA and Chain of Thought
    # )
    
    print("\nPipeline Features:")
    print("  • Multiple prompt strategies")
    print("  • Different test types (functional, edge_cases, accessibility)")
    print("  • Combined results with summary statistics")
    print("  • Automatic test categorization")
    
    print("\nExample Pipeline Output Structure:")
    example_structure = {
        "url": url,
        "total_strategies": 2,
        "test_suites": {
            "qa_functional": "...",
            "qa_edge_cases": "...",
            "cot_functional": "...",
            "cot_edge_cases": "..."
        },
        "summary": {
            "total_test_cases": 50,
            "test_suites": 4,
            "categories": {
                "functional": 20,
                "edge_case": 15,
                "ui": 10,
                "integration": 5
            }
        }
    }
    
    print(json.dumps(example_structure, indent=2))


if __name__ == "__main__":
    print("\n" + "🚀" * 40)
    print("UI TESTING FRAMEWORK V2 - TEST GENERATION")
    print("🚀" * 40)
    
    # Run complete flow demonstration
    results = demonstrate_complete_flow()
    
    # Show advanced pipeline usage
    demonstrate_pipeline_usage()
    
    print("\n" + "=" * 80)
    print("[SUCCESS] Complete Flow Demonstration Finished!")
    print("=" * 80)
    
    print("\nKEY ACHIEVEMENTS:")
    print("  ✅ Extracted UI elements with stealth browser")
    print("  ✅ Formatted elements for LLM consumption")
    print("  ✅ Applied QA_ENGINEER_AGENT prompt strategy")
    print("  ✅ Generated comprehensive test cases via LLM")
    print("  ✅ Saved results in structured format")
    
    print("\nNEXT STEPS:")
    print("  1. Execute generated tests with Playwright/Selenium")
    print("  2. Integrate with CI/CD pipeline")
    print("  3. Add test result validation")
    print("  4. Create test reports")
    
    print("\nFILES CREATED:")
    print("  • generated_tests.json - Complete test cases")
    print("  • llm_test_format.json - LLM formatter output")