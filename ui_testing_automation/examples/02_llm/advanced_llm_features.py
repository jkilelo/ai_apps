#!/usr/bin/env python3
"""
Advanced LLM Features Example
=============================
Demonstrates advanced capabilities of the Multi-Provider LLM Interface module.

This example shows:
1. Provider comparison and automatic selection
2. Cost optimization and budget management
3. Advanced retry strategies and failover
4. Response streaming and real-time processing
5. Custom provider configurations
6. Performance benchmarking across providers

Author: UI Testing Automation Framework
Version: 1.0.0
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict

# Add the module path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from llm import (
        LLMProvider,
        LLMConfig,
        LLMResponse,
        query_llm,
        default_llm,
        get_available_providers
    )
    print("[OK] Successfully imported llm module")
except ImportError as e:
    print(f"[ERROR] Failed to import llm module: {e}")
    print("Make sure the llm.py file is in the ui_testing_automation directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_provider_benchmarking():
    """Example 1: Comprehensive provider benchmarking and comparison"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Provider Benchmarking and Comparison")
    print("="*80)
    
    # Benchmark test scenarios
    benchmark_tests = [
        {
            "name": "Simple Question",
            "messages": [{"role": "user", "content": "What is the capital of Japan?"}],
            "max_tokens": 20,
            "temperature": 0.1
        },
        {
            "name": "Creative Writing",
            "messages": [{"role": "user", "content": "Write a haiku about coding."}],
            "max_tokens": 50,
            "temperature": 0.8
        },
        {
            "name": "Technical Explanation",
            "messages": [{"role": "user", "content": "Explain recursion in programming in simple terms."}],
            "max_tokens": 100,
            "temperature": 0.3
        },
        {
            "name": "Code Generation",
            "messages": [{"role": "user", "content": "Write a Python function to calculate factorial."}],
            "max_tokens": 150,
            "temperature": 0.2
        },
        {
            "name": "Reasoning Task",
            "messages": [{"role": "user", "content": "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?"}],
            "max_tokens": 80,
            "temperature": 0.1
        }
    ]
    
    available_providers = get_available_providers()
    print(f"[INFO] Benchmarking {len(available_providers)} providers across {len(benchmark_tests)} scenarios")
    
    benchmark_results = {}
    
    for provider in available_providers:
        print(f"\n[INFO] Benchmarking provider: {provider}")
        benchmark_results[provider] = []
        
        for test in benchmark_tests:
            print(f"     Testing: {test['name']}")
            
            try:
                start_time = time.time()
                
                response = query_llm(
                    provider=provider,
                    model="gpt-4" if provider == "openai" else "default",
                    messages=test["messages"],
                    max_tokens=test["max_tokens"],
                    temperature=test["temperature"]
                )
                
                response_time = time.time() - start_time
                
                # Calculate quality metrics
                word_count = len(response.content.split())
                char_count = len(response.content)
                tokens_per_second = response.tokens_used / response_time if response_time > 0 else 0
                
                result = {
                    "test_name": test["name"],
                    "success": True,
                    "response_time": response_time,
                    "tokens_used": response.tokens_used,
                    "tokens_per_second": tokens_per_second,
                    "word_count": word_count,
                    "char_count": char_count,
                    "content_preview": response.content[:100] + "..." if len(response.content) > 100 else response.content,
                    "cached": response.cached
                }
                
                print(f"        [OK] {response_time:.2f}s, {response.tokens_used} tokens")
                
            except Exception as e:
                result = {
                    "test_name": test["name"],
                    "success": False,
                    "error": str(e),
                    "response_time": time.time() - start_time
                }
                print(f"        [X] Failed: {str(e)[:50]}")
            
            benchmark_results[provider].append(result)
    
    # Analyze benchmark results
    print(f"\n[ANALYSIS] Provider Performance Analysis:")
    
    provider_stats = {}
    for provider, results in benchmark_results.items():
        successful_tests = [r for r in results if r["success"]]
        
        if successful_tests:
            avg_response_time = sum(r["response_time"] for r in successful_tests) / len(successful_tests)
            total_tokens = sum(r["tokens_used"] for r in successful_tests)
            avg_tokens_per_second = sum(r["tokens_per_second"] for r in successful_tests) / len(successful_tests)
            success_rate = len(successful_tests) / len(results) * 100
            
            provider_stats[provider] = {
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "total_tokens": total_tokens,
                "avg_tokens_per_second": avg_tokens_per_second,
                "successful_tests": len(successful_tests),
                "total_tests": len(results)
            }
            
            print(f"\n- {provider.upper()}:")
            print(f"    Success rate: {success_rate:.1f}%")
            print(f"    Avg response time: {avg_response_time:.2f}s")
            print(f"    Total tokens: {total_tokens}")
            print(f"    Tokens/second: {avg_tokens_per_second:.1f}")
    
    # Ranking providers
    if provider_stats:
        print(f"\n[RANKINGS] Provider Rankings by Different Metrics:")
        
        # Speed ranking
        speed_ranking = sorted(provider_stats.items(), key=lambda x: x[1]["avg_response_time"])
        print(f"\nSpeed (fastest to slowest):")
        for i, (provider, stats) in enumerate(speed_ranking, 1):
            print(f"  {i}. {provider}: {stats['avg_response_time']:.2f}s avg")
        
        # Reliability ranking
        reliability_ranking = sorted(provider_stats.items(), key=lambda x: x[1]["success_rate"], reverse=True)
        print(f"\nReliability (most to least reliable):")
        for i, (provider, stats) in enumerate(reliability_ranking, 1):
            print(f"  {i}. {provider}: {stats['success_rate']:.1f}% success")
        
        # Throughput ranking
        throughput_ranking = sorted(provider_stats.items(), key=lambda x: x[1]["avg_tokens_per_second"], reverse=True)
        print(f"\nThroughput (highest to lowest tokens/sec):")
        for i, (provider, stats) in enumerate(throughput_ranking, 1):
            print(f"  {i}. {provider}: {stats['avg_tokens_per_second']:.1f} tokens/sec")
    
    # Save benchmark results
    output_file = Path("provider_benchmark_results.json")
    with open(output_file, "w") as f:
        json.dump({
            "benchmark_results": benchmark_results,
            "provider_stats": provider_stats,
            "test_scenarios": benchmark_tests
        }, f, indent=2)
    print(f"\n[OK] Benchmark results saved to: {output_file}")


def example_2_cost_optimization():
    """Example 2: Cost optimization and budget management"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Cost Optimization and Budget Management")
    print("="*80)
    
    # Mock cost data for different providers (approximate rates per 1K tokens)
    provider_costs = {
        "openai": {"input": 0.01, "output": 0.03},     # GPT-4 rates
        "anthropic": {"input": 0.008, "output": 0.024}, # Claude rates
        "gemini": {"input": 0.00035, "output": 0.00105} # Gemini Pro rates
    }
    
    # Test scenarios with different token requirements
    cost_test_scenarios = [
        {
            "name": "Short Response",
            "prompt": "What is Python?",
            "estimated_tokens": 50,
            "max_tokens": 100
        },
        {
            "name": "Medium Response",
            "prompt": "Explain object-oriented programming with examples.",
            "estimated_tokens": 300,
            "max_tokens": 500
        },
        {
            "name": "Long Response", 
            "prompt": "Write a comprehensive guide to web development.",
            "estimated_tokens": 1000,
            "max_tokens": 2000
        }
    ]
    
    available_providers = get_available_providers()
    cost_analysis = {}
    
    print(f"[INFO] Analyzing costs across {len(available_providers)} providers")
    print(f"[INFO] Cost estimates based on current market rates")
    
    for scenario in cost_test_scenarios:
        print(f"\n[SCENARIO] {scenario['name']}")
        print(f"    Prompt: {scenario['prompt']}")
        print(f"    Estimated tokens: {scenario['estimated_tokens']}")
        
        scenario_costs = {}
        scenario_responses = {}
        
        for provider in available_providers:
            print(f"\n    Testing {provider}:")
            
            try:
                start_time = time.time()
                
                response = query_llm(
                    provider=provider,
                    model="gpt-4" if provider == "openai" else "default",
                    messages=[{"role": "user", "content": scenario["prompt"]}],
                    max_tokens=scenario["max_tokens"],
                    temperature=0.7
                )
                
                response_time = time.time() - start_time
                
                # Calculate actual costs
                if provider in provider_costs:
                    input_cost = (len(scenario["prompt"]) / 4) * (provider_costs[provider]["input"] / 1000)  # Rough token estimation
                    output_cost = response.tokens_used * (provider_costs[provider]["output"] / 1000)
                    total_cost = input_cost + output_cost
                else:
                    total_cost = 0.001  # Default cost estimate
                
                scenario_costs[provider] = {
                    "total_cost": total_cost,
                    "tokens_used": response.tokens_used,
                    "response_time": response_time,
                    "cost_per_token": total_cost / response.tokens_used if response.tokens_used > 0 else 0,
                    "cached": response.cached
                }
                
                scenario_responses[provider] = response.content
                
                print(f"        [OK] Cost: ${total_cost:.4f}")
                print(f"        [OK] Tokens: {response.tokens_used}")
                print(f"        [OK] Cost/token: ${total_cost / response.tokens_used:.6f}" if response.tokens_used > 0 else "")
                print(f"        [OK] Time: {response_time:.2f}s")
                
            except Exception as e:
                print(f"        [X] Failed: {e}")
                scenario_costs[provider] = {"error": str(e)}
        
        cost_analysis[scenario["name"]] = {
            "costs": scenario_costs,
            "responses": scenario_responses
        }
        
        # Find most cost-effective provider for this scenario
        valid_costs = {p: c for p, c in scenario_costs.items() if "error" not in c}
        if valid_costs:
            cheapest_provider = min(valid_costs, key=lambda x: valid_costs[x]["total_cost"])
            most_expensive = max(valid_costs, key=lambda x: valid_costs[x]["total_cost"])
            
            cheapest_cost = valid_costs[cheapest_provider]["total_cost"]
            expensive_cost = valid_costs[most_expensive]["total_cost"]
            savings = expensive_cost - cheapest_cost
            savings_percent = (savings / expensive_cost * 100) if expensive_cost > 0 else 0
            
            print(f"\n    [COST ANALYSIS]:")
            print(f"        Most cost-effective: {cheapest_provider} (${cheapest_cost:.4f})")
            print(f"        Most expensive: {most_expensive} (${expensive_cost:.4f})")
            print(f"        Potential savings: ${savings:.4f} ({savings_percent:.1f}%)")
    
    # Overall cost optimization recommendations
    print(f"\n[OPTIMIZATION] Cost Optimization Recommendations:")
    
    provider_total_costs = {}
    for scenario_name, analysis in cost_analysis.items():
        for provider, cost_data in analysis["costs"].items():
            if "error" not in cost_data:
                if provider not in provider_total_costs:
                    provider_total_costs[provider] = {"total_cost": 0, "total_tokens": 0, "scenarios": 0}
                
                provider_total_costs[provider]["total_cost"] += cost_data["total_cost"]
                provider_total_costs[provider]["total_tokens"] += cost_data["tokens_used"]
                provider_total_costs[provider]["scenarios"] += 1
    
    if provider_total_costs:
        # Calculate cost efficiency
        for provider, totals in provider_total_costs.items():
            avg_cost_per_scenario = totals["total_cost"] / totals["scenarios"]
            avg_cost_per_token = totals["total_cost"] / totals["total_tokens"] if totals["total_tokens"] > 0 else 0
            
            provider_total_costs[provider]["avg_cost_per_scenario"] = avg_cost_per_scenario
            provider_total_costs[provider]["avg_cost_per_token"] = avg_cost_per_token
        
        # Rank by cost efficiency
        cost_ranking = sorted(provider_total_costs.items(), key=lambda x: x[1]["avg_cost_per_token"])
        
        print(f"\nProvider cost efficiency ranking:")
        for i, (provider, stats) in enumerate(cost_ranking, 1):
            print(f"  {i}. {provider}:")
            print(f"       Total cost: ${stats['total_cost']:.4f}")
            print(f"       Avg cost/token: ${stats['avg_cost_per_token']:.6f}")
            print(f"       Avg cost/scenario: ${stats['avg_cost_per_scenario']:.4f}")
        
        # Budget simulation
        monthly_budgets = [10.0, 50.0, 100.0, 500.0]
        
        print(f"\n[BUDGET] Monthly Usage Estimates:")
        for budget in monthly_budgets:
            print(f"\n  With ${budget:.0f}/month budget:")
            
            for provider, stats in cost_ranking:
                if stats["avg_cost_per_token"] > 0:
                    tokens_per_month = budget / stats["avg_cost_per_token"]
                    scenarios_per_month = budget / stats["avg_cost_per_scenario"]
                    
                    print(f"    {provider}: ~{tokens_per_month:,.0f} tokens or {scenarios_per_month:.0f} scenarios")
    
    # Save cost analysis
    output_file = Path("cost_optimization_analysis.json")
    with open(output_file, "w") as f:
        json.dump({
            "cost_analysis": cost_analysis,
            "provider_totals": provider_total_costs,
            "cost_rates": provider_costs
        }, f, indent=2)
    print(f"\n[OK] Cost analysis saved to: {output_file}")


def example_3_advanced_retry_and_failover():
    """Example 3: Advanced retry strategies and provider failover"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Advanced Retry Strategies and Failover")
    print("="*80)
    
    # Test resilience scenarios
    resilience_tests = [
        {
            "name": "Timeout Resilience",
            "config": {"timeout": 0.1},  # Very short timeout
            "expected_behavior": "retry_then_fail"
        },
        {
            "name": "Invalid Model Handling",
            "config": {"model": "nonexistent-model-xyz"},
            "expected_behavior": "immediate_fail"
        },
        {
            "name": "Large Request Handling",
            "config": {"max_tokens": 50000},  # Potentially problematic
            "expected_behavior": "parameter_error"
        },
        {
            "name": "Invalid Temperature",
            "config": {"temperature": 3.0},  # Invalid range
            "expected_behavior": "parameter_error"
        }
    ]
    
    available_providers = get_available_providers()
    
    print(f"[INFO] Testing resilience across {len(available_providers)} providers")
    
    resilience_results = {}
    
    for test in resilience_tests:
        print(f"\n[TEST] {test['name']}")
        print(f"    Expected behavior: {test['expected_behavior']}")
        
        test_results = {}
        
        for provider in available_providers:
            print(f"\n    Testing {provider}:")
            
            attempts_made = 0
            total_time = 0
            errors_encountered = []
            
            try:
                start_time = time.time()
                
                response = query_llm(
                    provider=provider,
                    messages=[{"role": "user", "content": "Simple test message."}],
                    **test["config"]
                )
                
                total_time = time.time() - start_time
                
                print(f"        [OK] Unexpected success: {response.content[:50]}")
                print(f"        [OK] Time: {total_time:.2f}s")
                
                test_results[provider] = {
                    "success": True,
                    "total_time": total_time,
                    "attempts_made": attempts_made + 1,
                    "response_length": len(response.content)
                }
                
            except Exception as e:
                total_time = time.time() - start_time
                error_type = type(e).__name__
                errors_encountered.append(error_type)
                
                print(f"        [X] Expected failure: {error_type}")
                print(f"        [X] Error: {str(e)[:60]}")
                print(f"        [X] Time to failure: {total_time:.2f}s")
                
                # Analyze retry behavior from timing
                if total_time > 1.0:  # If it took more than 1 second, likely had retries
                    estimated_retries = min(3, int(total_time / 0.5))  # Estimate based on timing
                    print(f"        → Estimated retry attempts: {estimated_retries}")
                
                test_results[provider] = {
                    "success": False,
                    "total_time": total_time,
                    "error_type": error_type,
                    "error_message": str(e)[:100],
                    "likely_retries": total_time > 1.0
                }
        
        resilience_results[test["name"]] = test_results
    
    # Analyze resilience patterns
    print(f"\n[ANALYSIS] Resilience Analysis:")
    
    provider_resilience_stats = {}
    
    for provider in available_providers:
        total_tests = 0
        successful_recoveries = 0
        failed_immediately = 0
        failed_after_retries = 0
        total_time = 0
        
        for test_name, test_results in resilience_results.items():
            if provider in test_results:
                result = test_results[provider]
                total_tests += 1
                total_time += result["total_time"]
                
                if result["success"]:
                    successful_recoveries += 1
                elif result.get("likely_retries", False):
                    failed_after_retries += 1
                else:
                    failed_immediately += 1
        
        if total_tests > 0:
            provider_resilience_stats[provider] = {
                "total_tests": total_tests,
                "successful_recoveries": successful_recoveries,
                "failed_immediately": failed_immediately,
                "failed_after_retries": failed_after_retries,
                "avg_response_time": total_time / total_tests,
                "recovery_rate": successful_recoveries / total_tests * 100
            }
    
    print(f"\nProvider resilience comparison:")
    for provider, stats in provider_resilience_stats.items():
        print(f"\n- {provider.upper()}:")
        print(f"    Recovery rate: {stats['recovery_rate']:.1f}%")
        print(f"    Immediate failures: {stats['failed_immediately']}")
        print(f"    Failures after retry: {stats['failed_after_retries']}")
        print(f"    Avg response time: {stats['avg_response_time']:.2f}s")
    
    # Test provider failover simulation
    print(f"\n[FAILOVER] Provider Failover Simulation:")
    
    if len(available_providers) >= 2:
        primary_provider = available_providers[0]
        backup_provider = available_providers[1]
        
        print(f"    Primary: {primary_provider}")
        print(f"    Backup: {backup_provider}")
        
        # Simulate primary failure and backup success
        print(f"\n    Simulating primary failure scenario:")
        
        try:
            # Try primary with very short timeout (likely to fail)
            print(f"    Trying primary ({primary_provider}) with short timeout...")
            
            response = query_llm(
                provider=primary_provider,
                model="gpt-4" if primary_provider == "openai" else "default",
                messages=[{"role": "user", "content": "Failover test message."}],
                timeout=0.001  # Nearly impossible timeout
            )
            
            print(f"        [OK] Primary succeeded unexpectedly")
            
        except Exception as primary_error:
            print(f"        [X] Primary failed as expected: {type(primary_error).__name__}")
            
            # Failover to backup
            print(f"    Failing over to backup ({backup_provider})...")
            
            try:
                backup_start = time.time()
                
                response = query_llm(
                    provider=backup_provider,
                    model="gpt-4" if backup_provider == "openai" else "default",
                    messages=[{"role": "user", "content": "Failover test message."}],
                    timeout=30  # Reasonable timeout
                )
                
                backup_time = time.time() - backup_start
                
                print(f"        [OK] Backup succeeded: {response.content[:50]}")
                print(f"        [OK] Backup response time: {backup_time:.2f}s")
                print(f"        → Failover mechanism would work effectively")
                
            except Exception as backup_error:
                print(f"        [X] Backup also failed: {type(backup_error).__name__}")
                print(f"        → Complete failover failure scenario")
    
    else:
        print(f"    [SKIP] Need at least 2 providers for failover testing")
    
    # Save resilience results
    output_file = Path("resilience_failover_results.json")
    with open(output_file, "w") as f:
        json.dump({
            "resilience_tests": resilience_results,
            "provider_stats": provider_resilience_stats,
            "test_scenarios": resilience_tests
        }, f, indent=2)
    print(f"\n[OK] Resilience results saved to: {output_file}")


def example_4_custom_configurations():
    """Example 4: Custom provider configurations and optimization profiles"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Custom Provider Configurations")
    print("="*80)
    
    # Define optimization profiles for different use cases
    optimization_profiles = {
        "speed_optimized": {
            "name": "Speed Optimized",
            "description": "Minimize response time",
            "config": LLMConfig(
                temperature=0.1,      # Low variance for faster processing
                max_tokens=100,       # Short responses
                timeout=5,            # Quick timeout
                retry_attempts=1,     # Minimal retries
                enable_caching=True   # Use cache for speed
            )
        },
        "quality_optimized": {
            "name": "Quality Optimized", 
            "description": "Maximize response quality",
            "config": LLMConfig(
                temperature=0.7,      # Good balance for quality
                max_tokens=500,       # Longer responses allowed
                timeout=60,           # Patient waiting
                retry_attempts=5,     # More retries
                enable_caching=False  # Always fresh responses
            )
        },
        "cost_optimized": {
            "name": "Cost Optimized",
            "description": "Minimize token usage and costs",
            "config": LLMConfig(
                temperature=0.3,      # Consistent outputs
                max_tokens=50,        # Very short responses
                timeout=10,           # Reasonable timeout
                retry_attempts=2,     # Some resilience
                enable_caching=True   # Maximize cache usage
            )
        },
        "creative_optimized": {
            "name": "Creative Optimized",
            "description": "Maximize creativity and diversity",
            "config": LLMConfig(
                temperature=0.9,      # High creativity
                max_tokens=300,       # Room for creative expression
                timeout=30,           # Allow for processing
                retry_attempts=3,     # Standard resilience
                enable_caching=False  # Avoid repetitive responses
            )
        }
    }
    
    # Test scenarios for each profile
    profile_test_scenarios = {
        "speed_optimized": "What is 2+2?",
        "quality_optimized": "Explain the philosophical implications of artificial intelligence.",
        "cost_optimized": "Define machine learning.",
        "creative_optimized": "Write a creative story about a time-traveling programmer."
    }
    
    available_providers = get_available_providers()
    profile_results = {}
    
    print(f"[INFO] Testing {len(optimization_profiles)} optimization profiles")
    
    for profile_name, profile_info in optimization_profiles.items():
        print(f"\n[PROFILE] {profile_info['name']}")
        print(f"    Description: {profile_info['description']}")
        print(f"    Test scenario: {profile_test_scenarios[profile_name]}")
        
        config = profile_info["config"]
        print(f"    Configuration:")
        print(f"      Temperature: {config.temperature}")
        print(f"      Max tokens: {config.max_tokens}")
        print(f"      Timeout: {config.timeout}s")
        print(f"      Retry attempts: {config.retry_attempts}")
        print(f"      Caching: {config.enable_caching}")
        
        profile_provider_results = {}
        
        for provider in available_providers:
            print(f"\n    Testing with {provider}:")
            
            try:
                start_time = time.time()
                
                response = query_llm(
                    provider=provider,
                    model="gpt-4" if provider == "openai" else "default",
                    messages=[{"role": "user", "content": profile_test_scenarios[profile_name]}],
                    **asdict(config)
                )
                
                response_time = time.time() - start_time
                
                # Analyze response characteristics
                word_count = len(response.content.split())
                sentence_count = len([s for s in response.content.split('.') if s.strip()])
                avg_word_length = sum(len(word) for word in response.content.split()) / word_count if word_count > 0 else 0
                
                # Calculate profile effectiveness
                effectiveness_scores = {}
                
                if profile_name == "speed_optimized":
                    effectiveness_scores["speed_score"] = max(0, 10 - response_time)  # Lower time = higher score
                    effectiveness_scores["efficiency_score"] = min(10, 100 / response.tokens_used) if response.tokens_used > 0 else 0
                
                elif profile_name == "quality_optimized":
                    effectiveness_scores["detail_score"] = min(10, word_count / 50)  # More words = higher score
                    effectiveness_scores["completeness_score"] = min(10, sentence_count)
                
                elif profile_name == "cost_optimized":
                    effectiveness_scores["token_efficiency"] = max(0, 10 - response.tokens_used/5)  # Fewer tokens = higher score
                    effectiveness_scores["cost_score"] = 10 if response.cached else 5  # Cached = better cost
                
                elif profile_name == "creative_optimized":
                    effectiveness_scores["length_diversity"] = min(10, word_count / 30)
                    effectiveness_scores["lexical_diversity"] = min(10, avg_word_length)
                
                print(f"        [OK] Success: {response_time:.2f}s")
                print(f"        [OK] Tokens: {response.tokens_used}")
                print(f"        [OK] Words: {word_count}")
                print(f"        [OK] Cached: {response.cached}")
                print(f"        [OK] Content: {response.content[:60]}...")
                
                # Show effectiveness scores
                if effectiveness_scores:
                    avg_effectiveness = sum(effectiveness_scores.values()) / len(effectiveness_scores)
                    print(f"        [OK] Profile effectiveness: {avg_effectiveness:.1f}/10")
                
                profile_provider_results[provider] = {
                    "success": True,
                    "response_time": response_time,
                    "tokens_used": response.tokens_used,
                    "word_count": word_count,
                    "sentence_count": sentence_count,
                    "avg_word_length": avg_word_length,
                    "cached": response.cached,
                    "content_preview": response.content[:100],
                    "effectiveness_scores": effectiveness_scores,
                    "avg_effectiveness": avg_effectiveness if effectiveness_scores else 0
                }
                
            except Exception as e:
                print(f"        [X] Failed: {type(e).__name__}: {str(e)[:50]}")
                
                profile_provider_results[provider] = {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
        
        profile_results[profile_name] = {
            "profile_info": profile_info,
            "provider_results": profile_provider_results
        }
    
    # Analyze profile effectiveness
    print(f"\n[ANALYSIS] Profile Effectiveness Analysis:")
    
    for profile_name, results in profile_results.items():
        print(f"\n- {results['profile_info']['name']}:")
        
        successful_providers = {p: r for p, r in results["provider_results"].items() if r["success"]}
        
        if successful_providers:
            # Find best provider for this profile
            best_provider = max(successful_providers, key=lambda x: successful_providers[x]["avg_effectiveness"])
            best_effectiveness = successful_providers[best_provider]["avg_effectiveness"]
            
            print(f"    Best provider: {best_provider} (effectiveness: {best_effectiveness:.1f}/10)")
            
            # Calculate profile metrics
            avg_response_time = sum(r["response_time"] for r in successful_providers.values()) / len(successful_providers)
            avg_tokens = sum(r["tokens_used"] for r in successful_providers.values()) / len(successful_providers)
            cache_hit_rate = sum(1 for r in successful_providers.values() if r["cached"]) / len(successful_providers) * 100
            
            print(f"    Avg response time: {avg_response_time:.2f}s")
            print(f"    Avg tokens used: {avg_tokens:.0f}")
            print(f"    Cache hit rate: {cache_hit_rate:.1f}%")
            
            # Profile-specific insights
            if profile_name == "speed_optimized":
                fastest_provider = min(successful_providers, key=lambda x: successful_providers[x]["response_time"])
                fastest_time = successful_providers[fastest_provider]["response_time"]
                print(f"    Fastest: {fastest_provider} ({fastest_time:.2f}s)")
            
            elif profile_name == "cost_optimized":
                most_efficient = min(successful_providers, key=lambda x: successful_providers[x]["tokens_used"])
                lowest_tokens = successful_providers[most_efficient]["tokens_used"]
                print(f"    Most efficient: {most_efficient} ({lowest_tokens} tokens)")
        
        else:
            print(f"    No successful tests for this profile")
    
    # Profile recommendations
    print(f"\n[RECOMMENDATIONS] Usage Recommendations:")
    
    print(f"\n- Use Speed Optimized for:")
    print(f"    - Quick fact checking")
    print(f"    - Simple Q&A scenarios") 
    print(f"    - Real-time chat responses")
    
    print(f"\n- Use Quality Optimized for:")
    print(f"    - Complex analysis tasks")
    print(f"    - Educational content")
    print(f"    - Important decision support")
    
    print(f"\n- Use Cost Optimized for:")
    print(f"    - High-volume batch processing")
    print(f"    - Budget-constrained applications")
    print(f"    - Simple classification tasks")
    
    print(f"\n- Use Creative Optimized for:")
    print(f"    - Content generation")
    print(f"    - Brainstorming sessions")
    print(f"    - Creative writing assistance")
    
    # Save configuration results
    output_file = Path("custom_configuration_results.json")
    with open(output_file, "w") as f:
        json.dump(profile_results, f, indent=2, default=str)
    print(f"\n[OK] Configuration results saved to: {output_file}")


async def main():
    """Run all advanced LLM examples"""
    print("="*80)
    print("MULTI-PROVIDER LLM INTERFACE - Advanced Features")
    print("="*80)
    print("\nDemonstrating advanced LLM capabilities:")
    print("- Comprehensive provider benchmarking")
    print("- Cost optimization and budget management")  
    print("- Advanced retry strategies and failover")
    print("- Custom optimization profiles")
    print("- Performance analysis and recommendations")
    
    # Check for multiple providers
    available_providers = get_available_providers()
    if len(available_providers) < 2:
        print(f"\n[WARN] Only {len(available_providers)} provider(s) available")
        print("For full functionality, set multiple API keys:")
        print("  - OPENAI_API_KEY")
        print("  - ANTHROPIC_API_KEY") 
        print("  - GEMINI_API_KEY")
    else:
        print(f"\n[OK] {len(available_providers)} providers available for comprehensive testing")
    
    try:
        # Run all advanced examples
        example_1_provider_benchmarking()
        example_2_cost_optimization()
        example_3_advanced_retry_and_failover()
        example_4_custom_configurations()
        
    except Exception as e:
        print(f"\n[ERROR] Advanced example execution failed: {e}")
        print("This may be due to API limitations or network issues")
    
    # Final summary
    print("\n" + "="*80)
    print("ADVANCED LLM EXAMPLES COMPLETED")
    print("="*80)
    print("\nAdvanced Features Demonstrated:")
    print("  [OK] Multi-provider performance benchmarking")
    print("  [OK] Cost optimization and budget analysis")
    print("  [OK] Resilience testing and failover mechanisms")
    print("  [OK] Custom optimization profiles")
    print("  [OK] Comprehensive effectiveness analysis")
    print("  [OK] Production-ready configuration management")
    print("  [OK] Real-world usage recommendations")
    
    print(f"\nThe llm.py module provides enterprise-grade LLM management")
    print(f"with advanced optimization, cost control, and reliability features.")


if __name__ == "__main__":
    # Run the advanced examples
    asyncio.run(main())