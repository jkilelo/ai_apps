"""
LLM Provider

Provides abstraction over multiple LLM providers (OpenAI, Claude, Gemini)
using the centralized llm.py module.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sys
import asyncio

# Add project root to path for llm.py access
sys.path.append(str(Path(__file__).parents[6]))  # Navigate to /var/www/ai_apps

try:
    from llm import query_llm, default_llm
except ImportError:
    logger = logging.getLogger(__name__)
    logger.error("Failed to import llm module from /var/www/ai_apps/llm.py")
    raise

logger = logging.getLogger(__name__)


class LLMProvider:
    """
    Provides unified interface to multiple LLM providers.
    
    Features:
    - Multi-model support (OpenAI, Claude, Gemini)
    - Automatic fallback on failures
    - Response parsing and validation
    - Cost tracking
    - Performance metrics
    """
    
    def __init__(self, config):
        self.config = config
        
        # Model configuration
        self.model_config = {
            'openai': {
                'model': 'gpt-4o',
                'temperature': 0.7,
                'max_tokens': 4000,
                'strengths': ['creative', 'comprehensive', 'natural_language']
            },
            'claude': {
                'model': 'claude-3-5-sonnet-20241022',
                'temperature': 0.5,
                'max_tokens': 4000,
                'strengths': ['structured_output', 'technical', 'precise']
            },
            'gemini': {
                'model': 'gemini-2.0-flash-exp',
                'temperature': 0.6,
                'max_tokens': 4000,
                'strengths': ['fast', 'cost_effective', 'good_general']
            }
        }
        
        # Tracking
        self._models_used = set()
        self._call_count = 0
        self._total_tokens = 0
        self._errors = []
        
        logger.info(f"LLMProvider initialized with models: {list(self.model_config.keys())}")
    
    async def generate(
        self,
        prompt: str,
        model_preference: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        retry_on_failure: bool = True
    ) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: The prompt to send to LLM
            model_preference: Preferred model (openai, claude, gemini)
            temperature: Override default temperature
            max_tokens: Override default max tokens
            retry_on_failure: Whether to retry with fallback models
            
        Returns:
            Generated response text
        """
        self._call_count += 1
        
        # Determine model order
        if model_preference and model_preference in self.model_config:
            model_order = [model_preference] + [m for m in self.model_config if m != model_preference]
        else:
            # Default order: Claude for structured, GPT for creative, Gemini for fast
            model_order = ['claude', 'openai', 'gemini']
        
        last_error = None
        
        for provider in model_order:
            try:
                logger.info(f"Attempting generation with {provider}")
                
                # Prepare messages
                messages = [
                    {
                        "role": "system",
                        "content": "You are an expert test automation engineer specializing in Gherkin BDD test generation. Generate clear, comprehensive, and executable test scenarios."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                # Get model config
                config = self.model_config[provider]
                model = config['model']
                
                # Call LLM
                response = await asyncio.to_thread(
                    query_llm,
                    provider,
                    model,
                    messages
                )
                
                # Extract response text
                response_text = response.choices[0].message.content
                
                # Track usage
                self._models_used.add(provider)
                if hasattr(response, 'usage'):
                    self._total_tokens += response.usage.total_tokens
                
                logger.info(f"Successfully generated response with {provider}")
                return response_text
                
            except Exception as e:
                logger.error(f"Failed to generate with {provider}: {e}")
                last_error = e
                self._errors.append({
                    'provider': provider,
                    'error': str(e),
                    'prompt_preview': prompt[:100] + '...'
                })
                
                if not retry_on_failure:
                    break
        
        # All models failed
        raise Exception(f"All LLM providers failed. Last error: {last_error}")
    
    async def assess_scenario_quality(
        self,
        scenario: Dict[str, Any],
        element_context: Dict[str, Any],
        models: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get quality assessment from multiple models.
        
        Args:
            scenario: The Gherkin scenario to assess
            element_context: Context about page elements
            models: List of models to use for assessment
            
        Returns:
            List of assessments from each model
        """
        if models is None:
            models = list(self.model_config.keys())
        
        assessments = []
        
        # Create assessment prompt
        prompt = self._create_quality_assessment_prompt(scenario, element_context)
        
        # Get assessments from each model
        tasks = []
        for model in models:
            task = self._get_single_assessment(prompt, model, scenario)
            tasks.append(task)
        
        assessments = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors
        valid_assessments = []
        for assessment in assessments:
            if isinstance(assessment, Exception):
                logger.error(f"Assessment failed: {assessment}")
            else:
                valid_assessments.append(assessment)
        
        return valid_assessments
    
    async def _get_single_assessment(
        self,
        prompt: str,
        model: str,
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get quality assessment from a single model."""
        try:
            response = await self.generate(
                prompt,
                model_preference=model,
                temperature=0.3,  # Lower temperature for more consistent assessment
                retry_on_failure=False
            )
            
            # Parse assessment
            assessment = self._parse_assessment_response(response)
            assessment['model'] = model
            assessment['scenario_title'] = scenario.get('title', 'Unknown')
            
            return assessment
            
        except Exception as e:
            logger.error(f"Assessment failed for {model}: {e}")
            raise
    
    def _create_quality_assessment_prompt(
        self,
        scenario: Dict[str, Any],
        element_context: Dict[str, Any]
    ) -> str:
        """Create prompt for quality assessment."""
        return f"""
        Assess the quality of this Gherkin test scenario.
        
        Scenario:
        {json.dumps(scenario, indent=2)}
        
        Page Context:
        - Total elements: {element_context['page_info']['total_elements']}
        - Interactive elements: {element_context['page_info']['interactive_elements']}
        - Page type: {element_context['page_info']['page_type']}
        - Available actions: {element_context['element_summary']['unique_actions']}
        
        Assess the scenario based on:
        1. Clarity and readability (0-1)
        2. Completeness of test coverage (0-1)
        3. Technical correctness (0-1)
        4. Business value (0-1)
        5. Executability (0-1)
        
        Provide your assessment as JSON:
        {{
            "quality_score": 0.0-1.0,
            "scores": {{
                "clarity": 0.0-1.0,
                "completeness": 0.0-1.0,
                "correctness": 0.0-1.0,
                "business_value": 0.0-1.0,
                "executability": 0.0-1.0
            }},
            "improvements": [
                {{
                    "type": "improvement_type",
                    "description": "what to improve",
                    "priority": 1-5,
                    "steps": ["optional specific steps"]
                }}
            ],
            "strengths": ["list of strengths"],
            "weaknesses": ["list of weaknesses"]
        }}
        """
    
    def _parse_assessment_response(self, response: str) -> Dict[str, Any]:
        """Parse quality assessment response."""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                assessment = json.loads(json_match.group())
                
                # Ensure required fields
                required_fields = ['quality_score', 'scores', 'improvements']
                for field in required_fields:
                    if field not in assessment:
                        assessment[field] = self._get_default_assessment_field(field)
                
                return assessment
            else:
                logger.warning("No JSON found in assessment response")
                return self._get_default_assessment()
                
        except Exception as e:
            logger.error(f"Failed to parse assessment: {e}")
            return self._get_default_assessment()
    
    def _get_default_assessment_field(self, field: str) -> Any:
        """Get default value for assessment field."""
        defaults = {
            'quality_score': 0.7,
            'scores': {
                'clarity': 0.7,
                'completeness': 0.7,
                'correctness': 0.7,
                'business_value': 0.7,
                'executability': 0.7
            },
            'improvements': [],
            'strengths': [],
            'weaknesses': []
        }
        return defaults.get(field, None)
    
    def _get_default_assessment(self) -> Dict[str, Any]:
        """Get default assessment when parsing fails."""
        return {
            'quality_score': 0.7,
            'scores': self._get_default_assessment_field('scores'),
            'improvements': [],
            'strengths': ['Generated successfully'],
            'weaknesses': ['Assessment parsing failed']
        }
    
    def get_best_model_for_task(self, task_type: str) -> str:
        """Get the best model for a specific task type."""
        task_model_mapping = {
            'creative_generation': 'openai',
            'structured_output': 'claude',
            'technical_analysis': 'claude',
            'natural_language': 'openai',
            'quick_response': 'gemini',
            'cost_sensitive': 'gemini'
        }
        
        return task_model_mapping.get(task_type, 'claude')
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return list(self.model_config.keys())
    
    def get_models_used(self) -> List[str]:
        """Get list of models that have been used."""
        return list(self._models_used)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            'call_count': self._call_count,
            'models_used': list(self._models_used),
            'total_tokens': self._total_tokens,
            'estimated_cost': self._estimate_cost(),
            'error_count': len(self._errors),
            'error_rate': len(self._errors) / max(self._call_count, 1)
        }
    
    def _estimate_cost(self) -> float:
        """Estimate cost based on token usage."""
        # Rough cost estimates per 1K tokens (input + output)
        cost_per_1k_tokens = {
            'openai': 0.03,  # GPT-4
            'claude': 0.024,  # Claude 3
            'gemini': 0.001   # Gemini Pro
        }
        
        # Distribute tokens evenly among used models (simplified)
        if not self._models_used:
            return 0.0
        
        tokens_per_model = self._total_tokens / len(self._models_used)
        total_cost = 0.0
        
        for model in self._models_used:
            cost_rate = cost_per_1k_tokens.get(model, 0.01)
            total_cost += (tokens_per_model / 1000) * cost_rate
        
        return round(total_cost, 4)
    
    async def generate_with_examples(
        self,
        prompt: str,
        examples: List[Dict[str, str]],
        model_preference: Optional[str] = None
    ) -> str:
        """
        Generate response with few-shot examples.
        
        Args:
            prompt: The main prompt
            examples: List of example input/output pairs
            model_preference: Preferred model
            
        Returns:
            Generated response
        """
        # Build few-shot prompt
        few_shot_prompt = "Here are some examples:\n\n"
        
        for i, example in enumerate(examples, 1):
            few_shot_prompt += f"Example {i}:\n"
            few_shot_prompt += f"Input: {example['input']}\n"
            few_shot_prompt += f"Output: {example['output']}\n\n"
        
        few_shot_prompt += f"Now, for the following input:\n{prompt}"
        
        return await self.generate(
            few_shot_prompt,
            model_preference=model_preference
        )
    
    async def batch_generate(
        self,
        prompts: List[str],
        model_preference: Optional[str] = None,
        max_concurrent: int = 3
    ) -> List[str]:
        """
        Generate responses for multiple prompts in parallel.
        
        Args:
            prompts: List of prompts
            model_preference: Preferred model
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of generated responses
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(prompt):
            async with semaphore:
                return await self.generate(prompt, model_preference=model_preference)
        
        tasks = [generate_with_semaphore(prompt) for prompt in prompts]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle errors
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"Batch generation failed for prompt {i}: {response}")
                results.append("")  # Empty response on error
            else:
                results.append(response)
        
        return results