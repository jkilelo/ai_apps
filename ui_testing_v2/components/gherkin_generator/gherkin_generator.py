"""
Gherkin Test Case Generator

Main orchestrator for generating Gherkin format test cases from extracted elements
using LLM with two-step generation approach.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sys
import hashlib

# Add project root to path for llm.py access
sys.path.append(str(Path(__file__).parents[6]))  # Navigate to /var/www/ai_apps

from src.ui_testing_v2.core.config import Config
from src.ui_testing_v2.models.database import ExtractedElement
from .element_context_mapper import ElementContextMapper
from .prompt_templates import PromptTemplateManager
from .gherkin_formatter import GherkinFormatter
from .test_scenario_classifier import TestScenarioClassifier
from .llm_provider import LLMProvider
from .intermediate_format import IntermediateTestFormat
from .enhanced_test_generator import EnhancedTestGenerator, TestCoverageAnalyzer

logger = logging.getLogger(__name__)


class GherkinGenerator:
    """
    Advanced Gherkin test case generator using LLM with scientific approach.
    
    Features:
    - Two-step generation: elements → natural language → Gherkin
    - JSON intermediate format for reliability
    - Multi-model voting for quality improvement
    - Context-aware prompt engineering
    - Comprehensive test coverage analysis
    """
    
    def __init__(
        self,
        config: Config,
        cache_service=None,
        database_manager=None
    ):
        self.config = config
        self.cache_service = cache_service
        self.database_manager = database_manager
        
        # Initialize sub-components
        self.element_mapper = ElementContextMapper(config)
        self.prompt_manager = PromptTemplateManager(config)
        self.formatter = GherkinFormatter(config)
        self.scenario_classifier = TestScenarioClassifier(config)
        self.llm_provider = LLMProvider(config)
        self.enhanced_generator = EnhancedTestGenerator(self.llm_provider)
        self.coverage_analyzer = TestCoverageAnalyzer()
        
        # Generation configuration
        self.generation_config = {
            'max_scenarios_per_feature': 20,
            'max_steps_per_scenario': 15,
            'min_confidence_threshold': 0.7,
            'enable_multi_model_voting': True,
            'generate_edge_cases': True,
            'include_negative_scenarios': True,
            'use_page_object_pattern': True,
            'enable_data_tables': True,
            'enable_scenario_outlines': True
        }
        
        # Statistics tracking
        self._generation_stats = {
            'total_features_generated': 0,
            'total_scenarios_generated': 0,
            'llm_calls_made': 0,
            'cache_hits': 0,
            'generation_errors': 0
        }
        
        logger.info("GherkinGenerator initialized with advanced features")
    
    async def generate_gherkin_tests(
        self,
        elements: List[ExtractedElement],
        url: str,
        session_id: str,
        analysis_results: Optional[Dict[str, Any]] = None,
        generation_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate Gherkin format test cases from extracted elements.
        
        Args:
            elements: List of extracted elements from the page
            url: URL of the page being tested
            session_id: Session identifier
            analysis_results: Optional pre-computed element analysis
            generation_options: Optional configuration overrides
            
        Returns:
            Dictionary containing:
            - features: List of Gherkin features with scenarios
            - metadata: Generation metadata and statistics
            - intermediate_results: Step-by-step generation results
        """
        try:
            start_time = datetime.now()
            self._generation_stats['total_features_generated'] += 1
            
            # Merge configuration
            config = {**self.generation_config, **(generation_options or {})}
            
            # Check cache if enabled
            cache_key = self._generate_cache_key(url, elements, config)
            if self.cache_service and not config.get('force_refresh', False):
                cached_result = await self._check_cache(cache_key)
                if cached_result:
                    logger.info(f"Using cached Gherkin tests for {url}")
                    self._generation_stats['cache_hits'] += 1
                    return cached_result
            
            logger.info(f"Generating Gherkin tests for {url} with {len(elements)} elements")
            
            # Step 1: Map elements to rich context
            element_context = await self.element_mapper.create_element_context(
                elements, url, analysis_results
            )
            
            # Step 2: Classify test scenarios
            scenario_classifications = await self.scenario_classifier.classify_scenarios(
                element_context, analysis_results
            )
            
            # Step 3: Generate test scenarios using two-step approach
            generation_results = await self._generate_scenarios_two_step(
                element_context,
                scenario_classifications,
                url,
                config
            )
            
            # Step 4: Format as Gherkin features
            gherkin_features = await self.formatter.format_features(
                generation_results['scenarios'],
                url,
                element_context
            )
            
            # Step 5: Validate and optimize
            validated_features = await self._validate_and_optimize_features(
                gherkin_features,
                element_context
            )
            
            # Prepare final results
            results = {
                'success': True,
                'features': validated_features,
                'metadata': {
                    'url': url,
                    'session_id': session_id,
                    'generation_time': (datetime.now() - start_time).total_seconds(),
                    'total_elements': len(elements),
                    'total_features': len(validated_features),
                    'total_scenarios': sum(len(f['scenarios']) for f in validated_features),
                    'llm_calls': generation_results['llm_calls'],
                    'models_used': generation_results['models_used'],
                    'confidence_scores': generation_results['confidence_scores']
                },
                'intermediate_results': {
                    'element_context': element_context,
                    'scenario_classifications': scenario_classifications,
                    'raw_generation': generation_results
                }
            }
            
            # Update statistics
            self._generation_stats['total_scenarios_generated'] += results['metadata']['total_scenarios']
            self._generation_stats['llm_calls_made'] += generation_results['llm_calls']
            
            # Cache results if enabled
            if self.cache_service:
                await self._cache_results(cache_key, results)
            
            logger.info(f"Generated {len(validated_features)} features with "
                       f"{results['metadata']['total_scenarios']} scenarios in "
                       f"{results['metadata']['generation_time']:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Gherkin generation failed: {e}")
            self._generation_stats['generation_errors'] += 1
            return {
                'success': False,
                'error': str(e),
                'features': []
            }
    
    async def _generate_scenarios_two_step(
        self,
        element_context: Dict[str, Any],
        scenario_classifications: List[Dict[str, Any]],
        url: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate test scenarios using two-step approach:
        1. Elements → Natural language descriptions
        2. Natural language → Gherkin scenarios
        """
        generation_results = {
            'scenarios': [],
            'llm_calls': 0,
            'models_used': [],
            'confidence_scores': []
        }
        
        try:
            # Check if enhanced generation is enabled
            use_enhanced = config.get('use_enhanced_generation', True)
            
            if use_enhanced:
                # Use enhanced generator for comprehensive test generation
                logger.info("Using enhanced test generator for comprehensive coverage")
                
                # Configure generation options
                generation_options = {
                    'strategies': config.get('test_strategies', [
                        'happy_path', 'negative', 'edge_case', 'security',
                        'accessibility', 'data_variation'
                    ]),
                    'max_total_scenarios': config.get('max_scenarios_per_feature', 20),
                    'include_edge_cases': config.get('include_edge_cases', True),
                    'include_negative_tests': config.get('include_negative_tests', True)
                }
                
                # Generate comprehensive scenarios
                enhanced_scenarios = await self.enhanced_generator.generate_comprehensive_tests(
                    element_context,
                    generation_options
                )
                
                # Analyze coverage
                coverage_report = self.coverage_analyzer.analyze_coverage(
                    enhanced_scenarios,
                    element_context
                )
                
                logger.info(f"Test coverage: {coverage_report['coverage_percentage']:.1f}%")
                logger.info(f"Generated {len(enhanced_scenarios)} scenarios across "
                          f"{len(set(s.get('priority', 'medium') for s in enhanced_scenarios))} priority levels")
                
                # Update results - enhanced scenarios are already in the right format
                json_scenarios = enhanced_scenarios
                generation_results['llm_calls'] += len(generation_options['strategies'])
                generation_results['coverage_report'] = coverage_report
                
            else:
                # Original two-step approach
                # Step 1: Generate natural language test descriptions
                nl_descriptions = await self._generate_natural_language_tests(
                    element_context,
                    scenario_classifications,
                    config
                )
                generation_results['llm_calls'] += 1
                
                # Step 2: Convert natural language to structured JSON format
                json_scenarios = await self._convert_to_json_format(
                    nl_descriptions,
                    element_context,
                    config
                )
                generation_results['llm_calls'] += 1
            
            # Step 3: Convert JSON to Gherkin scenarios
            gherkin_scenarios = await self._json_to_gherkin_scenarios(
                json_scenarios,
                element_context,
                config
            )
            
            # Step 4: Apply multi-model voting if enabled
            if config.get('enable_multi_model_voting', True):
                enhanced_scenarios = await self._apply_multi_model_voting(
                    gherkin_scenarios,
                    element_context,
                    config
                )
                generation_results['llm_calls'] += len(self.llm_provider.get_available_models()) - 1
                generation_results['scenarios'] = enhanced_scenarios
            else:
                generation_results['scenarios'] = gherkin_scenarios
            
            # Track models used
            generation_results['models_used'] = self.llm_provider.get_models_used()
            
            # Calculate confidence scores
            for scenario in generation_results['scenarios']:
                confidence = scenario.get('confidence', 0.8)
                generation_results['confidence_scores'].append(confidence)
            
            return generation_results
            
        except Exception as e:
            logger.error(f"Two-step scenario generation failed: {e}")
            raise
    
    async def _generate_natural_language_tests(
        self,
        element_context: Dict[str, Any],
        scenario_classifications: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate natural language test descriptions from elements."""
        # Get appropriate prompt template
        prompt = self.prompt_manager.get_natural_language_prompt(
            element_context,
            scenario_classifications,
            config
        )
        
        # Call LLM to generate natural language descriptions
        response = await self.llm_provider.generate(
            prompt,
            model_preference='gpt-4'  # Best for creative test generation
        )
        
        # Parse and validate response
        nl_tests = self._parse_natural_language_response(response)
        
        logger.info(f"Generated {len(nl_tests)} natural language test descriptions")
        return nl_tests
    
    async def _convert_to_json_format(
        self,
        nl_descriptions: List[Dict[str, Any]],
        element_context: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Convert natural language descriptions to structured JSON format."""
        # Get JSON conversion prompt
        prompt = self.prompt_manager.get_json_conversion_prompt(
            nl_descriptions,
            element_context,
            config
        )
        
        # Call LLM to convert to JSON
        response = await self.llm_provider.generate(
            prompt,
            model_preference='claude'  # Best for structured output
        )
        
        # Parse JSON response
        json_scenarios = self._parse_json_response(response)
        
        # Validate against intermediate format schema
        validated_scenarios = IntermediateTestFormat.validate_scenarios(json_scenarios)
        
        logger.info(f"Converted to {len(validated_scenarios)} JSON scenarios")
        return validated_scenarios
    
    async def _json_to_gherkin_scenarios(
        self,
        json_scenarios: List[Dict[str, Any]],
        element_context: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Convert JSON scenarios to Gherkin format."""
        gherkin_scenarios = []
        
        for json_scenario in json_scenarios:
            # Map JSON to Gherkin structure
            gherkin_scenario = {
                'title': json_scenario.get('title', 'Test Scenario'),
                'description': json_scenario.get('description', ''),
                'tags': json_scenario.get('tags', []),
                'type': json_scenario.get('type', 'scenario'),
                'given_steps': [],
                'when_steps': [],
                'then_steps': [],
                'examples': json_scenario.get('examples', {}),
                'confidence': json_scenario.get('confidence', 0.8),
                'priority': json_scenario.get('priority', 'medium')
            }
            
            # Convert steps to Given-When-Then format
            for step in json_scenario.get('steps', []):
                step_type = self._classify_step_type(step)
                gherkin_step = self._create_gherkin_step(step, element_context)
                
                if step_type == 'given':
                    gherkin_scenario['given_steps'].append(gherkin_step)
                elif step_type == 'when':
                    gherkin_scenario['when_steps'].append(gherkin_step)
                else:  # then
                    gherkin_scenario['then_steps'].append(gherkin_step)
            
            gherkin_scenarios.append(gherkin_scenario)
        
        return gherkin_scenarios
    
    async def _apply_multi_model_voting(
        self,
        scenarios: List[Dict[str, Any]],
        element_context: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply multi-model voting to improve scenario quality."""
        enhanced_scenarios = []
        
        for scenario in scenarios:
            # Get quality assessment from multiple models
            assessments = await self.llm_provider.assess_scenario_quality(
                scenario,
                element_context,
                models=['gpt-4', 'claude', 'gemini']
            )
            
            # Aggregate assessments
            avg_quality = sum(a['quality_score'] for a in assessments) / len(assessments)
            improvements = self._aggregate_improvements(assessments)
            
            # Apply improvements if quality is below threshold
            if avg_quality < 0.85 and improvements:
                enhanced_scenario = await self._enhance_scenario(
                    scenario,
                    improvements,
                    element_context
                )
                enhanced_scenario['confidence'] = avg_quality
                enhanced_scenarios.append(enhanced_scenario)
            else:
                scenario['confidence'] = avg_quality
                enhanced_scenarios.append(scenario)
        
        return enhanced_scenarios
    
    async def _validate_and_optimize_features(
        self,
        features: List[Dict[str, Any]],
        element_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Validate and optimize Gherkin features."""
        validated_features = []
        
        for feature in features:
            # Validate Gherkin syntax
            validation_result = self.formatter.validate_feature(feature)
            
            if validation_result['valid']:
                # Optimize scenarios (remove duplicates, improve clarity)
                optimized_feature = await self._optimize_feature(feature, element_context)
                validated_features.append(optimized_feature)
            else:
                logger.warning(f"Invalid feature skipped: {validation_result['errors']}")
        
        return validated_features
    
    async def _optimize_feature(
        self,
        feature: Dict[str, Any],
        element_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize a Gherkin feature."""
        optimized_feature = feature.copy()
        
        # Remove duplicate scenarios
        unique_scenarios = []
        seen_scenarios = set()
        
        for scenario in feature['scenarios']:
            scenario_key = self._generate_scenario_key(scenario)
            if scenario_key not in seen_scenarios:
                seen_scenarios.add(scenario_key)
                unique_scenarios.append(scenario)
        
        optimized_feature['scenarios'] = unique_scenarios
        
        # Sort scenarios by priority and confidence
        optimized_feature['scenarios'].sort(
            key=lambda s: (
                {'high': 3, 'medium': 2, 'low': 1}.get(s.get('priority', 'medium'), 2),
                s.get('confidence', 0.5)
            ),
            reverse=True
        )
        
        return optimized_feature
    
    def _generate_cache_key(
        self,
        url: str,
        elements: List[ExtractedElement],
        config: Dict[str, Any]
    ) -> str:
        """Generate cache key for Gherkin generation results."""
        # Create a deterministic key based on URL, element signatures, and config
        element_signatures = []
        for elem in elements[:20]:  # Limit to first 20 elements
            sig = f"{elem.tag_name}:{elem.element_type}:{elem.css_selector}"
            element_signatures.append(sig)
        
        key_data = {
            'url': url,
            'element_signatures': sorted(element_signatures),
            'config': config
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return f"gherkin_gen_{hashlib.md5(key_string.encode()).hexdigest()}"
    
    async def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Check cache for existing results."""
        if not self.cache_service:
            return None
        
        try:
            return await self.cache_service.get(cache_key)
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
            return None
    
    async def _cache_results(self, cache_key: str, results: Dict[str, Any]):
        """Cache generation results."""
        if not self.cache_service:
            return
        
        try:
            # Cache for 24 hours by default
            await self.cache_service.set(cache_key, results, ttl=86400)
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    def _parse_natural_language_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response containing natural language test descriptions."""
        try:
            # For now, create basic test descriptions from response
            # In practice, would parse structured response from LLM
            test_descriptions = []
            
            # Simple parsing - split by numbered tests
            import re
            test_matches = re.findall(r'Test \d+:.*?(?=Test \d+:|$)', response, re.DOTALL)
            
            for i, test_text in enumerate(test_matches):
                test_descriptions.append({
                    'title': f'Test Case {i+1}',
                    'description': test_text.strip()
                })
            
            # If no matches, create a default test
            if not test_descriptions:
                test_descriptions.append({
                    'title': 'Login Test',
                    'description': 'Test user login functionality'
                })
            
            return test_descriptions
            
        except Exception as e:
            logger.error(f"Failed to parse natural language response: {e}")
            # Return default test description
            return [{
                'title': 'Default Test',
                'description': 'Basic functionality test'
            }]
    
    def _parse_json_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response containing JSON scenarios."""
        try:
            # First try direct parsing (in case response is clean JSON)
            try:
                data = json.loads(response.strip())
                if isinstance(data, list):
                    logger.debug(f"Parsed {len(data)} scenarios from direct JSON")
                    logger.debug(f"First scenario keys: {list(data[0].keys()) if data else 'None'}")
                    return data
                elif isinstance(data, dict):
                    if 'scenarios' in data:
                        logger.debug(f"Found scenarios key with {len(data['scenarios'])} scenarios")
                        return data['scenarios']
                    elif 'test_cases' in data:
                        logger.debug(f"Found test_cases key with {len(data['test_cases'])} scenarios")
                        return data['test_cases']
                    else:
                        logger.debug("Single dict scenario found")
                        return [data]
            except json.JSONDecodeError:
                pass  # Continue with regex extraction
            
            # Extract JSON from response
            import re
            
            # Clean common issues
            # Remove markdown code blocks
            cleaned = re.sub(r'```json\s*', '', response)
            cleaned = re.sub(r'```\s*', '', cleaned)
            
            # Try to find JSON array (be more careful with the regex)
            json_match = re.search(r'\[\s*\{[\s\S]*?\}\s*\]', cleaned)
            if json_match:
                try:
                    scenarios = json.loads(json_match.group())
                    if isinstance(scenarios, list):
                        return scenarios
                except json.JSONDecodeError as e:
                    logger.debug(f"Array parsing failed: {e}")
            
            # Try to find JSON object with scenarios key
            json_match = re.search(r'\{[\s\S]*"scenarios"[\s\S]*\}', cleaned)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    if isinstance(data, dict) and 'scenarios' in data:
                        return data['scenarios']
                except json.JSONDecodeError as e:
                    logger.debug(f"Object parsing failed: {e}")
            
            # Try to find any JSON object
            json_match = re.search(r'\{[\s\S]*?\}', cleaned)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    if isinstance(data, dict):
                        return [data]
                except json.JSONDecodeError as e:
                    logger.debug(f"Single object parsing failed: {e}")
            
            # Fallback: create default scenario
            logger.warning("Could not parse JSON from response, using default")
            return [{
                'title': 'User Login Test',
                'type': 'scenario',
                'tags': ['login', 'authentication'],
                'steps': [
                    {
                        'action': 'navigate',
                        'description': 'Navigate to login page',
                        'element_selector': '',
                        'test_data': {'url': '/login'}
                    },
                    {
                        'action': 'fill',
                        'description': 'Enter email',
                        'element_selector': 'input#email',
                        'test_data': {'value': 'test@example.com'}
                    },
                    {
                        'action': 'fill',
                        'description': 'Enter password',
                        'element_selector': 'input#password',
                        'test_data': {'value': 'password123'}
                    },
                    {
                        'action': 'click',
                        'description': 'Click login button',
                        'element_selector': 'button[type="submit"]',
                        'test_data': {}
                    }
                ]
            }]
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response was: {response[:500]}...")
            # Log more details for debugging
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Full response for debugging:")
                logger.debug("=" * 80)
                logger.debug(response)
                logger.debug("=" * 80)
            # Return default scenario
            return [{
                'title': 'Default Test Scenario',
                'type': 'scenario',
                'steps': []
            }]
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON: {e}")
            return []
    
    def _classify_step_type(self, step: Dict[str, Any]) -> str:
        """Classify step as given, when, or then."""
        action = step.get('action', '').lower()
        description = step.get('description', '').lower()
        
        # Given: Setup/preconditions
        if any(keyword in description for keyword in ['navigate', 'open', 'logged in', 'exists']):
            return 'given'
        
        # When: Actions
        if any(keyword in action for keyword in ['click', 'fill', 'select', 'submit', 'enter']):
            return 'when'
        
        # Then: Assertions
        if any(keyword in description for keyword in ['should', 'verify', 'check', 'display', 'visible']):
            return 'then'
        
        # Default based on position
        return 'when'
    
    def _create_gherkin_step(
        self,
        step: Dict[str, Any],
        element_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a Gherkin step from JSON step."""
        return {
            'text': step['description'],
            'element': step.get('element_selector', ''),
            'data': step.get('test_data', {}),
            'timeout': step.get('timeout', 10)
        }
    
    def _aggregate_improvements(
        self,
        assessments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Aggregate improvement suggestions from multiple models."""
        all_improvements = []
        for assessment in assessments:
            all_improvements.extend(assessment.get('improvements', []))
        
        # Deduplicate and prioritize improvements
        unique_improvements = {}
        for improvement in all_improvements:
            key = improvement.get('type', 'general')
            if key not in unique_improvements or improvement.get('priority', 0) > unique_improvements[key].get('priority', 0):
                unique_improvements[key] = improvement
        
        return list(unique_improvements.values())
    
    async def _enhance_scenario(
        self,
        scenario: Dict[str, Any],
        improvements: List[Dict[str, Any]],
        element_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance scenario based on improvement suggestions."""
        enhanced = scenario.copy()
        
        for improvement in improvements:
            if improvement['type'] == 'add_validation':
                # Add validation steps
                enhanced['then_steps'].extend(improvement['steps'])
            elif improvement['type'] == 'improve_clarity':
                # Improve step descriptions
                for step_list in [enhanced['given_steps'], enhanced['when_steps'], enhanced['then_steps']]:
                    for step in step_list:
                        step['text'] = self._improve_step_clarity(step['text'])
            elif improvement['type'] == 'add_data_variation':
                # Add scenario outline examples
                enhanced['examples'] = improvement['examples']
                enhanced['type'] = 'scenario_outline'
        
        return enhanced
    
    def _improve_step_clarity(self, text: str) -> str:
        """Improve clarity of step text."""
        # Simple improvements - in practice would be more sophisticated
        replacements = {
            'click button': 'click the',
            'fill field': 'enter',
            'should see': 'should display',
            'is visible': 'is displayed'
        }
        
        improved = text
        for old, new in replacements.items():
            improved = improved.replace(old, new)
        
        return improved
    
    def _generate_scenario_key(self, scenario: Dict[str, Any]) -> str:
        """Generate unique key for scenario deduplication."""
        # Create key from essential scenario elements
        steps = []
        for step_list in [scenario.get('given_steps', []), 
                         scenario.get('when_steps', []), 
                         scenario.get('then_steps', [])]:
            steps.extend([step['text'] for step in step_list])
        
        key_data = {
            'title': scenario.get('title', ''),
            'steps': steps
        }
        
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        return {
            'total_features_generated': self._generation_stats['total_features_generated'],
            'total_scenarios_generated': self._generation_stats['total_scenarios_generated'],
            'llm_calls_made': self._generation_stats['llm_calls_made'],
            'cache_hits': self._generation_stats['cache_hits'],
            'cache_hit_rate': (
                self._generation_stats['cache_hits'] / 
                max(self._generation_stats['total_features_generated'], 1)
            ),
            'generation_errors': self._generation_stats['generation_errors'],
            'error_rate': (
                self._generation_stats['generation_errors'] / 
                max(self._generation_stats['total_features_generated'], 1)
            )
        }