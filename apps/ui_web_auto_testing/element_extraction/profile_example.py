#!/usr/bin/env python3
"""
Profile-based Web Crawler Example

This example demonstrates how to use the profile-based crawler
for different use cases and user types.
"""

import asyncio
import json
from pathlib import Path
from apps.ui_web_auto_testing.element_extraction.profile_crawler import ProfileCrawler, ProfileType


async def demonstrate_profiles():
    """Demonstrate different profiles on a test website"""
    print("Profile-based Web Crawler Demonstration")
    print("=" * 60)
    
    crawler = ProfileCrawler()
    test_url = "https://httpbin.org/forms/post"  # Simple form for testing
    
    # List available profiles
    print("\\n1. Available Profiles:")
    print("-" * 30)
    profiles = crawler.list_available_profiles()
    for profile_type, description in profiles.items():
        print(f"• {profile_type}: {description}")
    
    # Test different profiles
    test_profiles = [
        ProfileType.QA_MANUAL_TESTER.value,
        ProfileType.QA_AUTOMATION_TESTER.value,
        ProfileType.UX_DESIGNER.value,
        ProfileType.ACCESSIBILITY_AUDITOR.value
    ]
    
    print(f"\\n2. Testing Profiles on {test_url}")
    print("-" * 50)
    
    results_summary = {}
    
    for profile_type in test_profiles:
        print(f"\\nTesting with {profile_type}...")
        
        try:
            # Quick scan with this profile
            result = await crawler.quick_scan(test_url, profile_type)
            
            # Extract key metrics
            crawl_info = result.get("crawl_info", {})
            summary = result.get("summary", {})
            page_analysis = result.get("page_analysis", {})
            
            profile_summary = {
                "profile": profile_type,
                "success": crawl_info.get("success", False),
                "duration": round(crawl_info.get("crawl_duration", 0), 2),
                "elements_found": summary.get("total_elements", 0),
                "interactive_elements": summary.get("interactive_elements", 0),
                "accessibility_score": page_analysis.get("accessibility_score", 0),
                "page_type": page_analysis.get("page_type", "unknown")
            }
            
            results_summary[profile_type] = profile_summary
            
            print(f"  ✅ Success: {profile_summary['success']}")
            print(f"  ⏱️  Duration: {profile_summary['duration']}s")
            print(f"  🎯 Elements: {profile_summary['elements_found']}")
            print(f"  🖱️  Interactive: {profile_summary['interactive_elements']}")
            print(f"  ♿ Accessibility: {profile_summary['accessibility_score']:.2f}")
            
            # Show profile-specific insights
            if "test_scenarios" in result and result["test_scenarios"]:
                print(f"  📝 Test Scenarios: {len(result['test_scenarios'])}")
            
            if "locator_strategies" in result and result["locator_strategies"]:
                print(f"  🎯 Locator Strategies: {len(result['locator_strategies'])}")
            
            if "accessibility_analysis" in result:
                issues = result["accessibility_analysis"].get("total_issues", 0)
                print(f"  ⚠️  A11y Issues: {issues}")
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results_summary[profile_type] = {"error": str(e)}
    
    # Show comparison
    print(f"\\n3. Profile Comparison Summary")
    print("-" * 40)
    print(f"{'Profile':<25} {'Elements':<10} {'Interactive':<12} {'Duration':<10}")
    print("-" * 60)
    
    for profile_type, summary in results_summary.items():
        if "error" not in summary:
            profile_short = profile_type.replace("_", " ").title()[:20]
            elements = summary.get("elements_found", 0)
            interactive = summary.get("interactive_elements", 0)
            duration = summary.get("duration", 0)
            print(f"{profile_short:<25} {elements:<10} {interactive:<12} {duration:<10}s")
    
    return results_summary


async def demonstrate_detailed_analysis():
    """Demonstrate detailed analysis with a specific profile"""
    print("\\n\\n4. Detailed Analysis Example")
    print("=" * 40)
    
    crawler = ProfileCrawler()
    
    try:
        # Detailed analysis with QA Manual Tester profile
        result = await crawler.crawl_with_profile(
            url="https://httpbin.org/forms/post",
            profile_type=ProfileType.QA_MANUAL_TESTER.value,
            max_depth=2,
            max_pages=3,
            save_results=True
        )
        
        print("QA Manual Tester - Detailed Analysis Results:")
        print("-" * 45)
        
        # Show elements by type
        elements = result.get("elements", [])
        element_types = {}
        
        for element in elements:
            elem_type = element["basic_info"]["element_type"]
            element_types[elem_type] = element_types.get(elem_type, 0) + 1
        
        print("\\nElements by Type:")
        for elem_type, count in sorted(element_types.items()):
            print(f"  • {elem_type}: {count}")
        
        # Show priority elements if available
        if "priority_elements" in result:
            print(f"\\nPriority Elements: {len(result['priority_elements'])}")
            for elem in result["priority_elements"][:3]:  # Show first 3
                basic_info = elem["basic_info"]
                print(f"  • {basic_info['element_type']}: {basic_info['text_content'][:50]}...")
        
        # Show test scenarios if available
        if "test_scenarios" in result and result["test_scenarios"]:
            print(f"\\nGenerated Test Scenarios:")
            for i, scenario in enumerate(result["test_scenarios"][:3], 1):  # Show first 3
                print(f"  {i}. Element: {scenario['element_type']}")
                for test_scenario in scenario["scenarios"][:2]:  # Show first 2 scenarios
                    print(f"     - {test_scenario}")
        
        # Show locator strategies if available
        if "locator_strategies" in result and result["locator_strategies"]:
            print(f"\\nBest Locator Strategies:")
            for strategy in result["locator_strategies"][:3]:  # Show first 3
                best_loc = strategy["best_locator"]
                print(f"  • {strategy['element_type']}: {best_loc['strategy']} = '{best_loc['value'][:50]}...'")
                print(f"    Reliability: {best_loc['reliability_score']:.2f}")
        
        if "output_file" in result:
            print(f"\\nFull results saved to: {result['output_file']}")
        
    except Exception as e:
        print(f"Error in detailed analysis: {e}")


async def demonstrate_simple_api():
    """Demonstrate simple API functions"""
    print("\\n\\n5. Simple API Functions")
    print("=" * 30)
    
    # Import the simple API functions
    from apps.ui_web_auto_testing.element_extraction.profile_crawler import (
        crawl_for_qa_testing, crawl_for_automation, 
        crawl_for_ux_design, crawl_for_accessibility
    )
    
    test_url = "https://example.com"
    
    print(f"Testing simple API functions on {test_url}...")
    
    try:
        # QA Testing
        qa_result = await crawl_for_qa_testing(test_url)
        print(f"\\n📋 QA Testing Result:")
        print(f"  Elements: {qa_result['summary']['total_elements']}")
        print(f"  Interactive: {qa_result['summary']['interactive_elements']}")
        
        # Automation Testing  
        auto_result = await crawl_for_automation(test_url)
        print(f"\\n🤖 Automation Result:")
        print(f"  Elements: {auto_result['summary']['total_elements']}")
        if "locator_strategies" in auto_result:
            reliable_locators = sum(1 for strategy in auto_result["locator_strategies"] 
                                  if strategy["best_locator"]["reliability_score"] >= 0.8)
            print(f"  Reliable Locators: {reliable_locators}")
        
        # UX Design
        ux_result = await crawl_for_ux_design(test_url)
        print(f"\\n🎨 UX Design Result:")
        print(f"  Elements: {ux_result['summary']['total_elements']}")
        print(f"  Page Type: {ux_result['page_analysis']['page_type']}")
        
        # Accessibility
        a11y_result = await crawl_for_accessibility(test_url)
        print(f"\\n♿ Accessibility Result:")
        print(f"  Elements: {a11y_result['summary']['total_elements']}")
        print(f"  Accessibility Score: {a11y_result['page_analysis']['accessibility_score']:.2f}")
        if "accessibility_analysis" in a11y_result:
            issues = a11y_result["accessibility_analysis"].get("total_issues", 0)
            print(f"  Issues Found: {issues}")
        
    except Exception as e:
        print(f"Error in simple API demo: {e}")


async def main():
    """Run all demonstrations"""
    try:
        # Demonstrate different profiles
        await demonstrate_profiles()
        
        # Demonstrate detailed analysis
        await demonstrate_detailed_analysis()
        
        # Demonstrate simple API
        await demonstrate_simple_api()
        
        print("\\n\\n🎉 Profile demonstration completed!")
        print("\\nYou can now use the profile crawler with:")
        print("  python profile_crawler.py <url> <profile> [options]")
        print("\\nOr use the simple API functions in your code:")
        print("  result = await crawl_for_qa_testing('https://example.com')")
        
    except KeyboardInterrupt:
        print("\\nDemonstration interrupted by user")
    except Exception as e:
        print(f"\\nError in demonstration: {e}")


if __name__ == "__main__":
    asyncio.run(main())