"""
Element Context Mapper

Maps extracted elements to rich context for LLM consumption.
Provides structured information about elements, their relationships,
and page context for intelligent test generation.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

from src.ui_testing_v2.models.database import ExtractedElement, ElementType, ElementInteractionType

logger = logging.getLogger(__name__)


class ElementContextMapper:
    """
    Creates rich contextual information from extracted elements.
    
    This mapper transforms raw element data into structured context
    that helps LLM understand:
    - Element relationships and hierarchies
    - Functional groupings (forms, navigation, etc.)
    - Interaction patterns and workflows
    - Business logic indicators
    - Page structure and layout
    """
    
    def __init__(self, config):
        self.config = config
        self.context_enrichment_enabled = True
        
        # Element grouping patterns
        self.form_indicators = {'form', 'input', 'textarea', 'select', 'button[type=submit]'}
        self.navigation_indicators = {'nav', 'menu', 'breadcrumb', 'pagination'}
        self.content_indicators = {'article', 'section', 'main', 'content'}
        self.interactive_indicators = {'button', 'link', 'input', 'select', 'textarea'}
        
        logger.info("ElementContextMapper initialized")
    
    async def create_element_context(
        self,
        elements: List[ExtractedElement],
        url: str,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive context from extracted elements.
        
        Returns:
            Dictionary containing:
            - page_info: General page information
            - element_groups: Functionally grouped elements
            - interaction_flows: Possible user workflows
            - form_structures: Detailed form analysis
            - navigation_structure: Site navigation mapping
            - element_relationships: Parent-child and sibling relationships
            - business_indicators: Detected business logic patterns
        """
        try:
            logger.info(f"Creating element context for {url} with {len(elements)} elements")
            
            context = {
                'page_info': self._extract_page_info(url, elements, analysis_results),
                'element_groups': await self._group_elements_functionally(elements),
                'interaction_flows': self._identify_interaction_flows(elements),
                'form_structures': self._analyze_form_structures(elements),
                'navigation_structure': self._extract_navigation_structure(elements),
                'element_relationships': self._build_element_relationships(elements),
                'business_indicators': self._detect_business_patterns(elements, analysis_results),
                'element_summary': self._create_element_summary(elements),
                'test_relevant_elements': self._identify_test_relevant_elements(elements)
            }
            
            # Enrich with analysis results if available
            if analysis_results:
                context['ai_insights'] = analysis_results.get('ai_analysis', {})
                context['page_classification'] = analysis_results.get('page_structure', {}).get('page_classification', {})
            
            logger.info(f"Created context with {len(context['element_groups'])} element groups")
            return context
            
        except Exception as e:
            logger.error(f"Failed to create element context: {e}")
            raise
    
    def _extract_page_info(
        self,
        url: str,
        elements: List[ExtractedElement],
        analysis_results: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract general page information."""
        # Count element types
        element_type_counts = defaultdict(int)
        for elem in elements:
            if elem.element_type:
                element_type_counts[str(elem.element_type)] += 1
        
        # Identify page characteristics
        has_forms = any(elem.element_type == ElementType.FORM for elem in elements)
        has_tables = any(elem.element_type == ElementType.TABLE for elem in elements)
        interactive_count = sum(1 for elem in elements if elem.is_interactable)
        
        page_info = {
            'url': url,
            'total_elements': len(elements),
            'interactive_elements': interactive_count,
            'element_type_distribution': dict(element_type_counts),
            'has_forms': has_forms,
            'has_tables': has_tables,
            'page_type': self._infer_page_type(element_type_counts, analysis_results),
            'complexity_score': self._calculate_page_complexity(elements),
            'accessibility_score': self._calculate_accessibility_score(elements)
        }
        
        return page_info
    
    async def _group_elements_functionally(
        self,
        elements: List[ExtractedElement]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group elements by their functional purpose."""
        groups = {
            'forms': [],
            'navigation': [],
            'actions': [],
            'content': [],
            'tables': [],
            'media': [],
            'inputs': [],
            'links': [],
            'modals': [],
            'other': []
        }
        
        # Group elements
        for i, elem in enumerate(elements):
            element_info = self._create_element_info(elem, i)
            
            # Determine primary group
            if elem.element_type == ElementType.FORM or self._is_form_element(elem):
                groups['forms'].append(element_info)
            elif elem.element_type == ElementType.NAVIGATION or self._is_navigation_element(elem):
                groups['navigation'].append(element_info)
            elif elem.element_type == ElementType.BUTTON:
                groups['actions'].append(element_info)
            elif elem.element_type == ElementType.TABLE:
                groups['tables'].append(element_info)
            elif elem.element_type in [ElementType.IMAGE, ElementType.VIDEO]:
                groups['media'].append(element_info)
            elif elem.element_type in [ElementType.INPUT, ElementType.SELECT]:
                groups['inputs'].append(element_info)
            elif elem.element_type == ElementType.LINK:
                groups['links'].append(element_info)
            # Note: MODAL type doesn't exist, skip for now
            elif elem.element_type in [ElementType.HEADER, ElementType.FOOTER]:
                groups['content'].append(element_info)
            else:
                groups['other'].append(element_info)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def _identify_interaction_flows(
        self,
        elements: List[ExtractedElement]
    ) -> List[Dict[str, Any]]:
        """Identify possible user interaction flows."""
        flows = []
        
        # Flow 1: Form submission flows
        forms = [e for e in elements if e.element_type == ElementType.FORM]
        for form in forms:
            # Find related inputs and submit buttons
            form_inputs = self._find_form_inputs(elements, form)
            submit_buttons = self._find_submit_buttons(elements, form)
            
            if form_inputs and submit_buttons:
                flow = {
                    'type': 'form_submission',
                    'name': 'Form Submission Flow',
                    'steps': [
                        {'action': 'fill_form', 'elements': len(form_inputs)},
                        {'action': 'submit', 'elements': len(submit_buttons)}
                    ],
                    'complexity': 'medium' if len(form_inputs) > 3 else 'simple',
                    'priority': 'high'
                }
                flows.append(flow)
        
        # Flow 2: Navigation flows
        nav_elements = [e for e in elements if self._is_navigation_element(e)]
        if nav_elements:
            flow = {
                'type': 'navigation',
                'name': 'Site Navigation Flow',
                'steps': [
                    {'action': 'navigate', 'elements': len(nav_elements)}
                ],
                'complexity': 'simple',
                'priority': 'medium'
            }
            flows.append(flow)
        
        # Flow 3: Search flows
        search_inputs = [e for e in elements if self._is_search_element(e)]
        if search_inputs:
            flow = {
                'type': 'search',
                'name': 'Search Flow',
                'steps': [
                    {'action': 'enter_search', 'elements': len(search_inputs)},
                    {'action': 'submit_search', 'elements': 1}
                ],
                'complexity': 'simple',
                'priority': 'high'
            }
            flows.append(flow)
        
        # Flow 4: Authentication flows
        auth_elements = self._find_auth_elements(elements)
        if auth_elements:
            flow = {
                'type': 'authentication',
                'name': 'Login/Authentication Flow',
                'steps': [
                    {'action': 'enter_credentials', 'elements': len(auth_elements['inputs'])},
                    {'action': 'submit_login', 'elements': len(auth_elements['buttons'])}
                ],
                'complexity': 'medium',
                'priority': 'critical'
            }
            flows.append(flow)
        
        return flows
    
    def _analyze_form_structures(
        self,
        elements: List[ExtractedElement]
    ) -> List[Dict[str, Any]]:
        """Analyze form structures in detail."""
        form_structures = []
        
        # Find all forms
        forms = [e for e in elements if e.element_type == ElementType.FORM]
        
        # Also detect implicit forms (groups of inputs without form tag)
        implicit_forms = self._detect_implicit_forms(elements)
        
        for form in forms + implicit_forms:
            structure = {
                'form_id': form.css_selector if hasattr(form, 'css_selector') else 'implicit_form',
                'fields': [],
                'required_fields': [],
                'optional_fields': [],
                'field_types': defaultdict(int),
                'has_validation': False,
                'submit_buttons': [],
                'estimated_complexity': 'simple'
            }
            
            # Find all inputs within form
            form_inputs = self._find_form_inputs(elements, form)
            
            for input_elem in form_inputs:
                field_info = {
                    'name': input_elem.attributes.get('name', '') if input_elem.attributes else '',
                    'type': input_elem.attributes.get('type', 'text') if input_elem.attributes else 'text',
                    'required': 'required' in (input_elem.attributes or {}),
                    'label': self._find_label_for_input(elements, input_elem),
                    'selector': input_elem.css_selector
                }
                
                structure['fields'].append(field_info)
                
                if field_info['required']:
                    structure['required_fields'].append(field_info)
                else:
                    structure['optional_fields'].append(field_info)
                
                structure['field_types'][field_info['type']] += 1
            
            # Find submit buttons
            structure['submit_buttons'] = [
                {'text': btn.text, 'selector': btn.css_selector}
                for btn in self._find_submit_buttons(elements, form)
            ]
            
            # Determine complexity
            total_fields = len(structure['fields'])
            if total_fields > 10:
                structure['estimated_complexity'] = 'complex'
            elif total_fields > 5:
                structure['estimated_complexity'] = 'medium'
            
            # Check for validation indicators
            structure['has_validation'] = any(
                'pattern' in (input_elem.attributes or {}) or
                'min' in (input_elem.attributes or {}) or
                'max' in (input_elem.attributes or {})
                for input_elem in form_inputs
            )
            
            form_structures.append(structure)
        
        return form_structures
    
    def _extract_navigation_structure(
        self,
        elements: List[ExtractedElement]
    ) -> Dict[str, Any]:
        """Extract navigation structure from elements."""
        navigation = {
            'main_navigation': [],
            'breadcrumbs': [],
            'pagination': [],
            'footer_links': [],
            'sidebar_navigation': []
        }
        
        for elem in elements:
            # Main navigation
            if elem.element_type == ElementType.NAVIGATION:
                nav_links = self._extract_navigation_links(elements, elem)
                navigation['main_navigation'].extend(nav_links)
            
            # Breadcrumbs
            elif self._is_breadcrumb(elem):
                breadcrumb_links = self._extract_navigation_links(elements, elem)
                navigation['breadcrumbs'].extend(breadcrumb_links)
            
            # Pagination
            elif self._is_pagination(elem):
                pagination_links = self._extract_navigation_links(elements, elem)
                navigation['pagination'].extend(pagination_links)
            
            # Footer navigation
            elif elem.element_type == ElementType.FOOTER:
                footer_links = self._extract_navigation_links(elements, elem)
                navigation['footer_links'].extend(footer_links)
        
        return navigation
    
    def _build_element_relationships(
        self,
        elements: List[ExtractedElement]
    ) -> Dict[str, Any]:
        """Build relationships between elements."""
        relationships = {
            'parent_child': defaultdict(list),
            'siblings': defaultdict(list),
            'form_associations': defaultdict(list),
            'label_input_pairs': []
        }
        
        # Build spatial relationships based on bounding boxes
        for i, elem1 in enumerate(elements):
            if not elem1.bounding_box:
                continue
            
            for j, elem2 in enumerate(elements):
                if i == j or not elem2.bounding_box:
                    continue
                
                # Check if elem2 is inside elem1 (parent-child)
                if self._is_element_inside(elem2.bounding_box, elem1.bounding_box):
                    relationships['parent_child'][i].append(j)
                
                # Check if elements are siblings (similar Y position)
                elif self._are_elements_siblings(elem1.bounding_box, elem2.bounding_box):
                    relationships['siblings'][i].append(j)
        
        # Find label-input associations
        labels = [e for e in elements if e.tag_name == 'label']
        inputs = [e for e in elements if e.element_type in [ElementType.INPUT, ElementType.SELECT]]
        
        for label in labels:
            associated_input = self._find_associated_input(label, inputs)
            if associated_input:
                relationships['label_input_pairs'].append({
                    'label': label.css_selector,
                    'input': associated_input.css_selector,
                    'label_text': label.text
                })
        
        return dict(relationships)
    
    def _detect_business_patterns(
        self,
        elements: List[ExtractedElement],
        analysis_results: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect business logic patterns from elements."""
        patterns = {
            'e_commerce': self._detect_ecommerce_patterns(elements),
            'authentication': self._detect_auth_patterns(elements),
            'search': self._detect_search_patterns(elements),
            'social': self._detect_social_patterns(elements),
            'content_management': self._detect_cms_patterns(elements),
            'data_entry': self._detect_data_entry_patterns(elements)
        }
        
        # Add AI insights if available
        if analysis_results and 'business_rules' in analysis_results:
            patterns['ai_detected_rules'] = analysis_results['business_rules']
        
        # Calculate confidence scores
        for pattern_type, pattern_data in patterns.items():
            if isinstance(pattern_data, dict) and 'indicators' in pattern_data:
                pattern_data['confidence'] = len(pattern_data['indicators']) / 10.0
        
        return patterns
    
    def _create_element_summary(
        self,
        elements: List[ExtractedElement]
    ) -> Dict[str, Any]:
        """Create a summary of elements for LLM consumption."""
        summary = {
            'total_count': len(elements),
            'interactive_count': sum(1 for e in elements if e.is_interactable),
            'visible_count': sum(1 for e in elements if e.is_visible),
            'top_elements': [],
            'unique_actions': set(),
            'common_patterns': []
        }
        
        # Get top interactive elements
        interactive_elements = [e for e in elements if e.is_interactable]
        for elem in interactive_elements[:20]:  # Top 20
            elem_summary = {
                'type': str(elem.element_type) if elem.element_type else 'unknown',
                'text': (elem.text or '')[:50],
                'selector': elem.css_selector,
                'interaction_type': str(elem.interaction_type) if elem.interaction_type else 'none',
                'confidence': elem.confidence_score
            }
            summary['top_elements'].append(elem_summary)
            
            if elem.interaction_type:
                summary['unique_actions'].add(str(elem.interaction_type))
        
        summary['unique_actions'] = list(summary['unique_actions'])
        
        # Detect common patterns
        summary['common_patterns'] = self._detect_common_patterns(elements)
        
        return summary
    
    def _identify_test_relevant_elements(
        self,
        elements: List[ExtractedElement]
    ) -> List[Dict[str, Any]]:
        """Identify elements most relevant for testing."""
        test_relevant = []
        
        for i, elem in enumerate(elements):
            relevance_score = 0
            reasons = []
            
            # High relevance: Interactive elements
            if elem.is_interactable:
                relevance_score += 0.3
                reasons.append('interactive')
            
            # High relevance: Form elements
            if elem.element_type in [ElementType.INPUT, ElementType.BUTTON, ElementType.SELECT]:
                relevance_score += 0.2
                reasons.append('form_element')
            
            # High relevance: Navigation elements
            if elem.element_type == ElementType.LINK:
                relevance_score += 0.1
                reasons.append('navigation')
            
            # High relevance: Has validation
            if elem.attributes and any(attr in elem.attributes for attr in ['required', 'pattern', 'min', 'max']):
                relevance_score += 0.2
                reasons.append('has_validation')
            
            # High relevance: Submit buttons
            if elem.element_type == ElementType.BUTTON and elem.attributes and elem.attributes.get('type') == 'submit':
                relevance_score += 0.2
                reasons.append('submit_action')
            
            if relevance_score > 0.3:  # Threshold for relevance
                test_relevant.append({
                    'element_index': i,
                    'type': str(elem.element_type) if elem.element_type else 'unknown',
                    'selector': elem.css_selector,
                    'relevance_score': relevance_score,
                    'reasons': reasons,
                    'text': (elem.text or '')[:100]
                })
        
        # Sort by relevance score
        test_relevant.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return test_relevant[:50]  # Top 50 most relevant
    
    # Helper methods
    def _create_element_info(self, elem: ExtractedElement, index: int) -> Dict[str, Any]:
        """Create standardized element information."""
        return {
            'index': index,
            'type': str(elem.element_type) if elem.element_type else elem.tag_name,
            'tag': elem.tag_name,
            'text': (elem.text or '')[:100],
            'selector': elem.css_selector,
            'attributes': elem.attributes or {},
            'is_interactive': elem.is_interactable,
            'is_visible': elem.is_visible,
            'interaction_type': str(elem.interaction_type) if elem.interaction_type else None,
            'confidence': elem.confidence_score
        }
    
    def _infer_page_type(
        self,
        element_type_counts: Dict[str, int],
        analysis_results: Optional[Dict[str, Any]]
    ) -> str:
        """Infer the type of page based on elements."""
        # Use AI analysis if available
        if analysis_results:
            page_class = analysis_results.get('page_structure', {}).get('page_classification', {})
            if page_class and 'type' in page_class:
                return page_class['type']
        
        # Heuristic-based inference
        if element_type_counts.get('form', 0) > 2:
            return 'form_heavy'
        elif element_type_counts.get('table', 0) > 0:
            return 'data_display'
        elif element_type_counts.get('link', 0) > 20:
            return 'navigation_heavy'
        elif element_type_counts.get('button', 0) > 5:
            return 'interactive'
        else:
            return 'content'
    
    def _calculate_page_complexity(self, elements: List[ExtractedElement]) -> float:
        """Calculate page complexity score (0-1)."""
        factors = {
            'total_elements': min(len(elements) / 500, 1.0) * 0.2,
            'interactive_elements': min(sum(1 for e in elements if e.is_interactable) / 50, 1.0) * 0.3,
            'form_elements': min(sum(1 for e in elements if e.element_type in [ElementType.INPUT, ElementType.SELECT]) / 20, 1.0) * 0.2,
            'unique_types': min(len(set(e.element_type for e in elements if e.element_type)) / 10, 1.0) * 0.3
        }
        
        return sum(factors.values())
    
    def _calculate_accessibility_score(self, elements: List[ExtractedElement]) -> float:
        """Calculate basic accessibility score (0-1)."""
        accessible_elements = 0
        total_interactive = 0
        
        for elem in elements:
            if elem.is_interactable:
                total_interactive += 1
                
                # Check for accessibility attributes
                if elem.attributes:
                    if any(attr in elem.attributes for attr in ['aria-label', 'aria-describedby', 'alt', 'title']):
                        accessible_elements += 1
        
        if total_interactive == 0:
            return 1.0
        
        return accessible_elements / total_interactive
    
    def _is_form_element(self, elem: ExtractedElement) -> bool:
        """Check if element is form-related."""
        return elem.element_type in [
            ElementType.INPUT,
            ElementType.SELECT, ElementType.BUTTON,
            ElementType.CHECKBOX, ElementType.RADIO
        ]
    
    def _is_navigation_element(self, elem: ExtractedElement) -> bool:
        """Check if element is navigation-related."""
        if elem.element_type == ElementType.NAVIGATION:
            return True
        
        if elem.attributes:
            classes = elem.attributes.get('class', '').lower()
            return any(nav in classes for nav in self.navigation_indicators)
        
        return False
    
    def _is_search_element(self, elem: ExtractedElement) -> bool:
        """Check if element is search-related."""
        if elem.element_type == ElementType.INPUT and elem.attributes:
            input_type = elem.attributes.get('type', '').lower()
            input_name = elem.attributes.get('name', '').lower()
            placeholder = elem.attributes.get('placeholder', '').lower()
            
            return (input_type == 'search' or 
                   'search' in input_name or 
                   'search' in placeholder)
        
        return False
    
    def _find_form_inputs(
        self,
        elements: List[ExtractedElement],
        form: ExtractedElement
    ) -> List[ExtractedElement]:
        """Find all input elements within a form."""
        form_inputs = []
        
        for elem in elements:
            if self._is_form_element(elem):
                # Simple proximity check - in practice would use DOM hierarchy
                if form.bounding_box and elem.bounding_box:
                    if self._is_element_inside(elem.bounding_box, form.bounding_box):
                        form_inputs.append(elem)
                else:
                    # Fallback: assume all inputs belong to form if no position info
                    form_inputs.append(elem)
        
        return form_inputs
    
    def _find_submit_buttons(
        self,
        elements: List[ExtractedElement],
        form: ExtractedElement
    ) -> List[ExtractedElement]:
        """Find submit buttons for a form."""
        submit_buttons = []
        
        for elem in elements:
            if elem.element_type == ElementType.BUTTON:
                # Check if it's a submit button
                if elem.attributes:
                    button_type = elem.attributes.get('type', '').lower()
                    button_text = (elem.text or '').lower()
                    
                    if (button_type == 'submit' or 
                        any(word in button_text for word in ['submit', 'send', 'save', 'continue'])):
                        submit_buttons.append(elem)
        
        return submit_buttons
    
    def _find_auth_elements(self, elements: List[ExtractedElement]) -> Dict[str, List]:
        """Find authentication-related elements."""
        auth_elements = {'inputs': [], 'buttons': []}
        
        for elem in elements:
            if elem.element_type == ElementType.INPUT and elem.attributes:
                input_type = elem.attributes.get('type', '').lower()
                input_name = elem.attributes.get('name', '').lower()
                
                if (input_type in ['password', 'email'] or
                    any(auth in input_name for auth in ['user', 'login', 'email', 'password'])):
                    auth_elements['inputs'].append(elem)
            
            elif elem.element_type == ElementType.BUTTON:
                button_text = (elem.text or '').lower()
                if any(auth in button_text for auth in ['login', 'sign in', 'log in']):
                    auth_elements['buttons'].append(elem)
        
        return auth_elements if auth_elements['inputs'] else {}
    
    def _detect_implicit_forms(self, elements: List[ExtractedElement]) -> List[ExtractedElement]:
        """Detect implicit forms (input groups without form tags)."""
        # This is a simplified version - would need more sophisticated clustering
        implicit_forms = []
        
        # Find groups of inputs that are close together
        inputs = [e for e in elements if self._is_form_element(e)]
        
        if len(inputs) > 2:
            # Create a mock form element to represent the implicit form
            mock_form = type('MockForm', (), {
                'css_selector': 'implicit_form_1',
                'bounding_box': self._calculate_bounding_box_for_elements(inputs)
            })()
            implicit_forms.append(mock_form)
        
        return implicit_forms
    
    def _find_label_for_input(
        self,
        elements: List[ExtractedElement],
        input_elem: ExtractedElement
    ) -> str:
        """Find label text for an input element."""
        # Check for explicit label association
        if input_elem.attributes and 'id' in input_elem.attributes:
            input_id = input_elem.attributes['id']
            
            for elem in elements:
                if elem.tag_name == 'label' and elem.attributes:
                    if elem.attributes.get('for') == input_id:
                        return elem.text or ''
        
        # Check for proximity-based label
        if input_elem.bounding_box:
            closest_label = None
            min_distance = float('inf')
            
            for elem in elements:
                if elem.tag_name == 'label' and elem.bounding_box:
                    distance = self._calculate_element_distance(
                        input_elem.bounding_box,
                        elem.bounding_box
                    )
                    if distance < min_distance:
                        min_distance = distance
                        closest_label = elem
            
            if closest_label and min_distance < 100:  # Threshold
                return closest_label.text or ''
        
        # Use placeholder as fallback
        if input_elem.attributes:
            return input_elem.attributes.get('placeholder', '')
        
        return ''
    
    def _is_breadcrumb(self, elem: ExtractedElement) -> bool:
        """Check if element is a breadcrumb navigation."""
        if elem.attributes:
            classes = elem.attributes.get('class', '').lower()
            aria_label = elem.attributes.get('aria-label', '').lower()
            
            return 'breadcrumb' in classes or 'breadcrumb' in aria_label
        
        return False
    
    def _is_pagination(self, elem: ExtractedElement) -> bool:
        """Check if element is pagination."""
        if elem.attributes:
            classes = elem.attributes.get('class', '').lower()
            role = elem.attributes.get('role', '').lower()
            
            return 'pagination' in classes or 'pagination' in role
        
        return False
    
    def _extract_navigation_links(
        self,
        elements: List[ExtractedElement],
        nav_container: ExtractedElement
    ) -> List[Dict[str, str]]:
        """Extract links within a navigation container."""
        nav_links = []
        
        for elem in elements:
            if elem.element_type == ElementType.LINK:
                # Check if link is within navigation container
                if (nav_container.bounding_box and elem.bounding_box and
                    self._is_element_inside(elem.bounding_box, nav_container.bounding_box)):
                    
                    nav_links.append({
                        'text': elem.text or '',
                        'href': elem.attributes.get('href', '') if elem.attributes else '',
                        'selector': elem.css_selector
                    })
        
        return nav_links
    
    def _is_element_inside(self, inner_box: Dict, outer_box: Dict) -> bool:
        """Check if one element is inside another based on bounding boxes."""
        return (inner_box['x'] >= outer_box['x'] and
                inner_box['y'] >= outer_box['y'] and
                inner_box['x'] + inner_box['width'] <= outer_box['x'] + outer_box['width'] and
                inner_box['y'] + inner_box['height'] <= outer_box['y'] + outer_box['height'])
    
    def _are_elements_siblings(self, box1: Dict, box2: Dict) -> bool:
        """Check if elements are siblings based on position."""
        # Elements are siblings if they have similar Y position
        y_threshold = 20  # pixels
        return abs(box1['y'] - box2['y']) < y_threshold
    
    def _find_associated_input(
        self,
        label: ExtractedElement,
        inputs: List[ExtractedElement]
    ) -> Optional[ExtractedElement]:
        """Find input associated with a label."""
        # Check explicit association
        if label.attributes and 'for' in label.attributes:
            for_id = label.attributes['for']
            for input_elem in inputs:
                if input_elem.attributes and input_elem.attributes.get('id') == for_id:
                    return input_elem
        
        # Check proximity
        if label.bounding_box:
            closest_input = None
            min_distance = float('inf')
            
            for input_elem in inputs:
                if input_elem.bounding_box:
                    distance = self._calculate_element_distance(
                        label.bounding_box,
                        input_elem.bounding_box
                    )
                    if distance < min_distance:
                        min_distance = distance
                        closest_input = input_elem
            
            if closest_input and min_distance < 100:  # Threshold
                return closest_input
        
        return None
    
    def _detect_ecommerce_patterns(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Detect e-commerce patterns."""
        indicators = []
        
        # Check for price indicators
        for elem in elements:
            text = (elem.text or '').lower()
            if any(indicator in text for indicator in ['$', '€', '£', 'price', 'cost', 'total']):
                indicators.append('price_display')
                break
        
        # Check for cart/basket
        for elem in elements:
            text = (elem.text or '').lower()
            if elem.attributes:
                classes = elem.attributes.get('class', '').lower()
                if any(cart in text + classes for cart in ['cart', 'basket', 'bag']):
                    indicators.append('shopping_cart')
                    break
        
        # Check for product indicators
        for elem in elements:
            if elem.attributes:
                classes = elem.attributes.get('class', '').lower()
                if any(prod in classes for prod in ['product', 'item', 'listing']):
                    indicators.append('product_display')
                    break
        
        return {
            'detected': len(indicators) > 0,
            'indicators': indicators,
            'pattern_type': 'e_commerce'
        }
    
    def _detect_auth_patterns(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Detect authentication patterns."""
        auth_elements = self._find_auth_elements(elements)
        
        return {
            'detected': bool(auth_elements),
            'indicators': ['login_form'] if auth_elements else [],
            'pattern_type': 'authentication',
            'element_count': len(auth_elements.get('inputs', [])) + len(auth_elements.get('buttons', []))
        }
    
    def _detect_search_patterns(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Detect search patterns."""
        search_elements = [e for e in elements if self._is_search_element(e)]
        
        return {
            'detected': len(search_elements) > 0,
            'indicators': ['search_input'] if search_elements else [],
            'pattern_type': 'search',
            'element_count': len(search_elements)
        }
    
    def _detect_social_patterns(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Detect social media patterns."""
        indicators = []
        
        social_keywords = ['share', 'like', 'follow', 'tweet', 'post', 'comment']
        
        for elem in elements:
            text = (elem.text or '').lower()
            if elem.attributes:
                classes = elem.attributes.get('class', '').lower()
                
                if any(social in text + classes for social in social_keywords):
                    indicators.append('social_action')
                    break
        
        return {
            'detected': len(indicators) > 0,
            'indicators': indicators,
            'pattern_type': 'social'
        }
    
    def _detect_cms_patterns(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Detect content management patterns."""
        indicators = []
        
        # Check for article/blog structures
        for elem in elements:
            if elem.element_type in [ElementType.HEADER, ElementType.ARTICLE]:
                indicators.append('article_structure')
                break
        
        # Check for content editing
        for elem in elements:
            if elem.element_type == ElementType.BUTTON:
                text = (elem.text or '').lower()
                if any(action in text for action in ['edit', 'publish', 'draft', 'delete']):
                    indicators.append('content_actions')
                    break
        
        return {
            'detected': len(indicators) > 0,
            'indicators': indicators,
            'pattern_type': 'content_management'
        }
    
    def _detect_data_entry_patterns(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
        """Detect data entry patterns."""
        form_count = sum(1 for e in elements if e.element_type == ElementType.FORM)
        input_count = sum(1 for e in elements if e.element_type == ElementType.INPUT)
        
        indicators = []
        if form_count > 1:
            indicators.append('multiple_forms')
        if input_count > 10:
            indicators.append('many_inputs')
        
        return {
            'detected': len(indicators) > 0,
            'indicators': indicators,
            'pattern_type': 'data_entry',
            'form_count': form_count,
            'input_count': input_count
        }
    
    def _detect_common_patterns(self, elements: List[ExtractedElement]) -> List[str]:
        """Detect common UI patterns."""
        patterns = []
        
        # Modal patterns
        # Note: MODAL type doesn't exist
        # if any(e.element_type == ElementType.MODAL for e in elements):
        #     patterns.append('modal_dialogs')
        
        # Table patterns
        if any(e.element_type == ElementType.TABLE for e in elements):
            patterns.append('data_tables')
        
        # Note: TAB, TOOLTIP, ALERT types don't exist in current ElementType enum
        # These would need to be detected differently (e.g., by role or class)
        
        return patterns
    
    def _calculate_bounding_box_for_elements(
        self,
        elements: List[ExtractedElement]
    ) -> Dict[str, float]:
        """Calculate bounding box that encompasses all elements."""
        if not elements or not any(e.bounding_box for e in elements):
            return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
        
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for elem in elements:
            if elem.bounding_box:
                box = elem.bounding_box
                min_x = min(min_x, box['x'])
                min_y = min(min_y, box['y'])
                max_x = max(max_x, box['x'] + box['width'])
                max_y = max(max_y, box['y'] + box['height'])
        
        return {
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x,
            'height': max_y - min_y
        }
    
    def _calculate_element_distance(self, box1: Dict, box2: Dict) -> float:
        """Calculate distance between two elements."""
        # Center points
        center1_x = box1['x'] + box1['width'] / 2
        center1_y = box1['y'] + box1['height'] / 2
        center2_x = box2['x'] + box2['width'] / 2
        center2_y = box2['y'] + box2['height'] / 2
        
        # Euclidean distance
        return ((center2_x - center1_x) ** 2 + (center2_y - center1_y) ** 2) ** 0.5