#!/usr/bin/env python3
"""
UI Testing Framework - Complete Pipeline Example
Demonstrates all 4 steps with a simple website
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

# Configuration for the demo
DEMO_URL = "http://quotes.toscrape.com"  # Simple, reliable test site
OUTPUT_DIR = Path("demo_output")

async def main():
    """Run complete pipeline demonstration"""
    
    print("\n" + "="*70)
    print("🚀 UI TESTING FRAMEWORK - COMPLETE PIPELINE DEMO")
    print("="*70)
    print(f"Target: {DEMO_URL}")
    print("="*70)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # ========================================================================
    # STEP 1: ELEMENT EXTRACTION
    # ========================================================================
    print("\n📍 Step 1: Extracting UI Elements...")
    
    from step1_element_extractor import UltimateElementExtractor, ExtractionConfig
    
    config = ExtractionConfig(
        headless=True,
        max_elements=30,
        timeout=30,
        enable_stealth=True
    )
    
    extractor = UltimateElementExtractor(config)
    elements = await extractor.extract(DEMO_URL)
    
    print(f"✅ Extracted {len(elements)} elements")
    
    # Convert to dict format and save
    elements_dict = []
    for elem in elements[:30]:  # Limit for demo
        elements_dict.append({
            'tag_name': elem.tag_name,
            'element_id': elem.element_id,
            'css_selector': elem.css_selector,
            'text_content': elem.text_content,
            'is_interactive': elem.is_interactive,
            'element_type': elem.element_type,
            'is_clickable': elem.is_clickable
        })
    
    # Save elements
    elements_file = OUTPUT_DIR / "extracted_elements.json"
    with open(elements_file, 'w') as f:
        json.dump(elements_dict, f, indent=2)
    
    # Show sample
    print("\nSample elements:")
    for elem in elements_dict[:3]:
        text = (elem.get('text_content') or '')[:40]
        print(f"  - <{elem['tag_name']}> {text}")
    
    # ========================================================================
    # STEP 2: GHERKIN GENERATION
    # ========================================================================
    print("\n📍 Step 2: Generating Gherkin Test Scenarios...")
    
    from step2_gherkin_generator import GherkinTestGenerator
    
    generator = GherkinTestGenerator()
    result = await generator.generate_gherkin_tests(
        elements=elements_dict,
        url=DEMO_URL,
        project_context="Testing a quotes website"
    )
    
    if result and result.get('gherkin_content'):
        # Save Gherkin
        feature_file = OUTPUT_DIR / "test.feature"
        with open(feature_file, 'w') as f:
            f.write(result['gherkin_content'])
        
        print(f"✅ Generated Gherkin feature file")
        
        # Show preview
        lines = result['gherkin_content'].split('\n')[:8]
        print("\nGherkin preview:")
        for line in lines:
            if line.strip():
                print(f"  {line}")
    else:
        print("⚠️ Could not generate Gherkin (LLM API needed)")
        # Create a simple fallback Gherkin for demo
        fallback_gherkin = """Feature: Quotes Website Testing
  
  Scenario: View quotes on homepage
    Given the user navigates to the quotes website
    When the page loads
    Then the user should see quote cards
    And each quote should have an author
    
  Scenario: Navigate to next page
    Given the user is on the homepage
    When the user clicks the "Next" button
    Then the user should see different quotes"""
        
        feature_file = OUTPUT_DIR / "test.feature"
        with open(feature_file, 'w') as f:
            f.write(fallback_gherkin)
        print("✅ Using fallback Gherkin for demo")
    
    # ========================================================================
    # STEP 3: CODE GENERATION
    # ========================================================================
    print("\n📍 Step 3: Generating Python Test Code...")
    
    from step3_code_generator import (
        PythonTestCodeGenerator, 
        TestCodeConfig,
        TestFramework,
        BrowserFramework
    )
    
    config = TestCodeConfig(
        test_framework=TestFramework.PYTEST,
        browser_framework=BrowserFramework.PLAYWRIGHT,
        output_dir=OUTPUT_DIR / "tests",
        use_async=True,
        generate_page_objects=True,
        add_retry_logic=False  # Keep simple for demo
    )
    
    generator = PythonTestCodeGenerator(config)
    
    try:
        generated = generator.generate_from_feature_file(
            feature_file=feature_file,
            elements=elements_dict
        )
        
        print(f"✅ Generated test files:")
        for key, value in generated.items():
            if value:
                print(f"  - {key}: {value}")
    except Exception as e:
        print(f"⚠️ Code generation issue: {e}")
        print("  (This is normal if LLM API is not configured)")
    
    # ========================================================================
    # STEP 4: TEST EXECUTION (Simulated)
    # ========================================================================
    print("\n📍 Step 4: Test Execution (Simulated for Demo)...")
    
    from step4_test_executor import (
        TestExecutor,
        ExecutionConfig,
        ExecutionMode,
        ReportFormat
    )
    
    config = ExecutionConfig(
        test_dir=OUTPUT_DIR / "tests",
        output_dir=OUTPUT_DIR / "results",
        execution_mode=ExecutionMode.SEQUENTIAL,
        generate_reports=[ReportFormat.JSON, ReportFormat.MARKDOWN],
        headless=True,
        verbose=False
    )
    
    print("✅ Test executor configured")
    print("  Mode: Sequential")
    print("  Reports: JSON, Markdown")
    
    # Note: Real execution would run the generated tests
    # For demo, we just show the configuration
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*70)
    print("📊 PIPELINE EXECUTION SUMMARY")
    print("="*70)
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "url": DEMO_URL,
        "elements_extracted": len(elements_dict),
        "gherkin_generated": feature_file.exists(),
        "tests_generated": (OUTPUT_DIR / "tests").exists(),
        "output_directory": str(OUTPUT_DIR.absolute())
    }
    
    # Save summary
    summary_file = OUTPUT_DIR / "pipeline_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Pipeline Status:")
    print(f"  • Elements extracted: {summary['elements_extracted']}")
    print(f"  • Gherkin generated: {'Yes' if summary['gherkin_generated'] else 'No'}")
    print(f"  • Tests generated: {'Yes' if summary['tests_generated'] else 'No'}")
    
    print(f"\n📁 Output Location:")
    print(f"  {OUTPUT_DIR.absolute()}/")
    print(f"    ├── extracted_elements.json")
    print(f"    ├── test.feature")
    print(f"    ├── tests/")
    print(f"    └── pipeline_summary.json")
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE!")
    print("="*70)
    print("\n💡 Next Steps:")
    print("  1. Review extracted elements in extracted_elements.json")
    print("  2. Examine generated Gherkin in test.feature")
    print("  3. Check generated tests in tests/ directory")
    print("  4. Configure .env for LLM to enable full functionality")
    
    return summary

if __name__ == "__main__":
    # Run the demo
    try:
        summary = asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()