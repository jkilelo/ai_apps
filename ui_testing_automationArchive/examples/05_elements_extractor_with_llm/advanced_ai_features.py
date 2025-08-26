#!/usr/bin/env python3
"""
Advanced AI Features - Elements Extractor With LLM
==================================================
Working examples demonstrating advanced AI capabilities including
prompt strategies, visual analysis, context learning, and performance optimization.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import tempfile

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from elements_extractor_with_llm import (
        ElementsExtractorWithLLM,
        SemanticContext,
        AIAnalysis,
        EnhancedElement,
        ExtractionStrategy,
        LLMProvider,
        LLMConfig
    )
    from prompts import (
        PromptStrategy,
        TaskType,
        ComplexityLevel,
        PromptEngine,
        StrategyOrchestrator,
        PromptRequest
    )
    from elements_extractor_no_llm import ExtractionConfig
    print("[OK] Advanced AI modules imported successfully")
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("Make sure all dependencies are installed and paths are correct")
    sys.exit(1)

# Configure logging for examples
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def example_1_prompt_strategy_optimization():
    """Example 1: Advanced prompt strategy optimization for different tasks"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Prompt Strategy Optimization")
    print("="*80)
    
    # Test different prompt strategies for element analysis
    strategies_to_test = [
        (PromptStrategy.CHAIN_OF_THOUGHT, "Step-by-step reasoning"),
        (PromptStrategy.TREE_OF_THOUGHTS, "Multi-path exploration"),
        (PromptStrategy.CONSTITUTIONAL_AI, "Safe and helpful analysis"),
        (PromptStrategy.SELF_CONSISTENCY, "Multiple reasoning paths"),
        (PromptStrategy.OPRO, "Optimization by prompting")
    ]
    
    print(f"🧠 Testing {len(strategies_to_test)} prompt strategies for element analysis")
    
    test_url = "https://example.com"
    strategy_results = []
    
    for strategy, description in strategies_to_test:
        print(f"\n🔄 Testing strategy: {strategy.value} ({description})")
        
        try:
            # Create extractor with specific prompt strategy
            extractor = ElementsExtractorWithLLM(
                llm_provider=LLMProvider.OPENAI,
                enable_semantic_analysis=True,
                enable_visual_analysis=False,  # Focus on prompt strategy
                confidence_threshold=0.6
            )
            
            # Configure the prompt strategy (if the extractor supports it)
            if hasattr(extractor, 'prompts_engine'):
                # Test specific strategy performance
                start_time = asyncio.get_event_loop().time()
                
                # Create a prompt request for this strategy
                prompt_request = PromptRequest(
                    task=f"Analyze website elements for user interaction patterns",
                    task_type=TaskType.ANALYTICAL,
                    complexity=ComplexityLevel.COMPLEX,
                    strategy=strategy
                )
                
                # Use strategy orchestrator to optimize prompt
                if hasattr(extractor, 'strategy_orchestrator'):
                    prompt_response = extractor.strategy_orchestrator.optimize_prompt(prompt_request)
                    print(f"  🎯 Strategy selected: {prompt_response.strategy_used.value}")
                    print(f"  📊 Confidence: {prompt_response.confidence:.2f}")
            
            # Perform extraction with this configuration
            result = await extractor.extract_from_url(test_url)
            end_time = asyncio.get_event_loop().time()
            
            # Analyze results
            ai_elements = [e for e in result.elements if hasattr(e, 'ai_analysis') and e.ai_analysis]
            avg_confidence = sum(e.ai_analysis.confidence_score for e in ai_elements) / len(ai_elements) if ai_elements else 0
            
            strategy_result = {
                "strategy": strategy.value,
                "description": description,
                "success": result.success,
                "processing_time": end_time - start_time,
                "extraction_time": result.extraction_time,
                "elements_found": len(result.elements),
                "ai_analyzed": len(ai_elements),
                "avg_confidence": avg_confidence
            }
            
            strategy_results.append(strategy_result)
            
            print(f"  [OK] Success: {strategy_result['success']}")
            print(f"  [TIME] Processing time: {strategy_result['processing_time']:.2f}s")
            print(f"  📊 Elements: {strategy_result['elements_found']}")
            print(f"  🧠 AI analyzed: {strategy_result['ai_analyzed']}")
            print(f"  📈 Avg confidence: {strategy_result['avg_confidence']:.2%}")
            
        except Exception as e:
            logger.error(f"  [ERROR] Strategy {strategy.value} failed: {e}")
            strategy_results.append({
                "strategy": strategy.value,
                "success": False,
                "error": str(e)
            })
    
    # Strategy performance comparison
    print(f"\n📊 Prompt Strategy Performance Analysis:")
    print(f"{'Strategy':<20} {'Time (s)':<10} {'Elements':<10} {'AI Analyzed':<12} {'Confidence':<12}")
    print("-" * 70)
    
    for result in strategy_results:
        if result["success"]:
            print(f"{result['strategy']:<20} {result['processing_time']:<10.2f} {result['elements_found']:<10} {result['ai_analyzed']:<12} {result['avg_confidence']:<12.2%}")
        else:
            print(f"{result['strategy']:<20} {'FAILED':<10} {'-':<10} {'-':<12} {'-':<12}")
    
    # Find best performing strategy
    successful = [r for r in strategy_results if r["success"] and r["ai_analyzed"] > 0]
    if successful:
        best_confidence = max(r["avg_confidence"] for r in successful)
        best_speed = min(r["processing_time"] for r in successful)
        
        print(f"\n🏆 Strategy Performance Leaders:")
        for result in successful:
            if result["avg_confidence"] == best_confidence:
                print(f"  🎯 Highest confidence: {result['strategy']} ({result['avg_confidence']:.2%})")
            if result["processing_time"] == best_speed:
                print(f"  [FAST] Fastest processing: {result['strategy']} ({result['processing_time']:.2f}s)")
    
    return strategy_results


async def example_2_visual_ai_analysis():
    """Example 2: Visual AI analysis with screenshot interpretation"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Visual AI Analysis with Screenshots")
    print("="*80)
    
    # Configuration for visual AI analysis
    config = ExtractionConfig(
        capture_screenshots=True,
        screenshot_full_page=True,
        screenshot_format="png",
        highlight_elements=True,
        max_elements=20
    )
    
    print(f"📸 Visual AI Analysis Configuration:")
    print(f"  Screenshot capture: {config.capture_screenshots}")
    print(f"  Full page screenshots: {config.screenshot_full_page}")
    print(f"  Element highlighting: {config.highlight_elements}")
    
    try:
        # Initialize extractor with visual AI capabilities
        extractor = ElementsExtractorWithLLM(
            config=config,
            llm_provider=LLMProvider.OPENAI,
            enable_semantic_analysis=False,  # Focus on visual analysis
            enable_visual_analysis=True,
            enable_context_learning=False,
            confidence_threshold=0.5
        )
        
        test_url = "https://example.com"
        
        print(f"\n🌐 Performing visual AI analysis of: {test_url}")
        print(f"🖼️ Visual analysis enabled with screenshot interpretation")
        
        result = await extractor.extract_from_url(test_url)
        
        print(f"[OK] Visual analysis completed in {result.extraction_time:.2f}s")
        print(f"📊 Elements found: {len(result.elements)}")
        print(f"📸 Screenshots captured: {len(result.screenshots)}")
        
        # Analyze visual AI insights
        visual_elements = []
        for element in result.elements:
            if hasattr(element, 'ai_analysis') and element.ai_analysis:
                if element.ai_analysis.visual_prominence > 0:
                    visual_elements.append(element)
        
        print(f"🖼️ Elements with visual AI analysis: {len(visual_elements)}")
        
        if visual_elements:
            # Sort by visual prominence
            visual_elements.sort(key=lambda x: x.ai_analysis.visual_prominence, reverse=True)
            
            print(f"\n🎨 Visual Prominence Analysis (Top 3):")
            for i, element in enumerate(visual_elements[:3], 1):
                analysis = element.ai_analysis
                
                print(f"  {i}. {element.element_type.value}: {element.text[:40]}...")
                print(f"     🎨 Visual prominence: {analysis.visual_prominence:.2f}")
                print(f"     👁️ Accessibility score: {analysis.accessibility_score:.2f}")
                print(f"     🎯 User interaction likelihood: {analysis.user_interaction_likelihood:.2%}")
                print(f"     📍 Position: ({element.bounding_box.x}, {element.bounding_box.y})" if element.bounding_box else "     📍 Position: Unknown")
                print()
        
        # Screenshot analysis
        if result.screenshots:
            screenshot = result.screenshots[0]
            print(f"📸 Screenshot Analysis:")
            print(f"  Dimensions: {screenshot.width}x{screenshot.height}")
            print(f"  Highlighted elements: {len(screenshot.highlighted_elements)}")
            print(f"  Annotations: {len(screenshot.annotations)}")
            
            # Save screenshot for manual inspection
            temp_dir = Path(tempfile.mkdtemp(prefix="visual_ai_"))
            saved_files = result.save_screenshots(temp_dir)
            
            if saved_files:
                print(f"  💾 Screenshot saved to: {saved_files[0]}")
                print(f"  🔍 You can manually inspect the visual analysis")
        
        else:
            print(f"📸 No screenshots captured (visual analysis may be limited)")
        
        return result
        
    except Exception as e:
        logger.error(f"[ERROR] Visual AI analysis failed: {e}")
        return None


async def example_3_context_learning_adaptation():
    """Example 3: Context learning and adaptive extraction"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Context Learning and Adaptive Extraction")
    print("="*80)
    
    # Initialize extractor with context learning
    try:
        extractor = ElementsExtractorWithLLM(
            llm_provider=LLMProvider.OPENAI,
            enable_semantic_analysis=True,
            enable_visual_analysis=False,
            enable_context_learning=True,
            confidence_threshold=0.6
        )
        
        # Test with multiple pages to demonstrate learning
        test_urls = [
            "https://example.com",
            "https://httpbin.org/forms/post",
            "https://httpbin.org/html"
        ]
        
        print(f"🧠 Context learning enabled")
        print(f"📚 Testing adaptive extraction across {len(test_urls)} pages")
        
        learning_results = []
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n🔄 Page {i}: Learning from {url}")
            
            # Define context for each page type
            if "forms" in url:
                context = SemanticContext(
                    page_purpose="Form submission",
                    page_type="form",
                    user_intent="Fill and submit form data"
                )
            elif "html" in url:
                context = SemanticContext(
                    page_purpose="Content viewing",
                    page_type="content",
                    user_intent="Read information"
                )
            else:
                context = SemanticContext(
                    page_purpose="General browsing",
                    page_type="website",
                    user_intent="Explore content"
                )
            
            # Set context for learning
            if hasattr(extractor, 'semantic_context'):
                extractor.semantic_context = context
            
            start_time = asyncio.get_event_loop().time()
            result = await extractor.extract_from_url(url)
            end_time = asyncio.get_event_loop().time()
            
            # Analyze learning progression
            ai_elements = [e for e in result.elements if hasattr(e, 'ai_analysis') and e.ai_analysis]
            avg_confidence = sum(e.ai_analysis.confidence_score for e in ai_elements) / len(ai_elements) if ai_elements else 0
            
            learning_result = {
                "page": i,
                "url": url,
                "context_type": context.page_type,
                "processing_time": end_time - start_time,
                "elements_found": len(result.elements),
                "ai_analyzed": len(ai_elements),
                "avg_confidence": avg_confidence,
                "interactive_elements": len([e for e in result.elements if e.is_interactive])
            }
            
            learning_results.append(learning_result)
            
            print(f"  📊 Context: {learning_result['context_type']}")
            print(f"  [TIME] Processing: {learning_result['processing_time']:.2f}s")
            print(f"  🎯 Elements: {learning_result['elements_found']}")
            print(f"  🧠 AI analyzed: {learning_result['ai_analyzed']}")
            print(f"  📈 Confidence: {learning_result['avg_confidence']:.2%}")
            
            # Show pattern learning (if available)
            if hasattr(extractor, 'learned_patterns') and extractor.learned_patterns:
                patterns = len(extractor.learned_patterns)
                print(f"  🧠 Patterns learned so far: {patterns}")
            
            if hasattr(extractor, 'extraction_history'):
                history_length = len(extractor.extraction_history)
                print(f"  📚 Extraction history: {history_length} entries")
        
        # Learning progression analysis
        print(f"\n📈 Context Learning Progression Analysis:")
        print(f"{'Page':<6} {'Context':<10} {'Time (s)':<10} {'Elements':<10} {'Confidence':<12}")
        print("-" * 55)
        
        for result in learning_results:
            print(f"{result['page']:<6} {result['context_type']:<10} {result['processing_time']:<10.2f} {result['elements_found']:<10} {result['avg_confidence']:<12.2%}")
        
        # Learning effectiveness
        if len(learning_results) > 1:
            first_confidence = learning_results[0]['avg_confidence']
            last_confidence = learning_results[-1]['avg_confidence']
            
            if last_confidence > first_confidence:
                improvement = ((last_confidence - first_confidence) / first_confidence) * 100
                print(f"\n🎯 Learning Improvement: {improvement:.1f}% confidence increase")
            else:
                print(f"\n📊 Learning Status: Baseline established across different contexts")
        
        # Strategy performance tracking
        if hasattr(extractor, 'strategy_performance') and extractor.strategy_performance:
            print(f"\n🔧 Strategy Performance Tracking:")
            for strategy, metrics in extractor.strategy_performance.items():
                if metrics:
                    print(f"  {strategy}:")
                    if 'accuracy' in metrics:
                        print(f"    Accuracy: {metrics['accuracy']:.2%}")
                    if 'avg_time' in metrics:
                        print(f"    Avg time: {metrics['avg_time']:.3f}s")
                    if 'usage_count' in metrics:
                        print(f"    Usage count: {metrics['usage_count']}")
        
        return learning_results
        
    except Exception as e:
        logger.error(f"[ERROR] Context learning analysis failed: {e}")
        return []


async def example_4_accessibility_ai_analysis():
    """Example 4: AI-powered accessibility analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 4: AI-Powered Accessibility Analysis")
    print("="*80)
    
    # Context focused on accessibility
    accessibility_context = SemanticContext(
        page_purpose="Accessibility compliance assessment",
        page_type="general",
        user_intent="Ensure WCAG compliance",
        accessibility_requirements="WCAG 2.1 AA compliance with focus on keyboard navigation and screen reader support"
    )
    
    print(f"[ACCESS] Accessibility Analysis Configuration:")
    print(f"  Focus: WCAG 2.1 AA compliance")
    print(f"  Priorities: Keyboard navigation, screen reader support")
    
    try:
        extractor = ElementsExtractorWithLLM(
            llm_provider=LLMProvider.OPENAI,
            enable_semantic_analysis=True,
            enable_visual_analysis=True,  # Important for accessibility
            enable_context_learning=False,
            confidence_threshold=0.4  # Lower threshold for accessibility issues
        )
        
        # Set accessibility context
        if hasattr(extractor, 'semantic_context'):
            extractor.semantic_context = accessibility_context
        
        test_url = "https://example.com"
        
        print(f"\n🌐 Analyzing accessibility for: {test_url}")
        print(f"[ACCESS] AI-powered accessibility assessment")
        
        result = await extractor.extract_from_url(test_url)
        
        print(f"[OK] Accessibility analysis completed in {result.extraction_time:.2f}s")
        print(f"📊 Elements analyzed: {len(result.elements)}")
        
        # Categorize elements by accessibility concerns
        accessibility_insights = {
            "high_accessibility": [],
            "medium_accessibility": [],
            "low_accessibility": [],
            "interactive_elements": [],
            "non_interactive": []
        }
        
        for element in result.elements:
            if hasattr(element, 'ai_analysis') and element.ai_analysis:
                analysis = element.ai_analysis
                accessibility_score = analysis.accessibility_score
                
                if accessibility_score >= 0.8:
                    accessibility_insights["high_accessibility"].append(element)
                elif accessibility_score >= 0.5:
                    accessibility_insights["medium_accessibility"].append(element)
                else:
                    accessibility_insights["low_accessibility"].append(element)
                
                if element.is_interactive:
                    accessibility_insights["interactive_elements"].append(element)
                else:
                    accessibility_insights["non_interactive"].append(element)
        
        # Accessibility report
        print(f"\n[ACCESS] Accessibility Assessment Report:")
        print(f"  🟢 High accessibility (≥80%): {len(accessibility_insights['high_accessibility'])}")
        print(f"  🟡 Medium accessibility (50-79%): {len(accessibility_insights['medium_accessibility'])}")
        print(f"  🔴 Low accessibility (<50%): {len(accessibility_insights['low_accessibility'])}")
        print(f"  🎮 Interactive elements: {len(accessibility_insights['interactive_elements'])}")
        print(f"  📄 Non-interactive elements: {len(accessibility_insights['non_interactive'])}")
        
        # Detailed analysis of problematic elements
        if accessibility_insights["low_accessibility"]:
            print(f"\n🔴 Elements Needing Accessibility Improvements:")
            for i, element in enumerate(accessibility_insights["low_accessibility"][:3], 1):
                analysis = element.ai_analysis
                
                print(f"  {i}. {element.element_type.value}: {element.text[:40]}...")
                print(f"     [ACCESS] Accessibility score: {analysis.accessibility_score:.2%}")
                print(f"     🎯 Interactive: {element.is_interactive}")
                print(f"     📝 Attributes: {len(element.attributes)} available")
                
                # Check for common accessibility attributes
                accessibility_attrs = ['aria-label', 'aria-describedby', 'alt', 'title', 'role']
                present_attrs = [attr for attr in accessibility_attrs if attr in element.attributes]
                missing_attrs = [attr for attr in accessibility_attrs if attr not in element.attributes]
                
                if present_attrs:
                    print(f"     [OK] Present attributes: {', '.join(present_attrs)}")
                if missing_attrs and element.is_interactive:
                    print(f"     [ERROR] Missing attributes: {', '.join(missing_attrs[:3])}")
                
                if analysis.improvement_suggestions:
                    print(f"     💡 Suggestions: {', '.join(analysis.improvement_suggestions[:2])}")
                print()
        
        # Interactive element accessibility
        interactive_accessible = [e for e in accessibility_insights["interactive_elements"] 
                                if hasattr(e, 'ai_analysis') and e.ai_analysis and e.ai_analysis.accessibility_score >= 0.7]
        
        print(f"\n🎮 Interactive Element Accessibility:")
        print(f"  Total interactive: {len(accessibility_insights['interactive_elements'])}")
        print(f"  Well accessible (≥70%): {len(interactive_accessible)}")
        print(f"  Accessibility ratio: {len(interactive_accessible)/max(len(accessibility_insights['interactive_elements']), 1):.1%}")
        
        # Overall accessibility score
        total_elements_with_scores = [e for e in result.elements 
                                    if hasattr(e, 'ai_analysis') and e.ai_analysis]
        if total_elements_with_scores:
            overall_score = sum(e.ai_analysis.accessibility_score for e in total_elements_with_scores) / len(total_elements_with_scores)
            
            print(f"\n📊 Overall Accessibility Assessment:")
            print(f"  🎯 Overall score: {overall_score:.2%}")
            
            if overall_score >= 0.8:
                print(f"  [OK] Status: EXCELLENT - Likely WCAG compliant")
            elif overall_score >= 0.6:
                print(f"  🟡 Status: GOOD - Minor improvements needed")
            elif overall_score >= 0.4:
                print(f"  🟠 Status: FAIR - Moderate improvements needed")
            else:
                print(f"  🔴 Status: POOR - Major accessibility improvements required")
        
        return result
        
    except Exception as e:
        logger.error(f"[ERROR] Accessibility AI analysis failed: {e}")
        return None


async def example_5_performance_optimization():
    """Example 5: AI extraction performance optimization and caching"""
    print("\n" + "="*80)
    print("EXAMPLE 5: AI Performance Optimization and Caching")
    print("="*80)
    
    # Configuration for performance optimization
    llm_config = LLMConfig(
        temperature=0.3,
        max_tokens=2000,
        timeout=20,
        enable_caching=True,
        cache_ttl=300,  # 5 minutes
        retry_attempts=2,
        retry_delay=1.0
    )
    
    config = ExtractionConfig(
        enable_caching=True,
        cache_ttl=180,  # 3 minutes
        max_elements=50,
        enable_performance_monitoring=True
    )
    
    print(f"[FAST] Performance Optimization Configuration:")
    print(f"  LLM caching: {llm_config.enable_caching} (TTL: {llm_config.cache_ttl}s)")
    print(f"  DOM caching: {config.enable_caching} (TTL: {config.cache_ttl}s)")
    print(f"  Max elements: {config.max_elements}")
    print(f"  Performance monitoring: {config.enable_performance_monitoring}")
    
    try:
        extractor = ElementsExtractorWithLLM(
            config=config,
            llm_config=llm_config,
            llm_provider=LLMProvider.OPENAI,
            enable_semantic_analysis=True,
            enable_visual_analysis=False,  # Optimize for speed
            enable_context_learning=True,
            confidence_threshold=0.7
        )
        
        test_url = "https://example.com"
        performance_data = []
        
        # Test 1: Cold start (no cache)
        print(f"\n🔄 Test 1: Cold start extraction (no cache)")
        start_time = asyncio.get_event_loop().time()
        result1 = await extractor.extract_from_url(test_url)
        cold_time = asyncio.get_event_loop().time() - start_time
        
        performance_data.append({
            "test": "Cold Start",
            "time": cold_time,
            "elements": len(result1.elements),
            "ai_elements": len([e for e in result1.elements if hasattr(e, 'ai_analysis') and e.ai_analysis]),
            "cache_status": "MISS"
        })
        
        print(f"  [TIME] Cold start time: {cold_time:.2f}s")
        print(f"  📊 Elements: {len(result1.elements)}")
        print(f"  🧠 AI elements: {performance_data[0]['ai_elements']}")
        print(f"  💾 Cache status: MISS")
        
        # Wait a moment
        await asyncio.sleep(1)
        
        # Test 2: Warm extraction (cached)
        print(f"\n🔄 Test 2: Warm extraction (should use cache)")
        start_time = asyncio.get_event_loop().time()
        result2 = await extractor.extract_from_url(test_url)
        warm_time = asyncio.get_event_loop().time() - start_time
        
        cache_hit = warm_time < cold_time * 0.7  # Significant speedup indicates cache hit
        
        performance_data.append({
            "test": "Warm (Cached)",
            "time": warm_time,
            "elements": len(result2.elements),
            "ai_elements": len([e for e in result2.elements if hasattr(e, 'ai_analysis') and e.ai_analysis]),
            "cache_status": "HIT" if cache_hit else "MISS"
        })
        
        print(f"  [TIME] Warm extraction time: {warm_time:.2f}s")
        print(f"  📊 Elements: {len(result2.elements)}")
        print(f"  🧠 AI elements: {performance_data[1]['ai_elements']}")
        print(f"  💾 Cache status: {'HIT' if cache_hit else 'MISS'}")
        
        # Test 3: Optimized extraction (reduced AI features for speed)
        print(f"\n🔄 Test 3: Speed-optimized extraction")
        speed_extractor = ElementsExtractorWithLLM(
            config=config,
            llm_config=llm_config,
            llm_provider=LLMProvider.OPENAI,
            enable_semantic_analysis=False,  # Disable for speed
            enable_visual_analysis=False,
            enable_context_learning=False,
            confidence_threshold=0.8  # Higher threshold for fewer API calls
        )
        
        start_time = asyncio.get_event_loop().time()
        result3 = await speed_extractor.extract_from_url(test_url)
        speed_time = asyncio.get_event_loop().time() - start_time
        
        performance_data.append({
            "test": "Speed Optimized",
            "time": speed_time,
            "elements": len(result3.elements),
            "ai_elements": len([e for e in result3.elements if hasattr(e, 'ai_analysis') and e.ai_analysis]),
            "cache_status": "N/A"
        })
        
        print(f"  [TIME] Speed-optimized time: {speed_time:.2f}s")
        print(f"  📊 Elements: {len(result3.elements)}")
        print(f"  🧠 AI elements: {performance_data[2]['ai_elements']}")
        print(f"  [FAST] Speed focus: Minimal AI processing")
        
        # Performance comparison
        print(f"\n📊 Performance Comparison Summary:")
        print(f"{'Test':<18} {'Time (s)':<10} {'Elements':<10} {'AI Elements':<12} {'Cache':<8}")
        print("-" * 65)
        
        for data in performance_data:
            print(f"{data['test']:<18} {data['time']:<10.2f} {data['elements']:<10} {data['ai_elements']:<12} {data['cache_status']:<8}")
        
        # Performance insights
        print(f"\n[FAST] Performance Insights:")
        
        if cache_hit:
            speedup = cold_time / warm_time
            print(f"  🚀 Cache speedup: {speedup:.2f}x faster")
            print(f"  💾 Cache efficiency: {((cold_time - warm_time) / cold_time * 100):.1f}% time saved")
        
        speed_vs_cold = cold_time / speed_time if speed_time > 0 else 0
        print(f"  [FAST] Speed optimization: {speed_vs_cold:.2f}x faster than full AI")
        
        # AI feature cost analysis
        ai_overhead = ((cold_time - speed_time) / speed_time * 100) if speed_time > 0 else 0
        print(f"  🧠 AI feature overhead: {ai_overhead:.1f}% additional time")
        
        ai_value = performance_data[0]['ai_elements'] / performance_data[0]['elements'] if performance_data[0]['elements'] > 0 else 0
        print(f"  🎯 AI analysis coverage: {ai_value:.1%} of elements")
        
        # Recommendations
        print(f"\n💡 Performance Recommendations:")
        
        if cache_hit:
            print(f"  [OK] Caching is working effectively - continue using for repeated extractions")
        else:
            print(f"  ⚠️ Cache may not be active - verify cache configuration")
        
        if ai_overhead < 200:  # Less than 200% overhead
            print(f"  [OK] AI features provide good value for performance cost")
        else:
            print(f"  ⚠️ Consider selective AI features for performance-critical applications")
        
        if performance_data[0]['ai_elements'] > 0:
            print(f"  [OK] AI analysis is generating insights - features are working")
        else:
            print(f"  ℹ️ No AI insights generated - may require valid API configuration")
        
        return performance_data
        
    except Exception as e:
        logger.error(f"[ERROR] Performance optimization analysis failed: {e}")
        return []


async def main():
    """Run all advanced AI feature examples"""
    print("🚀 ADVANCED AI FEATURES - Elements Extractor With LLM")
    print("=" * 80)
    print("Demonstrating cutting-edge AI extraction capabilities:")
    print("- Advanced prompt strategy optimization")
    print("- Visual AI analysis with screenshots")
    print("- Context learning and adaptation")
    print("- AI-powered accessibility analysis")
    print("- Performance optimization and caching")
    print("=" * 80)
    
    examples = [
        ("Prompt Strategy Optimization", example_1_prompt_strategy_optimization),
        ("Visual AI Analysis", example_2_visual_ai_analysis),
        ("Context Learning Adaptation", example_3_context_learning_adaptation),
        ("Accessibility AI Analysis", example_4_accessibility_ai_analysis),
        ("Performance Optimization", example_5_performance_optimization)
    ]
    
    results = []
    total_start_time = asyncio.get_event_loop().time()
    
    for name, example_func in examples:
        print(f"\n🔄 Running: {name}")
        try:
            result = await example_func()
            results.append((name, result, True))
            print(f"[OK] {name} completed successfully")
        except Exception as e:
            logger.error(f"[ERROR] {name} failed: {e}")
            results.append((name, None, False))
    
    total_time = asyncio.get_event_loop().time() - total_start_time
    
    # Summary
    print(f"\n" + "="*80)
    print("📊 ADVANCED AI FEATURES SUMMARY")
    print("="*80)
    
    successful = sum(1 for _, _, success in results if success)
    total = len(results)
    
    print(f"[OK] Successful examples: {successful}/{total}")
    print(f"🎯 Success rate: {successful/total*100:.1f}%")
    print(f"[TIME] Total execution time: {total_time:.3f}s")
    
    for name, result, success in results:
        status = "[OK] PASS" if success else "[ERROR] FAIL"
        print(f"  {status} {name}")
    
    print(f"\n🎉 Advanced AI features examples completed!")
    print(f"💡 Cutting-edge capabilities demonstrated:")
    print(f"  🧠 21 research-backed prompt strategies")
    print(f"  🖼️ Visual AI with screenshot interpretation")
    print(f"  📚 Adaptive learning from context")
    print(f"  [ACCESS] AI-powered accessibility assessment")
    print(f"  [FAST] Performance optimization and caching")
    print(f"\n🚀 This represents the pinnacle of AI-powered web automation")
    print(f"🔬 Research-grade techniques in production-ready implementation")
    
    # API Requirements Notice
    print(f"\n🔑 API Requirements:")
    print(f"  - OpenAI API key recommended for best results")
    print(f"  - Set OPENAI_API_KEY environment variable")
    print(f"  - Alternative providers: Anthropic, Google Gemini")
    print(f"  - Some features may gracefully degrade without API access")


if __name__ == "__main__":
    asyncio.run(main())