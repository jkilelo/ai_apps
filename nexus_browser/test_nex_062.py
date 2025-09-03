#!/usr/bin/env python3
"""
NEX-062 Test Script - Advanced Data Processing and Analysis Features
Test price extraction, reviews, DOM mutations, video info, performance, and structured data
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the nexus_browser directory to the path
sys.path.append(str(Path(__file__).parent))

try:
    from nexus import NexusBrowser
    print("SUCCESS: NexusBrowser imported successfully")
except Exception as e:
    print(f"ERROR: Import failed: {e}")
    sys.exit(1)

async def test_nex_062_methods():
    """Test the NEX-062 advanced data processing and analysis features"""
    print("\n" + "="*70)
    print("TESTING NEX-062 ADVANCED DATA PROCESSING AND ANALYSIS FEATURES")
    print("="*70)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    # Check method availability
    nex_062_methods = [
        'extract_price_information',
        'extract_comments_and_reviews',
        'monitor_dom_mutations',
        'extract_video_information',
        'analyze_page_load_performance',
        'extract_structured_data'
    ]
    
    print("\n1. CHECKING METHOD AVAILABILITY:")
    for method_name in nex_062_methods:
        if hasattr(browser, method_name):
            method = getattr(browser, method_name)
            if callable(method):
                print(f"SUCCESS: {method_name} - Available and callable")
            else:
                print(f"ERROR: {method_name} - Not callable")
        else:
            print(f"ERROR: {method_name} - Not found")
    
    try:
        # Initialize browser with Playwright
        print("\n2. INITIALIZING BROWSER...")
        await browser.awaken()
        
        if not browser.page:
            print("WARNING: Playwright not available. Testing error handling only.")
            await test_without_browser(browser, nex_062_methods)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        
        # Navigate to a test page
        await browser.page.goto("https://httpbin.org/html")
        
        # Test extract_price_information
        print("\n" + "-"*60)
        print("TESTING: extract_price_information()")
        print("-"*60)
        
        price_result = await browser.extract_price_information()
        print("PRICE EXTRACTION RESULT:", json.dumps({
            'success': price_result.get('success'),
            'currency_detected': price_result.get('currency_detected'),
            'statistics': price_result.get('statistics')
        }, indent=2))
        
        if price_result.get('success'):
            stats = price_result.get('statistics', {})
            print(f"SUCCESS: Found {stats.get('total_prices')} prices, {stats.get('total_products')} products")
            if stats.get('avg_price'):
                print(f"  Price range: ${stats.get('min_price', 0):.2f} - ${stats.get('max_price', 0):.2f}")
        
        # Test extract_comments_and_reviews
        print("\n" + "-"*60)
        print("TESTING: extract_comments_and_reviews()")
        print("-"*60)
        
        review_result = await browser.extract_comments_and_reviews()
        print("REVIEW EXTRACTION RESULT:", json.dumps({
            'success': review_result.get('success'),
            'aggregate_rating': review_result.get('aggregate_rating'),
            'statistics': review_result.get('statistics')
        }, indent=2))
        
        if review_result.get('success'):
            stats = review_result.get('statistics', {})
            print(f"SUCCESS: Found {stats.get('total_reviews')} reviews, {stats.get('total_ratings')} ratings")
            if stats.get('average_rating'):
                print(f"  Average rating: {stats.get('average_rating', 0):.1f}")
        
        # Test monitor_dom_mutations
        print("\n" + "-"*60)
        print("TESTING: monitor_dom_mutations()")
        print("-"*60)
        
        mutations_result = await browser.monitor_dom_mutations(
            duration=2000,
            target_selector=None
        )
        print("DOM MUTATIONS RESULT:", json.dumps({
            'success': mutations_result.get('success'),
            'monitoring_duration_ms': mutations_result.get('monitoring_duration_ms'),
            'statistics': mutations_result.get('statistics')
        }, indent=2))
        
        if mutations_result.get('success'):
            stats = mutations_result.get('statistics', {})
            summary = mutations_result.get('summary', {})
            print(f"SUCCESS: Captured {stats.get('total_mutations')} mutations in 2 seconds")
            print(f"  Mutations per second: {stats.get('mutations_per_second', 0):.2f}")
            print(f"  DOM activity level: {stats.get('dom_activity', 'low')}")
        
        # Test extract_video_information
        print("\n" + "-"*60)
        print("TESTING: extract_video_information()")
        print("-"*60)
        
        video_result = await browser.extract_video_information()
        print("VIDEO EXTRACTION RESULT:", json.dumps({
            'success': video_result.get('success'),
            'statistics': video_result.get('statistics'),
            'platforms': video_result.get('platforms')
        }, indent=2))
        
        if video_result.get('success'):
            stats = video_result.get('statistics', {})
            print(f"SUCCESS: Found {stats.get('total_videos')} videos")
            print(f"  HTML5: {stats.get('html5_videos')}, YouTube: {stats.get('youtube_embeds')}, Vimeo: {stats.get('vimeo_embeds')}")
        
        # Test analyze_page_load_performance
        print("\n" + "-"*60)
        print("TESTING: analyze_page_load_performance()")
        print("-"*60)
        
        perf_result = await browser.analyze_page_load_performance()
        print("PERFORMANCE ANALYSIS RESULT:", json.dumps({
            'success': perf_result.get('success'),
            'performance_score': perf_result.get('performance_score'),
            'grade': perf_result.get('grade'),
            'key_metrics': perf_result.get('key_metrics')
        }, indent=2))
        
        if perf_result.get('success'):
            print(f"SUCCESS: Performance Score: {perf_result.get('performance_score')}/100 (Grade: {perf_result.get('grade')})")
            metrics = perf_result.get('key_metrics', {})
            print(f"  Page load time: {metrics.get('page_load_time')}")
            print(f"  First contentful paint: {metrics.get('first_contentful_paint')}")
            recommendations = perf_result.get('recommendations', [])
            if recommendations:
                print(f"  Top recommendation: {recommendations[0]}")
        
        # Test extract_structured_data
        print("\n" + "-"*60)
        print("TESTING: extract_structured_data()")
        print("-"*60)
        
        structured_result = await browser.extract_structured_data()
        print("STRUCTURED DATA RESULT:", json.dumps({
            'success': structured_result.get('success'),
            'statistics': structured_result.get('statistics'),
            'rich_snippets_potential': structured_result.get('rich_snippets_potential')
        }, indent=2))
        
        if structured_result.get('success'):
            stats = structured_result.get('statistics', {})
            print(f"SUCCESS: Found {stats.get('total_json_ld')} JSON-LD, {stats.get('total_microdata')} Microdata, {stats.get('total_rdfa')} RDFa")
            if stats.get('has_open_graph'):
                print("  Has Open Graph metadata")
            if stats.get('has_twitter_card'):
                print("  Has Twitter Card metadata")
            rich = structured_result.get('rich_snippets_potential', {})
            if any(rich.values()):
                print(f"  Rich snippets potential: {', '.join(k.replace('has_', '') for k, v in rich.items() if v)}")
        
        print("\n" + "="*70)
        print("NEX-062 ADVANCED DATA PROCESSING AND ANALYSIS FEATURES TESTED!")
        print("="*70)
        
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if hasattr(browser, 'browser') and browser.browser:
            try:
                await browser.browser.close()
                print("\nBrowser closed successfully")
            except:
                pass

async def test_without_browser(browser, methods):
    """Test functionality when browser is not available"""
    print("\nTesting error handling (Playwright not available):")
    
    # Test each method returns proper error responses
    test_calls = [
        ('extract_price_information', ()),
        ('extract_comments_and_reviews', ()),
        ('monitor_dom_mutations', ()),
        ('extract_video_information', ()),
        ('analyze_page_load_performance', ()),
        ('extract_structured_data', ())
    ]
    
    for method_name, args in test_calls:
        if hasattr(browser, method_name):
            method = getattr(browser, method_name)
            result = await method(*args)
            
            if 'error' in result and 'No active page available' in result['error']:
                print(f"SUCCESS: {method_name}() handles no-browser condition correctly")
            else:
                print(f"WARNING: {method_name}() unexpected response: {result}")
        else:
            print(f"SKIP: {method_name}() not available")

if __name__ == "__main__":
    print("NEX-062 Advanced Data Processing and Analysis Features Test")
    print("Testing 6 features: prices, reviews, DOM, videos, performance, structured data")
    
    asyncio.run(test_nex_062_methods())