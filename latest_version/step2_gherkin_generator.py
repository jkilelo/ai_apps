#!/usr/bin/env python3
"""
Comprehensive Gherkin Test Generator
Generates high-quality Gherkin test cases from extracted elements using LLM.

Single-file implementation following CODER strategy.
Supports OpenAI, Claude, and Gemini models.
"""

import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# FOUNDATION LAYER - Data Models
# ============================================================================

@dataclass
class ExtractedElement:
    """Represents an extracted web element - compatible with ElementData from Step 1."""
    tag_name: str
    element_type: str
    xpath: str
    css_selector: str
    text_content: str = ""
    inner_html: str = ""  # Added for Step 1 compatibility
    outer_html: str = ""  # Added for Step 1 compatibility
    id: Optional[str] = None
    class_names: List[str] = field(default_factory=list)
    name: Optional[str] = None
    href: Optional[str] = None
    src: Optional[str] = None  # Added for Step 1 compatibility
    alt: Optional[str] = None  # Added for Step 1 compatibility
    title: Optional[str] = None  # Added for Step 1 compatibility
    is_clickable: bool = False
    is_visible: bool = True
    is_enabled: bool = True  # Added for Step 1 compatibility
    role: Optional[str] = None
    aria_label: Optional[str] = None
    placeholder: Optional[str] = None
    value: Optional[str] = None
    input_type: Optional[str] = None
    interaction_type: str = "unknown"
    confidence_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

@dataclass
class TestScenario:
    """Represents a test scenario."""
    name: str
    description: str
    scenario_type: str  # positive, negative, edge_case
    steps: List[Dict[str, str]]
    tags: List[str] = field(default_factory=list)
    examples: Optional[Dict[str, Any]] = None
    priority: str = "medium"  # high, medium, low
    confidence: float = 1.0

@dataclass
class GherkinFeature:
    """Represents a complete Gherkin feature."""
    name: str
    description: str
    scenarios: List[TestScenario]
    background: Optional[List[Dict[str, str]]] = None
    tags: List[str] = field(default_factory=list)
    url: str = ""
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_gherkin(self) -> str:
        """Convert to Gherkin format string."""
        lines = []
        
        # Feature tags
        if self.tags:
            lines.append(" ".join(f"@{tag}" for tag in self.tags))
        
        # Feature header
        lines.append(f"Feature: {self.name}")
        if self.description:
            for line in self.description.split("\n"):
                lines.append(f"  {line}")
        lines.append("")
        
        # Background
        if self.background:
            lines.append("  Background:")
            for step in self.background:
                lines.append(f"    {step['keyword']} {step['text']}")
            lines.append("")
        
        # Scenarios
        for scenario in self.scenarios:
            # Scenario tags
            if scenario.tags:
                lines.append("  " + " ".join(f"@{tag}" for tag in scenario.tags))
            
            # Scenario header
            if scenario.examples:
                lines.append(f"  Scenario Outline: {scenario.name}")
            else:
                lines.append(f"  Scenario: {scenario.name}")
            
            # Steps
            for step in scenario.steps:
                lines.append(f"    {step['keyword']} {step['text']}")
                if 'data_table' in step:
                    for row in step['data_table']:
                        lines.append(f"      | {' | '.join(row)} |")
            
            # Examples for Scenario Outline
            if scenario.examples:
                lines.append("    Examples:")
                headers = scenario.examples['headers']
                lines.append(f"      | {' | '.join(headers)} |")
                for row in scenario.examples['rows']:
                    lines.append(f"      | {' | '.join(str(v) for v in row)} |")
            
            lines.append("")
        
        return "\n".join(lines)

class ScenarioType(Enum):
    """Types of test scenarios."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    EDGE_CASE = "edge_case"
    SMOKE = "smoke"
    REGRESSION = "regression"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"

# ============================================================================
# LLM PROVIDER LAYER
# ============================================================================

class LLMProvider:
    """
    Unified interface for multiple LLM providers.
    Supports OpenAI, Claude, and Gemini.
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize LLM provider.
        
        Args:
            api_keys: Dictionary with keys 'openai', 'anthropic', 'google'
        """
        self.api_keys = api_keys or {}
        
        # Get API keys from environment if not provided
        if not self.api_keys.get('openai'):
            self.api_keys['openai'] = os.getenv('OPENAI_API_KEY', '')
        if not self.api_keys.get('anthropic'):
            self.api_keys['anthropic'] = os.getenv('ANTHROPIC_API_KEY', '')
        if not self.api_keys.get('google'):
            self.api_keys['google'] = os.getenv('GOOGLE_API_KEY', '')
        
        # Model configurations
        self.models = {
            'gpt-4': {'provider': 'openai', 'temperature': 0.7, 'max_tokens': 4000},
            'gpt-4-turbo': {'provider': 'openai', 'temperature': 0.7, 'max_tokens': 4000},
            'claude-3-opus': {'provider': 'anthropic', 'temperature': 0.5, 'max_tokens': 4000},
            'claude-3-sonnet': {'provider': 'anthropic', 'temperature': 0.5, 'max_tokens': 4000},
            'gemini-pro': {'provider': 'google', 'temperature': 0.6, 'max_tokens': 4000}
        }
        
        self._call_count = 0
        self._errors = []
        
        # Try to import providers
        self._init_providers()
    
    def _init_providers(self):
        """Initialize available providers."""
        self.providers = {}
        
        # We'll use the local llm.py module for all providers
        # Just mark them as available if API keys exist
        if self.api_keys.get('openai') or os.getenv('OPENAI_API_KEY'):
            self.providers['openai'] = True
            logger.info("OpenAI provider initialized")
        
        if self.api_keys.get('anthropic') or os.getenv('ANTHROPIC_API_KEY'):
            self.providers['anthropic'] = True
            logger.info("Anthropic provider initialized")
        
        if self.api_keys.get('google') or os.getenv('GOOGLE_API_KEY'):
            self.providers['google'] = True
            logger.info("Google Gemini provider initialized")
    
    async def generate(
        self,
        prompt: str,
        model: str = 'gpt-4',
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: The prompt to send
            model: Model to use
            temperature: Override temperature
            max_tokens: Override max tokens
            
        Returns:
            Generated response text
        """
        self._call_count += 1
        
        model_config = self.models.get(model, self.models['gpt-4'])
        provider = model_config['provider']
        
        if provider not in self.providers:
            # Fallback to any available provider
            if self.providers:
                provider = list(self.providers.keys())[0]
                logger.warning(f"Falling back to {provider} provider")
            else:
                raise ValueError("No LLM providers available. Please set API keys.")
        
        temp = temperature or model_config['temperature']
        tokens = max_tokens or model_config['max_tokens']
        
        try:
            if provider == 'openai':
                return await self._generate_openai(prompt, model, temp, tokens)
            elif provider == 'anthropic':
                return await self._generate_anthropic(prompt, model, temp, tokens)
            elif provider == 'google':
                return await self._generate_gemini(prompt, temp, tokens)
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            self._errors.append({'time': datetime.now(), 'error': str(e)})
            logger.error(f"LLM generation failed: {e}")
            raise
    
    async def _generate_openai(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        """Generate using OpenAI."""
        # Use the local llm.py module with correct model names
        from llm import query_llm
        
        messages = [
            {"role": "system", "content": "You are an expert QA engineer generating comprehensive test cases in Gherkin format."},
            {"role": "user", "content": prompt}
        ]
        
        # Use the actual model from llm.py - gpt-5 as shown in the test
        response = await asyncio.to_thread(
            query_llm,
            "openai",
            "gpt-5",  # Using the actual model from llm.py
            messages
        )
        
        return response.choices[0].message.content
    
    async def _generate_anthropic(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        """Generate using Anthropic Claude."""
        from llm import query_llm
        
        messages = [
            {"role": "system", "content": "You are an expert QA engineer generating comprehensive test cases in Gherkin format."},
            {"role": "user", "content": prompt}
        ]
        
        # Use the actual model from llm.py - claude-sonnet-4-20250514
        response = await asyncio.to_thread(
            query_llm,
            "claude",
            "claude-sonnet-4-20250514",  # Using the actual model from llm.py
            messages
        )
        
        return response.choices[0].message.content
    
    async def _generate_gemini(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate using Google Gemini."""
        from llm import query_llm
        
        messages = [
            {"role": "system", "content": "You are an expert QA engineer generating comprehensive test cases in Gherkin format."},
            {"role": "user", "content": prompt}
        ]
        
        # Use the actual model from llm.py - gemini-2.5-pro
        response = await asyncio.to_thread(
            query_llm,
            "gemini",
            "gemini-2.5-pro",  # Using the actual model from llm.py
            messages
        )
        
        return response.choices[0].message.content

# ============================================================================
# PROMPT ENGINEERING LAYER
# ============================================================================

class PromptTemplates:
    """Manages prompt templates for test generation."""
    
    @staticmethod
    def get_analysis_prompt(elements: List[ExtractedElement], url: str) -> str:
        """Get prompt for analyzing elements and identifying test scenarios."""
        
        # Prepare element summary
        element_summary = PromptTemplates._create_element_summary(elements)
        
        prompt = f"""Analyze the following web page elements and identify test scenarios.

URL: {url}
Total Elements: {len(elements)}

Element Summary:
{element_summary}

Identify and describe:
1. The main purpose of this page
2. Key user workflows that should be tested
3. Critical functionality that needs validation
4. Potential edge cases and error scenarios
5. Security and accessibility concerns

For each identified test scenario, specify:
- Scenario name
- Type (positive, negative, edge_case, security, accessibility)
- Priority (high, medium, low)
- Key elements involved

Provide your analysis in a structured format."""
        
        return prompt
    
    @staticmethod
    def get_gherkin_generation_prompt(
        elements: List[ExtractedElement],
        analysis: str,
        url: str,
        options: Dict[str, Any]
    ) -> str:
        """Get prompt for generating Gherkin scenarios."""
        
        element_reference = PromptTemplates._create_element_reference(elements)
        
        prompt = f"""Generate comprehensive Gherkin test scenarios based on the following analysis and elements.

URL: {url}
Analysis:
{analysis}

Available Elements for Testing:
{element_reference}

Requirements:
- Generate {options.get('max_scenarios', 10)} test scenarios
- Include {options.get('scenario_types', 'positive, negative, and edge cases')}
- Use proper Gherkin syntax (Given/When/Then)
- Make steps specific and actionable
- Reference actual elements from the page
- Include data tables where appropriate
- Use scenario outlines for data-driven tests

Format each scenario as follows:
Scenario: [Name]
  Given [precondition]
  When [action]
  Then [expected result]

Include tags for categorization (@smoke, @regression, @critical, etc.)

Generate comprehensive test coverage for this page."""
        
        return prompt
    
    @staticmethod
    def _create_element_summary(elements: List[ExtractedElement]) -> str:
        """Create a summary of elements by type."""
        summary = {}
        
        for elem in elements:
            elem_type = elem.interaction_type
            if elem_type not in summary:
                summary[elem_type] = []
            
            elem_desc = f"- {elem.tag_name}"
            if elem.text_content:
                elem_desc += f": '{elem.text_content[:50]}'"
            elif elem.aria_label:
                elem_desc += f": '{elem.aria_label}'"
            elif elem.placeholder:
                elem_desc += f": placeholder='{elem.placeholder}'"
            
            summary[elem_type].append(elem_desc)
        
        result = []
        for interaction_type, items in summary.items():
            result.append(f"\n{interaction_type.upper()} Elements ({len(items)}):")
            result.extend(items[:5])  # Show first 5 of each type
            if len(items) > 5:
                result.append(f"  ... and {len(items) - 5} more")
        
        return "\n".join(result)
    
    @staticmethod
    def _create_element_reference(elements: List[ExtractedElement]) -> str:
        """Create a detailed reference of testable elements."""
        reference = []
        
        # Group by interaction type
        grouped = {}
        for elem in elements:
            if elem.interaction_type not in grouped:
                grouped[elem.interaction_type] = []
            grouped[elem.interaction_type].append(elem)
        
        for interaction_type, elems in grouped.items():
            reference.append(f"\n{interaction_type.upper()} Elements:")
            
            for i, elem in enumerate(elems[:10], 1):  # Limit to 10 per type
                ref_line = f"{i}. {elem.tag_name}"
                
                # Add identifier
                if elem.id:
                    ref_line += f" (id='{elem.id}')"
                elif elem.name:
                    ref_line += f" (name='{elem.name}')"
                
                # Add description
                if elem.text_content:
                    ref_line += f" - Text: '{elem.text_content[:30]}'"
                elif elem.aria_label:
                    ref_line += f" - Label: '{elem.aria_label}'"
                elif elem.placeholder:
                    ref_line += f" - Placeholder: '{elem.placeholder}'"
                
                # Add xpath for reference
                ref_line += f"\n   XPath: {elem.xpath}"
                
                reference.append(ref_line)
        
        return "\n".join(reference)

# ============================================================================
# FORMATTING LAYER
# ============================================================================

class GherkinFormatter:
    """Formats and validates Gherkin output."""
    
    @staticmethod
    def parse_llm_response(response: str) -> List[TestScenario]:
        """Parse LLM response into TestScenario objects."""
        scenarios = []
        
        # Split response into scenario blocks
        scenario_blocks = re.split(r'(?=Scenario(?:\s+Outline)?:)', response)
        
        for block in scenario_blocks:
            if not block.strip() or not block.startswith('Scenario'):
                continue
            
            scenario = GherkinFormatter._parse_scenario_block(block)
            if scenario:
                scenarios.append(scenario)
        
        return scenarios
    
    @staticmethod
    def _parse_scenario_block(block: str) -> Optional[TestScenario]:
        """Parse a single scenario block."""
        lines = block.strip().split('\n')
        
        # Extract scenario name
        header_match = re.match(r'Scenario(?:\s+Outline)?:\s*(.+)', lines[0])
        if not header_match:
            return None
        
        name = header_match.group(1).strip()
        
        # Extract tags
        tags = []
        if lines and lines[0].startswith('@'):
            tags = re.findall(r'@(\w+)', lines[0])
            lines = lines[1:]
        
        # Extract steps
        steps = []
        current_step = None
        
        for line in lines[1:]:
            line = line.strip()
            
            # Check for step keywords
            step_match = re.match(r'(Given|When|Then|And|But)\s+(.+)', line)
            if step_match:
                if current_step:
                    steps.append(current_step)
                
                keyword = step_match.group(1)
                text = step_match.group(2)
                current_step = {'keyword': keyword, 'text': text}
            
            # Check for data tables
            elif line.startswith('|') and current_step:
                if 'data_table' not in current_step:
                    current_step['data_table'] = []
                
                # Parse table row
                row = [cell.strip() for cell in line.split('|')[1:-1]]
                current_step['data_table'].append(row)
            
            # Check for Examples section
            elif line.startswith('Examples:'):
                # Handle scenario outline examples
                # This would need more complex parsing
                pass
        
        # Add last step
        if current_step:
            steps.append(current_step)
        
        # Determine scenario type
        scenario_type = "positive"
        if any(tag in ['negative', 'error', 'failure'] for tag in tags):
            scenario_type = "negative"
        elif any(tag in ['edge', 'boundary'] for tag in tags):
            scenario_type = "edge_case"
        
        return TestScenario(
            name=name,
            description="",
            scenario_type=scenario_type,
            steps=steps,
            tags=tags
        )
    
    @staticmethod
    def validate_gherkin(feature: GherkinFeature) -> List[str]:
        """Validate Gherkin feature for common issues."""
        issues = []
        
        # Check feature has scenarios
        if not feature.scenarios:
            issues.append("Feature has no scenarios")
        
        # Check each scenario
        for i, scenario in enumerate(feature.scenarios):
            # Check scenario has steps
            if not scenario.steps:
                issues.append(f"Scenario {i+1} '{scenario.name}' has no steps")
            
            # Check step keywords
            if scenario.steps:
                first_step = scenario.steps[0]
                if first_step['keyword'] not in ['Given', 'When']:
                    issues.append(f"Scenario {i+1} should start with Given or When")
                
                # Check for Then step
                has_then = any(step['keyword'] == 'Then' for step in scenario.steps)
                if not has_then:
                    issues.append(f"Scenario {i+1} missing Then step")
        
        return issues

# ============================================================================
# ORCHESTRATION LAYER
# ============================================================================

class GherkinTestGenerator:
    """
    Main orchestrator for generating Gherkin tests from extracted elements.
    
    Features:
    - Multi-model LLM support
    - Two-stage generation process
    - Coverage analysis
    - Quality validation
    """
    
    def __init__(
        self,
        api_keys: Optional[Dict[str, str]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the generator.
        
        Args:
            api_keys: API keys for LLM providers
            config: Generation configuration
        """
        self.llm_provider = LLMProvider(api_keys)
        self.prompt_templates = PromptTemplates()
        self.formatter = GherkinFormatter()
        
        # Default configuration
        self.config = {
            'max_scenarios': 15,
            'include_negative': True,
            'include_edge_cases': True,
            'include_accessibility': True,
            'model': 'gpt-4',
            'temperature': 0.7,
            'validate_output': True
        }
        
        if config:
            self.config.update(config)
        
        self._stats = {
            'total_generated': 0,
            'llm_calls': 0,
            'errors': 0,
            'generation_time': 0
        }
        
        logger.info("GherkinTestGenerator initialized")
    
    async def generate(self, step1_output):
        """Generate Gherkin from Step 1 contract and return Step 2 contract.
        
        Args:
            step1_output: ElementExtraction contract from Step 1
            
        Returns:
            GherkinGeneration: Contract-compliant output
        """
        from data_contracts import GherkinGeneration, GherkinFeature as ContractFeature, ElementExtraction
        from datetime import datetime
        import time
        
        # Validate input is correct contract type
        if not isinstance(step1_output, ElementExtraction):
            raise TypeError(f"Expected ElementExtraction, got {type(step1_output).__name__}")
        
        start_time = time.time()
        success = True
        error_message = None
        features = []
        
        try:
            # Convert contract elements to format expected by internal method
            elements = [elem.model_dump() for elem in step1_output.elements]
            
            # Use internal generation method
            result = await self._generate_gherkin_internal(
                elements=elements,
                url=step1_output.url,
                feature_name=f"Tests for {step1_output.url}"
            )
            
            # Convert result to contract format
            if result and hasattr(result, 'scenarios'):
                features.append(ContractFeature(
                    name=result.name if hasattr(result, 'name') else "Generated Feature",
                    description=result.description if hasattr(result, 'description') else "",
                    scenarios=result.scenarios if hasattr(result, 'scenarios') else []
                ))
            
        except Exception as e:
            success = False
            error_message = str(e)
            logger.error(f"Gherkin generation failed: {e}")
        
        # Return contract
        return GherkinGeneration(
            source_url=step1_output.url,
            timestamp=datetime.now().isoformat(),
            success=success,
            features=features,
            metadata={
                "generator_version": "1.0.0",
                "llm_model": self.config.get('model', 'unknown'),
                "element_count": len(step1_output.elements)
            },
            error_message=error_message,
            generation_time=time.time() - start_time,
            llm_model=self.config.get('model', 'gpt-4')
        )
    
    async def _generate_gherkin_internal(
        self,
        elements: List[Union[ExtractedElement, Dict[str, Any]]],
        url: str,
        feature_name: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> GherkinFeature:
        """
        Generate Gherkin test cases from extracted elements.
        
        Args:
            elements: List of extracted elements (can be dicts or ExtractedElement objects)
            url: URL of the page
            feature_name: Optional feature name
            options: Generation options
            
        Returns:
            GherkinFeature object with generated tests
        """
        start_time = time.time()
        
        # Convert dict elements to ExtractedElement objects
        element_objects = []
        for elem in elements:
            if isinstance(elem, dict):
                # Filter only the fields that ExtractedElement accepts
                extracted_fields = {
                    k: v for k, v in elem.items() 
                    if k in ExtractedElement.__dataclass_fields__
                }
                element_objects.append(ExtractedElement(**extracted_fields))
            else:
                element_objects.append(elem)
        
        # Merge options with config
        gen_options = self.config.copy()
        if options:
            gen_options.update(options)
        
        try:
            # Stage 1: Analyze elements and identify scenarios
            logger.info("Stage 1: Analyzing elements...")
            analysis = await self._analyze_elements(element_objects, url)
            
            # Stage 2: Generate Gherkin scenarios
            logger.info("Stage 2: Generating Gherkin scenarios...")
            scenarios = await self._generate_scenarios(element_objects, analysis, url, gen_options)
            
            # Create feature
            feature = GherkinFeature(
                name=feature_name or self._generate_feature_name(url),
                description=f"Automated test cases for {url}",
                scenarios=scenarios,
                url=url,
                tags=['automated', 'ui-test']
            )
            
            # Validate if enabled
            if gen_options.get('validate_output', True):
                issues = self.formatter.validate_gherkin(feature)
                if issues:
                    logger.warning(f"Validation issues: {issues}")
            
            # Update stats
            self._stats['total_generated'] += len(scenarios)
            self._stats['generation_time'] = time.time() - start_time
            
            logger.info(f"Generated {len(scenarios)} scenarios in {self._stats['generation_time']:.2f}s")
            
            return feature
            
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"Generation failed: {e}")
            raise
    
    async def _analyze_elements(self, elements: List[ExtractedElement], url: str) -> str:
        """Analyze elements to identify test scenarios."""
        prompt = self.prompt_templates.get_analysis_prompt(elements, url)
        
        self._stats['llm_calls'] += 1
        analysis = await self.llm_provider.generate(
            prompt,
            model=self.config['model'],
            temperature=0.5  # Lower temperature for analysis
        )
        
        return analysis
    
    async def _generate_scenarios(
        self,
        elements: List[ExtractedElement],
        analysis: str,
        url: str,
        options: Dict[str, Any]
    ) -> List[TestScenario]:
        """Generate Gherkin scenarios based on analysis."""
        prompt = self.prompt_templates.get_gherkin_generation_prompt(
            elements, analysis, url, options
        )
        
        self._stats['llm_calls'] += 1
        response = await self.llm_provider.generate(
            prompt,
            model=self.config['model'],
            temperature=options.get('temperature', 0.7)
        )
        
        # Parse response into scenarios
        scenarios = self.formatter.parse_llm_response(response)
        
        # Add coverage metadata
        scenarios = self._add_coverage_metadata(scenarios, elements)
        
        return scenarios
    
    def _add_coverage_metadata(
        self,
        scenarios: List[TestScenario],
        elements: List[ExtractedElement]
    ) -> List[TestScenario]:
        """Add coverage metadata to scenarios."""
        # Track which elements are covered
        covered_elements = set()
        
        for scenario in scenarios:
            # Analyze which elements are referenced in steps
            for step in scenario.steps:
                step_text = step['text'].lower()
                
                for elem in elements:
                    # Check if element is referenced
                    if elem.text_content and elem.text_content.lower() in step_text:
                        covered_elements.add(elem.xpath)
                    elif elem.aria_label and elem.aria_label.lower() in step_text:
                        covered_elements.add(elem.xpath)
                    elif elem.id and elem.id.lower() in step_text:
                        covered_elements.add(elem.xpath)
        
        # Calculate coverage
        coverage = len(covered_elements) / len(elements) if elements else 0
        logger.info(f"Element coverage: {coverage:.1%} ({len(covered_elements)}/{len(elements)})")
        
        return scenarios
    
    def _generate_feature_name(self, url: str) -> str:
        """Generate a feature name from URL."""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        path = parsed.path.strip('/')
        
        if path:
            # Use path as feature name
            feature = path.replace('/', '_').replace('-', '_').title()
        else:
            # Use domain
            feature = domain.split('.')[0].title()
        
        return f"{feature} Tests"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generation statistics."""
        return self._stats.copy()

# ============================================================================
# PUBLIC API
# ============================================================================

async def generate_gherkin_tests(
    elements: List[Union[Dict[str, Any], Any]],
    url: str,
    api_keys: Optional[Dict[str, str]] = None,
    feature_name: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate Gherkin test cases from extracted elements.
    
    This is the main entry point for test generation.
    
    Args:
        elements: List of extracted elements (dicts or objects)
        url: URL of the page being tested
        api_keys: Optional API keys for LLM providers
        feature_name: Optional name for the feature
        config: Optional configuration overrides
        
    Returns:
        Gherkin format test cases as string
        
    Example:
        elements = await extract_elements("https://example.com")
        gherkin = await generate_gherkin_tests(
            elements,
            "https://example.com",
            api_keys={'openai': 'sk-...'}
        )
        print(gherkin)
    """
    generator = GherkinTestGenerator(api_keys, config)
    
    feature = await generator.generate_gherkin_tests(
        elements,
        url,
        feature_name,
        config
    )
    
    return feature.to_gherkin()

# ============================================================================
# CLI Interface
# ============================================================================

if __name__ == "__main__":
    import sys
    
    async def main():
        # Example usage with sample elements
        sample_elements = [
            {
                'tag_name': 'input',
                'element_type': 'text',
                'xpath': '//input[@id="username"]',
                'css_selector': '#username',
                'id': 'username',
                'placeholder': 'Enter username',
                'is_visible': True,
                'interaction_type': 'type'
            },
            {
                'tag_name': 'input',
                'element_type': 'password',
                'xpath': '//input[@id="password"]',
                'css_selector': '#password',
                'id': 'password',
                'placeholder': 'Enter password',
                'is_visible': True,
                'interaction_type': 'type'
            },
            {
                'tag_name': 'button',
                'element_type': 'submit',
                'xpath': '//button[@type="submit"]',
                'css_selector': 'button[type="submit"]',
                'text_content': 'Login',
                'is_clickable': True,
                'is_visible': True,
                'interaction_type': 'click'
            }
        ]
        
        # Get API key from environment or command line
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key and len(sys.argv) > 1:
            api_key = sys.argv[1]
        
        if not api_key:
            print("Please set OPENAI_API_KEY environment variable or pass as argument")
            print("Usage: python gherkin_test_generator.py [API_KEY]")
            sys.exit(1)
        
        print("Generating Gherkin tests...")
        
        try:
            gherkin = await generate_gherkin_tests(
                sample_elements,
                "https://example.com/login",
                api_keys={'openai': api_key},
                feature_name="Login Page",
                config={
                    'max_scenarios': 5,
                    'include_negative': True,
                    'include_edge_cases': True
                }
            )
            
            print("\n" + "="*60)
            print("GENERATED GHERKIN TESTS")
            print("="*60)
            print(gherkin)
            
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    asyncio.run(main())