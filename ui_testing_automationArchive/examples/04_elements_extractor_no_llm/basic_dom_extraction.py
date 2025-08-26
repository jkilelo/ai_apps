#!/usr/bin/env python3
"""
Basic DOM Extraction Examples - Elements Extractor No LLM
=========================================================
Working examples demonstrating pure DOM-based element extraction capabilities.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import List

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from elements_extractor_no_llm import (
    ElementsExtractorNoLLM,
    ExtractionConfig,
    ElementType,
    InteractionType,
    LocatorStrategy,
    ExtractedElement,
    ExtractionResult
)

# Configure logging for examples
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def example_1_basic_extraction():
    """Example 1: Basic element extraction with default configuration"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Element Extraction")
    print("="*80)
    
    # Initialize extractor with default configuration
    extractor = ElementsExtractorNoLLM()
    
    # Test URL (using example.com as it's universally available)
    test_url = "https://example.com"
    
    print(f"🌐 Extracting elements from: {test_url}")
    
    try:
        # Perform extraction
        result = await extractor.extract_from_url(test_url)
        
        # Display results
        print(f"[OK] Extraction completed in {result.extraction_time:.2f} seconds")
        print(f"📊 Total elements found: {result.total_elements_found}")
        print(f"🔍 Filtered elements: {len(result.elements)}")
        print(f"🎯 Success: {result.success}")
        
        # Show first 5 elements
        print(f"\n📋 First 5 elements:")
        for i, element in enumerate(result.elements[:5], 1):
            print(f"  {i}. {element.element_type.value.upper()}: {element.text[:50]}")
            print(f"     Tag: <{element.tag_name}>")
            print(f"     Selectors: {len(element.selectors)} available")
            print(f"     Confidence: {element.confidence_score:.2f}")
            print(f"     Interactive: {element.is_interactive}")
            print()
        
        # Element type distribution
        element_types = {}
        for element in result.elements:
            element_type = element.element_type.value
            element_types[element_type] = element_types.get(element_type, 0) + 1
        
        print(f"📈 Element type distribution:")
        for element_type, count in sorted(element_types.items()):
            print(f"  - {element_type}: {count}")
        
        return result
        
    except Exception as e:
        logger.error(f"[ERROR] Extraction failed: {e}")
        return None


async def example_2_selector_strategies():
    """Example 2: Demonstrating different selector strategies"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Selector Strategy Demonstration")
    print("="*80)
    
    # Initialize extractor
    extractor = ElementsExtractorNoLLM()
    
    # Extract from a site with various elements
    test_url = "https://httpbin.org/forms/post"  # Simple form for testing
    
    print(f"🌐 Analyzing selector strategies for: {test_url}")
    
    try:
        result = await extractor.extract_from_url(test_url)
        
        print(f"[OK] Found {len(result.elements)} elements")
        
        # Show selector strategies for interactive elements
        interactive_elements = [e for e in result.elements if e.is_interactive]
        print(f"\n🎯 Interactive elements with selector strategies:")
        
        for element in interactive_elements[:3]:
            print(f"\n  Element: {element.element_type.value} - '{element.text[:30]}'")
            print(f"  Tag: <{element.tag_name}>")
            
            # Show all available selectors
            for selector in element.selectors:
                print(f"    [OK] {selector.strategy.value}: {selector.value}")
                print(f"      Score: {selector.score:.2f}, Unique: {selector.is_unique}")
        
        return result
        
    except Exception as e:
        logger.error(f"[ERROR] Selector analysis failed: {e}")
        return None


async def example_3_element_classification():
    """Example 3: Element type classification and validation"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Element Classification and Validation")
    print("="*80)
    
    # Custom configuration with validation enabled
    config = ExtractionConfig(
        max_elements=50,  # Limit for demonstration
        enable_shadow_dom=True,
        enable_iframe_traversal=True,
        min_confidence_score=0.5,  # Only high-confidence elements
        enable_performance_monitoring=True
    )
    
    extractor = ElementsExtractorNoLLM(config)
    
    # Test with a content-rich site
    test_url = "https://example.com"
    
    print(f"🌐 Analyzing element classification for: {test_url}")
    print(f"🔧 Min confidence threshold: {config.min_confidence_score}")
    
    try:
        result = await extractor.extract_from_url(test_url)
        
        print(f"[OK] High-confidence elements: {len(result.elements)}")
        
        # Group by element type and interaction type
        type_stats = {}
        interaction_stats = {}
        
        for element in result.elements:
            # Element type stats
            elem_type = element.element_type.value
            type_stats[elem_type] = type_stats.get(elem_type, 0) + 1
            
            # Interaction type stats  
            interact_type = element.interaction_type.value
            interaction_stats[interact_type] = interaction_stats.get(interact_type, 0) + 1
        
        print(f"\n📊 Element Types Found:")
        for elem_type, count in sorted(type_stats.items()):
            print(f"  - {elem_type}: {count}")
        
        print(f"\n🎮 Interaction Types Available:")
        for interact_type, count in sorted(interaction_stats.items()):
            print(f"  - {interact_type}: {count}")
        
        # Show highest confidence elements
        high_conf_elements = sorted(result.elements, 
                                  key=lambda x: x.confidence_score, 
                                  reverse=True)[:3]
        
        print(f"\n🏆 Top 3 highest confidence elements:")
        for i, element in enumerate(high_conf_elements, 1):
            print(f"  {i}. {element.element_type.value}: {element.text[:40]}")
            print(f"     Confidence: {element.confidence_score:.3f}")
            print(f"     Visible: {element.is_visible}")
            print(f"     Interactive: {element.is_interactive}")
            print(f"     Best selector: {element.selectors[0].value if element.selectors else 'None'}")
            print()
        
        return result
        
    except Exception as e:
        logger.error(f"[ERROR] Classification analysis failed: {e}")
        return None


async def example_4_performance_monitoring():
    """Example 4: Performance monitoring and metrics"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Performance Monitoring")
    print("="*80)
    
    # Configuration with performance monitoring enabled
    config = ExtractionConfig(
        enable_performance_monitoring=True,
        enable_caching=True,
        cache_ttl=60,  # 1 minute cache
        rate_limit_enabled=True
    )
    
    extractor = ElementsExtractorNoLLM(config)
    
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://httpbin.org/forms/post"
    ]
    
    print(f"🌐 Performance testing with {len(test_urls)} URLs")
    print(f"[FAST] Caching enabled: {config.enable_caching}")
    print(f"🚦 Rate limiting: {config.rate_limit_enabled}")
    
    results = []
    total_start_time = asyncio.get_event_loop().time()
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🔄 Processing URL {i}/{len(test_urls)}: {url}")
        
        try:
            result = await extractor.extract_from_url(url)
            results.append(result)
            
            print(f"  [OK] Success: {result.success}")
            print(f"  [TIME]  Time: {result.extraction_time:.3f}s")
            print(f"  📊 Elements: {len(result.elements)}")
            print(f"  💾 Method: {result.extraction_method}")
            
        except Exception as e:
            logger.error(f"  [ERROR] Failed: {e}")
    
    total_time = asyncio.get_event_loop().time() - total_start_time
    
    # Performance summary
    print(f"\n📈 Performance Summary:")
    print(f"  🕐 Total time: {total_time:.3f}s")
    print(f"  [FAST] Average time per URL: {total_time/len(test_urls):.3f}s")
    
    successful_results = [r for r in results if r and r.success]
    if successful_results:
        avg_elements = sum(len(r.elements) for r in successful_results) / len(successful_results)
        avg_extraction_time = sum(r.extraction_time for r in successful_results) / len(successful_results)
        
        print(f"  📊 Average elements per page: {avg_elements:.1f}")
        print(f"  [TIME]  Average extraction time: {avg_extraction_time:.3f}s")
        print(f"  🎯 Success rate: {len(successful_results)/len(test_urls)*100:.1f}%")
    
    return results


async def example_5_element_details():
    """Example 5: Detailed element information and attributes"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Detailed Element Information")
    print("="*80)
    
    extractor = ElementsExtractorNoLLM()
    test_url = "https://example.com"
    
    print(f"🌐 Analyzing detailed element information: {test_url}")
    
    try:
        result = await extractor.extract_from_url(test_url)
        
        # Find the most interesting element (with most attributes)
        detailed_elements = sorted(result.elements, 
                                 key=lambda x: len(x.attributes), 
                                 reverse=True)[:2]
        
        print(f"🔍 Showing detailed information for top 2 elements:")
        
        for i, element in enumerate(detailed_elements, 1):
            print(f"\n{'='*60}")
            print(f"ELEMENT {i}: {element.element_type.value.upper()}")
            print(f"{'='*60}")
            
            print(f"📝 Basic Info:")
            print(f"  Tag: <{element.tag_name}>")
            print(f"  Text: '{element.text[:100]}...' " if len(element.text) > 100 else f"  Text: '{element.text}'")
            print(f"  Type: {element.element_type.value}")
            print(f"  Interaction: {element.interaction_type.value}")
            print(f"  Confidence: {element.confidence_score:.3f}")
            
            print(f"\n🎯 Visibility & Interaction:")
            print(f"  Visible: {element.is_visible}")
            print(f"  Interactive: {element.is_interactive}")
            print(f"  Children: {element.children_count}")
            
            print(f"\n🧭 Location & Paths:")
            print(f"  XPath: {element.xpath}")
            print(f"  CSS Path: {element.css_path}")
            
            if element.bounding_box:
                bbox = element.bounding_box
                print(f"\n📐 Bounding Box:")
                print(f"  Position: ({bbox.x}, {bbox.y})")
                print(f"  Size: {bbox.width}x{bbox.height}")
                print(f"  Area: {bbox.area:.0f}px²")
            
            print(f"\n🏷️  Attributes ({len(element.attributes)}):")
            for attr_name, attr_value in list(element.attributes.items())[:5]:
                display_value = attr_value[:50] + "..." if len(attr_value) > 50 else attr_value
                print(f"  {attr_name}: {display_value}")
            if len(element.attributes) > 5:
                print(f"  ... and {len(element.attributes) - 5} more attributes")
            
            print(f"\n🎯 Selectors ({len(element.selectors)}):")
            for selector in element.selectors[:3]:
                print(f"  {selector.strategy.value}: {selector.value}")
                print(f"    Score: {selector.score:.3f}, Unique: {selector.is_unique}")
            if len(element.selectors) > 3:
                print(f"  ... and {len(element.selectors) - 3} more selectors")
        
        return result
        
    except Exception as e:
        logger.error(f"[ERROR] Detailed analysis failed: {e}")
        return None


async def main():
    """Run all DOM extraction examples"""
    print("🚀 DOM EXTRACTION EXAMPLES - Elements Extractor No LLM")
    print("=" * 80)
    print("Demonstrating pure DOM-based element extraction capabilities")
    print("No LLM dependencies - Fast, reliable, and deterministic")
    print("=" * 80)
    
    examples = [
        ("Basic Extraction", example_1_basic_extraction),
        ("Selector Strategies", example_2_selector_strategies), 
        ("Element Classification", example_3_element_classification),
        ("Performance Monitoring", example_4_performance_monitoring),
        ("Detailed Element Info", example_5_element_details)
    ]
    
    results = []
    
    for name, example_func in examples:
        print(f"\n🔄 Running: {name}")
        try:
            result = await example_func()
            results.append((name, result, True))
            print(f"[OK] {name} completed successfully")
        except Exception as e:
            logger.error(f"[ERROR] {name} failed: {e}")
            results.append((name, None, False))
    
    # Summary
    print(f"\n" + "="*80)
    print("📊 EXAMPLES SUMMARY")
    print("="*80)
    
    successful = sum(1 for _, _, success in results if success)
    total = len(results)
    
    print(f"[OK] Successful examples: {successful}/{total}")
    print(f"🎯 Success rate: {successful/total*100:.1f}%")
    
    for name, result, success in results:
        status = "[OK] PASS" if success else "[ERROR] FAIL"
        element_count = f"({len(result.elements)} elements)" if result and hasattr(result, 'elements') else ""
        print(f"  {status} {name} {element_count}")
    
    print(f"\n🎉 DOM extraction examples completed!")
    print(f"💡 This module provides enterprise-grade element extraction")
    print(f"[FAST] No LLM dependencies for maximum speed and reliability")


if __name__ == "__main__":
    asyncio.run(main())