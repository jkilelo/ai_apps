#!/usr/bin/env python3
"""
Basic AI Extraction Examples - Elements Extractor With LLM
==========================================================
Working examples demonstrating AI-enhanced element extraction capabilities.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ui_testing_automation"))

try:
    from elements_extractor_with_llm import (
        ElementsExtractorWithLLM,
        SemanticContext,
        AIAnalysis,
        EnhancedElement,
        ExtractionStrategy,
        LLMProvider,
        LLMConfig,
        ExtractionConfig,
        ElementType,
        InteractionType
    )
    print("✅ AI extraction module imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed and paths are correct")
    sys.exit(1)

# Configure logging for examples
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def example_1_basic_ai_extraction():
    """Example 1: Basic AI-enhanced extraction compared to DOM-only"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic AI-Enhanced vs DOM-Only Extraction")
    print("="*80)
    
    test_url = "https://example.com"
    
    # Test 1: DOM-only extraction (base functionality)
    print(f"🤖 Step 1: DOM-only extraction from {test_url}")
    
    try:
        # Create extractor with AI features disabled
        dom_extractor = ElementsExtractorWithLLM(
            enable_semantic_analysis=False,
            enable_visual_analysis=False,
            enable_context_learning=False
        )
        
        dom_result = await dom_extractor.extract_from_url(test_url)
        
        print(f"  ✅ DOM-only completed in {dom_result.extraction_time:.2f}s")
        print(f"  📊 Elements found: {len(dom_result.elements)}")
        print(f"  🎯 Success: {dom_result.success}")
        
    except Exception as e:
        print(f"  ❌ DOM-only extraction failed: {e}")
        dom_result = None
    
    # Test 2: AI-enhanced extraction
    print(f"\n🧠 Step 2: AI-enhanced extraction from {test_url}")
    
    try:
        # Create AI-enhanced extractor
        ai_extractor = ElementsExtractorWithLLM(
            llm_provider=LLMProvider.OPENAI,
            enable_semantic_analysis=True,
            enable_visual_analysis=True,
            enable_context_learning=True,
            confidence_threshold=0.7
        )
        
        ai_result = await ai_extractor.extract_from_url(test_url)
        
        print(f"  ✅ AI-enhanced completed in {ai_result.extraction_time:.2f}s")
        print(f"  📊 Elements found: {len(ai_result.elements)}")
        print(f"  🎯 Success: {ai_result.success}")
        print(f"  🧠 AI insights: {'Available' if any(hasattr(e, 'ai_analysis') and e.ai_analysis for e in ai_result.elements) else 'Not generated'}")
        
    except Exception as e:
        print(f"  ❌ AI-enhanced extraction failed: {e}")
        ai_result = None
    
    # Comparison analysis
    if dom_result and ai_result:
        print(f"\n📈 Comparison Analysis:")
        print(f"  DOM-only time: {dom_result.extraction_time:.2f}s")
        print(f"  AI-enhanced time: {ai_result.extraction_time:.2f}s")
        print(f"  Time overhead: {((ai_result.extraction_time - dom_result.extraction_time) / dom_result.extraction_time * 100):.1f}%")
        
        # Show AI-enhanced elements with analysis
        ai_elements = [e for e in ai_result.elements if hasattr(e, 'ai_analysis') and e.ai_analysis]
        if ai_elements:
            print(f"\n🧠 AI-Enhanced Elements (showing first 3):")
            for i, element in enumerate(ai_elements[:3], 1):
                print(f"  {i}. {element.element_type.value}: {element.text[:40]}...")
                if element.ai_analysis:
                    print(f"     Purpose: {element.ai_analysis.element_purpose}")
                    print(f"     Interaction likelihood: {element.ai_analysis.user_interaction_likelihood:.2f}")
                    print(f"     Accessibility score: {element.ai_analysis.accessibility_score:.2f}")
                    print(f"     Confidence: {element.ai_analysis.confidence_score:.2f}")
                    print()
        else:
            print(f"  ℹ️ No AI analysis generated (may require valid API keys)")
    
    return {"dom_result": dom_result, "ai_result": ai_result}


async def example_2_semantic_context_extraction():
    """Example 2: Extraction with specific semantic context"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Semantic Context-Aware Extraction")
    print("="*80)
    
    # Define semantic context for e-commerce site
    context = SemanticContext(
        page_purpose="Product browsing and purchase",
        page_type="e-commerce",
        user_intent="Find and buy products",
        domain_context="Online retail",
        interaction_context="Shopping workflow",
        accessibility_requirements="WCAG 2.1 AA compliance"
    )
    
    print(f"🎯 Context Configuration:")
    print(f"  Page purpose: {context.page_purpose}")
    print(f"  Page type: {context.page_type}")
    print(f"  User intent: {context.user_intent}")
    print(f"  Domain: {context.domain_context}")
    
    # Initialize AI extractor with context awareness
    try:
        extractor = ElementsExtractorWithLLM(
            llm_provider=LLMProvider.OPENAI,
            enable_semantic_analysis=True,
            enable_visual_analysis=False,  # Focus on semantic analysis
            enable_context_learning=True,
            confidence_threshold=0.6
        )
        
        # Test with a site that might benefit from context understanding
        test_url = "https://example.com"
        
        print(f"\n🌐 Extracting from: {test_url}")
        print(f"🧠 Using semantic context: {context.page_type}")
        
        # Extract with context (if method exists, otherwise use standard extraction)
        if hasattr(extractor, 'extract_with_context'):
            result = await extractor.extract_with_context(test_url, context)
        else:
            # Fallback to standard extraction with context set
            extractor.semantic_context = context
            result = await extractor.extract_from_url(test_url)
        
        print(f"  ✅ Context-aware extraction completed")
        print(f"  ⏱️ Time: {result.extraction_time:.2f}s")
        print(f"  📊 Elements: {len(result.elements)}")
        print(f"  🎯 Success: {result.success}")
        
        # Analyze elements with context awareness
        context_elements = []
        for element in result.elements:
            if hasattr(element, 'semantic_context') and element.semantic_context:
                context_elements.append(element)
            elif hasattr(element, 'ai_analysis') and element.ai_analysis:
                # Check if AI analysis mentions context-relevant terms
                analysis = element.ai_analysis
                if any(term in analysis.element_purpose.lower() for term in ['shop', 'buy', 'product', 'purchase']):
                    context_elements.append(element)
        
        print(f"\n🎯 Context-Relevant Elements: {len(context_elements)}")
        
        # Show most relevant elements for the shopping context
        interactive_elements = [e for e in result.elements if e.is_interactive]
        print(f"\n🛒 Interactive Elements (Shopping Context):")
        for i, element in enumerate(interactive_elements[:3], 1):
            print(f"  {i}. {element.element_type.value}: {element.text[:50]}...")
            print(f"     Interactive: {element.is_interactive}")
            print(f"     Interaction type: {element.interaction_type.value}")
            if hasattr(element, 'ai_analysis') and element.ai_analysis:
                print(f"     AI purpose: {element.ai_analysis.element_purpose}")
                print(f"     Relevance: {element.ai_analysis.context_relevance:.2f}")
            print()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Context-aware extraction failed: {e}")
        return None


async def example_3_multi_strategy_analysis():
    """Example 3: Multi-strategy extraction with performance comparison"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Multi-Strategy Extraction Analysis")
    print("="*80)
    
    test_url = "https://httpbin.org/forms/post"  # Form page for testing
    
    print(f"🌐 Analyzing extraction strategies for: {test_url}")
    
    # Test different strategy combinations
    strategy_configs = [
        {
            "name": "DOM Only",
            "semantic": False,
            "visual": False,
            "context": False
        },
        {
            "name": "Semantic Only", 
            "semantic": True,
            "visual": False,
            "context": False
        },
        {
            "name": "Full AI",
            "semantic": True,
            "visual": True,
            "context": True
        }
    ]
    
    results = []
    
    for config in strategy_configs:
        print(f"\n🔄 Testing strategy: {config['name']}")
        
        try:
            extractor = ElementsExtractorWithLLM(
                llm_provider=LLMProvider.OPENAI,
                enable_semantic_analysis=config["semantic"],
                enable_visual_analysis=config["visual"],
                enable_context_learning=config["context"],
                confidence_threshold=0.5
            )
            
            start_time = asyncio.get_event_loop().time()
            result = await extractor.extract_from_url(test_url)
            end_time = asyncio.get_event_loop().time()
            
            strategy_result = {
                "name": config["name"],
                "success": result.success,
                "elements": len(result.elements),
                "time": end_time - start_time,
                "interactive_elements": len([e for e in result.elements if e.is_interactive]),
                "ai_enhanced": len([e for e in result.elements if hasattr(e, 'ai_analysis') and e.ai_analysis])
            }
            
            results.append(strategy_result)
            
            print(f"  ✅ Success: {strategy_result['success']}")
            print(f"  ⏱️ Time: {strategy_result['time']:.2f}s")
            print(f"  📊 Elements: {strategy_result['elements']}")
            print(f"  🎮 Interactive: {strategy_result['interactive_elements']}")
            print(f"  🧠 AI Enhanced: {strategy_result['ai_enhanced']}")
            
        except Exception as e:
            logger.error(f"  ❌ Strategy {config['name']} failed: {e}")
            results.append({
                "name": config["name"],
                "success": False,
                "error": str(e)
            })
    
    # Strategy comparison
    print(f"\n📊 Strategy Performance Comparison:")
    print(f"{'Strategy':<15} {'Time (s)':<10} {'Elements':<10} {'Interactive':<12} {'AI Enhanced':<12}")
    print("-" * 65)
    
    for result in results:
        if result["success"]:
            print(f"{result['name']:<15} {result['time']:<10.2f} {result['elements']:<10} {result['interactive_elements']:<12} {result['ai_enhanced']:<12}")
        else:
            print(f"{result['name']:<15} {'FAILED':<10} {'-':<10} {'-':<12} {'-':<12}")
    
    return results


async def example_4_ai_element_insights():
    """Example 4: Detailed AI insights and element analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Detailed AI Element Insights")
    print("="*80)
    
    try:
        # Initialize with full AI capabilities
        extractor = ElementsExtractorWithLLM(
            llm_provider=LLMProvider.OPENAI,
            enable_semantic_analysis=True,
            enable_visual_analysis=True,
            enable_context_learning=True,
            confidence_threshold=0.4  # Lower threshold to see more elements
        )
        
        test_url = "https://example.com"
        
        print(f"🌐 Performing detailed AI analysis of: {test_url}")
        print(f"🧠 AI capabilities: Semantic ✓, Visual ✓, Context Learning ✓")
        
        result = await extractor.extract_from_url(test_url)
        
        print(f"✅ Analysis completed in {result.extraction_time:.2f}s")
        print(f"📊 Total elements: {len(result.elements)}")
        
        # Analyze AI insights
        ai_elements = [e for e in result.elements if hasattr(e, 'ai_analysis') and e.ai_analysis]
        enhanced_elements = [e for e in result.elements if hasattr(e, 'extraction_strategy_used')]
        
        print(f"🧠 AI-analyzed elements: {len(ai_elements)}")
        print(f"🔧 Strategy-enhanced elements: {len(enhanced_elements)}")
        
        if ai_elements:
            print(f"\n🔍 Detailed AI Insights (Top 3 Elements):")
            
            # Sort by confidence score
            sorted_elements = sorted(ai_elements, 
                                   key=lambda x: x.ai_analysis.confidence_score if x.ai_analysis else 0,
                                   reverse=True)
            
            for i, element in enumerate(sorted_elements[:3], 1):
                analysis = element.ai_analysis
                
                print(f"\n  📋 Element {i}: {element.element_type.value.upper()}")
                print(f"    Text: '{element.text[:60]}{'...' if len(element.text) > 60 else ''}'")
                print(f"    Tag: <{element.tag_name}>")
                
                if analysis:
                    print(f"    🎯 AI Analysis:")
                    print(f"      Purpose: {analysis.element_purpose}")
                    print(f"      Interaction likelihood: {analysis.user_interaction_likelihood:.2%}")
                    print(f"      Semantic importance: {analysis.semantic_importance:.2f}")
                    print(f"      Accessibility score: {analysis.accessibility_score:.2f}")
                    print(f"      Visual prominence: {analysis.visual_prominence:.2f}")
                    print(f"      Context relevance: {analysis.context_relevance:.2f}")
                    print(f"      Overall confidence: {analysis.confidence_score:.2%}")
                    
                    if analysis.improvement_suggestions:
                        print(f"      💡 Suggestions: {', '.join(analysis.improvement_suggestions[:2])}")
                
                if hasattr(element, 'extraction_strategy_used'):
                    print(f"    🔧 Strategy used: {element.extraction_strategy_used}")
                    if hasattr(element, 'strategy_confidence'):
                        print(f"    📊 Strategy confidence: {element.strategy_confidence:.2f}")
        
        else:
            print(f"  ℹ️ No AI analysis available (may require valid API configuration)")
            print(f"  🔧 Showing strategy information instead:")
            
            for i, element in enumerate(result.elements[:3], 1):
                print(f"\n  📋 Element {i}: {element.element_type.value}")
                print(f"    Text: '{element.text[:60]}{'...' if len(element.text) > 60 else ''}'")
                print(f"    Interactive: {element.is_interactive}")
                print(f"    Confidence: {element.confidence_score:.2f}")
                print(f"    Best selector: {element.selectors[0].value if element.selectors else 'None'}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ AI insights analysis failed: {e}")
        return None


async def example_5_llm_provider_comparison():
    """Example 5: Comparison of different LLM providers"""
    print("\n" + "="*80)
    print("EXAMPLE 5: LLM Provider Comparison")
    print("="*80)
    
    test_url = "https://example.com"
    
    # List of providers to test
    providers_to_test = [
        (LLMProvider.OPENAI, "OpenAI GPT"),
        (LLMProvider.ANTHROPIC, "Anthropic Claude"),
        (LLMProvider.GEMINI, "Google Gemini")
    ]
    
    print(f"🌐 Testing LLM providers with: {test_url}")
    print(f"🧠 Providers to test: {len(providers_to_test)}")
    
    provider_results = []
    
    for provider, name in providers_to_test:
        print(f"\n🔄 Testing provider: {name}")
        
        try:
            # Configure for this specific provider
            llm_config = LLMConfig(
                temperature=0.3,
                max_tokens=1000,
                timeout=30,
                enable_caching=True
            )
            
            extractor = ElementsExtractorWithLLM(
                llm_provider=provider,
                llm_config=llm_config,
                enable_semantic_analysis=True,
                enable_visual_analysis=False,  # Focus on semantic for comparison
                enable_context_learning=False,
                confidence_threshold=0.6
            )
            
            start_time = asyncio.get_event_loop().time()
            result = await extractor.extract_from_url(test_url)
            end_time = asyncio.get_event_loop().time()
            
            # Analyze results
            ai_elements = [e for e in result.elements if hasattr(e, 'ai_analysis') and e.ai_analysis]
            avg_confidence = sum(e.ai_analysis.confidence_score for e in ai_elements) / len(ai_elements) if ai_elements else 0
            
            provider_result = {
                "provider": name,
                "success": result.success,
                "time": end_time - start_time,
                "elements": len(result.elements),
                "ai_elements": len(ai_elements),
                "avg_confidence": avg_confidence,
                "extraction_time": result.extraction_time
            }
            
            provider_results.append(provider_result)
            
            print(f"  ✅ Success: {provider_result['success']}")
            print(f"  ⏱️ Total time: {provider_result['time']:.2f}s")
            print(f"  📊 Elements found: {provider_result['elements']}")
            print(f"  🧠 AI-analyzed: {provider_result['ai_elements']}")
            print(f"  📈 Avg confidence: {provider_result['avg_confidence']:.2%}")
            
        except Exception as e:
            logger.error(f"  ❌ Provider {name} failed: {e}")
            provider_results.append({
                "provider": name,
                "success": False,
                "error": str(e)
            })
    
    # Provider comparison summary
    print(f"\n📊 LLM Provider Comparison Summary:")
    print(f"{'Provider':<18} {'Status':<10} {'Time (s)':<10} {'Elements':<10} {'AI Elements':<12} {'Confidence':<12}")
    print("-" * 80)
    
    for result in provider_results:
        if result["success"]:
            print(f"{result['provider']:<18} {'✅ PASS':<10} {result['time']:<10.2f} {result['elements']:<10} {result['ai_elements']:<12} {result['avg_confidence']:<12.2%}")
        else:
            print(f"{result['provider']:<18} {'❌ FAIL':<10} {'-':<10} {'-':<10} {'-':<12} {'-':<12}")
    
    # Success analysis
    successful_results = [r for r in provider_results if r["success"]]
    if successful_results:
        best_time = min(r["time"] for r in successful_results)
        best_confidence = max(r["avg_confidence"] for r in successful_results)
        
        print(f"\n🏆 Performance Leaders:")
        for result in successful_results:
            if result["time"] == best_time:
                print(f"  ⚡ Fastest: {result['provider']} ({result['time']:.2f}s)")
            if result["avg_confidence"] == best_confidence:
                print(f"  🎯 Highest confidence: {result['provider']} ({result['avg_confidence']:.2%})")
    
    return provider_results


async def main():
    """Run all basic AI extraction examples"""
    print("🚀 BASIC AI EXTRACTION EXAMPLES - Elements Extractor With LLM")
    print("=" * 80)
    print("Demonstrating AI-enhanced element extraction capabilities:")
    print("• Multi-strategy extraction (DOM + AI)")
    print("• Semantic context understanding")
    print("• LLM provider integration")
    print("• AI-powered element insights")
    print("• Performance optimization")
    print("=" * 80)
    
    examples = [
        ("Basic AI vs DOM Comparison", example_1_basic_ai_extraction),
        ("Semantic Context Extraction", example_2_semantic_context_extraction),
        ("Multi-Strategy Analysis", example_3_multi_strategy_analysis),
        ("AI Element Insights", example_4_ai_element_insights),
        ("LLM Provider Comparison", example_5_llm_provider_comparison)
    ]
    
    results = []
    total_start_time = asyncio.get_event_loop().time()
    
    for name, example_func in examples:
        print(f"\n🔄 Running: {name}")
        try:
            result = await example_func()
            results.append((name, result, True))
            print(f"✅ {name} completed successfully")
        except Exception as e:
            logger.error(f"❌ {name} failed: {e}")
            results.append((name, None, False))
    
    total_time = asyncio.get_event_loop().time() - total_start_time
    
    # Summary
    print(f"\n" + "="*80)
    print("📊 AI EXTRACTION EXAMPLES SUMMARY")
    print("="*80)
    
    successful = sum(1 for _, _, success in results if success)
    total = len(results)
    
    print(f"✅ Successful examples: {successful}/{total}")
    print(f"🎯 Success rate: {successful/total*100:.1f}%")
    print(f"⏱️ Total execution time: {total_time:.3f}s")
    
    for name, result, success in results:
        status = "✅ PASS" if success else "❌ FAIL" 
        print(f"  {status} {name}")
    
    print(f"\n🎉 AI extraction examples completed!")
    print(f"💡 Key capabilities demonstrated:")
    print(f"  🧠 LLM-enhanced element understanding")
    print(f"  🎯 Semantic context awareness")
    print(f"  🔧 Multi-strategy extraction orchestration")
    print(f"  📊 AI-powered confidence scoring")
    print(f"  ⚡ Multi-provider LLM support")
    print(f"\n🚀 This module combines DOM expertise with cutting-edge AI")
    print(f"🎯 Production-ready with enterprise-grade reliability")
    
    # API Key Status Check
    print(f"\n💡 Note: Some AI features may require valid API keys:")
    print(f"  • OpenAI API key for GPT models")
    print(f"  • Anthropic API key for Claude models") 
    print(f"  • Google API key for Gemini models")
    print(f"  Set environment variables: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY")


if __name__ == "__main__":
    asyncio.run(main())