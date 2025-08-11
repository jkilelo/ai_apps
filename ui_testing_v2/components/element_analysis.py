"""
Element analysis service for intelligent element understanding and test generation.
Provides AI-powered analysis of extracted elements with testing recommendations.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
import hashlib

from ui_testing_v2.models.database import ExtractedElement, ElementType, ElementInteractionType
from ui_testing_v2.services.ai_services import AIService, AIServiceFactory
from ui_testing_v2.services.cache import CacheService, CacheKey
from ui_testing_v2.core.config import Config

logger = logging.getLogger(__name__)


class ElementAnalysisService:
    """Service for analyzing extracted elements with AI-powered insights"""
    
    def __init__(
        self,
        config: Config,
        ai_service_factory: AIServiceFactory,
        cache_service: CacheService
    ):
        self.config = config
        self.ai_service_factory = ai_service_factory
        self.cache_service = cache_service
        
        # Analysis scoring weights
        self.scoring_weights = {
            'stability': 0.25,
            'testability': 0.30,
            'business_importance': 0.25,
            'automation_suitability': 0.20
        }
        
        logger.info("ElementAnalysisService initialized")
    
    async def analyze_page_elements(
        self,
        elements: List[ExtractedElement],
        url: str,
        session_id: str,
        analysis_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of page elements
        
        Args:
            elements: List of extracted elements to analyze
            url: URL of the page being analyzed
            session_id: Session ID for tracking
            analysis_config: Optional configuration for analysis
            
        Returns:
            Comprehensive analysis results with recommendations
        """
        try:
            if not elements:
                return {
                    'success': False,
                    'error': 'No elements provided for analysis',
                    'analysis': {}
                }
            
            # Check cache first
            cache_key = CacheKey.element_analysis(session_id, url)
            cached_analysis = await self.cache_service.get(cache_key)
            
            if cached_analysis and not analysis_config.get('force_refresh', False):
                logger.info(f"Using cached element analysis for {url}")
                return cached_analysis
            
            logger.info(f"Analyzing {len(elements)} elements from {url}")
            
            # Perform multi-faceted analysis
            analysis_results = {
                'page_info': {
                    'url': url,
                    'session_id': session_id,
                    'total_elements': len(elements),
                    'analysis_timestamp': datetime.now(timezone.utc).isoformat()
                },
                'element_insights': await self._analyze_individual_elements(elements, analysis_config),
                'page_structure': await self._analyze_page_structure(elements, url),
                'testing_strategy': await self._generate_testing_strategy(elements, url),
                'automation_recommendations': await self._generate_automation_recommendations(elements),
                'quality_metrics': await self._calculate_quality_metrics(elements),
                'ai_insights': await self._get_ai_insights(elements, url, analysis_config)
            }
            
            # Cache the results
            await self.cache_service.set(
                cache_key,
                analysis_results,
                ttl=self.config.cache.element_analysis_ttl
            )
            
            analysis_results['success'] = True
            logger.info(f"Element analysis completed for {len(elements)} elements")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Element analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': {}
            }
    
    async def _analyze_individual_elements(
        self,
        elements: List[ExtractedElement],
        analysis_config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze each element individually"""
        element_insights = []
        
        for i, element in enumerate(elements):
            try:
                insight = {
                    'element_index': i,
                    'element_id': element.id if hasattr(element, 'id') else f"element_{i}",
                    'basic_info': {
                        'tag_name': element.tag_name,
                        'element_type': element.element_type.value if element.element_type else 'unknown',
                        'interaction_type': element.interaction_type.value if element.interaction_type else 'unknown',
                        'text': element.text[:100] if element.text else '',
                        'css_selector': element.css_selector,
                        'xpath': element.xpath
                    },
                    'visibility': {
                        'is_visible': element.is_visible,
                        'is_interactable': element.is_interactable,
                        'bounding_box': element.bounding_box
                    },
                    'quality_scores': {
                        'stability_score': element.stability_score,
                        'confidence_score': element.confidence_score,
                        'overall_score': await self._calculate_element_score(element)
                    },
                    'testing_attributes': await self._analyze_testing_attributes(element),
                    'ai_analysis': element.ai_analysis if element.ai_analysis else {},
                    'recommendations': await self._generate_element_recommendations(element)
                }
                
                element_insights.append(insight)
                
            except Exception as e:
                logger.warning(f"Failed to analyze element {i}: {e}")
                continue
        
        return element_insights
    
    async def _analyze_page_structure(
        self,
        elements: List[ExtractedElement],
        url: str
    ) -> Dict[str, Any]:
        """Analyze overall page structure and patterns"""
        try:
            # Categorize elements by type
            element_types = {}
            interaction_types = {}
            
            for element in elements:
                # Count element types
                elem_type = element.element_type.value if element.element_type else 'unknown'
                element_types[elem_type] = element_types.get(elem_type, 0) + 1
                
                # Count interaction types
                interaction_type = element.interaction_type.value if element.interaction_type else 'unknown'
                interaction_types[interaction_type] = interaction_types.get(interaction_type, 0) + 1
            
            # Identify forms and their elements
            forms = await self._identify_forms(elements)
            
            # Identify navigation elements
            navigation = await self._identify_navigation_elements(elements)
            
            # Identify content areas
            content_areas = await self._identify_content_areas(elements)
            
            # Calculate complexity metrics
            complexity_score = await self._calculate_page_complexity(elements)
            
            # Determine page type
            page_type = await self._determine_page_type(elements, url)
            
            return {
                'element_distribution': {
                    'by_type': element_types,
                    'by_interaction': interaction_types
                },
                'structural_components': {
                    'forms': forms,
                    'navigation': navigation,
                    'content_areas': content_areas
                },
                'complexity_metrics': {
                    'overall_score': complexity_score,
                    'total_interactive_elements': sum(interaction_types.values()),
                    'unique_element_types': len(element_types),
                    'form_complexity': len(forms)
                },
                'page_classification': {
                    'type': page_type,
                    'confidence': await self._calculate_page_type_confidence(elements, page_type)
                }
            }
            
        except Exception as e:
            logger.error(f"Page structure analysis failed: {e}")
            return {'error': str(e)}
    
    async def _generate_testing_strategy(
        self,
        elements: List[ExtractedElement],
        url: str
    ) -> Dict[str, Any]:
        """Generate comprehensive testing strategy"""
        try:
            # Prioritize elements for testing
            priority_elements = await self._prioritize_elements_for_testing(elements)
            
            # Generate test scenarios
            test_scenarios = await self._generate_test_scenarios(elements)
            
            # Identify critical paths
            critical_paths = await self._identify_critical_paths(elements)
            
            # Suggest test data requirements
            test_data_requirements = await self._analyze_test_data_requirements(elements)
            
            # Calculate testing effort estimation
            effort_estimation = await self._estimate_testing_effort(elements)
            
            return {
                'priority_elements': priority_elements,
                'test_scenarios': test_scenarios,
                'critical_paths': critical_paths,
                'test_data_requirements': test_data_requirements,
                'effort_estimation': effort_estimation,
                'testing_approach': await self._recommend_testing_approach(elements)
            }
            
        except Exception as e:
            logger.error(f"Testing strategy generation failed: {e}")
            return {'error': str(e)}
    
    async def _generate_automation_recommendations(
        self,
        elements: List[ExtractedElement]
    ) -> Dict[str, Any]:
        """Generate automation-specific recommendations"""
        try:
            # Identify best elements for automation
            automation_candidates = []
            problematic_elements = []
            
            for element in elements:
                automation_score = await self._calculate_automation_suitability(element)
                
                if automation_score >= 0.7:
                    automation_candidates.append({
                        'element': {
                            'tag_name': element.tag_name,
                            'css_selector': element.css_selector,
                            'xpath': element.xpath,
                            'text': element.text[:50] if element.text else ''
                        },
                        'score': automation_score,
                        'reasons': await self._get_automation_score_reasons(element, automation_score)
                    })
                elif automation_score < 0.4:
                    problematic_elements.append({
                        'element': {
                            'tag_name': element.tag_name,
                            'css_selector': element.css_selector,
                            'text': element.text[:50] if element.text else ''
                        },
                        'score': automation_score,
                        'issues': await self._identify_automation_issues(element)
                    })
            
            # Sort by score
            automation_candidates.sort(key=lambda x: x['score'], reverse=True)
            problematic_elements.sort(key=lambda x: x['score'])
            
            # Generate selector recommendations
            selector_recommendations = await self._generate_selector_recommendations(elements)
            
            # Maintenance predictions
            maintenance_predictions = await self._predict_maintenance_needs(elements)
            
            return {
                'automation_candidates': automation_candidates[:20],  # Top 20
                'problematic_elements': problematic_elements[:10],    # Bottom 10
                'selector_recommendations': selector_recommendations,
                'maintenance_predictions': maintenance_predictions,
                'automation_summary': {
                    'total_elements': len(elements),
                    'suitable_for_automation': len(automation_candidates),
                    'problematic': len(problematic_elements),
                    'automation_readiness': len(automation_candidates) / len(elements) if elements else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Automation recommendations generation failed: {e}")
            return {'error': str(e)}
    
    async def _calculate_quality_metrics(
        self,
        elements: List[ExtractedElement]
    ) -> Dict[str, Any]:
        """Calculate various quality metrics for the page"""
        try:
            if not elements:
                return {'error': 'No elements to analyze'}
            
            # Stability metrics
            stability_scores = [elem.stability_score for elem in elements if elem.stability_score is not None]
            avg_stability = sum(stability_scores) / len(stability_scores) if stability_scores else 0
            
            # Confidence metrics
            confidence_scores = [elem.confidence_score for elem in elements if elem.confidence_score is not None]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            # Testability metrics
            elements_with_ids = sum(1 for elem in elements if elem.attributes and elem.attributes.get('id'))
            elements_with_test_ids = sum(1 for elem in elements if elem.attributes and 'data-testid' in elem.attributes)
            elements_with_stable_selectors = sum(1 for elem in elements if await self._has_stable_selector(elem))
            
            # Accessibility metrics
            elements_with_aria = sum(1 for elem in elements if await self._has_aria_attributes(elem))
            elements_with_labels = sum(1 for elem in elements if await self._has_proper_labels(elem))
            
            return {
                'stability': {
                    'average_score': round(avg_stability, 3),
                    'distribution': await self._calculate_score_distribution(stability_scores),
                    'stable_elements_count': sum(1 for score in stability_scores if score >= 0.7)
                },
                'confidence': {
                    'average_score': round(avg_confidence, 3),
                    'distribution': await self._calculate_score_distribution(confidence_scores),
                    'high_confidence_count': sum(1 for score in confidence_scores if score >= 0.8)
                },
                'testability': {
                    'elements_with_ids': elements_with_ids,
                    'elements_with_test_ids': elements_with_test_ids,
                    'elements_with_stable_selectors': elements_with_stable_selectors,
                    'testability_score': (elements_with_test_ids + elements_with_stable_selectors) / len(elements)
                },
                'accessibility': {
                    'elements_with_aria': elements_with_aria,
                    'elements_with_labels': elements_with_labels,
                    'accessibility_score': (elements_with_aria + elements_with_labels) / (len(elements) * 2)
                },
                'overall_quality': {
                    'composite_score': await self._calculate_composite_quality_score(elements),
                    'grade': await self._assign_quality_grade(elements)
                }
            }
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed: {e}")
            return {'error': str(e)}
    
    async def _get_ai_insights(
        self,
        elements: List[ExtractedElement],
        url: str,
        analysis_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get AI-powered insights about the elements and page"""
        try:
            # Get AI service
            ai_service = await self.ai_service_factory.get_service('openai')
            if not ai_service:
                return {'error': 'AI service not available'}
            
            # Create AI insights prompt
            insights_prompt = await self._create_ai_insights_prompt(elements, url)
            
            # Check cache for AI insights
            prompt_hash = hashlib.md5(insights_prompt.encode()).hexdigest()
            ai_cache_key = CacheKey.ai_analysis("openai_insights", prompt_hash)
            cached_insights = await self.cache_service.get(ai_cache_key)
            
            if cached_insights:
                logger.info("Using cached AI insights")
                return cached_insights
            
            # Get AI insights
            logger.info("Generating AI insights for page analysis")
            ai_response = await ai_service.analyze_elements(insights_prompt)
            
            if ai_response and ai_response.get('success'):
                insights = ai_response.get('analysis', {})
                
                # Cache AI insights
                await self.cache_service.set(
                    ai_cache_key,
                    insights,
                    ttl=self.config.cache.ai_analysis_ttl
                )
                
                return insights
            else:
                return {'error': 'AI insights generation failed'}
                
        except Exception as e:
            logger.error(f"AI insights generation failed: {e}")
            return {'error': str(e)}
    
    async def _calculate_element_score(self, element: ExtractedElement) -> float:
        """Calculate overall score for an element"""
        try:
            stability = element.stability_score or 0.5
            confidence = element.confidence_score or 0.5
            
            # Calculate testability score
            testability = 0.0
            if element.attributes:
                if element.attributes.get('id'):
                    testability += 0.3
                if 'data-testid' in element.attributes:
                    testability += 0.4
                if element.attributes.get('name'):
                    testability += 0.2
                if any(attr.startswith('data-') for attr in element.attributes):
                    testability += 0.1
            
            # Calculate business importance (basic heuristics)
            business_importance = 0.5
            if element.element_type == ElementType.BUTTON:
                business_importance = 0.8
            elif element.element_type in [ElementType.INPUT, ElementType.TEXTAREA]:
                business_importance = 0.7
            elif element.element_type == ElementType.LINK:
                business_importance = 0.6
            
            # Calculate automation suitability
            automation_suitability = await self._calculate_automation_suitability(element)
            
            # Weighted score
            overall_score = (
                stability * self.scoring_weights['stability'] +
                testability * self.scoring_weights['testability'] +
                business_importance * self.scoring_weights['business_importance'] +
                automation_suitability * self.scoring_weights['automation_suitability']
            )
            
            return round(overall_score, 3)
            
        except Exception as e:
            logger.warning(f"Element score calculation failed: {e}")
            return 0.5
    
    async def _analyze_testing_attributes(self, element: ExtractedElement) -> Dict[str, Any]:
        """Analyze element attributes for testing purposes"""
        try:
            attributes = element.attributes or {}
            
            testing_attributes = {
                'has_id': bool(attributes.get('id')),
                'has_name': bool(attributes.get('name')),
                'has_test_id': 'data-testid' in attributes,
                'has_role': bool(attributes.get('role')),
                'has_aria_label': bool(attributes.get('aria-label')),
                'has_class': bool(attributes.get('class')),
                'data_attributes': [attr for attr in attributes.keys() if attr.startswith('data-')],
                'selector_options': {
                    'id_selector': f"#{attributes['id']}" if attributes.get('id') else None,
                    'name_selector': f"[name='{attributes['name']}']" if attributes.get('name') else None,
                    'testid_selector': f"[data-testid='{attributes['data-testid']}']" if 'data-testid' in attributes else None,
                    'css_selector': element.css_selector,
                    'xpath': element.xpath
                },
                'recommended_selector': await self._get_recommended_selector(element)
            }
            
            return testing_attributes
            
        except Exception as e:
            logger.warning(f"Testing attributes analysis failed: {e}")
            return {}
    
    async def _prioritize_elements_for_testing(self, elements: List[ExtractedElement]) -> List[Dict[str, Any]]:
        """Prioritize elements for testing based on multiple factors"""
        try:
            priority_elements = []
            
            for i, element in enumerate(elements):
                # Calculate priority score
                priority_score = 0.0
                
                # Element type priority
                if element.element_type == ElementType.BUTTON:
                    priority_score += 0.3
                elif element.element_type in [ElementType.INPUT, ElementType.TEXTAREA]:
                    priority_score += 0.25
                elif element.element_type == ElementType.SELECT:
                    priority_score += 0.2
                elif element.element_type == ElementType.LINK:
                    priority_score += 0.15
                
                # Stability and confidence
                priority_score += (element.stability_score or 0.5) * 0.2
                priority_score += (element.confidence_score or 0.5) * 0.15
                
                # AI analysis bonus
                if element.ai_analysis:
                    ai_priority = element.ai_analysis.get('interaction_priority', 5) / 10.0
                    priority_score += ai_priority * 0.1
                
                # Determine priority level
                if priority_score >= 0.7:
                    priority_level = 'high'
                elif priority_score >= 0.4:
                    priority_level = 'medium'
                else:
                    priority_level = 'low'
                
                priority_elements.append({
                    'element_index': i,
                    'element_info': {
                        'tag_name': element.tag_name,
                        'element_type': element.element_type.value if element.element_type else 'unknown',
                        'css_selector': element.css_selector,
                        'text': element.text[:50] if element.text else ''
                    },
                    'priority_level': priority_level,
                    'priority_score': round(priority_score, 3),
                    'reasoning': self._get_priority_reasoning(element, priority_score)
                })
            
            # Sort by priority score
            priority_elements.sort(key=lambda x: x['priority_score'], reverse=True)
            return priority_elements
            
        except Exception as e:
            logger.error(f"Element prioritization failed: {e}")
            return []
    
    async def _generate_test_scenarios(self, elements: List[ExtractedElement]) -> List[Dict[str, Any]]:
        """Generate test scenarios based on element analysis"""
        try:
            scenarios = []
            
            # Group elements by functionality
            forms = [elem for elem in elements if elem.element_type == ElementType.FORM]
            inputs = [elem for elem in elements if elem.element_type in [ElementType.INPUT, ElementType.TEXTAREA]]
            buttons = [elem for elem in elements if elem.element_type == ElementType.BUTTON]
            links = [elem for elem in elements if elem.element_type == ElementType.LINK]
            
            # Form scenarios
            if forms and inputs:
                scenarios.append({
                    'scenario_type': 'form_interaction',
                    'title': 'Complete form submission workflow',
                    'description': 'Test complete form filling and submission process',
                    'steps': [
                        'Fill all required form fields',
                        'Validate field validation rules',
                        'Submit form',
                        'Verify success/error messages'
                    ],
                    'elements_involved': len(inputs) + len([b for b in buttons if 'submit' in str(b.attributes.get('type', ''))]),
                    'complexity': 'medium' if len(inputs) <= 5 else 'high'
                })
            
            # Navigation scenarios
            if links:
                scenarios.append({
                    'scenario_type': 'navigation',
                    'title': 'Navigation link verification',
                    'description': 'Test all navigation links and page transitions',
                    'steps': [
                        'Click each navigation link',
                        'Verify page loads correctly',
                        'Check URL changes',
                        'Validate page content'
                    ],
                    'elements_involved': len(links),
                    'complexity': 'low' if len(links) <= 3 else 'medium'
                })
            
            # Interactive element scenarios
            if buttons:
                scenarios.append({
                    'scenario_type': 'button_interactions',
                    'title': 'Button functionality testing',
                    'description': 'Test all interactive buttons and their responses',
                    'steps': [
                        'Click each button',
                        'Verify expected actions occur',
                        'Check state changes',
                        'Validate user feedback'
                    ],
                    'elements_involved': len(buttons),
                    'complexity': 'medium'
                })
            
            return scenarios
            
        except Exception as e:
            logger.error(f"Test scenario generation failed: {e}")
            return []
    
    async def _identify_critical_paths(self, elements: List[ExtractedElement]) -> List[Dict[str, Any]]:
        """Identify critical user paths through the page"""
        try:
            critical_paths = []
            
            # Identify form submission paths
            submit_buttons = [elem for elem in elements if elem.element_type == ElementType.BUTTON and 
                            elem.attributes and 'submit' in str(elem.attributes.get('type', ''))]
            
            if submit_buttons:
                inputs = [elem for elem in elements if elem.element_type in [ElementType.INPUT, ElementType.TEXTAREA]]
                critical_paths.append({
                    'path_type': 'form_submission',
                    'description': 'User completes and submits form',
                    'steps': [
                        f'Fill input field: {inp.attributes.get("name", inp.css_selector)}' 
                        for inp in inputs[:5]  # Limit to first 5
                    ] + ['Submit form'],
                    'business_impact': 'high',
                    'elements_count': len(inputs) + len(submit_buttons)
                })
            
            # Identify primary action paths
            primary_buttons = [elem for elem in elements if elem.element_type == ElementType.BUTTON and
                             elem.ai_analysis and elem.ai_analysis.get('business_importance', 0) > 7]
            
            if primary_buttons:
                critical_paths.append({
                    'path_type': 'primary_actions',
                    'description': 'User performs primary page actions',
                    'steps': [f'Click {btn.text or btn.css_selector}' for btn in primary_buttons[:3]],
                    'business_impact': 'high',
                    'elements_count': len(primary_buttons)
                })
            
            return critical_paths
            
        except Exception as e:
            logger.error(f"Critical path identification failed: {e}")
            return []
    
    async def _analyze_test_data_requirements(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Analyze what test data is needed for testing"""
        try:
            test_data_requirements = {
                'input_fields': [],
                'selection_fields': [],
                'file_uploads': [],
                'data_types_needed': set()
            }
            
            for element in elements:
                if element.element_type == ElementType.INPUT and element.attributes:
                    input_type = element.attributes.get('type', 'text')
                    field_name = element.attributes.get('name', element.css_selector)
                    
                    field_info = {
                        'field_name': field_name,
                        'input_type': input_type,
                        'required': 'required' in element.attributes,
                        'placeholder': element.attributes.get('placeholder', ''),
                        'max_length': element.attributes.get('maxlength'),
                        'pattern': element.attributes.get('pattern')
                    }
                    
                    test_data_requirements['input_fields'].append(field_info)
                    
                    # Determine data type needed
                    if input_type in ['email']:
                        test_data_requirements['data_types_needed'].add('email_addresses')
                    elif input_type in ['tel', 'phone']:
                        test_data_requirements['data_types_needed'].add('phone_numbers')
                    elif input_type in ['password']:
                        test_data_requirements['data_types_needed'].add('passwords')
                    elif input_type in ['date']:
                        test_data_requirements['data_types_needed'].add('dates')
                    elif input_type in ['number']:
                        test_data_requirements['data_types_needed'].add('numbers')
                    else:
                        test_data_requirements['data_types_needed'].add('text_strings')
                
                elif element.element_type == ElementType.SELECT:
                    test_data_requirements['selection_fields'].append({
                        'field_name': element.attributes.get('name', element.css_selector),
                        'multiple': 'multiple' in element.attributes
                    })
                    test_data_requirements['data_types_needed'].add('selection_options')
                
                elif element.element_type == ElementType.INPUT and element.attributes.get('type') == 'file':
                    test_data_requirements['file_uploads'].append({
                        'field_name': element.attributes.get('name', element.css_selector),
                        'accept': element.attributes.get('accept', '*/*'),
                        'multiple': 'multiple' in element.attributes
                    })
                    test_data_requirements['data_types_needed'].add('test_files')
            
            # Convert set to list for JSON serialization
            test_data_requirements['data_types_needed'] = list(test_data_requirements['data_types_needed'])
            
            return test_data_requirements
            
        except Exception as e:
            logger.error(f"Test data requirements analysis failed: {e}")
            return {}
    
    async def _estimate_testing_effort(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Estimate testing effort based on page complexity"""
        try:
            # Base effort calculation
            total_elements = len(elements)
            interactive_elements = sum(1 for elem in elements if elem.is_interactable)
            forms = sum(1 for elem in elements if elem.element_type == ElementType.FORM)
            
            # Effort points calculation
            effort_points = 0
            effort_points += total_elements * 0.5  # Base effort per element
            effort_points += interactive_elements * 1.5  # Extra effort for interactive elements
            effort_points += forms * 5  # Significant effort for forms
            
            # Time estimation (in hours)
            estimated_hours = effort_points / 10  # Rough conversion
            
            # Complexity assessment
            if effort_points < 20:
                complexity = 'low'
                risk_level = 'low'
            elif effort_points < 50:
                complexity = 'medium'
                risk_level = 'medium'
            else:
                complexity = 'high'
                risk_level = 'high'
            
            return {
                'effort_points': round(effort_points, 1),
                'estimated_hours': round(estimated_hours, 1),
                'complexity': complexity,
                'risk_level': risk_level,
                'breakdown': {
                    'total_elements': total_elements,
                    'interactive_elements': interactive_elements,
                    'forms': forms,
                    'unique_element_types': len(set(elem.element_type for elem in elements))
                }
            }
            
        except Exception as e:
            logger.error(f"Testing effort estimation failed: {e}")
            return {}
    
    async def _recommend_testing_approach(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Recommend testing approach based on analysis"""
        try:
            approach = {
                'recommended_strategy': 'hybrid',
                'test_types': [],
                'automation_percentage': 0,
                'manual_testing_areas': [],
                'tools_recommended': []
            }
            
            # Analyze automation potential
            automation_suitable = sum(1 for elem in elements if await self._calculate_automation_suitability(elem) >= 0.7)
            automation_percentage = automation_suitable / len(elements) if elements else 0
            
            approach['automation_percentage'] = round(automation_percentage * 100, 1)
            
            # Recommend test types
            if any(elem.element_type == ElementType.FORM for elem in elements):
                approach['test_types'].extend(['functional', 'validation', 'integration'])
            
            if any(elem.element_type == ElementType.LINK for elem in elements):
                approach['test_types'].append('navigation')
            
            if automation_percentage >= 0.7:
                approach['test_types'].append('automated_regression')
                approach['recommended_strategy'] = 'automation_first'
            elif automation_percentage >= 0.3:
                approach['test_types'].append('selective_automation')
            else:
                approach['recommended_strategy'] = 'manual_first'
                approach['manual_testing_areas'].extend(['complex_interactions', 'visual_validation'])
            
            # Tool recommendations
            if automation_percentage >= 0.5:
                approach['tools_recommended'].extend(['playwright', 'selenium'])
            
            approach['tools_recommended'].extend(['postman', 'manual_testing'])
            
            return approach
            
        except Exception as e:
            logger.error(f"Testing approach recommendation failed: {e}")
            return {}
    
    def _get_priority_reasoning(self, element: ExtractedElement, priority_score: float) -> str:
        """Get reasoning for element priority"""
        reasons = []
        
        if element.element_type == ElementType.BUTTON:
            reasons.append("Interactive button element")
        if element.stability_score and element.stability_score >= 0.7:
            reasons.append("High stability score")
        if element.attributes and 'data-testid' in element.attributes:
            reasons.append("Has test ID attribute")
        if element.ai_analysis and element.ai_analysis.get('business_importance', 0) > 7:
            reasons.append("High business importance")
        
        if not reasons:
            reasons.append("Standard element priority")
        
        return "; ".join(reasons)
    
    async def _get_automation_score_reasons(self, element: ExtractedElement, score: float) -> List[str]:
        """Get reasons for automation suitability score"""
        reasons = []
        attributes = element.attributes or {}
        
        if attributes.get('id'):
            reasons.append("Has unique ID attribute")
        if 'data-testid' in attributes:
            reasons.append("Has data-testid attribute")
        if element.is_visible and element.is_interactable:
            reasons.append("Visible and interactable")
        if element.stability_score and element.stability_score >= 0.7:
            reasons.append("High stability score")
        if score < 0.4:
            reasons.append("Missing stable selectors")
        
        return reasons
    
    async def _identify_automation_issues(self, element: ExtractedElement) -> List[str]:
        """Identify specific automation issues with element"""
        issues = []
        attributes = element.attributes or {}
        
        if not attributes.get('id') and 'data-testid' not in attributes:
            issues.append("No stable ID or test ID attribute")
        if not element.is_visible:
            issues.append("Element not visible")
        if not element.is_interactable:
            issues.append("Element not interactable")
        if element.stability_score and element.stability_score < 0.3:
            issues.append("Low stability score")
        if not element.css_selector or len(element.css_selector) > 100:
            issues.append("Complex or unreliable CSS selector")
        
        return issues
    
    async def _generate_selector_recommendations(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Generate recommendations for better selectors"""
        recommendations = {
            'add_test_ids': [],
            'improve_selectors': [],
            'best_practices': []
        }
        
        for element in elements:
            attributes = element.attributes or {}
            
            if not attributes.get('id') and 'data-testid' not in attributes:
                recommendations['add_test_ids'].append({
                    'element': element.css_selector,
                    'suggestion': f"Add data-testid='{element.tag_name}_{hash(element.css_selector) % 10000}'"
                })
            
            if element.stability_score and element.stability_score < 0.5:
                recommendations['improve_selectors'].append({
                    'element': element.css_selector,
                    'current_score': element.stability_score,
                    'suggestions': ["Add unique ID", "Use data attributes", "Avoid position-based selectors"]
                })
        
        recommendations['best_practices'] = [
            "Use data-testid attributes for test automation",
            "Prefer ID selectors over class-based selectors",
            "Avoid complex CSS selectors with multiple levels",
            "Use semantic attributes when possible"
        ]
        
        return recommendations
    
    async def _predict_maintenance_needs(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Predict maintenance needs for automated tests"""
        predictions = {
            'high_maintenance_elements': [],
            'stable_elements': [],
            'maintenance_score': 0.0
        }
        
        high_maintenance_count = 0
        stable_count = 0
        
        for element in elements:
            if element.stability_score and element.stability_score < 0.4:
                high_maintenance_count += 1
                predictions['high_maintenance_elements'].append({
                    'element': element.css_selector,
                    'stability_score': element.stability_score,
                    'risks': ["Selector may break with UI changes", "Position-dependent locator"]
                })
            elif element.stability_score and element.stability_score >= 0.7:
                stable_count += 1
                predictions['stable_elements'].append(element.css_selector)
        
        if elements:
            predictions['maintenance_score'] = round(stable_count / len(elements), 3)
        
        return predictions
    
    async def _calculate_page_type_confidence(self, elements: List[ExtractedElement], page_type: str) -> float:
        """Calculate confidence in page type classification"""
        try:
            confidence = 0.5  # Base confidence
            
            # Confidence factors based on element patterns
            forms = sum(1 for elem in elements if elem.element_type == ElementType.FORM)
            inputs = sum(1 for elem in elements if elem.element_type in [ElementType.INPUT, ElementType.TEXTAREA])
            buttons = sum(1 for elem in elements if elem.element_type == ElementType.BUTTON)
            links = sum(1 for elem in elements if elem.element_type == ElementType.LINK)
            
            if page_type == 'form_page' and forms > 0 and inputs > 3:
                confidence = 0.9
            elif page_type == 'navigation_page' and links > 5:
                confidence = 0.8
            elif page_type == 'application_page' and buttons > 5:
                confidence = 0.7
            
            return round(confidence, 2)
            
        except:
            return 0.5
    
    async def _generate_element_recommendations(self, element: ExtractedElement) -> List[str]:
        """Generate recommendations for improving element testability"""
        recommendations = []
        
        try:
            attributes = element.attributes or {}
            
            # ID recommendations
            if not attributes.get('id'):
                recommendations.append("Add unique 'id' attribute for more stable element identification")
            
            # Test ID recommendations
            if 'data-testid' not in attributes:
                recommendations.append("Add 'data-testid' attribute for test automation")
            
            # Accessibility recommendations
            if element.element_type in [ElementType.BUTTON, ElementType.LINK] and not attributes.get('aria-label'):
                recommendations.append("Add 'aria-label' for better accessibility and testing")
            
            # Text content recommendations
            if element.element_type == ElementType.BUTTON and not element.text.strip():
                recommendations.append("Add visible text content for better element identification")
            
            # Selector stability recommendations
            if element.stability_score < 0.5:
                recommendations.append("Improve selector stability with more specific attributes")
            
            # Interaction recommendations
            if not element.is_interactable and element.element_type in [ElementType.BUTTON, ElementType.INPUT]:
                recommendations.append("Ensure element is properly interactable")
            
        except Exception as e:
            logger.warning(f"Element recommendations generation failed: {e}")
        
        return recommendations
    
    async def _calculate_automation_suitability(self, element: ExtractedElement) -> float:
        """Calculate how suitable an element is for automation"""
        try:
            score = 0.0
            attributes = element.attributes or {}
            
            # Stability factors
            if element.stability_score:
                score += element.stability_score * 0.3
            
            # Selector reliability
            if attributes.get('id'):
                score += 0.25
            if 'data-testid' in attributes:
                score += 0.20
            if attributes.get('name'):
                score += 0.15
            
            # Visibility and interactability
            if element.is_visible:
                score += 0.1
            if element.is_interactable:
                score += 0.1
            
            # Element type suitability
            if element.element_type in [ElementType.BUTTON, ElementType.INPUT, ElementType.SELECT]:
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.warning(f"Automation suitability calculation failed: {e}")
            return 0.5
    
    # Helper methods for analysis components
    async def _identify_forms(self, elements: List[ExtractedElement]) -> List[Dict[str, Any]]:
        """Identify forms and their constituent elements"""
        forms = []
        form_elements = [elem for elem in elements if elem.element_type == ElementType.FORM]
        
        for form_elem in form_elements:
            form_info = {
                'form_element': {
                    'css_selector': form_elem.css_selector,
                    'attributes': form_elem.attributes
                },
                'input_elements': [],
                'submit_buttons': [],
                'complexity_score': 0
            }
            
            # Find related input elements (simplified - in real implementation, 
            # we'd need DOM tree analysis)
            for elem in elements:
                if elem.element_type in [ElementType.INPUT, ElementType.TEXTAREA, ElementType.SELECT]:
                    form_info['input_elements'].append({
                        'type': elem.element_type.value,
                        'css_selector': elem.css_selector,
                        'attributes': elem.attributes
                    })
                elif elem.element_type == ElementType.BUTTON and elem.attributes.get('type') == 'submit':
                    form_info['submit_buttons'].append({
                        'css_selector': elem.css_selector,
                        'text': elem.text
                    })
            
            form_info['complexity_score'] = len(form_info['input_elements'])
            forms.append(form_info)
        
        return forms
    
    async def _identify_navigation_elements(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Identify navigation-related elements"""
        nav_links = [elem for elem in elements if elem.element_type == ElementType.LINK]
        nav_buttons = [elem for elem in elements if elem.element_type == ElementType.BUTTON and 
                      'nav' in (elem.attributes.get('class', '') + elem.attributes.get('role', '')).lower()]
        
        return {
            'links': len(nav_links),
            'buttons': len(nav_buttons),
            'total_navigation_elements': len(nav_links) + len(nav_buttons)
        }
    
    async def _identify_content_areas(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Identify content areas and their characteristics"""
        content_elements = [elem for elem in elements if elem.element_type == ElementType.OTHER]
        interactive_elements = [elem for elem in elements if elem.is_interactable]
        
        return {
            'content_elements': len(content_elements),
            'interactive_elements': len(interactive_elements),
            'content_to_interaction_ratio': len(content_elements) / max(len(interactive_elements), 1)
        }
    
    async def _calculate_page_complexity(self, elements: List[ExtractedElement]) -> float:
        """Calculate overall page complexity score"""
        try:
            total_elements = len(elements)
            if total_elements == 0:
                return 0.0
            
            interactive_elements = sum(1 for elem in elements if elem.is_interactable)
            unique_types = len(set(elem.element_type for elem in elements))
            
            # Normalize to 0-1 scale
            complexity = min((interactive_elements / 10) + (unique_types / 10) + (total_elements / 100), 1.0)
            return round(complexity, 3)
            
        except:
            return 0.5
    
    async def _determine_page_type(self, elements: List[ExtractedElement], url: str) -> str:
        """Determine the type/purpose of the page"""
        try:
            # Analyze element patterns
            forms = sum(1 for elem in elements if elem.element_type == ElementType.FORM)
            inputs = sum(1 for elem in elements if elem.element_type in [ElementType.INPUT, ElementType.TEXTAREA])
            buttons = sum(1 for elem in elements if elem.element_type == ElementType.BUTTON)
            links = sum(1 for elem in elements if elem.element_type == ElementType.LINK)
            
            # Simple heuristics for page type
            if forms > 0 and inputs > 3:
                return 'form_page'
            elif links > inputs and links > buttons:
                return 'navigation_page'
            elif buttons > 5:
                return 'application_page'
            elif 'login' in url.lower():
                return 'login_page'
            elif 'register' in url.lower() or 'signup' in url.lower():
                return 'registration_page'
            else:
                return 'content_page'
                
        except:
            return 'unknown'
    
    # Additional helper methods would continue here...
    # For brevity, I'm including the key methods that demonstrate the architecture
    
    async def _create_ai_insights_prompt(self, elements: List[ExtractedElement], url: str) -> str:
        """Create prompt for AI insights analysis"""
        
        # Prepare element summaries for AI (limit for token efficiency)
        element_summaries = []
        for i, elem in enumerate(elements[:20]):  # Limit to first 20 elements
            summary = {
                'index': i,
                'tag': elem.tag_name,
                'type': elem.element_type.value if elem.element_type else 'unknown',
                'text': elem.text[:50] if elem.text else '',
                'attributes': {
                    'id': elem.attributes.get('id', '') if elem.attributes else '',
                    'class': elem.attributes.get('class', '') if elem.attributes else '',
                    'role': elem.attributes.get('role', '') if elem.attributes else ''
                },
                'is_visible': elem.is_visible,
                'is_interactable': elem.is_interactable
            }
            element_summaries.append(summary)
        
        prompt = f"""
        Analyze this webpage and provide insights for test automation strategy.
        
        URL: {url}
        Elements analyzed: {len(element_summaries)} of {len(elements)} total
        
        Page Elements:
        {json.dumps(element_summaries, indent=2)}
        
        Please provide:
        1. Page workflow analysis - what is the main user journey on this page?
        2. Testing priorities - which elements are most critical for testing?
        3. Risk assessment - what could go wrong during testing?
        4. Automation strategy - best approach for automating tests on this page
        5. Maintainability concerns - what might make tests fragile?
        6. Business impact assessment - which features are most important?
        
        Return as JSON with this structure:
        {{
            "workflow_analysis": {{
                "primary_purpose": "description",
                "user_journey_steps": ["step1", "step2"],
                "key_interactions": ["interaction1", "interaction2"]
            }},
            "testing_priorities": [
                {{"element_index": 0, "priority": "high", "reason": "explanation"}}
            ],
            "risk_assessment": {{
                "high_risk_elements": [],
                "potential_failures": [],
                "stability_concerns": []
            }},
            "automation_strategy": {{
                "recommended_approach": "description",
                "test_types": ["unit", "integration", "e2e"],
                "tools_suggestions": []
            }},
            "maintainability": {{
                "fragile_selectors": [],
                "improvement_suggestions": [],
                "monitoring_recommendations": []
            }},
            "business_impact": {{
                "critical_paths": [],
                "revenue_affecting_elements": [],
                "user_experience_factors": []
            }}
        }}
        """
        
        return prompt
    
    async def _has_stable_selector(self, element: ExtractedElement) -> bool:
        """Check if element has stable selector attributes"""
        if not element.attributes:
            return False
        
        stable_attributes = ['id', 'data-testid', 'name']
        return any(attr in element.attributes for attr in stable_attributes)
    
    async def _has_aria_attributes(self, element: ExtractedElement) -> bool:
        """Check if element has ARIA attributes"""
        if not element.attributes:
            return False
        
        return any(attr.startswith('aria-') for attr in element.attributes)
    
    async def _has_proper_labels(self, element: ExtractedElement) -> bool:
        """Check if element has proper labels"""
        if not element.attributes:
            return False
        
        return bool(element.attributes.get('aria-label') or element.attributes.get('label'))
    
    async def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of scores"""
        if not scores:
            return {'low': 0, 'medium': 0, 'high': 0}
        
        low = sum(1 for score in scores if score < 0.4)
        medium = sum(1 for score in scores if 0.4 <= score < 0.7)
        high = sum(1 for score in scores if score >= 0.7)
        
        return {'low': low, 'medium': medium, 'high': high}
    
    async def _calculate_composite_quality_score(self, elements: List[ExtractedElement]) -> float:
        """Calculate composite quality score for all elements"""
        if not elements:
            return 0.0
        
        scores = []
        for element in elements:
            element_score = await self._calculate_element_score(element)
            scores.append(element_score)
        
        return round(sum(scores) / len(scores), 3)
    
    async def _assign_quality_grade(self, elements: List[ExtractedElement]) -> str:
        """Assign quality grade based on analysis"""
        composite_score = await self._calculate_composite_quality_score(elements)
        
        if composite_score >= 0.8:
            return 'A'
        elif composite_score >= 0.6:
            return 'B'
        elif composite_score >= 0.4:
            return 'C'
        elif composite_score >= 0.2:
            return 'D'
        else:
            return 'F'
    
    async def _get_recommended_selector(self, element: ExtractedElement) -> str:
        """Get the most recommended selector for the element"""
        attributes = element.attributes or {}
        
        # Priority order: data-testid > id > name > css_selector > xpath
        if 'data-testid' in attributes:
            return f"[data-testid='{attributes['data-testid']}']"
        elif attributes.get('id'):
            return f"#{attributes['id']}"
        elif attributes.get('name'):
            return f"[name='{attributes['name']}']"
        elif element.css_selector:
            return element.css_selector
        elif element.xpath:
            return element.xpath
        else:
            return f"{element.tag_name}:contains('{element.text[:20]}')" if element.text else element.tag_name
