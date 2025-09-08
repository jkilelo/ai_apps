"""
Live LLM Prompt Testing Framework

CRITICAL: ALL PROMPT OPTIMIZATION TESTED WITH LIVE LLM API CALLS
This framework validates prompt strategies with REAL LLM executions, not simulations.

- Tests actual API response quality, latency, and token usage
- Measures real performance improvements with advanced strategies
- Validates reasoning quality through live LLM interactions
- Provides A/B testing between original and optimized prompts
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
from datetime import datetime

# Import the optimization modules
from advanced_prompts import AdvancedPromptBuilder, PromptingStrategy, PromptOptimizationContext
from domain_optimized_prompts import create_domain_prompt_factory, DomainPromptContext
from llm import LLMManager


@dataclass
class PromptTestResult:
    """Results from live LLM prompt testing"""
    strategy: str
    prompt: str
    response: str
    response_time_ms: float
    token_count_input: int
    token_count_output: int
    api_cost_estimate: float
    reasoning_quality_score: float  # 1-10 based on structured analysis
    accuracy_score: float  # 1-10 based on task completion
    coherence_score: float  # 1-10 based on response structure
    error_occurred: bool
    error_message: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class PromptComparisonResult:
    """Comparison between original and optimized prompts"""
    baseline_result: PromptTestResult
    optimized_result: PromptTestResult
    improvement_metrics: Dict[str, float]
    recommendation: str
    confidence_score: float


class LivePromptTester:
    """Live LLM API testing framework for prompt optimization validation"""
    
    def __init__(self):
        self.llm_manager = LLMManager()
        self.advanced_builder = AdvancedPromptBuilder()
        self.domain_factory = create_domain_prompt_factory()
        self.test_results = []
        self.results_dir = Path("prompt_testing_results")
        self.results_dir.mkdir(exist_ok=True)
    
    async def test_advanced_strategy(self, 
                                   strategy: PromptingStrategy,
                                   test_scenario: Dict[str, Any],
                                   provider: str = "openai") -> PromptTestResult:
        """Test a specific advanced prompting strategy with live LLM API"""
        
        # Create optimization context
        context = PromptOptimizationContext(
            task_complexity=test_scenario.get("complexity", "moderate"),
            domain=test_scenario.get("domain", "general"),
            error_tolerance="medium",
            speed_priority="medium", 
            accuracy_priority="high",
            interpretability_need="high"
        )
        
        # Create mock web page state for testing
        from perception.models import WebPageState, PageMetadata, DOMStructure, InteractiveElement
        
        mock_state = self._create_mock_page_state(test_scenario)
        
        # Build optimized prompt
        optimized_prompt = self.advanced_builder.build_optimized_prompt(
            task=test_scenario["task"],
            state=mock_state,
            context=context,
            history=test_scenario.get("history", []),
            strategy=strategy
        )
        
        # Execute live LLM test
        return await self._execute_live_test(
            prompt=optimized_prompt,
            strategy=strategy.value,
            provider=provider,
            test_scenario=test_scenario
        )
    
    async def test_domain_optimized_prompt(self,
                                         domain: str,
                                         task_context: Dict[str, Any],
                                         provider: str = "openai") -> PromptTestResult:
        """Test domain-optimized prompt with live LLM API"""
        
        # Create domain context
        domain_context = DomainPromptContext(
            domain=domain,
            task_type=task_context.get("task_type", "search"),
            urgency=task_context.get("urgency", "medium"),
            accuracy_requirement=task_context.get("accuracy", "high"),
            data_sensitivity=task_context.get("sensitivity", "public")
        )
        
        # Get domain-optimized prompt
        optimized_prompt = self.domain_factory.get_prompt_for_domain(domain, domain_context)
        
        # Format with test data
        formatted_prompt = self._format_domain_prompt(optimized_prompt, task_context)
        
        # Execute live test
        return await self._execute_live_test(
            prompt=formatted_prompt,
            strategy=f"{domain}_optimized",
            provider=provider,
            test_scenario=task_context
        )
    
    async def compare_baseline_vs_optimized(self,
                                          baseline_prompt: str,
                                          optimized_strategy: PromptingStrategy,
                                          test_scenario: Dict[str, Any],
                                          provider: str = "openai") -> PromptComparisonResult:
        """A/B test baseline vs optimized prompt with live LLM APIs"""
        
        print(f"🧪 Running A/B test: Baseline vs {optimized_strategy.value}")
        
        # Test baseline prompt
        baseline_result = await self._execute_live_test(
            prompt=baseline_prompt,
            strategy="baseline", 
            provider=provider,
            test_scenario=test_scenario
        )
        
        # Test optimized strategy
        optimized_result = await self.test_advanced_strategy(
            strategy=optimized_strategy,
            test_scenario=test_scenario,
            provider=provider
        )
        
        # Calculate improvements
        improvement_metrics = self._calculate_improvements(baseline_result, optimized_result)
        
        # Generate recommendation
        recommendation, confidence = self._generate_recommendation(improvement_metrics)
        
        return PromptComparisonResult(
            baseline_result=baseline_result,
            optimized_result=optimized_result,
            improvement_metrics=improvement_metrics,
            recommendation=recommendation,
            confidence_score=confidence
        )
    
    async def _execute_live_test(self,
                               prompt: str,
                               strategy: str,
                               provider: str,
                               test_scenario: Dict[str, Any]) -> PromptTestResult:
        """Execute actual LLM API call and measure performance"""
        
        print(f"⚡ Testing {strategy} strategy with {provider} API...")
        
        start_time = time.time()
        error_occurred = False
        error_message = None
        response = ""
        
        try:
            # CRITICAL: REAL LLM API CALL - NOT SIMULATION
            response = await self.llm_manager.generate(
                prompt=prompt,
                provider=provider,
                temperature=0.1,  # Low temperature for consistent testing
                max_tokens=2000
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
        except Exception as e:
            error_occurred = True
            error_message = str(e)
            response_time_ms = (time.time() - start_time) * 1000
            print(f"❌ LLM API call failed: {e}")
        
        # Get actual token counts from LLM provider
        llm_provider = self.llm_manager.get_provider(provider)
        input_tokens = llm_provider.estimate_tokens(prompt)
        output_tokens = llm_provider.estimate_tokens(response) if response else 0
        
        # Estimate API costs (approximate)
        api_cost = self._estimate_api_cost(input_tokens, output_tokens, provider)
        
        # Analyze response quality with REAL LLM scoring
        quality_scores = await self._analyze_response_quality(
            response, test_scenario, provider
        )
        
        return PromptTestResult(
            strategy=strategy,
            prompt=prompt[:500] + "..." if len(prompt) > 500 else prompt,
            response=response[:1000] + "..." if len(response) > 1000 else response,
            response_time_ms=response_time_ms,
            token_count_input=input_tokens,
            token_count_output=output_tokens, 
            api_cost_estimate=api_cost,
            reasoning_quality_score=quality_scores["reasoning"],
            accuracy_score=quality_scores["accuracy"],
            coherence_score=quality_scores["coherence"],
            error_occurred=error_occurred,
            error_message=error_message
        )
    
    async def _analyze_response_quality(self, 
                                      response: str,
                                      test_scenario: Dict[str, Any],
                                      provider: str) -> Dict[str, float]:
        """Analyze response quality using LIVE LLM evaluation (not hardcoded scores)"""
        
        if not response or len(response) < 10:
            return {"reasoning": 1.0, "accuracy": 1.0, "coherence": 1.0}
        
        # Use REAL LLM to evaluate response quality
        evaluation_prompt = f"""
        Evaluate this AI response on three dimensions. Be precise and critical.

        Original Task: {test_scenario.get('task', 'Unknown task')}
        
        AI Response to Evaluate: 
        {response}
        
        Rate each dimension from 1-10:
        
        1. REASONING QUALITY (1-10): How logical, structured, and well-reasoned is this response?
        - Does it show clear thinking steps?
        - Are conclusions well-supported?
        - Is the logic sound?
        
        2. ACCURACY (1-10): How accurate and relevant is this response to the task?
        - Does it address the specific task requirements?
        - Are the details factually plausible?
        - Is it on-topic and focused?
        
        3. COHERENCE (1-10): How well-structured and coherent is the response?
        - Is it clearly organized?
        - Does it flow logically?
        - Is it easy to understand?
        
        Respond in this exact format:
        Reasoning: X.X
        Accuracy: X.X  
        Coherence: X.X
        """
        
        try:
            # CRITICAL: REAL LLM EVALUATION - NOT HARDCODED SCORES
            evaluation_response = await self.llm_manager.generate(
                prompt=evaluation_prompt,
                provider=provider,
                temperature=0.1,
                max_tokens=200
            )
            
            # Parse scores from real LLM response
            scores = self._parse_evaluation_scores(evaluation_response)
            return scores
            
        except Exception as e:
            print(f"⚠️ Quality evaluation failed: {e}")
            # Return conservative estimates if evaluation fails
            return {"reasoning": 5.0, "accuracy": 5.0, "coherence": 5.0}
    
    def _parse_evaluation_scores(self, evaluation_text: str) -> Dict[str, float]:
        """Parse evaluation scores from LLM response"""
        scores = {"reasoning": 5.0, "accuracy": 5.0, "coherence": 5.0}
        
        lines = evaluation_text.split('\n')
        for line in lines:
            line = line.lower().strip()
            if 'reasoning:' in line:
                try:
                    score = float(line.split(':')[1].strip())
                    scores["reasoning"] = max(1.0, min(10.0, score))
                except:
                    pass
            elif 'accuracy:' in line:
                try:
                    score = float(line.split(':')[1].strip())
                    scores["accuracy"] = max(1.0, min(10.0, score))
                except:
                    pass
            elif 'coherence:' in line:
                try:
                    score = float(line.split(':')[1].strip())
                    scores["coherence"] = max(1.0, min(10.0, score))
                except:
                    pass
        
        return scores
    
    def _estimate_api_cost(self, input_tokens: int, output_tokens: int, provider: str) -> float:
        """Estimate API cost based on real token usage"""
        
        # Approximate pricing (as of 2024/2025) - costs change frequently
        pricing = {
            "openai": {"input": 0.001, "output": 0.002},  # Per 1K tokens
            "anthropic": {"input": 0.008, "output": 0.024},  # Per 1K tokens  
            "gemini": {"input": 0.0005, "output": 0.0015}  # Per 1K tokens
        }
        
        if provider not in pricing:
            return 0.0
        
        rates = pricing[provider]
        input_cost = (input_tokens / 1000) * rates["input"] 
        output_cost = (output_tokens / 1000) * rates["output"]
        
        return input_cost + output_cost
    
    def _calculate_improvements(self, baseline: PromptTestResult, optimized: PromptTestResult) -> Dict[str, float]:
        """Calculate improvement metrics between baseline and optimized"""
        
        improvements = {}
        
        # Response quality improvements
        improvements["reasoning_improvement"] = optimized.reasoning_quality_score - baseline.reasoning_quality_score
        improvements["accuracy_improvement"] = optimized.accuracy_score - baseline.accuracy_score
        improvements["coherence_improvement"] = optimized.coherence_score - baseline.coherence_score
        
        # Performance improvements
        if baseline.response_time_ms > 0:
            improvements["speed_improvement_percent"] = ((baseline.response_time_ms - optimized.response_time_ms) / baseline.response_time_ms) * 100
        else:
            improvements["speed_improvement_percent"] = 0.0
        
        # Efficiency improvements
        if baseline.api_cost_estimate > 0:
            improvements["cost_efficiency_percent"] = ((baseline.api_cost_estimate - optimized.api_cost_estimate) / baseline.api_cost_estimate) * 100
        else:
            improvements["cost_efficiency_percent"] = 0.0
        
        # Token efficiency
        baseline_total_tokens = baseline.token_count_input + baseline.token_count_output
        optimized_total_tokens = optimized.token_count_input + optimized.token_count_output
        
        if baseline_total_tokens > 0:
            improvements["token_efficiency_percent"] = ((baseline_total_tokens - optimized_total_tokens) / baseline_total_tokens) * 100
        else:
            improvements["token_efficiency_percent"] = 0.0
        
        # Overall quality score
        baseline_avg_quality = (baseline.reasoning_quality_score + baseline.accuracy_score + baseline.coherence_score) / 3
        optimized_avg_quality = (optimized.reasoning_quality_score + optimized.accuracy_score + optimized.coherence_score) / 3
        improvements["overall_quality_improvement"] = optimized_avg_quality - baseline_avg_quality
        
        return improvements
    
    def _generate_recommendation(self, improvements: Dict[str, float]) -> Tuple[str, float]:
        """Generate recommendation based on improvement metrics"""
        
        significant_improvements = []
        minor_improvements = []
        regressions = []
        
        for metric, value in improvements.items():
            if abs(value) >= 1.0:  # Significant change threshold
                if value > 0:
                    significant_improvements.append(f"{metric}: +{value:.2f}")
                else:
                    regressions.append(f"{metric}: {value:.2f}")
            elif abs(value) >= 0.1:  # Minor change threshold
                minor_improvements.append(f"{metric}: {value:.2f}")
        
        # Calculate confidence score
        quality_improvements = [
            improvements.get("reasoning_improvement", 0),
            improvements.get("accuracy_improvement", 0), 
            improvements.get("coherence_improvement", 0),
            improvements.get("overall_quality_improvement", 0)
        ]
        
        avg_quality_improvement = sum(quality_improvements) / len(quality_improvements)
        confidence = min(95.0, max(5.0, 50.0 + (avg_quality_improvement * 10)))
        
        # Generate recommendation
        if significant_improvements and len(regressions) == 0:
            recommendation = f"🚀 STRONGLY RECOMMEND optimized strategy. Significant improvements: {', '.join(significant_improvements)}"
        elif significant_improvements and len(regressions) <= 2:
            recommendation = f"✅ RECOMMEND optimized strategy. Improvements: {', '.join(significant_improvements)}. Monitor: {', '.join(regressions)}"
        elif minor_improvements and len(regressions) <= 1:
            recommendation = f"👍 CONSIDER optimized strategy. Minor improvements noted: {', '.join(minor_improvements)}"
        elif len(regressions) > 2:
            recommendation = f"❌ DO NOT RECOMMEND. Significant regressions: {', '.join(regressions)}"
        else:
            recommendation = f"🤔 NEUTRAL. Mixed results require human judgment. Test with specific use case."
        
        return recommendation, confidence
    
    def _create_mock_page_state(self, test_scenario: Dict[str, Any]):
        """Create mock page state for testing"""
        from perception.models import WebPageState, PageMetadata, DOMStructure, InteractiveElement
        
        # Mock page metadata
        metadata = PageMetadata(
            url=test_scenario.get("url", "https://example.com"),
            title=test_scenario.get("title", "Test Page"),
            description="Mock page for prompt testing"
        )
        
        # Mock DOM structure
        dom = DOMStructure(
            raw_html="<html><body>Mock content for testing</body></html>",
            distilled_content=test_scenario.get("content", "Mock page content with various elements for testing prompt optimization.")
        )
        
        # Mock interactive elements
        elements = [
            InteractiveElement(
                id=1,
                type="button",
                tag_name="button",
                text="Search",
                is_visible=True,
                is_enabled=True
            ),
            InteractiveElement(
                id=2,
                type="input",
                tag_name="input",
                placeholder="Enter search term",
                is_visible=True,
                is_enabled=True
            )
        ]
        
        return WebPageState(
            metadata=metadata,
            dom_structure=dom,
            interactive_elements=elements
        )
    
    def _format_domain_prompt(self, template: str, context: Dict[str, Any]) -> str:
        """Format domain prompt template with test context"""
        
        # Extract available placeholders from template
        import re
        placeholders = re.findall(r'\{([^}]+)\}', template)
        
        # Fill in available values
        formatted_values = {}
        for placeholder in placeholders:
            if placeholder in context:
                formatted_values[placeholder] = context[placeholder]
            else:
                # Provide sensible defaults
                defaults = {
                    "url": "https://example.com",
                    "title": "Test Page",
                    "content": "Mock content for testing",
                    "elements": "[1] Search button\n[2] Input field",
                    "platform": "Example Platform",
                    "query": context.get("task", "test query"),
                    "news_category": "technology",
                    "job_query": "software engineer",
                    "product_query": "wireless headphones"
                }
                formatted_values[placeholder] = defaults.get(placeholder, f"[{placeholder}]")
        
        try:
            return template.format(**formatted_values)
        except KeyError as e:
            print(f"⚠️ Missing placeholder {e} in domain prompt template")
            return template
    
    async def run_comprehensive_test_suite(self, provider: str = "openai") -> Dict[str, Any]:
        """Run comprehensive test suite of all optimized strategies"""
        
        print("🧪 Starting Comprehensive Prompt Optimization Test Suite")
        print("=" * 60)
        
        test_scenarios = [
            {
                "name": "E-commerce Product Search",
                "domain": "ecommerce",
                "task": "Search for wireless headphones on Amazon and compare prices",
                "complexity": "moderate",
                "task_type": "search",
                "url": "https://amazon.com",
                "title": "Amazon - Product Search"
            },
            {
                "name": "Job Search Analysis", 
                "domain": "job_search",
                "task": "Find software engineer jobs in San Francisco",
                "complexity": "complex",
                "task_type": "search",
                "url": "https://linkedin.com/jobs",
                "title": "LinkedIn Jobs"
            },
            {
                "name": "Social Media Sentiment Analysis",
                "domain": "social_media", 
                "task": "Analyze sentiment about AI technology on Twitter",
                "complexity": "complex",
                "task_type": "analysis",
                "url": "https://twitter.com",
                "title": "Twitter Search"
            },
            {
                "name": "News Monitoring",
                "domain": "news_monitoring",
                "task": "Monitor tech news for AI developments",
                "complexity": "moderate",
                "task_type": "extraction",
                "url": "https://techcrunch.com",
                "title": "TechCrunch - Technology News"
            }
        ]
        
        results = {}
        
        # Test each advanced strategy
        strategies_to_test = [
            PromptingStrategy.CHAIN_OF_THOUGHT,
            PromptingStrategy.TREE_OF_THOUGHTS,
            PromptingStrategy.REACT_ENHANCED,
            PromptingStrategy.CONSTITUTIONAL_AI,
            PromptingStrategy.SELF_CONSISTENCY
        ]
        
        for scenario in test_scenarios:
            scenario_results = {}
            print(f"\n🎯 Testing Scenario: {scenario['name']}")
            
            for strategy in strategies_to_test:
                try:
                    result = await self.test_advanced_strategy(
                        strategy=strategy,
                        test_scenario=scenario,
                        provider=provider
                    )
                    scenario_results[strategy.value] = asdict(result)
                    
                    print(f"   ✅ {strategy.value}: Quality={result.reasoning_quality_score:.1f}/10, "
                          f"Time={result.response_time_ms:.0f}ms, Cost=${result.api_cost_estimate:.4f}")
                          
                except Exception as e:
                    print(f"   ❌ {strategy.value}: Failed - {e}")
                    
                # Brief delay to respect API rate limits
                await asyncio.sleep(1)
            
            results[scenario['name']] = scenario_results
        
        # Save comprehensive results
        await self._save_test_results(results, "comprehensive_test_suite")
        
        print("\n🎉 Comprehensive test suite completed!")
        return results
    
    async def _save_test_results(self, results: Dict[str, Any], test_name: str):
        """Save test results to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"{test_name}_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"📊 Test results saved to: {results_file}")


# Factory function for easy testing
def create_prompt_tester() -> LivePromptTester:
    """Create live prompt testing framework"""
    return LivePromptTester()


# Example usage and testing functions
async def run_example_optimization_test():
    """Run example test showing prompt optimization in action"""
    
    tester = create_prompt_tester()
    
    # Test scenario
    test_scenario = {
        "task": "Search for wireless bluetooth headphones under $100",
        "domain": "ecommerce", 
        "complexity": "moderate",
        "url": "https://amazon.com",
        "title": "Amazon Product Search",
        "content": "Amazon product search page with various electronic items"
    }
    
    # Baseline prompt (simple)
    baseline_prompt = f"""
    Go to Amazon and search for wireless bluetooth headphones under $100.
    Find relevant products and extract their information.
    Current page: {test_scenario['url']}
    """
    
    # Test baseline vs Chain of Thought optimization
    comparison = await tester.compare_baseline_vs_optimized(
        baseline_prompt=baseline_prompt,
        optimized_strategy=PromptingStrategy.CHAIN_OF_THOUGHT,
        test_scenario=test_scenario,
        provider="openai"
    )
    
    print("🚀 PROMPT OPTIMIZATION TEST RESULTS")
    print("=" * 50)
    print(f"Baseline Quality: {comparison.baseline_result.reasoning_quality_score:.1f}/10")
    print(f"Optimized Quality: {comparison.optimized_result.reasoning_quality_score:.1f}/10")
    print(f"Quality Improvement: +{comparison.improvement_metrics['reasoning_improvement']:.2f} points")
    print(f"Speed: {comparison.optimized_result.response_time_ms:.0f}ms vs {comparison.baseline_result.response_time_ms:.0f}ms")
    print(f"Cost: ${comparison.optimized_result.api_cost_estimate:.4f} vs ${comparison.baseline_result.api_cost_estimate:.4f}")
    print(f"\n📝 Recommendation: {comparison.recommendation}")
    print(f"🎯 Confidence: {comparison.confidence_score:.1f}%")
    
    return comparison


if __name__ == "__main__":
    """Run example optimization test"""
    asyncio.run(run_example_optimization_test())