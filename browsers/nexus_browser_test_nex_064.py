#!/usr/bin/env python3
"""
NEX-064 Test Script - Advanced Real-time Monitoring and Analytics Features
Test real-time monitoring, user journey, caching, benchmarking, automated testing, and reporting
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

async def test_nex_064_methods():
    """Test the NEX-064 advanced real-time monitoring and analytics features"""
    print("\n" + "="*70)
    print("TESTING NEX-064 ADVANCED REAL-TIME MONITORING AND ANALYTICS FEATURES")
    print("="*70)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    # Check method availability
    nex_064_methods = [
        'setup_real_time_monitoring',
        'capture_user_journey',
        'implement_advanced_caching',
        'create_performance_benchmark',
        'setup_automated_testing',
        'generate_comprehensive_report'
    ]
    
    print("\n1. CHECKING METHOD AVAILABILITY:")
    for method_name in nex_064_methods:
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
            await test_without_browser(browser, nex_064_methods)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        
        # Navigate to a test page
        await browser.page.goto("https://httpbin.org/forms/post")
        
        # Test setup_real_time_monitoring
        print("\n" + "-"*60)
        print("TESTING: setup_real_time_monitoring()")
        print("-"*60)
        
        monitoring_result = await browser.setup_real_time_monitoring(
            metrics=['performance', 'errors', 'dom'],
            alert_threshold=0.7,
            monitoring_interval=3000
        )
        print("REAL-TIME MONITORING RESULT:", json.dumps({
            'success': monitoring_result.get('success'),
            'metrics_monitored': monitoring_result.get('monitoring_config', {}).get('metrics_monitored'),
            'effectiveness_score': monitoring_result.get('monitoring_config', {}).get('effectiveness_score')
        }, indent=2))
        
        if monitoring_result.get('success'):
            config = monitoring_result.get('monitoring_config', {})
            capabilities = monitoring_result.get('monitoring_capabilities', {})
            print(f"SUCCESS: Monitoring setup with {len(config.get('metrics_monitored', []))} metrics")
            print(f"  Performance tracking: {capabilities.get('performance_tracking')}")
            print(f"  Error tracking: {capabilities.get('error_tracking')}")
            print(f"  DOM observation: {capabilities.get('dom_observation')}")
        
        # Test capture_user_journey
        print("\n" + "-"*60)
        print("TESTING: capture_user_journey()")
        print("-"*60)
        
        journey_result = await browser.capture_user_journey(
            journey_name="test_journey",
            track_interactions=True,
            include_screenshots=False
        )
        print("USER JOURNEY CAPTURE RESULT:", json.dumps({
            'success': journey_result.get('success'),
            'journey_id': journey_result.get('journey_id'),
            'tracking_effectiveness': journey_result.get('journey_config', {}).get('tracking_effectiveness')
        }, indent=2))
        
        if journey_result.get('success'):
            config = journey_result.get('journey_config', {})
            capabilities = journey_result.get('tracking_capabilities', {})
            print(f"SUCCESS: User journey tracking configured")
            print(f"  Click tracking: {capabilities.get('click_tracking')}")
            print(f"  Scroll tracking: {capabilities.get('scroll_tracking')}")
            print(f"  Navigation tracking: {capabilities.get('navigation_tracking')}")
        
        # Test implement_advanced_caching
        print("\n" + "-"*60)
        print("TESTING: implement_advanced_caching()")
        print("-"*60)
        
        caching_result = await browser.implement_advanced_caching(
            cache_strategy="smart",
            cache_duration=1800,
            cache_size_limit=50
        )
        print("ADVANCED CACHING RESULT:", json.dumps({
            'success': caching_result.get('success'),
            'strategy': caching_result.get('cache_implementation', {}).get('strategy'),
            'effectiveness_score': caching_result.get('cache_implementation', {}).get('effectiveness_score')
        }, indent=2))
        
        if caching_result.get('success'):
            implementation = caching_result.get('cache_implementation', {})
            benefits = caching_result.get('performance_benefits', {})
            print(f"SUCCESS: {implementation.get('strategy')} caching implemented")
            print(f"  Expected load time reduction: {benefits.get('expected_load_time_reduction')}")
            print(f"  Bandwidth savings: {benefits.get('bandwidth_savings')}")
        
        # Test create_performance_benchmark
        print("\n" + "-"*60)
        print("TESTING: create_performance_benchmark()")
        print("-"*60)
        
        benchmark_result = await browser.create_performance_benchmark(
            benchmark_name="test_benchmark",
            test_scenarios=['load', 'memory'],
            iterations=2
        )
        print("PERFORMANCE BENCHMARK RESULT:", json.dumps({
            'success': benchmark_result.get('success'),
            'overall_score': benchmark_result.get('benchmark_results', {}).get('summary', {}).get('overall_performance_score'),
            'grade': benchmark_result.get('benchmark_results', {}).get('summary', {}).get('grade')
        }, indent=2))
        
        if benchmark_result.get('success'):
            summary = benchmark_result.get('benchmark_results', {}).get('summary', {})
            insights = benchmark_result.get('performance_insights', {})
            print(f"SUCCESS: Performance benchmark completed")
            print(f"  Overall score: {summary.get('overall_performance_score')}/100 (Grade: {summary.get('grade')})")
            print(f"  Test scenarios: {summary.get('test_scenarios_completed')}")
            print(f"  Analysis: {insights.get('comparative_analysis')}")
        
        # Test setup_automated_testing
        print("\n" + "-"*60)
        print("TESTING: setup_automated_testing()")
        print("-"*60)
        
        testing_result = await browser.setup_automated_testing(
            test_types=['functional', 'performance'],
            test_frequency='daily'
        )
        print("AUTOMATED TESTING RESULT:", json.dumps({
            'success': testing_result.get('success'),
            'overall_status': testing_result.get('test_suite_summary', {}).get('overall_status'),
            'test_types_run': testing_result.get('test_suite_summary', {}).get('test_types_run')
        }, indent=2))
        
        if testing_result.get('success'):
            summary = testing_result.get('test_suite_summary', {})
            automation = testing_result.get('automation_features', {})
            print(f"SUCCESS: Automated testing configured")
            print(f"  Test suite status: {summary.get('overall_status')}")
            print(f"  Test types: {summary.get('test_types_run')}")
            print(f"  Historical tracking: {automation.get('historical_tracking')}")
        
        # Test generate_comprehensive_report
        print("\n" + "-"*60)
        print("TESTING: generate_comprehensive_report()")
        print("-"*60)
        
        report_result = await browser.generate_comprehensive_report(
            report_type="summary",
            include_screenshots=False,
            export_format="json"
        )
        print("COMPREHENSIVE REPORT RESULT:", json.dumps({
            'success': report_result.get('success'),
            'overall_score': report_result.get('report_data', {}).get('report_summary', {}).get('overall_score'),
            'sections_analyzed': report_result.get('report_data', {}).get('report_summary', {}).get('sections_analyzed')
        }, indent=2))
        
        if report_result.get('success'):
            summary = report_result.get('report_data', {}).get('report_summary', {})
            capabilities = report_result.get('analysis_capabilities', {})
            export_info = report_result.get('export_info', {})
            print(f"SUCCESS: Comprehensive report generated")
            print(f"  Overall score: {summary.get('overall_score')}/100")
            print(f"  Sections analyzed: {summary.get('sections_analyzed')}")
            print(f"  Export format: {export_info.get('format')} ({export_info.get('file_size_estimate')} bytes)")
        
        print("\n" + "="*70)
        print("NEX-064 ADVANCED REAL-TIME MONITORING AND ANALYTICS FEATURES TESTED!")
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
        ('setup_real_time_monitoring', ()),
        ('capture_user_journey', ()),
        ('implement_advanced_caching', ()),
        ('create_performance_benchmark', ()),
        ('setup_automated_testing', ()),
        ('generate_comprehensive_report', ())
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
    print("NEX-064 Advanced Real-time Monitoring and Analytics Features Test")
    print("Testing 6 features: monitoring, journey, caching, benchmarking, testing, reporting")
    
    asyncio.run(test_nex_064_methods())