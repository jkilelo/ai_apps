"""
Gherkin Formatter

Formats test scenarios into proper Gherkin syntax with validation.
Ensures generated tests follow BDD best practices.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class GherkinFormatter:
    """
    Formats test scenarios into Gherkin syntax.
    
    Features:
    - Proper Gherkin syntax formatting
    - Feature file generation
    - Scenario and Scenario Outline support
    - Background steps
    - Data tables and examples
    - Syntax validation
    - Pretty printing
    """
    
    def __init__(self, config):
        self.config = config
        
        # Gherkin keywords
        self.keywords = {
            'feature': 'Feature',
            'background': 'Background',
            'scenario': 'Scenario',
            'scenario_outline': 'Scenario Outline',
            'given': 'Given',
            'when': 'When',
            'then': 'Then',
            'and': 'And',
            'but': 'But',
            'examples': 'Examples'
        }
        
        # Indentation settings
        self.indent_size = 2
        self.scenario_indent = ' ' * self.indent_size
        self.step_indent = ' ' * (self.indent_size * 2)
        self.table_indent = ' ' * (self.indent_size * 3)
        
        # Validation patterns
        self.tag_pattern = re.compile(r'^@[a-zA-Z0-9_-]+$')
        self.placeholder_pattern = re.compile(r'<[^>]+>')
        
        logger.info("GherkinFormatter initialized")
    
    async def format_features(
        self,
        scenarios: List[Dict[str, Any]],
        url: str,
        element_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Format scenarios into Gherkin features.
        
        Groups related scenarios into features and formats them.
        """
        try:
            # Group scenarios by feature
            feature_groups = self._group_scenarios_by_feature(scenarios, element_context)
            
            features = []
            
            for feature_name, feature_scenarios in feature_groups.items():
                feature = {
                    'name': feature_name,
                    'description': self._generate_feature_description(feature_name, url, element_context),
                    'url': url,
                    'tags': self._extract_feature_tags(feature_scenarios),
                    'background': self._extract_background_steps(feature_scenarios, element_context),
                    'scenarios': [],
                    'metadata': {
                        'generated_at': datetime.now().isoformat(),
                        'total_scenarios': len(feature_scenarios),
                        'page_type': element_context['page_info'].get('page_type', 'unknown')
                    }
                }
                
                # Format each scenario
                for scenario in feature_scenarios:
                    formatted_scenario = self._format_scenario(scenario)
                    if formatted_scenario:
                        feature['scenarios'].append(formatted_scenario)
                
                # Generate Gherkin text
                feature['gherkin_text'] = self._generate_feature_text(feature)
                
                features.append(feature)
            
            logger.info(f"Formatted {len(features)} features with "
                       f"{sum(len(f['scenarios']) for f in features)} scenarios")
            
            return features
            
        except Exception as e:
            logger.error(f"Feature formatting failed: {e}")
            raise
    
    def _group_scenarios_by_feature(
        self,
        scenarios: List[Dict[str, Any]],
        element_context: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group scenarios into logical features."""
        feature_groups = {}
        
        for scenario in scenarios:
            # Determine feature based on tags and scenario type
            feature_name = self._determine_feature_name(scenario, element_context)
            
            if feature_name not in feature_groups:
                feature_groups[feature_name] = []
            
            feature_groups[feature_name].append(scenario)
        
        return feature_groups
    
    def _determine_feature_name(
        self,
        scenario: Dict[str, Any],
        element_context: Dict[str, Any]
    ) -> str:
        """Determine which feature a scenario belongs to."""
        # Check tags for feature hints
        tags = scenario.get('tags', [])
        
        # Feature mapping based on tags
        tag_feature_map = {
            'authentication': 'User Authentication',
            'login': 'User Authentication',
            'registration': 'User Registration',
            'search': 'Search Functionality',
            'navigation': 'Site Navigation',
            'form': 'Form Interactions',
            'shopping_cart': 'Shopping Cart',
            'checkout': 'Checkout Process',
            'user_profile': 'User Profile Management',
            'admin': 'Admin Functions',
            'api': 'API Testing',
            'accessibility': 'Accessibility Tests',
            'performance': 'Performance Tests'
        }
        
        for tag in tags:
            if tag in tag_feature_map:
                return tag_feature_map[tag]
        
        # Use scenario priority to group
        priority = scenario.get('priority', 'medium')
        if priority in ['critical', 'high']:
            return 'Core Functionality'
        
        # Use page type from context
        page_type = element_context['page_info'].get('page_type', 'general')
        page_type_map = {
            'form_heavy': 'Form Interactions',
            'navigation_heavy': 'Site Navigation',
            'data_display': 'Data Viewing and Interaction',
            'interactive': 'Interactive Features',
            'content': 'Content Display'
        }
        
        return page_type_map.get(page_type, 'General Features')
    
    def _generate_feature_description(
        self,
        feature_name: str,
        url: str,
        element_context: Dict[str, Any]
    ) -> str:
        """Generate a description for the feature."""
        page_type = element_context['page_info'].get('page_type', 'web page')
        
        descriptions = {
            'User Authentication': f'Test user authentication flows for {page_type} at {url}',
            'User Registration': f'Test new user registration and account creation at {url}',
            'Search Functionality': f'Test search features and result handling at {url}',
            'Site Navigation': f'Test navigation and menu interactions across {url}',
            'Form Interactions': f'Test form filling, validation, and submission at {url}',
            'Shopping Cart': f'Test e-commerce cart functionality at {url}',
            'Checkout Process': f'Test purchase and checkout workflows at {url}',
            'Core Functionality': f'Test critical business functions for {page_type} at {url}',
            'General Features': f'Test general functionality of {page_type} at {url}'
        }
        
        return descriptions.get(feature_name, f'Test {feature_name} functionality at {url}')
    
    def _extract_feature_tags(self, scenarios: List[Dict[str, Any]]) -> List[str]:
        """Extract common tags for the feature."""
        all_tags = []
        
        for scenario in scenarios:
            all_tags.extend(scenario.get('tags', []))
        
        # Get unique tags that appear in multiple scenarios
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Feature tags are those that appear in >30% of scenarios
        threshold = len(scenarios) * 0.3
        feature_tags = [tag for tag, count in tag_counts.items() if count >= threshold]
        
        # Always include test type tags
        if not any(tag in feature_tags for tag in ['ui', 'functional', 'integration']):
            feature_tags.append('ui')
        
        return feature_tags
    
    def _extract_background_steps(
        self,
        scenarios: List[Dict[str, Any]],
        element_context: Dict[str, Any]
    ) -> Optional[List[Dict[str, str]]]:
        """Extract common steps that should be in Background."""
        if len(scenarios) < 2:
            return None
        
        # Find common given steps
        common_given_steps = []
        
        # Get first scenario's given steps as baseline
        first_scenario = scenarios[0]
        first_given = first_scenario.get('given_steps', [])
        
        # Check which steps are common across all scenarios
        for step in first_given:
            is_common = True
            
            for scenario in scenarios[1:]:
                scenario_given = scenario.get('given_steps', [])
                if not self._step_exists_in_list(step, scenario_given):
                    is_common = False
                    break
            
            if is_common:
                common_given_steps.append(step)
        
        # Only create background if we have common steps
        if common_given_steps:
            return common_given_steps
        
        # Check for common navigation step
        if all('navigate' in str(s.get('given_steps', [])) for s in scenarios):
            return [{
                'text': f'I am on the {element_context["page_info"]["page_type"]} page',
                'element': '',
                'data': {'url': element_context['page_info']['url']}
            }]
        
        return None
    
    def _step_exists_in_list(
        self,
        step: Dict[str, Any],
        step_list: List[Dict[str, Any]]
    ) -> bool:
        """Check if a step exists in a list of steps."""
        step_text = step.get('text', '')
        
        for list_step in step_list:
            if list_step.get('text', '') == step_text:
                return True
        
        return False
    
    def _format_scenario(self, scenario: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format a single scenario."""
        try:
            formatted = {
                'title': scenario.get('title', 'Untitled Scenario'),
                'type': scenario.get('type', 'scenario'),
                'tags': self._format_tags(scenario.get('tags', [])),
                'steps': [],
                'confidence': scenario.get('confidence', 0.8),
                'priority': scenario.get('priority', 'medium')
            }
            
            # Format steps in Given-When-Then order
            all_steps = []
            
            # Given steps
            for i, step in enumerate(scenario.get('given_steps', [])):
                keyword = 'Given' if i == 0 else 'And'
                all_steps.append(self._format_step(step, keyword))
            
            # When steps
            for i, step in enumerate(scenario.get('when_steps', [])):
                keyword = 'When' if i == 0 and not all_steps else 'And'
                all_steps.append(self._format_step(step, keyword))
            
            # Then steps
            for i, step in enumerate(scenario.get('then_steps', [])):
                keyword = 'Then' if i == 0 and len(all_steps) > 0 else 'And'
                all_steps.append(self._format_step(step, keyword))
            
            formatted['steps'] = all_steps
            
            # Add examples for scenario outlines
            if scenario.get('type') == 'scenario_outline' and scenario.get('examples'):
                formatted['examples'] = self._format_examples(scenario['examples'])
            
            # Generate Gherkin text
            formatted['gherkin_text'] = self._generate_scenario_text(formatted)
            
            return formatted
            
        except Exception as e:
            logger.error(f"Failed to format scenario: {e}")
            return None
    
    def _format_tags(self, tags: List[str]) -> List[str]:
        """Format and validate tags."""
        formatted_tags = []
        
        for tag in tags:
            # Ensure tag starts with @
            if not tag.startswith('@'):
                tag = f'@{tag}'
            
            # Validate tag format
            if self.tag_pattern.match(tag):
                formatted_tags.append(tag)
            else:
                # Fix common tag issues
                fixed_tag = '@' + re.sub(r'[^a-zA-Z0-9_-]', '_', tag[1:])
                formatted_tags.append(fixed_tag)
        
        return formatted_tags
    
    def _format_step(self, step: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """Format a single step."""
        formatted_step = {
            'keyword': keyword,
            'text': self._clean_step_text(step.get('text', '')),
            'data_table': None,
            'doc_string': None
        }
        
        # Add data table if present
        if 'data' in step and isinstance(step['data'], dict) and len(step['data']) > 1:
            formatted_step['data_table'] = self._format_data_table(step['data'])
        
        # Add doc string for complex data
        if 'doc_string' in step:
            formatted_step['doc_string'] = step['doc_string']
        
        return formatted_step
    
    def _clean_step_text(self, text: str) -> str:
        """Clean and format step text."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Ensure proper sentence structure
        if text and not text[0].isupper():
            text = text[0].upper() + text[1:]
        
        # Ensure no trailing punctuation (Gherkin convention)
        text = text.rstrip('.,;:')
        
        # Replace common patterns for better readability
        replacements = {
            'click on the': 'click the',
            'fill in the': 'enter',
            'is visible': 'is displayed',
            'should be visible': 'should be displayed'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _format_data_table(self, data: Dict[str, Any]) -> List[List[str]]:
        """Format data as a Gherkin data table."""
        if not data:
            return []
        
        # Convert to table format
        headers = list(data.keys())
        values = [str(data[key]) for key in headers]
        
        return [headers, values]
    
    def _format_examples(self, examples: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Format examples for scenario outline."""
        if not examples:
            return {}
        
        formatted = {
            'headers': list(examples.keys()),
            'rows': []
        }
        
        # Get number of rows
        num_rows = len(list(examples.values())[0]) if examples else 0
        
        # Build rows
        for i in range(num_rows):
            row = []
            for header in formatted['headers']:
                value = examples[header][i] if i < len(examples[header]) else ''
                row.append(str(value))
            formatted['rows'].append(row)
        
        return formatted
    
    def _generate_feature_text(self, feature: Dict[str, Any]) -> str:
        """Generate complete Gherkin text for a feature."""
        lines = []
        
        # Feature tags
        if feature.get('tags'):
            lines.append(' '.join(feature['tags']))
        
        # Feature declaration
        lines.append(f"{self.keywords['feature']}: {feature['name']}")
        
        # Feature description
        if feature.get('description'):
            lines.append(f"  {feature['description']}")
        
        lines.append("")  # Blank line
        
        # Background
        if feature.get('background'):
            lines.append(f"  {self.keywords['background']}:")
            for step in feature['background']:
                lines.append(f"    {self.keywords['given']} {step['text']}")
            lines.append("")
        
        # Scenarios
        for scenario in feature.get('scenarios', []):
            if 'gherkin_text' in scenario:
                # Indent scenario text
                scenario_lines = scenario['gherkin_text'].split('\n')
                for line in scenario_lines:
                    if line:
                        lines.append(f"  {line}")
                lines.append("")  # Blank line between scenarios
        
        return '\n'.join(lines)
    
    def _generate_scenario_text(self, scenario: Dict[str, Any]) -> str:
        """Generate Gherkin text for a scenario."""
        lines = []
        
        # Tags
        if scenario.get('tags'):
            lines.append(' '.join(scenario['tags']))
        
        # Scenario declaration
        scenario_keyword = self.keywords.get(scenario['type'], 'Scenario')
        lines.append(f"{scenario_keyword}: {scenario['title']}")
        
        # Steps
        for step in scenario.get('steps', []):
            step_line = f"  {step['keyword']} {step['text']}"
            lines.append(step_line)
            
            # Data table
            if step.get('data_table'):
                for row in step['data_table']:
                    lines.append(f"    | {' | '.join(row)} |")
            
            # Doc string
            if step.get('doc_string'):
                lines.append('    """')
                lines.append(f"    {step['doc_string']}")
                lines.append('    """')
        
        # Examples (for scenario outline)
        if scenario.get('examples'):
            lines.append("")
            lines.append(f"  {self.keywords['examples']}:")
            
            examples = scenario['examples']
            
            # Headers
            headers = examples.get('headers', [])
            if headers:
                lines.append(f"    | {' | '.join(headers)} |")
                
                # Rows
                for row in examples.get('rows', []):
                    lines.append(f"    | {' | '.join(row)} |")
        
        return '\n'.join(lines)
    
    def validate_feature(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a feature's Gherkin syntax."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check feature name
        if not feature.get('name'):
            validation_result['valid'] = False
            validation_result['errors'].append('Feature must have a name')
        
        # Check scenarios
        if not feature.get('scenarios'):
            validation_result['valid'] = False
            validation_result['errors'].append('Feature must have at least one scenario')
        
        # Validate each scenario
        for i, scenario in enumerate(feature.get('scenarios', [])):
            scenario_validation = self._validate_scenario(scenario, i)
            
            if not scenario_validation['valid']:
                validation_result['valid'] = False
                validation_result['errors'].extend(scenario_validation['errors'])
            
            validation_result['warnings'].extend(scenario_validation['warnings'])
        
        # Check for duplicate scenario titles
        titles = [s.get('title', '') for s in feature.get('scenarios', [])]
        if len(titles) != len(set(titles)):
            validation_result['warnings'].append('Feature contains duplicate scenario titles')
        
        return validation_result
    
    def _validate_scenario(self, scenario: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate a single scenario."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check title
        if not scenario.get('title'):
            validation_result['valid'] = False
            validation_result['errors'].append(f'Scenario {index} must have a title')
        
        # Check steps
        steps = scenario.get('steps', [])
        if not steps:
            validation_result['valid'] = False
            validation_result['errors'].append(f'Scenario "{scenario.get("title", index)}" must have steps')
        
        # Validate step order (should have Given/When/Then structure)
        has_given = any(s['keyword'] in ['Given', 'And'] for s in steps[:1])
        has_action = any(s['keyword'] in ['When', 'And'] for s in steps)
        has_assertion = any(s['keyword'] in ['Then', 'And'] for s in steps)
        
        if not (has_given or has_action or has_assertion):
            validation_result['warnings'].append(
                f'Scenario "{scenario.get("title", index)}" should follow Given-When-Then structure'
            )
        
        # Check scenario outline
        if scenario.get('type') == 'scenario_outline':
            # Check for placeholders in steps
            has_placeholders = False
            for step in steps:
                if self.placeholder_pattern.search(step.get('text', '')):
                    has_placeholders = True
                    break
            
            if not has_placeholders:
                validation_result['warnings'].append(
                    f'Scenario Outline "{scenario.get("title", index)}" has no placeholders'
                )
            
            # Check examples
            if not scenario.get('examples'):
                validation_result['valid'] = False
                validation_result['errors'].append(
                    f'Scenario Outline "{scenario.get("title", index)}" must have examples'
                )
        
        return validation_result
    
    def pretty_print_feature(self, feature: Dict[str, Any]) -> str:
        """Generate a pretty-printed version of the feature."""
        if 'gherkin_text' in feature:
            return feature['gherkin_text']
        
        return self._generate_feature_text(feature)
    
    def export_feature_file(self, feature: Dict[str, Any], filename: str) -> str:
        """Export feature to a .feature file format."""
        content = self.pretty_print_feature(feature)
        
        # Add metadata as comments
        metadata_lines = [
            f"# Generated: {datetime.now().isoformat()}",
            f"# URL: {feature.get('url', 'Unknown')}",
            f"# Total Scenarios: {len(feature.get('scenarios', []))}",
            "#"
        ]
        
        return '\n'.join(metadata_lines) + '\n' + content