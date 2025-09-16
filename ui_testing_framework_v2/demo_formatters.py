"""
Demonstrate different output formats for various use cases
Shows how the same extraction can be formatted for LLM test generation,
accessibility testing, visual testing, and API testing
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui_testing_framework_v2 import extract
from ui_testing_framework_v2.formatters import format_output


def demonstrate_formatters():
    """Show all formatter outputs for the same extraction"""
    
    print("=" * 80)
    print("OUTPUT FORMATTERS DEMONSTRATION")
    print("Different formats for different use cases")
    print("=" * 80)
    
    # Extract elements using interactive profile
    url = "https://www.google.com"
    print(f"\nExtracting from: {url} with 'interactive' profile")
    elements = extract(url, profile="interactive")
    
    metadata = {
        "url": url,
        "profile": "interactive",
        "element_count": len(elements)
    }
    
    print(f"Extracted {len(elements)} elements\n")
    
    # 1. LLM TEST GENERATION FORMAT (Highest Priority)
    print("\n" + "=" * 80)
    print("1. LLM TEST GENERATION FORMAT")
    print("   Optimized for feeding to LLMs to generate test cases")
    print("=" * 80)
    
    llm_format = format_output(elements, "llm_test", metadata)
    
    print("\n--- Page Context ---")
    print(json.dumps(llm_format["page_context"], indent=2))
    
    print("\n--- Testable Elements Summary ---")
    for element_type, data in llm_format["testable_elements"].items():
        if data["count"] > 0:
            print(f"\n{element_type.upper()}: {data['count']} elements")
            print(f"  Test Hints: {', '.join(data['test_hints'])}")
            if data["elements"][:2]:  # Show first 2
                for elem in data["elements"][:2]:
                    print(f"  - {elem['description']} [{elem['selector']}]")
    
    print("\n--- Suggested Test Scenarios ---")
    for scenario in llm_format["suggested_test_scenarios"]:
        print(f"  • {scenario}")
    
    print("\n--- LLM Prompt Context ---")
    print(f"  {llm_format['llm_prompt_context']}")
    
    # Save LLM format for inspection
    with open("llm_test_format.json", "w") as f:
        json.dump(llm_format, f, indent=2)
    print("\n[Saved to llm_test_format.json]")
    
    # 2. ACCESSIBILITY TESTING FORMAT
    print("\n" + "=" * 80)
    print("2. ACCESSIBILITY TESTING FORMAT")
    print("   Focus on ARIA attributes and accessibility compliance")
    print("=" * 80)
    
    accessibility_format = format_output(elements, "accessibility", metadata)
    
    print("\n--- Accessibility Summary ---")
    print(json.dumps(accessibility_format["accessibility_summary"], indent=2))
    
    if accessibility_format["recommendations"]:
        print("\n--- Recommendations ---")
        for rec in accessibility_format["recommendations"]:
            print(f"  • {rec}")
    
    # 3. VISUAL TESTING FORMAT
    print("\n" + "=" * 80)
    print("3. VISUAL TESTING FORMAT")
    print("   Bounding boxes and regions for visual regression testing")
    print("=" * 80)
    
    visual_format = format_output(elements, "visual", metadata)
    
    print("\n--- Visual Coverage ---")
    print(json.dumps(visual_format["viewport_coverage"], indent=2))
    
    print("\n--- Top 3 Largest Elements ---")
    for region in visual_format["visual_regions"][:3]:
        print(f"  {region['selector']}: {region['area']}px² at ({region['region']['x']}, {region['region']['y']})")
    
    print("\n--- Screenshot Regions ---")
    for region in visual_format["screenshot_regions"]:
        print(f"  {region['name']}: {region['region']}")
    
    # 4. API TESTING FORMAT
    print("\n" + "=" * 80)
    print("4. API TESTING FORMAT")
    print("   Forms, fields, and potential API endpoints")
    print("=" * 80)
    
    api_format = format_output(elements, "api", metadata)
    
    print("\n--- Forms Found ---")
    print(f"  Count: {len(api_format['forms'])}")
    
    print("\n--- Input Fields ---")
    for field in api_format["input_fields"][:5]:  # First 5
        print(f"  {field['name'] or 'unnamed'}: type={field['type']}, required={field.get('required', False)}")
    
    if api_format["test_data_requirements"]:
        print("\n--- Test Data Requirements ---")
        for req in api_format["test_data_requirements"]:
            print(f"  • {req}")
    
    return llm_format


def demonstrate_llm_test_generation_flow():
    """
    Show the complete flow for LLM test generation:
    1. Extract with interactive profile
    2. Format for LLM
    3. Create prompt for test generation
    """
    
    print("\n" + "=" * 80)
    print("LLM TEST GENERATION FLOW")
    print("=" * 80)
    
    # Step 1: Extract
    print("\nStep 1: Extract interactive elements")
    elements = extract("https://www.google.com", profile="interactive")
    print(f"  [OK] Extracted {len(elements)} interactive elements")
    
    # Step 2: Format for LLM
    print("\nStep 2: Format output for LLM consumption")
    llm_format = format_output(elements, "llm_test", {"url": "https://www.google.com"})
    print(f"  [OK] Formatted into LLM-optimized structure")
    
    # Step 3: Create test generation prompt
    print("\nStep 3: Create test generation prompt")
    
    test_prompt = f"""
Based on the following UI elements, generate comprehensive test cases:

Page Type: {llm_format['page_context']['page_type']}
URL: {llm_format['page_context']['url']}
Interactive Elements: {llm_format['page_context']['total_interactive_elements']}

Key Elements:
"""
    
    for element_type, data in llm_format["testable_elements"].items():
        if data["count"] > 0:
            test_prompt += f"\n{element_type.upper()} ({data['count']}): "
            test_prompt += ", ".join([e["description"] for e in data["elements"][:3]])
    
    test_prompt += f"""

Test Scenarios to Cover:
{chr(10).join(['- ' + s for s in llm_format['suggested_test_scenarios']])}

Generate test cases that cover:
1. Happy path scenarios
2. Edge cases and validation
3. Error handling
4. Accessibility requirements
"""
    
    print(test_prompt)
    
    print("\n" + "=" * 80)
    print("This prompt can now be sent to any LLM (GPT-4, Claude, Gemini)")
    print("to generate comprehensive test cases based on the extracted elements")
    print("=" * 80)
    
    return test_prompt


if __name__ == "__main__":
    # Show all formatters
    llm_format = demonstrate_formatters()
    
    # Show complete LLM test generation flow
    test_prompt = demonstrate_llm_test_generation_flow()
    
    print("\n[SUCCESS] Demonstration complete!")
    print("Files created:")
    print("  - llm_test_format.json (complete LLM format)")
    print("\nNext steps:")
    print("  1. Send the formatted output to LLM for test generation")
    print("  2. Use prompts from prompts_optimized.py for advanced strategies")
    print("  3. Receive and execute generated test cases")