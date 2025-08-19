"""
Test script for Element Extractor
Tests the extraction of UI elements from webpages
"""

import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from apps.ui_web_auto_testing_v2.element_extractor import extract_elements_from_url


async def test_extraction():
    """Test element extraction with different websites"""
    
    # Test URLs
    test_urls = [
        "https://example.com",  # Simple test page
        "https://quotes.toscrape.com",  # More complex page with forms
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print('='*60)
        
        try:
            # Extract elements without LLM analysis first (faster)
            print("\n[INFO] Extracting elements...")
            result = await extract_elements_from_url(
                url, 
                headless=False,  # Set to True for headless mode
                analyze=False    # Set to True to enable LLM analysis
            )
            
            # Display results
            print(f"[SUCCESS] Successfully extracted {result['total_elements']} elements")
            print(json.dumps(result, indent=2))
            
            # Show breakdown by category
            print("\nElements by Category:")
            for category, elements in result.get('elements_by_category', {}).items():
                print(f"  - {category}: {len(elements)} elements")
            
            # Show details of first few elements
            print("\nSample Elements (first 5):")
            for i, elem in enumerate(result['elements'][:5], 1):
                print(f"\n  {i}. {elem.get('description', 'No description')}")
                print(f"     - Tag: {elem.get('tag_name')}")
                print(f"     - Category: {elem.get('category')}")
                print(f"     - Priority: {elem.get('test_priority')}")
                print(f"     - Interaction: {elem.get('interaction_pattern')}")
                if elem.get('id'):
                    print(f"     - ID: {elem.get('id')}")
                if elem.get('cssSelector'):
                    print(f"     - CSS: {elem.get('cssSelector')}")
            
            # Save results to file
            output_file = f"test_results_{url.replace('https://', '').replace('/', '_')}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n[SAVED] Full results saved to: {output_file}")
            
        except Exception as e:
            print(f"[ERROR] Error testing {url}: {e}")
            import traceback
            traceback.print_exc()


async def test_with_llm_analysis():
    """Test extraction with LLM analysis"""
    
    url = "https://example.com"
    
    print(f"\n{'='*60}")
    print(f"Testing with LLM Analysis: {url}")
    print('='*60)
    
    try:
        print("\n[INFO] Extracting and analyzing elements...")
        result = await extract_elements_from_url(
            url,
            headless=False,
            analyze=True  # Enable LLM analysis
        )
        
        print(f"[SUCCESS] Extracted {result['total_elements']} elements")
        
        # Show LLM analysis if available
        if 'llm_analysis' in result:
            print("\nLLM Analysis Results:")
            analysis = result['llm_analysis']
            
            if isinstance(analysis, dict):
                for key, value in analysis.items():
                    print(f"\n{key.replace('_', ' ').title()}:")
                    if isinstance(value, list):
                        for item in value:
                            print(f"  - {item}")
                    else:
                        print(f"  {value}")
            else:
                print(analysis)
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function"""
    
    print("Element Extractor Test Suite")
    print("================================\n")
    
    # Test basic extraction
    await test_extraction()
    
    # Optionally test with LLM analysis (requires API key)
    # Uncomment to test LLM analysis
    # await test_with_llm_analysis()
    
    print("\n[SUCCESS] All tests completed!")


if __name__ == "__main__":
    # Run the tests
    asyncio.run(main())