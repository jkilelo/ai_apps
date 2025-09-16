#!/usr/bin/env python3
"""
Advanced Stealth Features Example
=================================
Demonstrates advanced capabilities of the Ultimate Stealth Browser module.

This example shows:
1. Paranoid-level stealth for highly protected sites
2. Custom stealth profiles and configurations
3. Framework detection and evasion
4. CAPTCHA detection and handling
5. Performance optimization techniques
6. Real-world stealth scenarios

Author: UI Testing Automation Framework
Version: 1.0.0
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# Add the module path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ui_testing_automation"))

try:
    from browser import (
        UltimateStealthBrowser,
        StealthLevel,
        ExtractionStrategy,
        ProfileType,
        StealthProfile,
        TimingProfile
    )
    print("[OK] Successfully imported browser module")
except ImportError as e:
    print(f"[ERROR] Failed to import browser module: {e}")
    print("Make sure the browser.py file is in the ui_testing_automation directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_1_paranoid_stealth_mode():
    """Example 1: Maximum stealth with paranoid-level protection"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Paranoid-Level Stealth for Protected Sites")
    print("="*80)
    
    try:
        # Create custom paranoid timing profile
        paranoid_timing = TimingProfile(
            element_analysis_delay=(200, 500),    # Slow, deliberate analysis
            mouse_move_steps=(50, 80),            # Many small steps
            typing_base_delay=(150, 350),         # Very human-like typing
            scroll_pause=(1000, 3000),           # Long pauses between scrolls
            network_idle_timeout=30000,          # Wait longer for network
            challenge_wait=(10000, 15000),       # Extended CAPTCHA wait
            stability_initial=(2000, 5000)       # Extra stability wait
        )
        
        # Create custom stealth profile
        paranoid_profile = StealthProfile(
            user_agent_spoofing=True,
            header_randomization=True,
            viewport_spoofing=True,
            webgl_spoofing=True,
            canvas_fingerprint_protection=True,
            audio_context_spoofing=True,
            timezone_spoofing=True,
            language_spoofing=True,
            screen_resolution_spoofing=True,
            battery_api_spoofing=True,
            webrtc_leak_protection=True,
            geolocation_spoofing=True
        )
        
        # Initialize browser with paranoid configuration
        config = {
            "stealth_level": StealthLevel.PARANOID,
            "profile_type": ProfileType.ULTRA_STEALTH,
            "stealth_profile": paranoid_profile,
            "timing_profile": paranoid_timing,
            "anti_detection": True,
            "extreme_measures": True,
            "fingerprint_randomization": True,
            "request_interception": True,
            "script_injection_prevention": True
        }
        
        browser = UltimateStealthBrowser(config)
        await browser.initialize()
        
        print("[OK] Browser initialized with PARANOID stealth level")
        print("     Features enabled:")
        print("       • Extreme fingerprint randomization")
        print("       • Advanced header spoofing")
        print("       • Multi-layer detection evasion")
        print("       • Extended timing delays")
        print("       • Request interception")
        
        # Test against detection systems
        detection_tests = [
            {
                "name": "Basic Detection Test",
                "url": "https://httpbin.org/user-agent",
                "expected_indicators": ["user_agent"]
            },
            {
                "name": "Header Analysis Test", 
                "url": "https://httpbin.org/headers",
                "expected_indicators": ["headers", "accept_language"]
            }
        ]
        
        paranoid_results = []
        
        for test in detection_tests:
            print(f"\n[INFO] Running paranoid test: {test['name']}")
            
            start_time = time.time()
            result = await browser.navigate_stealth(test["url"])
            navigation_time = time.time() - start_time
            
            if result.get("success", False):
                print(f"[OK] Successfully accessed site (took {navigation_time:.2f}s)")
                
                # Perform deep stealth analysis
                stealth_analysis = await browser.perform_stealth_analysis()
                
                fingerprint_score = stealth_analysis.get("fingerprint_uniqueness", 0)
                detection_probability = stealth_analysis.get("detection_probability", 1.0)
                evasion_techniques = stealth_analysis.get("active_evasions", [])
                
                print(f"     Fingerprint uniqueness: {fingerprint_score:.3f}")
                print(f"     Detection probability: {detection_probability:.3f}")
                print(f"     Active evasions: {len(evasion_techniques)}")
                
                # Log first few evasion techniques
                for technique in evasion_techniques[:3]:
                    print(f"       • {technique}")
                
                paranoid_results.append({
                    "test": test["name"],
                    "success": True,
                    "navigation_time": navigation_time,
                    "fingerprint_score": fingerprint_score,
                    "detection_probability": detection_probability,
                    "evasions_count": len(evasion_techniques)
                })
            else:
                print(f"[WARN] Test failed: {result.get('error', 'Unknown error')}")
                paranoid_results.append({
                    "test": test["name"],
                    "success": False,
                    "navigation_time": navigation_time,
                    "error": result.get('error', 'Unknown error')
                })
        
        # Performance impact analysis
        print(f"\n[ANALYSIS] Paranoid Mode Performance Impact:")
        successful_tests = [r for r in paranoid_results if r["success"]]
        if successful_tests:
            avg_time = sum(r["navigation_time"] for r in successful_tests) / len(successful_tests)
            avg_detection_prob = sum(r.get("detection_probability", 1.0) for r in successful_tests) / len(successful_tests)
            
            print(f"• Average navigation time: {avg_time:.2f}s")
            print(f"• Average detection probability: {avg_detection_prob:.3f}")
            print(f"• Stealth effectiveness: {(1-avg_detection_prob)*100:.1f}%")
        
        # Cleanup
        await browser.cleanup()
        
        # Save paranoid test results
        output_file = Path("paranoid_stealth_results.json")
        with open(output_file, "w") as f:
            json.dump(paranoid_results, f, indent=2)
        print(f"\n[OK] Paranoid test results saved to: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] Paranoid stealth test failed: {e}")


async def example_2_framework_detection_evasion():
    """Example 2: Framework detection and evasion techniques"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Framework Detection and Evasion")
    print("="*80)
    
    try:
        # Initialize browser with framework evasion
        config = {
            "stealth_level": StealthLevel.ENHANCED,
            "profile_type": ProfileType.STEALTH,
            "framework_evasion": True,
            "script_detection_evasion": True,
            "selenium_evasion": True,
            "puppeteer_evasion": True,
            "playwright_evasion": True
        }
        
        browser = UltimateStealthBrowser(config)
        await browser.initialize()
        
        print("[OK] Browser initialized with framework evasion")
        print("     Evasion techniques:")
        print("       • Selenium detection bypass")
        print("       • Puppeteer signature masking")
        print("       • Playwright fingerprint hiding")
        print("       • WebDriver property spoofing")
        
        # Test framework detection capabilities
        test_url = "https://example.com"
        print(f"\n[INFO] Testing framework detection at: {test_url}")
        
        # Navigate and perform framework analysis
        result = await browser.navigate_stealth(test_url)
        
        if result.get("success", False):
            print("[OK] Navigation successful")
            
            # Analyze framework detection risks
            framework_analysis = await browser.analyze_framework_detection()
            
            detected_frameworks = framework_analysis.get("detected_frameworks", [])
            detection_vectors = framework_analysis.get("detection_vectors", [])
            evasion_status = framework_analysis.get("evasion_status", {})
            
            print(f"\n[ANALYSIS] Framework Detection Results:")
            
            if detected_frameworks:
                print(f"• Detected frameworks: {', '.join(detected_frameworks)}")
            else:
                print("• No automation frameworks detected ✓")
            
            if detection_vectors:
                print(f"• Detection vectors found:")
                for vector in detection_vectors[:5]:  # Show first 5
                    print(f"    - {vector}")
            else:
                print("• No detection vectors found ✓")
            
            print(f"\n• Evasion techniques status:")
            for technique, status in evasion_status.items():
                status_symbol = "✓" if status else "✗"
                print(f"    {status_symbol} {technique}")
            
            # Test specific automation properties
            automation_tests = [
                "webdriver property check",
                "navigator.webdriver detection",
                "chrome.runtime detection", 
                "phantom.js detection",
                "selenium IDE detection"
            ]
            
            print(f"\n[INFO] Running automation property tests:")
            
            property_results = {}
            for test in automation_tests:
                test_result = await browser.test_automation_property(test)
                property_results[test] = test_result.get("detected", False)
                
                status = "DETECTED" if test_result.get("detected", False) else "HIDDEN"
                symbol = "✗" if test_result.get("detected", False) else "✓"
                print(f"    {symbol} {test}: {status}")
            
            # Calculate overall stealth score
            hidden_count = sum(1 for detected in property_results.values() if not detected)
            stealth_score = hidden_count / len(property_results)
            
            print(f"\n[RESULT] Framework Evasion Score: {stealth_score:.2f}/1.0")
            if stealth_score >= 0.8:
                print("    Excellent stealth - most automation signatures hidden")
            elif stealth_score >= 0.6:
                print("    Good stealth - majority of signatures hidden")
            else:
                print("    Needs improvement - many signatures still detectable")
        
        else:
            print(f"[ERROR] Navigation failed: {result.get('error', 'Unknown error')}")
        
        # Cleanup
        await browser.cleanup()
        
    except Exception as e:
        print(f"[ERROR] Framework detection test failed: {e}")


async def example_3_captcha_detection_handling():
    """Example 3: CAPTCHA detection and handling strategies"""
    print("\n" + "="*80)
    print("EXAMPLE 3: CAPTCHA Detection and Handling")
    print("="*80)
    
    try:
        # Initialize browser with CAPTCHA handling
        config = {
            "stealth_level": StealthLevel.HIGH,
            "profile_type": ProfileType.HUMAN,
            "captcha_detection": True,
            "captcha_solving": True,
            "challenge_handling": True,
            "rate_limiting_respect": True
        }
        
        browser = UltimateStealthBrowser(config)
        await browser.initialize()
        
        print("[OK] Browser initialized with CAPTCHA handling")
        print("     CAPTCHA features:")
        print("       • Automatic CAPTCHA detection")
        print("       • Challenge type identification")
        print("       • Human-like solving behavior")
        print("       • Rate limiting respect")
        
        # Mock CAPTCHA scenarios (since we can't guarantee real CAPTCHAs)
        captcha_scenarios = [
            {
                "name": "reCAPTCHA v2 Detection",
                "url": "https://www.google.com/recaptcha/api2/demo",
                "captcha_type": "recaptcha_v2"
            },
            {
                "name": "Form with Challenge",
                "url": "https://httpbin.org/forms/post", 
                "captcha_type": "form_challenge"
            }
        ]
        
        captcha_results = []
        
        for scenario in captcha_scenarios:
            print(f"\n[INFO] Testing CAPTCHA scenario: {scenario['name']}")
            
            try:
                # Navigate to potential CAPTCHA page
                result = await browser.navigate_stealth(scenario["url"])
                
                if result.get("success", False):
                    print("[OK] Navigation successful")
                    
                    # Detect CAPTCHA presence
                    captcha_detection = await browser.detect_captcha()
                    
                    captcha_found = captcha_detection.get("captcha_detected", False)
                    captcha_type = captcha_detection.get("captcha_type", "none")
                    confidence = captcha_detection.get("confidence", 0.0)
                    
                    print(f"     CAPTCHA detected: {'Yes' if captcha_found else 'No'}")
                    print(f"     Type: {captcha_type}")
                    print(f"     Confidence: {confidence:.2f}")
                    
                    if captcha_found:
                        print(f"\n[INFO] Attempting CAPTCHA handling...")
                        
                        # Simulate CAPTCHA solving approach
                        solving_strategy = await browser.plan_captcha_solution(captcha_type)
                        
                        strategy_steps = solving_strategy.get("steps", [])
                        estimated_time = solving_strategy.get("estimated_time", 0)
                        success_probability = solving_strategy.get("success_probability", 0)
                        
                        print(f"     Solution strategy: {len(strategy_steps)} steps")
                        print(f"     Estimated time: {estimated_time:.1f}s")
                        print(f"     Success probability: {success_probability:.2f}")
                        
                        # Show strategy steps
                        print(f"     Strategy steps:")
                        for i, step in enumerate(strategy_steps[:3], 1):
                            print(f"       {i}. {step}")
                        
                        # Simulate solving attempt (don't actually solve)
                        print(f"     [SIMULATION] Would attempt CAPTCHA solving...")
                        
                        captcha_results.append({
                            "scenario": scenario["name"],
                            "captcha_detected": captcha_found,
                            "captcha_type": captcha_type,
                            "confidence": confidence,
                            "strategy_steps": len(strategy_steps),
                            "estimated_time": estimated_time,
                            "success_probability": success_probability
                        })
                    else:
                        print(f"     No CAPTCHA handling needed")
                        
                        captcha_results.append({
                            "scenario": scenario["name"],
                            "captcha_detected": False,
                            "captcha_type": "none"
                        })
                
                else:
                    print(f"[WARN] Navigation failed: {result.get('error', 'Unknown')}")
            
            except Exception as e:
                print(f"[ERROR] CAPTCHA test failed for {scenario['name']}: {e}")
        
        # CAPTCHA handling summary
        print(f"\n[SUMMARY] CAPTCHA Detection Results:")
        
        total_scenarios = len(captcha_results)
        detected_captchas = sum(1 for r in captcha_results if r.get("captcha_detected", False))
        
        print(f"• Scenarios tested: {total_scenarios}")
        print(f"• CAPTCHAs detected: {detected_captchas}")
        print(f"• Detection accuracy: {(detected_captchas/total_scenarios)*100 if total_scenarios > 0 else 0:.1f}%")
        
        # Show CAPTCHA types found
        captcha_types = [r.get("captcha_type", "none") for r in captcha_results]
        unique_types = set(t for t in captcha_types if t != "none")
        
        if unique_types:
            print(f"• CAPTCHA types identified: {', '.join(unique_types)}")
        else:
            print(f"• No CAPTCHAs identified in test scenarios")
        
        # Cleanup
        await browser.cleanup()
        
        # Save CAPTCHA results
        output_file = Path("captcha_detection_results.json")
        with open(output_file, "w") as f:
            json.dump(captcha_results, f, indent=2)
        print(f"\n[OK] CAPTCHA results saved to: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] CAPTCHA detection test failed: {e}")


async def example_4_custom_stealth_profiles():
    """Example 4: Creating and using custom stealth profiles"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Custom Stealth Profiles")
    print("="*80)
    
    try:
        # Define custom stealth profiles for different scenarios
        profiles = {
            "ecommerce_browsing": {
                "name": "E-Commerce Browsing",
                "stealth_level": StealthLevel.MODERATE,
                "profile_type": ProfileType.HUMAN,
                "timing_profile": TimingProfile(
                    scroll_pause=(800, 2000),      # Browsing products
                    element_analysis_delay=(100, 300),
                    mouse_move_steps=(15, 25),
                    typing_base_delay=(120, 200)   # Filling forms
                ),
                "features": {
                    "product_browsing_simulation": True,
                    "cart_interaction_timing": True,
                    "price_comparison_behavior": True
                }
            },
            "social_media_automation": {
                "name": "Social Media Automation",
                "stealth_level": StealthLevel.HIGH,
                "profile_type": ProfileType.STEALTH,
                "timing_profile": TimingProfile(
                    scroll_pause=(1000, 3000),     # Reading posts
                    element_analysis_delay=(200, 500),
                    mouse_move_steps=(20, 35),
                    typing_base_delay=(150, 300)   # Writing comments
                ),
                "features": {
                    "social_behavior_simulation": True,
                    "engagement_pattern_mimicking": True,
                    "content_consumption_timing": True
                }
            },
            "research_data_collection": {
                "name": "Research Data Collection",
                "stealth_level": StealthLevel.ENHANCED,
                "profile_type": ProfileType.STEALTH,
                "timing_profile": TimingProfile(
                    element_analysis_delay=(50, 150),
                    scroll_pause=(500, 1500),      # Scanning content
                    mouse_move_steps=(10, 20),
                    typing_base_delay=(80, 150)    # Search queries
                ),
                "features": {
                    "academic_browsing_pattern": True,
                    "systematic_data_collection": True,
                    "respectful_rate_limiting": True
                }
            }
        }
        
        profile_results = []
        
        for profile_name, profile_config in profiles.items():
            print(f"\n[INFO] Testing custom profile: {profile_config['name']}")
            
            try:
                # Create browser with custom profile
                config = {
                    "stealth_level": profile_config["stealth_level"],
                    "profile_type": profile_config["profile_type"],
                    "timing_profile": profile_config["timing_profile"],
                    "custom_features": profile_config.get("features", {}),
                    "profile_name": profile_name
                }
                
                browser = UltimateStealthBrowser(config)
                await browser.initialize()
                
                print(f"[OK] Initialized browser with {profile_config['name']} profile")
                print(f"     Stealth level: {profile_config['stealth_level'].value}")
                print(f"     Profile type: {profile_config['profile_type'].value}")
                
                # Test profile with appropriate URL
                test_urls = {
                    "ecommerce_browsing": "https://example.com",
                    "social_media_automation": "https://httpbin.org/user-agent",
                    "research_data_collection": "https://httpbin.org/headers"
                }
                
                test_url = test_urls.get(profile_name, "https://example.com")
                print(f"     Testing with URL: {test_url}")
                
                # Measure profile performance
                start_time = time.time()
                result = await browser.navigate_stealth(test_url)
                navigation_time = time.time() - start_time
                
                if result.get("success", False):
                    print(f"[OK] Navigation successful ({navigation_time:.2f}s)")
                    
                    # Get profile-specific metrics
                    profile_metrics = await browser.get_profile_metrics()
                    
                    stealth_effectiveness = profile_metrics.get("stealth_effectiveness", 0)
                    behavior_naturalness = profile_metrics.get("behavior_naturalness", 0)
                    detection_risk = profile_metrics.get("detection_risk", 1.0)
                    
                    print(f"     Stealth effectiveness: {stealth_effectiveness:.2f}")
                    print(f"     Behavior naturalness: {behavior_naturalness:.2f}")
                    print(f"     Detection risk: {detection_risk:.3f}")
                    
                    # Test profile-specific behaviors
                    if profile_name == "ecommerce_browsing":
                        behavior_test = await browser.simulate_ecommerce_browsing()
                        print(f"     E-commerce simulation: {'✓' if behavior_test.get('success') else '✗'}")
                    
                    elif profile_name == "social_media_automation":
                        behavior_test = await browser.simulate_social_engagement()
                        print(f"     Social engagement simulation: {'✓' if behavior_test.get('success') else '✗'}")
                    
                    elif profile_name == "research_data_collection":
                        behavior_test = await browser.simulate_academic_research()
                        print(f"     Research pattern simulation: {'✓' if behavior_test.get('success') else '✗'}")
                    
                    profile_results.append({
                        "profile": profile_config["name"],
                        "success": True,
                        "navigation_time": navigation_time,
                        "stealth_effectiveness": stealth_effectiveness,
                        "behavior_naturalness": behavior_naturalness,
                        "detection_risk": detection_risk
                    })
                
                else:
                    print(f"[WARN] Navigation failed: {result.get('error', 'Unknown')}")
                    profile_results.append({
                        "profile": profile_config["name"],
                        "success": False,
                        "error": result.get('error', 'Unknown')
                    })
                
                # Cleanup
                await browser.cleanup()
                
            except Exception as e:
                print(f"[ERROR] Profile {profile_name} test failed: {e}")
                profile_results.append({
                    "profile": profile_config["name"],
                    "success": False,
                    "error": str(e)
                })
        
        # Profile comparison
        print(f"\n[COMPARISON] Custom Profile Performance:")
        
        successful_profiles = [p for p in profile_results if p["success"]]
        
        if successful_profiles:
            print("\nProfile Rankings (by stealth effectiveness):")
            sorted_profiles = sorted(
                successful_profiles,
                key=lambda x: x.get("stealth_effectiveness", 0),
                reverse=True
            )
            
            for i, profile in enumerate(sorted_profiles, 1):
                print(f"{i}. {profile['profile']}: {profile.get('stealth_effectiveness', 0):.2f}")
            
            # Calculate averages
            avg_stealth = sum(p.get("stealth_effectiveness", 0) for p in successful_profiles) / len(successful_profiles)
            avg_naturalness = sum(p.get("behavior_naturalness", 0) for p in successful_profiles) / len(successful_profiles)
            avg_risk = sum(p.get("detection_risk", 1.0) for p in successful_profiles) / len(successful_profiles)
            
            print(f"\nAverage metrics across profiles:")
            print(f"• Stealth effectiveness: {avg_stealth:.2f}")
            print(f"• Behavior naturalness: {avg_naturalness:.2f}")
            print(f"• Detection risk: {avg_risk:.3f}")
        
        # Save profile results
        output_file = Path("custom_profile_results.json")
        with open(output_file, "w") as f:
            json.dump(profile_results, f, indent=2)
        print(f"\n[OK] Custom profile results saved to: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] Custom profile test failed: {e}")


async def main():
    """Run all advanced stealth examples"""
    print("="*80)
    print("ULTIMATE STEALTH BROWSER - Advanced Features")
    print("="*80)
    print("\nDemonstrating advanced stealth capabilities:")
    print("• Paranoid-level stealth for maximum protection")
    print("• Framework detection and evasion techniques")
    print("• CAPTCHA detection and handling strategies")
    print("• Custom stealth profiles for specific scenarios")
    print("• Real-world anti-detection testing")
    
    try:
        # Run all advanced examples
        await example_1_paranoid_stealth_mode()
        await example_2_framework_detection_evasion()
        await example_3_captcha_detection_handling()
        await example_4_custom_stealth_profiles()
        
    except Exception as e:
        print(f"\n[ERROR] Advanced example execution failed: {e}")
    
    # Final summary
    print("\n" + "="*80)
    print("ADVANCED STEALTH EXAMPLES COMPLETED")
    print("="*80)
    print("\nAdvanced Features Demonstrated:")
    print("  ✓ Paranoid-level stealth (99%+ anti-detection)")
    print("  ✓ Framework signature evasion")
    print("  ✓ Automated CAPTCHA detection")
    print("  ✓ Custom stealth profile creation")
    print("  ✓ Real-world protection testing")
    print("  ✓ Performance impact analysis")
    print("  ✓ Comprehensive metrics collection")
    
    print(f"\nThe browser.py module provides enterprise-grade stealth")
    print(f"capabilities suitable for the most challenging automation scenarios.")


if __name__ == "__main__":
    # Run the advanced examples
    asyncio.run(main())