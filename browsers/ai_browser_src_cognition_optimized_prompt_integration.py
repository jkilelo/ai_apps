"""
Optimized Prompt Integration Layer

This module provides seamless integration of advanced prompting strategies
into existing real-world AI Browser examples.

Key Features:
- Drop-in replacement for existing prompt usage
- Automatic strategy selection based on context
- Performance monitoring and optimization
- Backward compatibility with existing code
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio

from advanced_prompts import AdvancedPromptBuilder, PromptingStrategy, PromptOptimizationContext
from domain_optimized_prompts import create_domain_prompt_factory, DomainPromptContext, get_optimized_prompt_for_example
from llm import LLMManager


@dataclass
class OptimizedPromptConfig:
    """Configuration for optimized prompt usage"""
    enable_optimization: bool = True
    preferred_strategy: Optional[PromptingStrategy] = None
    domain: Optional[str] = None
    performance_monitoring: bool = True
    fallback_to_baseline: bool = True


class OptimizedPromptManager:
    """Manager for integrating optimized prompts into existing examples"""
    
    def __init__(self, config: OptimizedPromptConfig = None):
        self.config = config or OptimizedPromptConfig()
        self.llm_manager = LLMManager()
        self.advanced_builder = AdvancedPromptBuilder()
        self.domain_factory = create_domain_prompt_factory()
        self.performance_history = []
    
    async def generate_optimized_task_prompt(self, 
                                           task: str,
                                           context: Dict[str, Any],
                                           example_type: str = "general") -> str:
        """
        Generate optimized prompt for task execution
        
        This is the main integration point for existing examples.
        Simply replace existing prompt generation with this method.
        """
        
        if not self.config.enable_optimization:
            return self._create_baseline_prompt(task, context)
        
        try:
            # Determine optimal strategy based on context
            if self.config.preferred_strategy:
                strategy = self.config.preferred_strategy
            else:
                strategy = self._auto_select_strategy(task, context, example_type)
            
            # Get domain-specific optimized prompt if available
            domain_prompt = self._get_domain_optimized_prompt(example_type, task, context)
            if domain_prompt:
                return domain_prompt
            
            # Fall back to advanced strategy prompt
            return await self._build_advanced_strategy_prompt(task, context, strategy)
            
        except Exception as e:
            if self.config.fallback_to_baseline:
                print(f"⚠️ Optimization failed, falling back to baseline: {e}")
                return self._create_baseline_prompt(task, context)
            else:
                raise e
    
    async def execute_optimized_llm_call(self,
                                       task: str, 
                                       context: Dict[str, Any],
                                       example_type: str = "general",
                                       provider: str = None) -> str:
        """
        Execute LLM call with optimized prompt
        
        Drop-in replacement for existing LLM generate calls
        """
        
        # Generate optimized prompt
        optimized_prompt = await self.generate_optimized_task_prompt(
            task=task,
            context=context,
            example_type=example_type
        )
        
        # Execute with performance monitoring
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await self.llm_manager.generate(
                prompt=optimized_prompt,
                provider=provider,
                temperature=0.1,
                max_tokens=2000
            )
            
            # Record performance metrics
            if self.config.performance_monitoring:
                self._record_performance(
                    task=task,
                    example_type=example_type,
                    response_time=asyncio.get_event_loop().time() - start_time,
                    success=True,
                    strategy=self.config.preferred_strategy.value if self.config.preferred_strategy else "auto"
                )
            
            return response
            
        except Exception as e:
            self._record_performance(
                task=task,
                example_type=example_type,
                response_time=asyncio.get_event_loop().time() - start_time,
                success=False,
                error=str(e),
                strategy=self.config.preferred_strategy.value if self.config.preferred_strategy else "auto"
            )
            raise e
    
    def _auto_select_strategy(self, task: str, context: Dict[str, Any], example_type: str) -> PromptingStrategy:
        """Automatically select optimal strategy based on context"""
        
        task_lower = task.lower()
        
        # Critical tasks use Self-Consistency
        if any(word in task_lower for word in ['critical', 'important', 'financial', 'legal', 'security']):
            return PromptingStrategy.CONSTITUTIONAL_AI
        
        # Complex analysis tasks use Tree of Thoughts  
        if any(word in task_lower for word in ['analyze', 'compare', 'evaluate', 'assess', 'research']):
            if len(task) > 100:  # Complex task
                return PromptingStrategy.TREE_OF_THOUGHTS
            else:
                return PromptingStrategy.CHAIN_OF_THOUGHT
        
        # Social media and news analysis use specialized strategies
        if example_type in ['social_media_analysis', 'news_monitoring']:
            return PromptingStrategy.CONSTITUTIONAL_AI  # For bias awareness
        
        # Job applications use Constitutional AI for ethics
        if example_type == 'job_automation':
            return PromptingStrategy.CONSTITUTIONAL_AI
        
        # E-commerce uses Chain of Thought for systematic analysis
        if example_type == 'ecommerce_research':
            return PromptingStrategy.CHAIN_OF_THOUGHT
        
        # Default to enhanced ReAct for most tasks
        return PromptingStrategy.REACT_ENHANCED
    
    def _get_domain_optimized_prompt(self, example_type: str, task: str, context: Dict[str, Any]) -> Optional[str]:
        """Get domain-specific optimized prompt if available"""
        
        try:
            # Map to task context
            task_context = {
                "task": task,
                "task_type": context.get("task_type", "search"),
                "urgency": "medium",
                "accuracy": "high", 
                "sensitivity": "public",
                **context
            }
            
            return get_optimized_prompt_for_example(example_type, task_context)
            
        except Exception as e:
            print(f"⚠️ Domain-optimized prompt not available: {e}")
            return None
    
    async def _build_advanced_strategy_prompt(self, 
                                            task: str, 
                                            context: Dict[str, Any], 
                                            strategy: PromptingStrategy) -> str:
        """Build advanced strategy prompt"""
        
        # Create optimization context
        optimization_context = PromptOptimizationContext(
            task_complexity=context.get("complexity", "moderate"),
            domain=context.get("domain", "general"),
            error_tolerance="medium",
            speed_priority="medium",
            accuracy_priority="high", 
            interpretability_need="high"
        )
        
        # Create mock page state if not provided
        from perception.models import WebPageState, PageMetadata, DOMStructure, InteractiveElement
        
        if "page_state" not in context:
            mock_metadata = PageMetadata(
                url=context.get("url", "https://example.com"),
                title=context.get("title", "Web Page"),
                description="Automated browser task page"
            )
            
            mock_dom = DOMStructure(
                raw_html="<html><body>Mock content</body></html>",
                distilled_content=context.get("content", "Page content for automated task execution")
            )
            
            mock_elements = [
                InteractiveElement(
                    id=i+1,
                    type=elem_type,
                    tag_name=elem_type,
                    text=elem_text,
                    is_visible=True,
                    is_enabled=True
                )
                for i, (elem_type, elem_text) in enumerate([
                    ("button", "Search"), 
                    ("input", "Search input"),
                    ("link", "Navigation link")
                ])
            ]
            
            page_state = WebPageState(
                metadata=mock_metadata,
                dom_structure=mock_dom, 
                interactive_elements=mock_elements
            )
        else:
            page_state = context["page_state"]
        
        # Build optimized prompt
        return self.advanced_builder.build_optimized_prompt(
            task=task,
            state=page_state,
            context=optimization_context,
            history=context.get("history", []),
            strategy=strategy
        )
    
    def _create_baseline_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Create baseline prompt for fallback"""
        
        url = context.get("url", "https://example.com")
        page_info = context.get("content", "Current web page")
        
        return f"""
        Complete this web automation task: {task}
        
        Current page: {url}
        Page context: {page_info}
        
        Navigate the page and complete the requested task efficiently.
        Provide clear reasoning for your actions.
        """
    
    def _record_performance(self, **metrics):
        """Record performance metrics for analysis"""
        
        metrics["timestamp"] = asyncio.get_event_loop().time()
        self.performance_history.append(metrics)
        
        # Keep only recent history
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-50:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for optimization analysis"""
        
        if not self.performance_history:
            return {"message": "No performance data available"}
        
        successful_calls = [h for h in self.performance_history if h.get("success", False)]
        failed_calls = [h for h in self.performance_history if not h.get("success", True)]
        
        return {
            "total_calls": len(self.performance_history),
            "success_rate": len(successful_calls) / len(self.performance_history) * 100,
            "average_response_time": sum(h.get("response_time", 0) for h in successful_calls) / max(len(successful_calls), 1),
            "strategy_breakdown": self._get_strategy_breakdown(),
            "common_errors": self._get_common_errors(failed_calls)
        }
    
    def _get_strategy_breakdown(self) -> Dict[str, int]:
        """Get breakdown of strategies used"""
        strategy_counts = {}
        for history in self.performance_history:
            strategy = history.get("strategy", "unknown")
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        return strategy_counts
    
    def _get_common_errors(self, failed_calls: List[Dict]) -> List[str]:
        """Get list of common errors"""
        error_counts = {}
        for call in failed_calls:
            error = call.get("error", "Unknown error")
            error_counts[error] = error_counts.get(error, 0) + 1
        
        return sorted(error_counts.keys(), key=lambda x: error_counts[x], reverse=True)[:5]


# Global optimized prompt manager instance
_global_prompt_manager = None


def get_optimized_prompt_manager(config: OptimizedPromptConfig = None) -> OptimizedPromptManager:
    """Get global optimized prompt manager instance"""
    global _global_prompt_manager
    
    if _global_prompt_manager is None:
        _global_prompt_manager = OptimizedPromptManager(config)
    
    return _global_prompt_manager


# Convenience functions for easy integration
async def generate_optimized_prompt(task: str, 
                                  context: Dict[str, Any],
                                  example_type: str = "general") -> str:
    """Convenience function for generating optimized prompts"""
    manager = get_optimized_prompt_manager()
    return await manager.generate_optimized_task_prompt(task, context, example_type)


async def execute_optimized_llm(task: str,
                              context: Dict[str, Any], 
                              example_type: str = "general",
                              provider: str = None) -> str:
    """Convenience function for executing optimized LLM calls"""
    manager = get_optimized_prompt_manager()
    return await manager.execute_optimized_llm_call(task, context, example_type, provider)


def configure_optimization(enable: bool = True,
                          strategy: PromptingStrategy = None,
                          domain: str = None,
                          monitoring: bool = True) -> None:
    """Configure global optimization settings"""
    global _global_prompt_manager
    
    config = OptimizedPromptConfig(
        enable_optimization=enable,
        preferred_strategy=strategy,
        domain=domain,
        performance_monitoring=monitoring
    )
    
    _global_prompt_manager = OptimizedPromptManager(config)