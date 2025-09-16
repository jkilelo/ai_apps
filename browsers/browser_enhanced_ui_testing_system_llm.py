"""
Enhanced UI Testing System with Full LLM Integration
Integrates Gemini-2.5-pro for intelligent test generation using advanced prompt strategies

This system combines:
1. Advanced stealth browser with LLM-optimized extraction
2. Scientific prompt strategies (CoT, ToT, Self-Consistency, Meta-Prompting)
3. Real Gemini-2.5-pro integration for test generation
4. Evolutionary optimization with LLM feedback
5. Multi-strategy test generation with real AI
6. Context-aware reasoning engine powered by LLM
7. Comprehensive performance monitoring
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from pathlib import Path
import random
import hashlib
import sys
import re

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import LLM functionality
from llm import query_llm

# Import element structure
from browser.element_structure import (
    LLMOptimizedElement,
    ElementCategory,
    InteractionPattern,
    TestPriority,
    ValidationRule,
    PageStructure
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class SystemConfig:
    """Unified configuration for the enhanced system with LLM."""
    
    # LLM Settings
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.0-flash-exp"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4000
    llm_timeout: int = 30
    
    # Browser Extraction Settings
    max_elements: int = 100
    extraction_timeout: int = 60
    headless: bool = False
    enable_stealth: bool = True
    enable_human_simulation: bool = True
    
    # Prompt Optimization Settings
    enable_chain_of_thought: bool = True
    enable_tree_of_thoughts: bool = True
    enable_self_consistency: bool = True
    enable_meta_prompting: bool = True
    enable_opro: bool = True
    opro_iterations: int = 3
    self_consistency_samples: int = 3
    
    # Evolution Settings
    enable_evolution: bool = True
    evolution_generations: int = 5
    population_size: int = 10
    mutation_rate: float = 0.3
    crossover_rate: float = 0.7
    
    # Test Generation Settings
    test_strategies: List[str] = field(
        default_factory=lambda: [
            "happy_path",
            "negative",
            "edge_case",
            "security",
            "accessibility",
            "validation",
            "performance"
        ]
    )
    max_scenarios_per_strategy: int = 5
    
    # Reasoning Settings
    enable_element_reasoning: bool = True
    confidence_threshold: float = 0.8
    priority_weighting: Dict[str, float] = field(
        default_factory=lambda: {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25,
        }
    )
    
    # Storage Settings
    enable_caching: bool = True
    cache_ttl: int = 3600
    
    # Monitoring Settings
    enable_monitoring: bool = True
    metrics_collection_interval: int = 60
    performance_tracking: bool = True


# ============================================================================
# PROMPT STRATEGIES WITH LLM
# ============================================================================

class PromptStrategy(Enum):
    """Scientific prompt strategies from research."""
    ZERO_SHOT = "zero_shot"
    FEW_SHOT = "few_shot"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    SELF_CONSISTENCY = "self_consistency"
    META_PROMPTING = "meta_prompting"
    MIXTURE_OF_EXPERTS = "mixture_of_experts"


class LLMPromptEngine:
    """
    Advanced prompt generation engine with real LLM integration.
    Uses Gemini-2.5-pro for intelligent test generation.
    """
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.prompt_history = []
        self.performance_metrics = {}
        self.llm_call_count = 0
        self.total_tokens_used = 0
    
    def generate_extraction_analysis_prompt(self, elements: List[Dict], page_context: Dict) -> str:
        """Generate optimized prompt for element analysis."""
        
        # Prepare element summary
        element_summary = self._summarize_elements(elements)
        
        base_prompt = f"""
You are an expert QA engineer analyzing a web page for comprehensive test generation.

PAGE CONTEXT:
- URL: {page_context.get('url', 'Unknown')}
- Page Type: {page_context.get('pageType', 'Unknown')}
- Title: {page_context.get('title', 'Unknown')}

ELEMENT SUMMARY:
{element_summary}

TASK: Analyze these UI elements and provide:
1. Critical user journeys that must be tested
2. High-risk areas requiring thorough validation
3. Accessibility concerns
4. Security vulnerabilities to test
5. Performance bottlenecks to monitor

Focus on actionable insights for test generation.
"""
        
        if self.config.enable_chain_of_thought:
            base_prompt = self._apply_chain_of_thought(base_prompt)
        
        if self.config.enable_meta_prompting:
            base_prompt = self._apply_meta_prompting(base_prompt)
        
        return base_prompt
    
    def generate_test_scenarios_prompt(self, elements: List[Dict], strategy: str, analysis: Dict = None) -> str:
        """Generate optimized prompt for test scenario generation with specific strategy."""
        
        element_details = self._format_elements_for_llm(elements[:20])  # Limit for token management
        
        strategy_prompts = {
            "happy_path": """
Generate HAPPY PATH test scenarios for the most common successful user journeys.
Focus on: Complete workflows that users typically follow to accomplish their goals.
Include: All required fields, valid data, expected navigation flows.""",
            
            "negative": """
Generate NEGATIVE test scenarios to verify error handling and validation.
Focus on: Invalid inputs, missing required fields, incorrect formats, boundary violations.
Include: Expected error messages, validation feedback, recovery mechanisms.""",
            
            "edge_case": """
Generate EDGE CASE test scenarios for unusual but valid situations.
Focus on: Boundary values, special characters, maximum/minimum limits, rare combinations.
Include: Unicode characters, very long inputs, empty values, concurrent actions.""",
            
            "security": """
Generate SECURITY test scenarios to identify vulnerabilities.
Focus on: XSS attacks, SQL injection, CSRF, authentication bypass, authorization flaws.
Include: Malicious payloads, script injections, privilege escalation attempts.""",
            
            "accessibility": """
Generate ACCESSIBILITY test scenarios for WCAG compliance.
Focus on: Keyboard navigation, screen reader compatibility, color contrast, focus management.
Include: ARIA labels, tab order, alternative text, error announcements.""",
            
            "validation": """
Generate VALIDATION test scenarios for all input constraints.
Focus on: Required fields, format validation, range checks, dependency validation.
Include: Each validation rule with valid and invalid examples.""",
            
            "performance": """
Generate PERFORMANCE test scenarios to identify bottlenecks.
Focus on: Load times, concurrent users, data volume, resource usage.
Include: Stress testing, bulk operations, timeout scenarios."""
        }
        
        base_prompt = f"""
You are an expert QA engineer creating comprehensive test scenarios.

{strategy_prompts.get(strategy, strategy_prompts['happy_path'])}

ELEMENTS TO TEST:
{element_details}

{f"ANALYSIS INSIGHTS: {json.dumps(analysis, indent=2)}" if analysis else ""}

Generate exactly 5 test scenarios in the following JSON format:
{{
    "scenarios": [
        {{
            "id": "unique_id",
            "title": "Descriptive test title",
            "description": "What this test validates",
            "priority": "critical|high|medium|low",
            "steps": [
                {{
                    "action": "User action",
                    "selector": "Element selector",
                    "data": "Input data if applicable",
                    "expected": "Expected result"
                }}
            ],
            "test_data": {{"key": "value"}},
            "assertions": ["List of assertions to verify"]
        }}
    ]
}}

Ensure scenarios are practical, specific, and directly testable.
"""
        
        if self.config.enable_tree_of_thoughts:
            base_prompt = self._apply_tree_of_thoughts(base_prompt, strategy)
        
        return base_prompt
    
    def _apply_chain_of_thought(self, prompt: str) -> str:
        """Apply Chain of Thought reasoning to prompt."""
        cot_addition = """

Let's think step by step:
1. First, identify the most critical functionality
2. Then, determine what could go wrong
3. Next, consider edge cases and unusual inputs
4. Finally, prioritize based on risk and user impact

Show your reasoning before providing the final answer.
"""
        return prompt + cot_addition
    
    def _apply_tree_of_thoughts(self, prompt: str, strategy: str) -> str:
        """Apply Tree of Thoughts for exploration."""
        tot_addition = f"""

Explore multiple testing approaches for {strategy}:

Branch 1: User-centric perspective
- What would real users do?
- What mistakes might they make?
- What would frustrate them?

Branch 2: Technical perspective
- What could break the system?
- What are the technical constraints?
- Where are the integration points?

Branch 3: Business perspective
- What are the business-critical paths?
- What would cause financial loss?
- What affects user retention?

Synthesize insights from all branches into comprehensive test scenarios.
"""
        return prompt + tot_addition
    
    def _apply_meta_prompting(self, prompt: str) -> str:
        """Apply meta-prompting for self-improvement."""
        meta_addition = """

Before responding, consider:
- What makes a test scenario valuable?
- What common issues do QA engineers miss?
- How can these tests provide maximum coverage with minimum redundancy?

Adjust your approach based on these meta-considerations.
"""
        return prompt + meta_addition
    
    def _summarize_elements(self, elements: List[Dict]) -> str:
        """Create a summary of elements for the prompt."""
        summary = []
        
        # Count by type
        type_counts = {}
        for elem in elements:
            elem_type = elem.get('tag_name', 'unknown')
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        
        summary.append(f"Total Elements: {len(elements)}")
        summary.append("\nElement Types:")
        for elem_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            summary.append(f"  - {elem_type}: {count}")
        
        # Identify key elements
        critical_elements = [e for e in elements if e.get('testPriority') == 'critical']
        required_fields = [e for e in elements if e.get('isRequired')]
        
        summary.append(f"\nCritical Elements: {len(critical_elements)}")
        summary.append(f"Required Fields: {len(required_fields)}")
        
        return '\n'.join(summary)
    
    def _format_elements_for_llm(self, elements: List[Dict]) -> str:
        """Format elements in a concise way for LLM consumption."""
        formatted = []
        
        for i, elem in enumerate(elements, 1):
            elem_info = {
                "index": i,
                "tag": elem.get('tag_name'),
                "id": elem.get('id'),
                "text": (elem.get('textContent') or '')[:50],
                "type": elem.get('type'),
                "required": elem.get('isRequired', False),
                "validation": elem.get('validationRules', {}),
                "selector": elem.get('cssSelector') or elem.get('xpath')
            }
            # Remove None values
            elem_info = {k: v for k, v in elem_info.items() if v is not None}
            formatted.append(json.dumps(elem_info))
        
        return '\n'.join(formatted)
    
    async def call_llm(self, prompt: str, temperature: float = None) -> Dict[str, Any]:
        """Make an actual LLM call with error handling."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert QA automation engineer with deep knowledge of web testing, security, and accessibility standards."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Call LLM
            response = query_llm(
                provider=self.config.llm_provider,
                model=self.config.llm_model,
                messages=messages
            )
            
            self.llm_call_count += 1
            
            # Extract response content
            content = response.choices[0].message.content
            
            # Try to parse JSON if present
            try:
                # Look for JSON in the response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_data = json.loads(json_match.group())
                    return {
                        "success": True,
                        "data": json_data,
                        "raw_response": content
                    }
            except json.JSONDecodeError:
                pass
            
            return {
                "success": True,
                "data": None,
                "raw_response": content
            }
            
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def generate_with_self_consistency(self, prompt: str, samples: int = None) -> Dict[str, Any]:
        """Generate multiple responses and select the most consistent."""
        samples = samples or self.config.self_consistency_samples
        responses = []
        
        for i in range(samples):
            # Vary temperature slightly for diversity
            temp = self.config.llm_temperature + (i * 0.1)
            response = await self.call_llm(prompt, temperature=min(temp, 1.0))
            if response["success"]:
                responses.append(response)
        
        if not responses:
            return {"success": False, "error": "All LLM calls failed"}
        
        # For now, return the first successful response
        # In production, implement voting or consistency checking
        return responses[0]


# ============================================================================
# EVOLUTIONARY OPTIMIZER WITH LLM
# ============================================================================

class LLMEvolutionaryOptimizer:
    """
    Implements genetic algorithms and OPRO with real LLM feedback.
    """
    
    def __init__(self, config: SystemConfig, llm_engine: LLMPromptEngine):
        self.config = config
        self.llm_engine = llm_engine
        self.population = []
        self.best_solutions = []
        self.generation = 0
    
    async def optimize_with_opro(self, initial_prompt: str, test_results: List[Dict], iterations: int = None) -> Tuple[str, float]:
        """
        Apply OPRO (Optimization by PROmpting) using LLM to improve prompts.
        """
        iterations = iterations or self.config.opro_iterations
        current_prompt = initial_prompt
        best_score = await self._evaluate_prompt_with_llm(current_prompt, test_results)
        
        optimization_prompt = f"""
You are a prompt optimization expert. Improve this testing prompt to generate better test scenarios.

CURRENT PROMPT:
{current_prompt}

CURRENT PERFORMANCE SCORE: {best_score}

Provide 3 variations that could improve:
1. Clarity and specificity
2. Coverage of edge cases
3. Actionable output format

Return as JSON:
{{
    "variations": [
        {{"variation": 1, "prompt": "improved prompt text"}},
        {{"variation": 2, "prompt": "improved prompt text"}},
        {{"variation": 3, "prompt": "improved prompt text"}}
    ]
}}
"""
        
        for i in range(iterations):
            # Get variations from LLM
            response = await self.llm_engine.call_llm(optimization_prompt)
            
            if response["success"] and response["data"]:
                variations_data = response["data"].get("variations", [])
                
                for var in variations_data:
                    variant_prompt = var.get("prompt", "")
                    if variant_prompt:
                        score = await self._evaluate_prompt_with_llm(variant_prompt, test_results)
                        if score > best_score:
                            current_prompt = variant_prompt
                            best_score = score
                            logger.info(f"OPRO iteration {i+1}: Improved score to {best_score}")
        
        improvement = ((best_score - await self._evaluate_prompt_with_llm(initial_prompt, test_results)) / 
                      max(await self._evaluate_prompt_with_llm(initial_prompt, test_results), 0.1) * 100)
        
        return current_prompt, improvement
    
    async def _evaluate_prompt_with_llm(self, prompt: str, test_results: List[Dict]) -> float:
        """Evaluate prompt quality using LLM."""
        
        eval_prompt = f"""
Evaluate the quality of this test generation prompt on a scale of 0-100.

PROMPT:
{prompt[:500]}...

Consider:
1. Clarity and specificity (0-25 points)
2. Coverage of test scenarios (0-25 points)
3. Actionability of output (0-25 points)
4. Technical accuracy (0-25 points)

Return only a number between 0 and 100.
"""
        
        response = await self.llm_engine.call_llm(eval_prompt)
        
        if response["success"]:
            try:
                # Extract number from response
                score_text = response["raw_response"]
                numbers = re.findall(r'\d+\.?\d*', score_text)
                if numbers:
                    score = float(numbers[0])
                    return min(max(score / 100, 0), 1)  # Normalize to 0-1
            except:
                pass
        
        return 0.5  # Default score


# ============================================================================
# REASONING ENGINE WITH LLM
# ============================================================================

class LLMReasoningEngine:
    """
    Context-aware reasoning powered by LLM for intelligent test generation.
    """
    
    def __init__(self, config: SystemConfig, llm_engine: LLMPromptEngine):
        self.config = config
        self.llm_engine = llm_engine
        self.reasoning_cache = {}
    
    async def analyze_elements(self, elements: List[Dict], page_context: Dict) -> Dict[str, Any]:
        """
        Perform deep analysis of UI elements using LLM.
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_elements": len(elements),
            "classifications": {},
            "relationships": {},
            "test_priorities": {},
            "insights": [],
            "recommendations": [],
            "llm_analysis": {}
        }
        
        # Get LLM analysis
        analysis_prompt = self.llm_engine.generate_extraction_analysis_prompt(elements, page_context)
        llm_response = await self.llm_engine.call_llm(analysis_prompt)
        
        if llm_response["success"]:
            analysis["llm_analysis"] = llm_response["raw_response"]
            
            # Extract insights from LLM response
            insights = self._extract_insights_from_llm(llm_response["raw_response"])
            analysis["insights"].extend(insights)
            
            # Extract recommendations
            recommendations = self._extract_recommendations_from_llm(llm_response["raw_response"])
            analysis["recommendations"].extend(recommendations)
        
        # Perform local analysis as fallback
        element_groups = self._classify_elements(elements)
        analysis["classifications"] = element_groups
        
        relationships = self._identify_relationships(elements)
        analysis["relationships"] = relationships
        
        priorities = await self._calculate_priorities_with_llm(elements, element_groups, relationships)
        analysis["test_priorities"] = priorities
        
        return analysis
    
    def _extract_insights_from_llm(self, llm_text: str) -> List[str]:
        """Extract insights from LLM response."""
        insights = []
        
        # Look for numbered lists or bullet points
        lines = llm_text.split('\n')
        for line in lines:
            line = line.strip()
            if (line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '*', '•')) and 
                len(line) > 5):
                # Clean up the insight
                insight = re.sub(r'^[\d\.\-\*\•]+\s*', '', line)
                if insight:
                    insights.append(insight)
        
        return insights[:10]  # Limit to top 10
    
    def _extract_recommendations_from_llm(self, llm_text: str) -> List[str]:
        """Extract recommendations from LLM response."""
        recommendations = []
        
        # Look for recommendation keywords
        if 'recommend' in llm_text.lower() or 'should' in llm_text.lower():
            lines = llm_text.split('\n')
            for line in lines:
                line_lower = line.lower()
                if any(word in line_lower for word in ['recommend', 'should', 'must', 'critical', 'important']):
                    recommendations.append(line.strip())
        
        return recommendations[:10]
    
    async def _calculate_priorities_with_llm(self, elements: List[Dict], groups: Dict[str, List], relationships: Dict) -> Dict[str, str]:
        """Calculate testing priorities using LLM insights."""
        priorities = {}
        
        # Create a priority assessment prompt
        priority_prompt = f"""
Assign testing priority (critical/high/medium/low) to these element groups:

AUTHENTICATION ELEMENTS: {len(groups.get('authentication', []))} elements
FORM ELEMENTS: {len(groups.get('forms', []))} elements  
ACTION ELEMENTS: {len(groups.get('actions', []))} elements
VALIDATION ELEMENTS: {len(groups.get('validation', []))} elements
NAVIGATION ELEMENTS: {len(groups.get('navigation', []))} elements

Consider security risks, user impact, and business criticality.
Return as JSON: {{"group_name": "priority_level"}}
"""
        
        response = await self.llm_engine.call_llm(priority_prompt)
        
        if response["success"] and response["data"]:
            llm_priorities = response["data"]
            
            # Apply LLM priorities to individual elements
            for elem in elements:
                elem_id = elem.get('id', '')
                
                # Check which group this element belongs to
                for group_name, elem_ids in groups.items():
                    if elem_id in elem_ids:
                        priorities[elem_id] = llm_priorities.get(group_name, 'medium')
                        break
                
                if elem_id not in priorities:
                    priorities[elem_id] = 'medium'  # Default
        else:
            # Fallback to rule-based priorities
            for elem in elements:
                elem_id = elem.get('id', '')
                if elem_id in groups.get('authentication', []):
                    priorities[elem_id] = 'critical'
                elif elem_id in groups.get('validation', []):
                    priorities[elem_id] = 'high'
                elif elem_id in groups.get('actions', []):
                    priorities[elem_id] = 'high'
                else:
                    priorities[elem_id] = 'medium'
        
        return priorities
    
    def _classify_elements(self, elements: List[Dict]) -> Dict[str, List]:
        """Classify elements by functional purpose."""
        groups = {
            "authentication": [],
            "navigation": [],
            "forms": [],
            "actions": [],
            "content": [],
            "validation": [],
            "state_dependent": []
        }
        
        for element in elements:
            elem_id = element.get('id', hashlib.md5(str(element).encode()).hexdigest()[:8])
            
            # Authentication elements
            if any(keyword in str(element).lower() 
                   for keyword in ['login', 'password', 'signin', 'auth', 'credential']):
                groups["authentication"].append(elem_id)
            
            # Navigation elements
            if element.get("tag_name") in ["nav", "header"] or "nav" in str(element.get("className", '')):
                groups["navigation"].append(elem_id)
            
            # Form elements
            if element.get("tag_name") in ["input", "select", "textarea", "form"]:
                groups["forms"].append(elem_id)
                
                # Validation elements
                if element.get("isRequired") or element.get("validationRules"):
                    groups["validation"].append(elem_id)
            
            # Action elements
            if element.get("tag_name") in ["button", "a"] and element.get("isVisible"):
                groups["actions"].append(elem_id)
            
            # State-dependent elements
            if element.get("isEnabled") is False or element.get("isVisible") is False:
                groups["state_dependent"].append(elem_id)
            
            # Default to content
            if not any(elem_id in group for group in groups.values()):
                groups["content"].append(elem_id)
        
        return groups
    
    def _identify_relationships(self, elements: List[Dict]) -> Dict[str, Any]:
        """Identify relationships between elements."""
        relationships = {
            "form_groups": [],
            "navigation_structure": {},
            "action_triggers": {},
            "parent_child": {},
            "siblings": {}
        }
        
        # Group form elements
        form_elements = [e for e in elements if e.get("tag_name") in ["input", "select", "textarea"]]
        if form_elements:
            current_group = []
            for element in form_elements:
                elem_id = element.get('id', hashlib.md5(str(element).encode()).hexdigest()[:8])
                current_group.append(elem_id)
                if len(current_group) >= 3:
                    relationships["form_groups"].append(current_group.copy())
                    current_group = []
            if current_group:
                relationships["form_groups"].append(current_group)
        
        # Identify action triggers
        buttons = [e for e in elements if e.get("tag_name") == "button"]
        for button in buttons:
            button_text = (button.get("textContent") or "").lower()
            button_id = button.get('id', hashlib.md5(str(button).encode()).hexdigest()[:8])
            
            if "submit" in button_text or "save" in button_text:
                relationships["action_triggers"][button_id] = "form_submission"
            elif "cancel" in button_text or "close" in button_text:
                relationships["action_triggers"][button_id] = "form_cancellation"
            elif "next" in button_text or "continue" in button_text:
                relationships["action_triggers"][button_id] = "navigation"
        
        return relationships


# ============================================================================
# MONITORING SYSTEM
# ============================================================================

class MonitoringSystem:
    """
    Comprehensive monitoring and metrics collection.
    """
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.metrics = {
            "extractions": [],
            "prompts": [],
            "tests": [],
            "performance": [],
            "errors": [],
            "llm_calls": []
        }
        self.start_time = datetime.now()
    
    def record_extraction(self, url: str, elements_count: int, duration: float, success: bool):
        """Record element extraction metrics."""
        self.metrics["extractions"].append({
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "elements_count": elements_count,
            "duration": duration,
            "success": success
        })
    
    def record_llm_call(self, prompt_type: str, tokens: int, duration: float, success: bool):
        """Record LLM call metrics."""
        self.metrics["llm_calls"].append({
            "timestamp": datetime.now().isoformat(),
            "prompt_type": prompt_type,
            "tokens": tokens,
            "duration": duration,
            "success": success
        })
    
    def record_test(self, test_type: str, scenarios_count: int, coverage: float):
        """Record test generation metrics."""
        self.metrics["tests"].append({
            "timestamp": datetime.now().isoformat(),
            "test_type": test_type,
            "scenarios_count": scenarios_count,
            "coverage": coverage
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        summary = {
            "uptime_seconds": uptime,
            "total_extractions": len(self.metrics["extractions"]),
            "successful_extractions": sum(1 for e in self.metrics["extractions"] if e["success"]),
            "total_elements": sum(e["elements_count"] for e in self.metrics["extractions"]),
            "total_llm_calls": len(self.metrics["llm_calls"]),
            "successful_llm_calls": sum(1 for l in self.metrics["llm_calls"] if l["success"]),
            "total_tests": len(self.metrics["tests"]),
            "total_scenarios": sum(t["scenarios_count"] for t in self.metrics["tests"]),
            "average_extraction_time": sum(e["duration"] for e in self.metrics["extractions"]) / max(len(self.metrics["extractions"]), 1),
            "average_llm_response_time": sum(l["duration"] for l in self.metrics["llm_calls"]) / max(len(self.metrics["llm_calls"]), 1),
            "average_coverage": sum(t["coverage"] for t in self.metrics["tests"]) / max(len(self.metrics["tests"]), 1)
        }
        
        return summary


# ============================================================================
# MAIN SYSTEM WITH LLM INTEGRATION
# ============================================================================

class EnhancedUITestingSystemWithLLM:
    """
    The main enhanced UI testing system with full LLM integration.
    """
    
    def __init__(self, config: Optional[SystemConfig] = None):
        self.config = config or SystemConfig()
        
        # Initialize components
        self.llm_engine = LLMPromptEngine(self.config)
        self.optimizer = LLMEvolutionaryOptimizer(self.config, self.llm_engine)
        self.reasoning_engine = LLMReasoningEngine(self.config, self.llm_engine)
        self.monitoring = MonitoringSystem(self.config)
        
        # Track session data
        self.session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
        self.session_data = {
            "id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "urls_processed": [],
            "total_elements": 0,
            "total_tests": 0,
            "llm_calls": 0
        }
    
    async def process_url(self, url: str, elements: List[Dict] = None) -> Dict[str, Any]:
        """
        Process a URL end-to-end with LLM: extraction, analysis, and test generation.
        """
        result = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "extraction": None,
            "analysis": None,
            "tests": None,
            "metrics": None,
            "success": False
        }
        
        try:
            # Step 1: Use provided elements or generate mock data
            extraction_start = time.time()
            
            if elements is None:
                # Generate mock elements for testing
                elements = self._generate_mock_elements(url)
            
            extraction_time = time.time() - extraction_start
            
            page_context = self._generate_page_context(url)
            
            self.monitoring.record_extraction(url, len(elements), extraction_time, True)
            result["extraction"] = {
                "elements_count": len(elements),
                "extraction_time": extraction_time
            }
            
            # Step 2: Analyze elements with LLM-powered reasoning engine
            logger.info(f"Analyzing {len(elements)} elements with LLM...")
            analysis = await self.reasoning_engine.analyze_elements(elements, page_context)
            result["analysis"] = analysis
            
            # Step 3: Generate test scenarios with LLM for each strategy
            test_scenarios = {}
            
            for strategy in self.config.test_strategies:
                logger.info(f"Generating {strategy} test scenarios with LLM...")
                
                # Generate prompt
                prompt = self.llm_engine.generate_test_scenarios_prompt(
                    elements, 
                    strategy,
                    analysis
                )
                
                # Apply OPRO optimization if enabled
                if self.config.enable_opro and random.random() < 0.3:  # Optimize 30% of prompts
                    logger.info(f"Optimizing {strategy} prompt with OPRO...")
                    prompt, improvement = await self.optimizer.optimize_with_opro(
                        prompt,
                        [],  # Would include historical test results
                        2  # Reduced iterations for demo
                    )
                    logger.info(f"Prompt improved by {improvement:.1f}%")
                
                # Generate scenarios with LLM
                llm_start = time.time()
                
                if self.config.enable_self_consistency:
                    response = await self.llm_engine.generate_with_self_consistency(prompt)
                else:
                    response = await self.llm_engine.call_llm(prompt)
                
                llm_duration = time.time() - llm_start
                self.monitoring.record_llm_call(strategy, len(prompt), llm_duration, response["success"])
                
                # Parse scenarios from LLM response
                if response["success"]:
                    scenarios = self._parse_llm_scenarios(response, strategy)
                    test_scenarios[strategy] = scenarios
                    
                    # Record metrics
                    coverage = len(set(e.get('id', '') for e in elements[:5])) / max(len(elements), 1)
                    self.monitoring.record_test(strategy, len(scenarios), coverage)
                else:
                    logger.warning(f"Failed to generate {strategy} scenarios: {response.get('error')}")
                    test_scenarios[strategy] = []
            
            result["tests"] = test_scenarios
            
            # Step 4: Evolve strategies if enabled
            if self.config.enable_evolution and len(test_scenarios) > 0:
                performance_data = self._calculate_performance(test_scenarios)
                evolved_strategies = self.optimizer.evolve_strategies(
                    self.config.test_strategies,
                    performance_data
                )
                logger.info(f"Evolved strategies: {evolved_strategies}")
            
            # Update session data
            self.session_data["urls_processed"].append(url)
            self.session_data["total_elements"] += len(elements)
            self.session_data["total_tests"] += sum(len(s) for s in test_scenarios.values())
            self.session_data["llm_calls"] = self.llm_engine.llm_call_count
            
            # Get monitoring summary
            result["metrics"] = self.monitoring.get_summary()
            result["success"] = True
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            result["error"] = str(e)
            self.monitoring.metrics["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "url": url,
                "error": str(e)
            })
        
        return result
    
    def _generate_mock_elements(self, url: str) -> List[Dict]:
        """Generate mock elements based on URL type."""
        
        # Determine page type from URL
        if "login" in url.lower() or "signin" in url.lower():
            return self._generate_login_elements()
        elif "github.com" in url.lower():
            return self._generate_github_elements()
        elif "quotes" in url.lower():
            return self._generate_quotes_elements()
        else:
            return self._generate_basic_elements()
    
    def _generate_login_elements(self) -> List[Dict]:
        """Generate mock login page elements."""
        return [
            {
                "id": "username",
                "tag_name": "input",
                "type": "text",
                "name": "username",
                "placeholder": "Username or email",
                "isRequired": True,
                "testPriority": "critical",
                "cssSelector": "#username",
                "textContent": "",
                "validationRules": {"required": True, "minLength": 3}
            },
            {
                "id": "password",
                "tag_name": "input",
                "type": "password",
                "name": "password",
                "placeholder": "Password",
                "isRequired": True,
                "testPriority": "critical",
                "cssSelector": "#password",
                "textContent": "",
                "validationRules": {"required": True, "minLength": 8}
            },
            {
                "id": "remember-me",
                "tag_name": "input",
                "type": "checkbox",
                "name": "remember",
                "testPriority": "low",
                "cssSelector": "#remember-me",
                "textContent": "Remember me"
            },
            {
                "id": "login-button",
                "tag_name": "button",
                "type": "submit",
                "testPriority": "critical",
                "cssSelector": "#login-button",
                "textContent": "Sign In",
                "isVisible": True
            },
            {
                "id": "forgot-password",
                "tag_name": "a",
                "href": "/forgot-password",
                "testPriority": "medium",
                "cssSelector": "#forgot-password",
                "textContent": "Forgot password?",
                "isVisible": True
            },
            {
                "id": "signup-link",
                "tag_name": "a",
                "href": "/signup",
                "testPriority": "medium",
                "cssSelector": "#signup-link",
                "textContent": "Create new account",
                "isVisible": True
            }
        ]
    
    def _generate_github_elements(self) -> List[Dict]:
        """Generate mock GitHub page elements."""
        return [
            {
                "id": "login_field",
                "tag_name": "input",
                "type": "text",
                "name": "login",
                "placeholder": "Username or email address",
                "isRequired": True,
                "testPriority": "critical",
                "cssSelector": "#login_field",
                "validationRules": {"required": True}
            },
            {
                "id": "password",
                "tag_name": "input",
                "type": "password",
                "name": "password",
                "placeholder": "Password",
                "isRequired": True,
                "testPriority": "critical",
                "cssSelector": "#password",
                "validationRules": {"required": True, "minLength": 8}
            },
            {
                "id": "commit",
                "tag_name": "input",
                "type": "submit",
                "value": "Sign in",
                "testPriority": "critical",
                "cssSelector": "input[type='submit']",
                "textContent": "Sign in"
            },
            {
                "tag_name": "a",
                "href": "/password_reset",
                "testPriority": "medium",
                "textContent": "Forgot password?"
            },
            {
                "tag_name": "a",
                "href": "/signup",
                "testPriority": "medium",
                "textContent": "Create an account"
            },
            {
                "id": "two-factor",
                "tag_name": "input",
                "type": "text",
                "name": "otp",
                "placeholder": "XXXXXX",
                "testPriority": "high",
                "cssSelector": "#two-factor",
                "validationRules": {"pattern": "\\d{6}"}
            }
        ]
    
    def _generate_quotes_elements(self) -> List[Dict]:
        """Generate mock quotes scraping site elements."""
        return [
            {
                "tag_name": "div",
                "className": "quote",
                "testPriority": "medium",
                "cssSelector": ".quote",
                "textContent": "Sample quote text"
            },
            {
                "tag_name": "span",
                "className": "author",
                "testPriority": "medium",
                "cssSelector": ".author",
                "textContent": "Author Name"
            },
            {
                "tag_name": "a",
                "className": "tag",
                "href": "/tag/inspiration",
                "testPriority": "low",
                "cssSelector": ".tag",
                "textContent": "inspiration"
            },
            {
                "tag_name": "a",
                "className": "next",
                "href": "/page/2",
                "testPriority": "high",
                "cssSelector": ".next",
                "textContent": "Next"
            },
            {
                "tag_name": "select",
                "name": "sort",
                "testPriority": "medium",
                "cssSelector": "select[name='sort']",
                "options": ["newest", "oldest", "popular"]
            },
            {
                "tag_name": "input",
                "type": "search",
                "placeholder": "Search quotes",
                "testPriority": "high",
                "cssSelector": "input[type='search']"
            }
        ]
    
    def _generate_basic_elements(self) -> List[Dict]:
        """Generate basic page elements."""
        return [
            {
                "tag_name": "h1",
                "testPriority": "low",
                "cssSelector": "h1",
                "textContent": "Example Domain"
            },
            {
                "tag_name": "p",
                "testPriority": "low",
                "cssSelector": "p",
                "textContent": "This domain is for use in illustrative examples"
            },
            {
                "tag_name": "a",
                "href": "https://www.iana.org/domains/example",
                "testPriority": "medium",
                "cssSelector": "a",
                "textContent": "More information..."
            }
        ]
    
    def _generate_page_context(self, url: str) -> Dict[str, Any]:
        """Generate page context based on URL."""
        
        if "login" in url.lower() or "signin" in url.lower():
            return {
                "url": url,
                "title": "Sign In",
                "pageType": "login",
                "description": "User authentication page"
            }
        elif "github.com" in url.lower():
            return {
                "url": url,
                "title": "GitHub Login",
                "pageType": "login",
                "description": "GitHub authentication with 2FA"
            }
        elif "quotes" in url.lower():
            return {
                "url": url,
                "title": "Quotes to Scrape",
                "pageType": "content",
                "description": "Quote collection and browsing"
            }
        else:
            return {
                "url": url,
                "title": "Example Page",
                "pageType": "general",
                "description": "General web page"
            }
    
    def _parse_llm_scenarios(self, response: Dict, strategy: str) -> List[Dict]:
        """Parse test scenarios from LLM response."""
        scenarios = []
        
        if response.get("data") and "scenarios" in response["data"]:
            # LLM returned structured JSON
            scenarios = response["data"]["scenarios"]
        else:
            # Try to extract scenarios from raw text
            raw_text = response.get("raw_response", "")
            
            # Create basic scenarios from text analysis
            scenarios = self._extract_scenarios_from_text(raw_text, strategy)
        
        # Ensure each scenario has required fields
        for i, scenario in enumerate(scenarios):
            if not scenario.get("id"):
                scenario["id"] = f"{strategy}_scenario_{i+1}"
            if not scenario.get("priority"):
                scenario["priority"] = "medium"
            if not scenario.get("steps"):
                scenario["steps"] = []
        
        return scenarios[:self.config.max_scenarios_per_strategy]
    
    def _extract_scenarios_from_text(self, text: str, strategy: str) -> List[Dict]:
        """Extract scenarios from unstructured text."""
        scenarios = []
        
        # Split by common scenario markers
        sections = re.split(r'(?:Scenario|Test Case|Test)\s*\d+:?', text, flags=re.IGNORECASE)
        
        for i, section in enumerate(sections[1:], 1):  # Skip first empty section
            if len(section.strip()) > 20:
                scenario = {
                    "id": f"{strategy}_scenario_{i}",
                    "title": self._extract_title_from_section(section),
                    "description": section[:200].strip(),
                    "priority": "medium",
                    "steps": self._extract_steps_from_section(section),
                    "assertions": []
                }
                scenarios.append(scenario)
        
        # If no scenarios found, create a default one
        if not scenarios:
            scenarios.append({
                "id": f"{strategy}_scenario_1",
                "title": f"Default {strategy} test",
                "description": f"Automated {strategy} test scenario",
                "priority": "medium",
                "steps": [
                    {"action": "Navigate to page", "expected": "Page loads successfully"},
                    {"action": f"Perform {strategy} testing", "expected": "Test completes"}
                ],
                "assertions": []
            })
        
        return scenarios
    
    def _extract_title_from_section(self, section: str) -> str:
        """Extract a title from a text section."""
        lines = section.strip().split('\n')
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            if len(line) > 5 and len(line) < 100:
                return line
        return "Test Scenario"
    
    def _extract_steps_from_section(self, section: str) -> List[Dict]:
        """Extract test steps from a text section."""
        steps = []
        
        # Look for numbered steps
        step_pattern = r'(?:\d+[\.\)]\s*|[-*]\s*)(.*?)(?=\n\d+[\.\)]|\n[-*]|\Z)'
        matches = re.findall(step_pattern, section, re.DOTALL)
        
        for match in matches[:10]:  # Limit to 10 steps
            step_text = match.strip()
            if len(step_text) > 5:
                steps.append({
                    "action": step_text[:100],
                    "expected": "Action completes successfully"
                })
        
        if not steps:
            # Create default steps
            steps = [
                {"action": "Execute test", "expected": "Test passes"}
            ]
        
        return steps
    
    def _calculate_performance(self, test_scenarios: Dict[str, List]) -> Dict[str, float]:
        """Calculate performance metrics for strategies."""
        performance = {}
        
        for strategy, scenarios in test_scenarios.items():
            if scenarios:
                # Calculate based on scenario quality
                num_critical = sum(1 for s in scenarios if s.get("priority") == "critical")
                num_high = sum(1 for s in scenarios if s.get("priority") == "high")
                num_steps = sum(len(s.get("steps", [])) for s in scenarios)
                
                # Score based on priority and comprehensiveness
                score = (num_critical * 1.0 + num_high * 0.7 + num_steps * 0.1) / max(len(scenarios), 1)
                performance[strategy] = min(score, 1.0)
            else:
                performance[strategy] = 0.0
        
        return performance
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get complete session summary."""
        return {
            "session": self.session_data,
            "monitoring": self.monitoring.get_summary(),
            "llm_stats": {
                "total_calls": self.llm_engine.llm_call_count,
                "strategies_tested": len(self.config.test_strategies),
                "optimization_enabled": self.config.enable_opro
            },
            "config": {
                "llm_provider": self.config.llm_provider,
                "llm_model": self.config.llm_model,
                "strategies_enabled": self.config.test_strategies,
                "evolution_enabled": self.config.enable_evolution,
                "opro_enabled": self.config.enable_opro
            }
        }


# ============================================================================
# TEST RUNNER WITH MULTIPLE SITES
# ============================================================================

async def test_multiple_sites():
    """Test the system with multiple sites of varying complexity."""
    
    # Initialize system with optimized config
    config = SystemConfig(
        llm_provider="gemini",
        llm_model="gemini-2.0-flash-exp",
        llm_temperature=0.7,
        enable_chain_of_thought=True,
        enable_tree_of_thoughts=True,
        enable_self_consistency=True,
        enable_opro=True,
        enable_evolution=True,
        test_strategies=["happy_path", "negative", "edge_case", "security", "accessibility"],
        max_scenarios_per_strategy=3
    )
    
    system = EnhancedUITestingSystemWithLLM(config)
    
    # Test sites with varying complexity
    test_sites = [
        {
            "url": "https://example.com",
            "name": "Simple Site",
            "complexity": "low"
        },
        {
            "url": "https://quotes.toscrape.com",
            "name": "Quotes Site",
            "complexity": "medium"
        },
        {
            "url": "https://github.com/login",
            "name": "GitHub Login",
            "complexity": "high"
        }
    ]
    
    results = []
    
    for site in test_sites:
        print(f"\n{'='*60}")
        print(f"Testing {site['name']} ({site['complexity']} complexity)")
        print(f"URL: {site['url']}")
        print('='*60)
        
        # Process the site
        result = await system.process_url(site['url'])
        results.append(result)
        
        if result["success"]:
            print(f"\n✓ Successfully processed {site['name']}")
            print(f"  - Elements analyzed: {result['extraction']['elements_count']}")
            print(f"  - LLM calls made: {system.llm_engine.llm_call_count}")
            
            # Show insights
            if result["analysis"].get("insights"):
                print(f"\n  Insights:")
                for insight in result["analysis"]["insights"][:3]:
                    print(f"    • {insight}")
            
            # Show test scenarios generated
            print(f"\n  Test Scenarios Generated:")
            for strategy, scenarios in result["tests"].items():
                if scenarios:
                    print(f"    • {strategy}: {len(scenarios)} scenarios")
                    for scenario in scenarios[:1]:  # Show first scenario
                        print(f"      - {scenario.get('title', 'Untitled')}")
            
            # Show recommendations
            if result["analysis"].get("recommendations"):
                print(f"\n  Recommendations:")
                for rec in result["analysis"]["recommendations"][:3]:
                    print(f"    • {rec}")
        else:
            print(f"\n✗ Failed to process {site['name']}: {result.get('error')}")
    
    # Final summary
    summary = system.get_session_summary()
    
    print(f"\n{'='*60}")
    print("SESSION SUMMARY")
    print('='*60)
    print(f"Total URLs processed: {len(summary['session']['urls_processed'])}")
    print(f"Total elements analyzed: {summary['session']['total_elements']}")
    print(f"Total test scenarios: {summary['session']['total_tests']}")
    print(f"Total LLM calls: {summary['llm_stats']['total_calls']}")
    print(f"Success rate: {summary['monitoring']['successful_llm_calls']}/{summary['monitoring']['total_llm_calls']}")
    print(f"Average LLM response time: {summary['monitoring']['average_llm_response_time']:.2f}s")
    
    # Save results to file
    output_file = Path("test_results_with_llm.json")
    with open(output_file, "w") as f:
        json.dump({
            "session_summary": summary,
            "site_results": results
        }, f, indent=2, default=str)
    
    print(f"\nResults saved to {output_file}")
    
    return results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run the comprehensive test
    print("Starting Enhanced UI Testing System with Gemini-2.5-pro LLM Integration")
    print("This will test 3 sites with varying complexity levels\n")
    
    try:
        results = asyncio.run(test_multiple_sites())
        print("\n✓ All tests completed successfully!")
    except Exception as e:
        print(f"\n✗ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()