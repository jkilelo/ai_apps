"""
Enhanced Test Generator with Multiple Test Strategies

Implements comprehensive test generation using multiple strategies:
1. Happy path testing
2. Negative testing 
3. Edge case testing
4. Security testing
5. Performance testing
6. Accessibility testing
7. Cross-browser testing
8. Data variation testing
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class EnhancedTestGenerator:
    """
    Generate comprehensive test scenarios using multiple strategies.
    """
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.test_strategies = {
            'happy_path': self._generate_happy_path_tests,
            'negative': self._generate_negative_tests,
            'edge_case': self._generate_edge_case_tests,
            'security': self._generate_security_tests,
            'performance': self._generate_performance_tests,
            'accessibility': self._generate_accessibility_tests,
            'cross_browser': self._generate_cross_browser_tests,
            'data_variation': self._generate_data_variation_tests
        }
        
    async def generate_comprehensive_tests(
        self,
        element_context: Dict[str, Any],
        generation_options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate comprehensive test scenarios using all strategies."""
        all_scenarios = []
        
        # Determine which strategies to use
        strategies_to_use = generation_options.get('strategies', list(self.test_strategies.keys()))
        
        # Generate tests for each strategy
        for strategy in strategies_to_use:
            if strategy in self.test_strategies:
                logger.info(f"Generating {strategy} tests...")
                scenarios = await self.test_strategies[strategy](element_context, generation_options)
                all_scenarios.extend(scenarios)
        
        # Remove duplicates and organize
        unique_scenarios = self._deduplicate_scenarios(all_scenarios)
        
        # Prioritize scenarios
        prioritized_scenarios = self._prioritize_scenarios(unique_scenarios)
        
        # Apply limits if specified
        max_scenarios = generation_options.get('max_total_scenarios', 50)
        if len(prioritized_scenarios) > max_scenarios:
            prioritized_scenarios = prioritized_scenarios[:max_scenarios]
        
        logger.info(f"Generated {len(prioritized_scenarios)} unique test scenarios")
        return prioritized_scenarios
    
    async def _generate_happy_path_tests(
        self,
        element_context: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate happy path test scenarios."""
        prompt = f"""
        Generate happy path test scenarios for a web application based on these elements:
        
        Page Type: {element_context['page_info']['page_type']}
        Interactive Elements: {element_context['page_info']['interactive_elements']}
        Forms: {len(element_context.get('form_structures', []))}
        
        Key interaction flows:
        {json.dumps(element_context.get('interaction_flows', []), indent=2)}
        
        Generate 5-10 happy path scenarios that:
        1. Test the primary user journeys
        2. Cover main functionality
        3. Use valid data
        4. Follow expected user behavior
        5. Verify successful outcomes
        
        Format as JSON array with each scenario containing:
        - title: descriptive title
        - type: "scenario"
        - tags: ["happy_path", "functional", etc.]
        - priority: "critical", "high", "medium", or "low"
        - steps: array of test steps with action, description, element_selector, test_data
        
        Focus on real-world usage patterns.
        """
        
        response = await self.llm_provider.generate(prompt, temperature=0.7)
        return self._parse_scenario_response(response)
    
    async def _generate_negative_tests(
        self,
        element_context: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate negative test scenarios."""
        prompt = f"""
        Generate negative test scenarios for error handling and validation:
        
        Form Fields: {json.dumps(element_context.get('form_structures', [{}])[0].get('fields', []), indent=2)}
        
        Generate 5-8 negative test scenarios that:
        1. Test with invalid data (empty fields, wrong formats, SQL injection, XSS)
        2. Test boundary conditions
        3. Test unauthorized access
        4. Test missing required fields
        5. Test invalid state transitions
        6. Verify proper error messages
        
        Include scenarios for:
        - Empty required fields
        - Invalid email/phone formats
        - Passwords that don't meet requirements
        - Special characters in text fields
        - Numbers outside valid ranges
        - Future/past dates where inappropriate
        
        Format as JSON array with proper test steps.
        """
        
        response = await self.llm_provider.generate(prompt, temperature=0.7)
        return self._parse_scenario_response(response)
    
    async def _generate_edge_case_tests(
        self,
        element_context: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate edge case test scenarios."""
        prompt = f"""
        Generate edge case test scenarios for unusual but valid conditions:
        
        Page Elements: {element_context['page_info']['total_elements']}
        Element Types: {json.dumps(element_context['page_info'].get('element_type_distribution', {}), indent=2)}
        
        Generate 5-8 edge case scenarios that test:
        1. Maximum length inputs
        2. Unicode and special characters
        3. Concurrent operations
        4. Rapid clicking/submissions
        5. Browser back/forward navigation
        6. Session timeouts
        7. Network interruptions
        8. Large file uploads
        9. Multiple browser tabs
        10. Different screen resolutions
        
        Focus on technically valid but unusual scenarios.
        Format as JSON array with detailed test steps.
        """
        
        response = await self.llm_provider.generate(prompt, temperature=0.8)
        return self._parse_scenario_response(response)
    
    async def _generate_security_tests(
        self,
        element_context: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate security test scenarios."""
        prompt = f"""
        Generate security test scenarios for common vulnerabilities:
        
        Forms: {len(element_context.get('form_structures', []))}
        Input Fields: {sum(1 for g in element_context.get('element_groups', {}).values() for e in g if 'input' in str(e))}
        
        Generate 4-6 security test scenarios that check for:
        1. SQL injection attempts
        2. Cross-site scripting (XSS)
        3. Cross-site request forgery (CSRF)
        4. Authentication bypass attempts
        5. Session hijacking
        6. Insecure direct object references
        7. File upload vulnerabilities
        
        Include common attack patterns but ensure tests are ethical.
        Format as JSON array with test steps.
        """
        
        response = await self.llm_provider.generate(prompt, temperature=0.6)
        return self._parse_scenario_response(response)
    
    async def _generate_performance_tests(
        self,
        element_context: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate performance test scenarios."""
        prompt = f"""
        Generate performance test scenarios:
        
        Total Elements: {element_context['page_info']['total_elements']}
        Interactive Elements: {element_context['page_info']['interactive_elements']}
        
        Generate 3-5 performance scenarios that test:
        1. Page load time under normal conditions
        2. Response time for user interactions
        3. Behavior with slow network (3G simulation)
        4. Multiple rapid form submissions
        5. Large data set handling
        6. Memory usage over time
        7. Concurrent user simulations
        
        Format as JSON array with measurable performance criteria.
        """
        
        response = await self.llm_provider.generate(prompt, temperature=0.5)
        return self._parse_scenario_response(response)
    
    async def _generate_accessibility_tests(
        self,
        element_context: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate accessibility test scenarios."""
        prompt = f"""
        Generate accessibility test scenarios for WCAG compliance:
        
        Forms: {len(element_context.get('form_structures', []))}
        Navigation Elements: {len(element_context.get('element_groups', {}).get('navigation', []))}
        
        Generate 4-6 accessibility scenarios that test:
        1. Keyboard navigation (Tab order, Enter/Space activation)
        2. Screen reader compatibility
        3. Color contrast requirements
        4. Focus indicators
        5. Alt text for images
        6. Form labels and error messages
        7. ARIA labels and roles
        8. Skip navigation links
        
        Format as JSON array following WCAG 2.1 AA standards.
        """
        
        response = await self.llm_provider.generate(prompt, temperature=0.6)
        return self._parse_scenario_response(response)
    
    async def _generate_cross_browser_tests(
        self,
        element_context: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate cross-browser test scenarios."""
        prompt = f"""
        Generate cross-browser compatibility test scenarios:
        
        Key Features: {json.dumps([f['name'] for f in element_context.get('interaction_flows', [])[:3]], indent=2)}
        
        Generate 3-4 scenarios that test compatibility across:
        1. Chrome (latest)
        2. Firefox (latest)
        3. Safari (latest)
        4. Edge (latest)
        5. Mobile browsers (iOS Safari, Chrome Android)
        
        Focus on:
        - CSS rendering differences
        - JavaScript compatibility
        - Form behavior
        - Media playback
        - Touch vs mouse interactions
        
        Format as JSON array with browser-specific steps.
        """
        
        response = await self.llm_provider.generate(prompt, temperature=0.5)
        return self._parse_scenario_response(response)
    
    async def _generate_data_variation_tests(
        self,
        element_context: Dict[str, Any],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate data variation test scenarios."""
        prompt = f"""
        Generate data-driven test scenarios with multiple data sets:
        
        Forms: {json.dumps(element_context.get('form_structures', [])[:1], indent=2)}
        
        Generate 3-5 scenario outlines that test with various data:
        1. Different valid input combinations
        2. Internationalization (different languages/locales)
        3. Various user roles/permissions
        4. Different data volumes
        5. Date/time in different timezones
        
        Use scenario outlines with example tables for:
        - User registration (different countries, ages, names)
        - Search functionality (different queries, filters)
        - Product filtering (price ranges, categories)
        - Date selection (past, present, future)
        
        Format as JSON array with 'scenario_outline' type and examples table.
        """
        
        response = await self.llm_provider.generate(prompt, temperature=0.7)
        return self._parse_scenario_response(response)
    
    def _parse_scenario_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response to extract scenarios."""
        try:
            # Try direct parsing
            scenarios = json.loads(response.strip())
            if isinstance(scenarios, list):
                return scenarios
        except:
            pass
        
        # Try to extract JSON from response
        import re
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            try:
                scenarios = json.loads(json_match.group())
                return scenarios
            except:
                pass
        
        # Return empty list if parsing fails
        logger.warning("Failed to parse scenario response")
        return []
    
    def _deduplicate_scenarios(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate scenarios based on title similarity."""
        unique = []
        seen_titles = set()
        
        for scenario in scenarios:
            title = scenario.get('title', '').lower()
            # Simple deduplication - could be enhanced with fuzzy matching
            if title not in seen_titles:
                seen_titles.add(title)
                unique.append(scenario)
        
        return unique
    
    def _prioritize_scenarios(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize scenarios based on importance."""
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        
        return sorted(scenarios, key=lambda s: (
            priority_order.get(s.get('priority', 'medium'), 2),
            'happy_path' not in s.get('tags', []),  # Happy path first
            'security' not in s.get('tags', []),    # Then security
            random.random()  # Random for same priority
        ))


class TestCoverageAnalyzer:
    """Analyze test coverage and suggest missing scenarios."""
    
    def __init__(self):
        self.coverage_requirements = {
            'authentication': ['login', 'logout', 'password_reset', 'remember_me', 'two_factor'],
            'forms': ['valid_submission', 'validation_errors', 'empty_fields', 'special_characters'],
            'navigation': ['menu_navigation', 'breadcrumbs', 'back_button', 'deep_linking'],
            'search': ['basic_search', 'advanced_filters', 'no_results', 'special_queries'],
            'crud': ['create', 'read', 'update', 'delete', 'bulk_operations'],
            'errors': ['404_page', '500_error', 'network_timeout', 'permission_denied'],
            'responsive': ['mobile_view', 'tablet_view', 'desktop_view', 'orientation_change']
        }
    
    def analyze_coverage(
        self,
        generated_scenarios: List[Dict[str, Any]],
        element_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze test coverage and identify gaps."""
        coverage_report = {
            'total_scenarios': len(generated_scenarios),
            'coverage_by_type': {},
            'missing_scenarios': [],
            'coverage_percentage': 0,
            'recommendations': []
        }
        
        # Analyze what's covered
        covered_areas = set()
        for scenario in generated_scenarios:
            tags = scenario.get('tags', [])
            title = scenario.get('title', '').lower()
            
            # Check coverage areas
            for area, keywords in self.coverage_requirements.items():
                if any(keyword in title or keyword in tags for keyword in keywords):
                    covered_areas.add(area)
                    coverage_report['coverage_by_type'][area] = \
                        coverage_report['coverage_by_type'].get(area, 0) + 1
        
        # Identify gaps
        page_type = element_context['page_info'].get('page_type', 'unknown')
        expected_areas = self._get_expected_areas(page_type, element_context)
        
        for area in expected_areas:
            if area not in covered_areas:
                coverage_report['missing_scenarios'].append({
                    'area': area,
                    'description': f"No test scenarios found for {area}",
                    'suggested_scenarios': self.coverage_requirements.get(area, [])
                })
        
        # Calculate coverage percentage
        if expected_areas:
            coverage_report['coverage_percentage'] = \
                (len(covered_areas) / len(expected_areas)) * 100
        
        # Generate recommendations
        coverage_report['recommendations'] = self._generate_recommendations(
            coverage_report, element_context
        )
        
        return coverage_report
    
    def _get_expected_areas(
        self,
        page_type: str,
        element_context: Dict[str, Any]
    ) -> Set[str]:
        """Determine expected test areas based on page type."""
        expected = set()
        
        # Always expect basic areas
        expected.add('navigation')
        expected.add('errors')
        expected.add('responsive')
        
        # Add based on page elements
        if element_context.get('form_structures'):
            expected.add('forms')
        
        if any('login' in str(f).lower() or 'auth' in str(f).lower() 
               for f in element_context.get('interaction_flows', [])):
            expected.add('authentication')
        
        if any('search' in str(e).lower() 
               for g in element_context.get('element_groups', {}).values() 
               for e in g):
            expected.add('search')
        
        return expected
    
    def _generate_recommendations(
        self,
        coverage_report: Dict[str, Any],
        element_context: Dict[str, Any]
    ) -> List[str]:
        """Generate specific recommendations for improving coverage."""
        recommendations = []
        
        if coverage_report['coverage_percentage'] < 70:
            recommendations.append(
                f"Coverage is only {coverage_report['coverage_percentage']:.1f}%. "
                "Consider adding more test scenarios."
            )
        
        if 'security' not in coverage_report['coverage_by_type']:
            recommendations.append(
                "No security tests found. Add SQL injection, XSS, and CSRF tests."
            )
        
        if 'accessibility' not in coverage_report['coverage_by_type']:
            recommendations.append(
                "No accessibility tests found. Add keyboard navigation and screen reader tests."
            )
        
        if coverage_report['total_scenarios'] < 10:
            recommendations.append(
                "Only {} scenarios generated. Consider expanding test coverage.".format(
                    coverage_report['total_scenarios']
                )
            )
        
        return recommendations