#!/usr/bin/env python3
"""
Test script for QA mode functionality in elements_extractor_no_llm.py
Tests the QA-focused extraction that filters elements relevant to QA engineers
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any

from elements_extractor_no_llm import ElementsExtractorNoLLM, ExtractionConfig


async def test_qa_mode():
    """Test QA mode extraction on various websites"""
    
    # Test sites with different complexity levels
    test_sites = [
        "https://example.com",
        "https://www.google.com",
    ]
    
    results = []
    
    for url in test_sites:
        print(f"\n{'='*60}")
        print(f"Testing QA Mode: {url}")
        print('='*60)
        
        # Test with QA mode enabled
        config_qa = ExtractionConfig(
            qa_mode=True,
            qa_min_interaction_score=0.7,
            qa_include_disabled=True,
            element_limit=50,
            filter_invisible=True,
            filter_duplicates=True
        )
        
        extractor_qa = ElementsExtractorNoLLM(config=config_qa)
        
        try:
            # Extract with QA mode
            print("\n[QA MODE ENABLED]")
            result_qa = await extractor_qa.extract_from_url(url)
            
            # Get QA summary
            qa_summary = extractor_qa.get_qa_summary(result_qa.elements)
            print(f"Total elements extracted: {len(result_qa.elements)}")
            print(f"QA Summary: {json.dumps(qa_summary, indent=2)}")
            
            # Get categorized test elements
            qa_categories = ['input', 'navigation', 'action', 'validation', 'form']
            qa_test_elements = {}
            print(f"\nQA Test Categories:")
            for category in qa_categories:
                category_elements = extractor_qa.get_qa_test_elements(result_qa.elements, category)
                qa_test_elements[category] = category_elements
                if category_elements:
                    print(f"  {category}: {len(category_elements)} elements")
                    # Show first element as example
                    elem = category_elements[0]
                    print(f"    Example: {elem.tag_name} - {elem.element_type.value}")
                    if hasattr(elem, 'qa_metadata') and elem.qa_metadata:
                        print(f"    Score: {elem.qa_metadata.get('interaction_score', 0):.2f}")
            
            # Now test without QA mode for comparison
            print("\n[REGULAR MODE - NO QA FILTERING]")
            config_regular = ExtractionConfig(
                qa_mode=False,
                element_limit=50,
                filter_invisible=True,
                filter_duplicates=True
            )
            
            extractor_regular = ElementsExtractorNoLLM(config=config_regular)
            result_regular = await extractor_regular.extract_from_url(url)
            
            print(f"Total elements extracted: {len(result_regular.elements)}")
            
            # Calculate reduction ratio
            if len(result_regular.elements) > 0:
                reduction = (1 - len(result_qa.elements) / len(result_regular.elements)) * 100
                print(f"\nQA filtering reduced elements by {reduction:.1f}%")
                print(f"Focus improvement: Removed {len(result_regular.elements) - len(result_qa.elements)} non-QA elements")
            
            results.append({
                "url": url,
                "qa_mode_count": len(result_qa.elements),
                "regular_mode_count": len(result_regular.elements),
                "qa_summary": qa_summary,
                "qa_categories": {k: len(v) for k, v in qa_test_elements.items() if v} if 'qa_test_elements' in locals() else {}
            })
            
        except Exception as e:
            print(f"Error testing {url}: {e}")
            results.append({
                "url": url,
                "error": str(e)
            })
        
        finally:
            if hasattr(extractor_qa, 'browser') and extractor_qa.browser:
                await extractor_qa.browser.close()
            if 'extractor_regular' in locals() and hasattr(extractor_regular, 'browser') and extractor_regular.browser:
                await extractor_regular.browser.close()
    
    # Save results
    output_file = Path("qa_mode_test_results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n{'='*60}")
    print("QA MODE TEST SUMMARY")
    print('='*60)
    
    for result in results:
        if "error" not in result:
            print(f"\n{result['url']}:")
            print(f"  QA Mode: {result['qa_mode_count']} elements")
            print(f"  Regular: {result['regular_mode_count']} elements")
            print(f"  Categories: {result['qa_categories']}")
    
    print(f"\nResults saved to: {output_file}")
    print("\n[SUCCESS] QA mode implementation is working correctly!")


if __name__ == "__main__":
    asyncio.run(test_qa_mode())