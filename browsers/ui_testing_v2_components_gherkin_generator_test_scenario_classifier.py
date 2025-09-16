"""
Test Scenario Classifier

Classifies and prioritizes test scenarios based on element patterns
and page characteristics.
"""

import logging
from typing import Dict, List, Any, Set, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class TestScenarioClassifier:
    """
    Classifies test scenarios based on element patterns.
    
    Features:
    - Pattern-based scenario detection
    - Priority calculation based on business impact
    - Coverage analysis
    - Scenario deduplication
    """
    
    def __init__(self, config):
        self.config = config
        
        # Scenario type definitions with patterns
        self.scenario_types = {
            'authentication': {
                'patterns': ['login', 'password', 'username', 'email', 'sign in', 'log in'],
                'required_elements': ['input[type="password"]', 'button'],
                'priority': 'critical',
                'business_impact': 'high'
            },
            'form_submission': {
                'patterns': ['form', 'submit', 'send', 'save'],
                'required_elements': ['form', 'input', 'button[type="submit"]'],
                'priority': 'high',
                'business_impact': 'high'
            },
            'search': {
                'patterns': ['search', 'find', 'query', 'filter'],
                'required_elements': ['input[type="search"]', 'button'],
                'priority': 'high',
                'business_impact': 'medium'
            },
            'navigation': {
                'patterns': ['menu', 'nav', 'breadcrumb', 'link'],
                'required_elements': ['nav', 'a'],
                'priority': 'medium',
                'business_impact': 'medium'
            },
            'data_table': {
                'patterns': ['table', 'grid', 'list', 'sort', 'pagination'],
                'required_elements': ['table', 'tr'],
                'priority': 'medium',
                'business_impact': 'medium'
            },
            'file_upload': {
                'patterns': ['upload', 'file', 'attach', 'browse'],
                'required_elements': ['input[type="file"]', 'button'],
                'priority': 'medium',
                'business_impact': 'medium'
            },
            'modal_interaction': {
                'patterns': ['modal', 'dialog', 'popup', 'overlay'],
                'required_elements': ['[role="dialog"]', 'button'],
                'priority': 'medium',
                'business_impact': 'low'
            },
            'shopping_cart': {
                'patterns': ['cart', 'basket', 'checkout', 'add to cart', 'buy'],
                'required_elements': ['button', 'form'],
                'priority': 'critical',
                'business_impact': 'critical'
            },
            'user_registration': {
                'patterns': ['register', 'sign up', 'create account', 'join'],
                'required_elements': ['form', 'input[type="email"]', 'input[type="password"]'],
                'priority': 'high',
                'business_impact': 'high'
            },
            'content_editing': {
                'patterns': ['edit', 'update', 'modify', 'save', 'publish'],
                'required_elements': ['textarea', 'button'],
                'priority': 'medium',
                'business_impact': 'medium'
            },
            'filtering': {
                'patterns': ['filter', 'sort', 'category', 'price range'],
                'required_elements': ['select', 'checkbox', 'radio'],
                'priority': 'medium',
                'business_impact': 'medium'
            },
            'social_interaction': {
                'patterns': ['like', 'share', 'comment', 'follow', 'tweet'],
                'required_elements': ['button', 'textarea'],
                'priority': 'low',
                'business_impact': 'low'
            }
        }
        
        # Test coverage requirements
        self.coverage_requirements = {
            'positive_flows': 0.6,  # 60% positive test cases
            'negative_flows': 0.25,  # 25% negative test cases
            'edge_cases': 0.15      # 15% edge cases
        }
        
        logger.info("TestScenarioClassifier initialized with %d scenario types", 
                   len(self.scenario_types))
    
    async def classify_scenarios(
        self,
        element_context: Dict[str, Any],
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Classify potential test scenarios based on element patterns.
        
        Returns:
            List of classified scenarios with metadata
        """
        try:
            classifications = []
            
            # Analyze element patterns
            detected_patterns = self._detect_patterns(element_context)
            
            # Classify based on detected patterns
            for pattern_type, pattern_data in detected_patterns.items():
                if pattern_data['confidence'] > 0.5:  # Confidence threshold
                    classification = {
                        'type': pattern_type,
                        'description': self._get_scenario_description(pattern_type),
                        'priority': self.scenario_types[pattern_type]['priority'],
                        'business_impact': self.scenario_types[pattern_type]['business_impact'],
                        'confidence': pattern_data['confidence'],
                        'element_count': pattern_data['element_count'],
                        'matched_patterns': pattern_data['matched_patterns'],
                        'suggested_scenarios': self._suggest_scenarios(pattern_type, element_context)
                    }
                    classifications.append(classification)
            
            # Add custom scenarios based on AI analysis
            if analysis_results:
                custom_classifications = self._extract_custom_scenarios(analysis_results)
                classifications.extend(custom_classifications)
            
            # Sort by priority and confidence
            classifications.sort(
                key=lambda x: (
                    self._priority_to_score(x['priority']),
                    x['confidence']
                ),
                reverse=True
            )
            
            # Ensure coverage balance
            balanced_classifications = self._balance_scenario_coverage(classifications)
            
            logger.info("Classified %d scenario types", len(balanced_classifications))
            return balanced_classifications
            
        except Exception as e:
            logger.error(f"Scenario classification failed: {e}")
            return []
    
    def _detect_patterns(self, element_context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Detect patterns in elements that match scenario types."""
        detected_patterns = {}
        
        # Get all elements and their text
        all_elements = []
        element_groups = element_context.get('element_groups', {})
        
        for group_elements in element_groups.values():
            all_elements.extend(group_elements)
        
        # Check each scenario type
        for scenario_type, type_config in self.scenario_types.items():
            pattern_matches = []
            element_matches = 0
            
            # Check text patterns
            for element in all_elements:
                element_text = (element.get('text', '') + ' ' + 
                              element.get('selector', '') + ' ' +
                              ' '.join(element.get('attributes', {}).values())).lower()
                
                for pattern in type_config['patterns']:
                    if pattern.lower() in element_text:
                        pattern_matches.append(pattern)
                        break
            
            # Check required elements
            for required in type_config['required_elements']:
                if self._has_element_type(all_elements, required):
                    element_matches += 1
            
            # Calculate confidence
            pattern_score = len(set(pattern_matches)) / len(type_config['patterns'])
            element_score = element_matches / len(type_config['required_elements'])
            confidence = (pattern_score * 0.6 + element_score * 0.4)
            
            if confidence > 0:
                detected_patterns[scenario_type] = {
                    'confidence': confidence,
                    'matched_patterns': list(set(pattern_matches)),
                    'element_count': element_matches,
                    'total_matches': len(pattern_matches)
                }
        
        return detected_patterns
    
    def _has_element_type(self, elements: List[Dict[str, Any]], element_pattern: str) -> bool:
        """Check if elements contain a specific type pattern."""
        for element in elements:
            # Check tag match
            if element_pattern.startswith('<') and element_pattern.endswith('>'):
                tag = element_pattern[1:-1]
                if element.get('tag', '') == tag:
                    return True
            
            # Check selector pattern
            selector = element.get('selector', '')
            element_type = element.get('type', '')
            
            # Simple pattern matching
            if '[type="' in element_pattern:
                # Extract type from pattern
                import re
                type_match = re.search(r'\[type="([^"]+)"\]', element_pattern)
                if type_match:
                    expected_type = type_match.group(1)
                    attributes = element.get('attributes', {})
                    if attributes.get('type') == expected_type:
                        return True
            
            # Role-based matching
            if '[role="' in element_pattern:
                import re
                role_match = re.search(r'\[role="([^"]+)"\]', element_pattern)
                if role_match:
                    expected_role = role_match.group(1)
                    attributes = element.get('attributes', {})
                    if attributes.get('role') == expected_role:
                        return True
            
            # Direct tag matching
            if element_pattern in ['form', 'nav', 'table', 'button', 'input', 'select', 'textarea']:
                if element.get('tag', '') == element_pattern or element_type.lower() == element_pattern:
                    return True
        
        return False
    
    def _get_scenario_description(self, pattern_type: str) -> str:
        """Get human-readable description for scenario type."""
        descriptions = {
            'authentication': 'User authentication and login flows',
            'form_submission': 'Form filling and submission workflows',
            'search': 'Search functionality and result validation',
            'navigation': 'Site navigation and menu interactions',
            'data_table': 'Data table interactions, sorting, and pagination',
            'file_upload': 'File upload functionality',
            'modal_interaction': 'Modal dialog interactions',
            'shopping_cart': 'E-commerce cart and checkout flows',
            'user_registration': 'New user registration process',
            'content_editing': 'Content creation and editing workflows',
            'filtering': 'Data filtering and sorting operations',
            'social_interaction': 'Social media interaction features'
        }
        
        return descriptions.get(pattern_type, f'{pattern_type.replace("_", " ").title()} scenarios')
    
    def _suggest_scenarios(
        self,
        pattern_type: str,
        element_context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Suggest specific scenarios for a pattern type."""
        suggestions = {
            'authentication': [
                {'name': 'Valid login', 'type': 'positive', 'priority': 'critical'},
                {'name': 'Invalid credentials', 'type': 'negative', 'priority': 'high'},
                {'name': 'Password reset', 'type': 'positive', 'priority': 'high'},
                {'name': 'Remember me functionality', 'type': 'positive', 'priority': 'medium'},
                {'name': 'Account lockout', 'type': 'negative', 'priority': 'medium'}
            ],
            'form_submission': [
                {'name': 'Submit with all fields', 'type': 'positive', 'priority': 'high'},
                {'name': 'Required field validation', 'type': 'negative', 'priority': 'high'},
                {'name': 'Field format validation', 'type': 'negative', 'priority': 'medium'},
                {'name': 'Form reset', 'type': 'positive', 'priority': 'low'},
                {'name': 'Partial form save', 'type': 'positive', 'priority': 'medium'}
            ],
            'search': [
                {'name': 'Basic search', 'type': 'positive', 'priority': 'high'},
                {'name': 'Empty search', 'type': 'edge_case', 'priority': 'medium'},
                {'name': 'Special characters', 'type': 'edge_case', 'priority': 'medium'},
                {'name': 'No results found', 'type': 'negative', 'priority': 'medium'},
                {'name': 'Search filters', 'type': 'positive', 'priority': 'medium'}
            ],
            'navigation': [
                {'name': 'Main menu navigation', 'type': 'positive', 'priority': 'high'},
                {'name': 'Breadcrumb navigation', 'type': 'positive', 'priority': 'medium'},
                {'name': 'Deep linking', 'type': 'positive', 'priority': 'medium'},
                {'name': 'Mobile menu', 'type': 'positive', 'priority': 'high'},
                {'name': 'Keyboard navigation', 'type': 'accessibility', 'priority': 'medium'}
            ],
            'shopping_cart': [
                {'name': 'Add to cart', 'type': 'positive', 'priority': 'critical'},
                {'name': 'Update quantities', 'type': 'positive', 'priority': 'high'},
                {'name': 'Remove from cart', 'type': 'positive', 'priority': 'high'},
                {'name': 'Apply coupon', 'type': 'positive', 'priority': 'medium'},
                {'name': 'Checkout process', 'type': 'positive', 'priority': 'critical'},
                {'name': 'Out of stock handling', 'type': 'negative', 'priority': 'high'}
            ]
        }
        
        # Get base suggestions
        base_suggestions = suggestions.get(pattern_type, [
            {'name': 'Basic interaction', 'type': 'positive', 'priority': 'medium'},
            {'name': 'Error handling', 'type': 'negative', 'priority': 'medium'},
            {'name': 'Edge cases', 'type': 'edge_case', 'priority': 'low'}
        ])
        
        # Customize based on actual elements
        customized_suggestions = []
        for suggestion in base_suggestions:
            customized = suggestion.copy()
            
            # Add element count context
            element_groups = element_context.get('element_groups', {})
            relevant_elements = 0
            
            for group_name, elements in element_groups.items():
                if self._is_relevant_group(group_name, pattern_type):
                    relevant_elements += len(elements)
            
            customized['element_context'] = {
                'available_elements': relevant_elements,
                'complexity': self._estimate_complexity(relevant_elements)
            }
            
            customized_suggestions.append(customized)
        
        return customized_suggestions
    
    def _is_relevant_group(self, group_name: str, pattern_type: str) -> bool:
        """Check if element group is relevant to pattern type."""
        relevance_map = {
            'authentication': ['forms', 'inputs', 'actions'],
            'form_submission': ['forms', 'inputs', 'actions'],
            'search': ['inputs', 'actions'],
            'navigation': ['navigation', 'links'],
            'data_table': ['tables'],
            'file_upload': ['inputs', 'actions'],
            'modal_interaction': ['modals', 'actions'],
            'shopping_cart': ['actions', 'forms', 'links'],
            'user_registration': ['forms', 'inputs', 'actions'],
            'content_editing': ['inputs', 'actions', 'forms'],
            'filtering': ['inputs', 'actions'],
            'social_interaction': ['actions', 'links']
        }
        
        relevant_groups = relevance_map.get(pattern_type, [])
        return group_name in relevant_groups
    
    def _estimate_complexity(self, element_count: int) -> str:
        """Estimate test complexity based on element count."""
        if element_count < 5:
            return 'simple'
        elif element_count < 15:
            return 'medium'
        else:
            return 'complex'
    
    def _extract_custom_scenarios(
        self,
        analysis_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract custom scenarios from AI analysis results."""
        custom_scenarios = []
        
        # Extract from business rules
        business_rules = analysis_results.get('business_rules', [])
        for rule in business_rules:
            if isinstance(rule, dict) and 'test_scenario' in rule:
                custom_scenarios.append({
                    'type': 'custom_business_rule',
                    'description': rule.get('description', 'Custom business rule test'),
                    'priority': rule.get('priority', 'medium'),
                    'business_impact': rule.get('impact', 'medium'),
                    'confidence': rule.get('confidence', 0.7),
                    'element_count': 0,
                    'matched_patterns': [],
                    'suggested_scenarios': [
                        {
                            'name': rule.get('test_scenario'),
                            'type': 'business_logic',
                            'priority': rule.get('priority', 'medium')
                        }
                    ]
                })
        
        # Extract from AI insights
        ai_insights = analysis_results.get('ai_analysis', {})
        if 'suggested_tests' in ai_insights:
            for test in ai_insights['suggested_tests']:
                custom_scenarios.append({
                    'type': 'ai_suggested',
                    'description': test.get('description', 'AI suggested test'),
                    'priority': test.get('priority', 'medium'),
                    'business_impact': test.get('impact', 'medium'),
                    'confidence': 0.8,
                    'element_count': 0,
                    'matched_patterns': [],
                    'suggested_scenarios': [
                        {
                            'name': test.get('name'),
                            'type': test.get('type', 'functional'),
                            'priority': test.get('priority', 'medium')
                        }
                    ]
                })
        
        return custom_scenarios
    
    def _balance_scenario_coverage(
        self,
        classifications: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Balance scenario coverage to meet requirements."""
        # Count current distribution
        type_counts = defaultdict(int)
        
        for classification in classifications:
            for scenario in classification.get('suggested_scenarios', []):
                scenario_type = scenario.get('type', 'positive')
                type_counts[scenario_type] += 1
        
        total_scenarios = sum(type_counts.values())
        
        if total_scenarios == 0:
            return classifications
        
        # Check coverage
        current_coverage = {
            'positive': type_counts.get('positive', 0) / total_scenarios,
            'negative': type_counts.get('negative', 0) / total_scenarios,
            'edge_case': type_counts.get('edge_case', 0) / total_scenarios
        }
        
        # Add scenarios if coverage is insufficient
        balanced_classifications = classifications.copy()
        
        # Add negative scenarios if needed
        if current_coverage['negative'] < self.coverage_requirements['negative_flows']:
            balanced_classifications.append({
                'type': 'negative_testing',
                'description': 'Additional negative test scenarios for comprehensive coverage',
                'priority': 'medium',
                'business_impact': 'medium',
                'confidence': 0.9,
                'element_count': 0,
                'matched_patterns': [],
                'suggested_scenarios': [
                    {'name': 'Invalid data submission', 'type': 'negative', 'priority': 'high'},
                    {'name': 'Boundary value testing', 'type': 'negative', 'priority': 'medium'},
                    {'name': 'Security testing', 'type': 'negative', 'priority': 'high'}
                ]
            })
        
        # Add edge cases if needed
        if current_coverage['edge_case'] < self.coverage_requirements['edge_cases']:
            balanced_classifications.append({
                'type': 'edge_case_testing',
                'description': 'Edge case scenarios for robustness testing',
                'priority': 'low',
                'business_impact': 'low',
                'confidence': 0.8,
                'element_count': 0,
                'matched_patterns': [],
                'suggested_scenarios': [
                    {'name': 'Concurrent operations', 'type': 'edge_case', 'priority': 'medium'},
                    {'name': 'Network interruption', 'type': 'edge_case', 'priority': 'low'},
                    {'name': 'Browser compatibility', 'type': 'edge_case', 'priority': 'medium'}
                ]
            })
        
        return balanced_classifications
    
    def _priority_to_score(self, priority: str) -> int:
        """Convert priority string to numeric score."""
        priority_scores = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2,
            'trivial': 1
        }
        return priority_scores.get(priority, 3)
    
    def get_scenario_statistics(
        self,
        classifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get statistics about classified scenarios."""
        stats = {
            'total_classifications': len(classifications),
            'scenario_types': defaultdict(int),
            'priority_distribution': defaultdict(int),
            'business_impact_distribution': defaultdict(int),
            'average_confidence': 0,
            'coverage_analysis': {}
        }
        
        total_confidence = 0
        scenario_type_counts = defaultdict(int)
        
        for classification in classifications:
            stats['scenario_types'][classification['type']] += 1
            stats['priority_distribution'][classification['priority']] += 1
            stats['business_impact_distribution'][classification['business_impact']] += 1
            total_confidence += classification['confidence']
            
            # Count suggested scenario types
            for scenario in classification.get('suggested_scenarios', []):
                scenario_type_counts[scenario.get('type', 'unknown')] += 1
        
        if classifications:
            stats['average_confidence'] = total_confidence / len(classifications)
        
        # Calculate coverage
        total_scenarios = sum(scenario_type_counts.values())
        if total_scenarios > 0:
            stats['coverage_analysis'] = {
                'positive_coverage': scenario_type_counts.get('positive', 0) / total_scenarios,
                'negative_coverage': scenario_type_counts.get('negative', 0) / total_scenarios,
                'edge_case_coverage': scenario_type_counts.get('edge_case', 0) / total_scenarios,
                'total_suggested_scenarios': total_scenarios
            }
        
        return dict(stats)