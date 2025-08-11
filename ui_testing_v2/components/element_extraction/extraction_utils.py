"""
Unified utility functions for element extraction.
Consolidates common functionality from multiple extractors to eliminate duplication.
"""

import re
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ElementType(Enum):
    """Unified element type enumeration"""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    IMAGE = "image"
    TEXT = "text"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    FORM = "form"
    TABLE = "table"
    LIST = "list"
    NAVIGATION = "navigation"
    HEADER = "header"
    FOOTER = "footer"
    DIALOG = "dialog"
    VIDEO = "video"
    AUDIO = "audio"
    CANVAS = "canvas"
    IFRAME = "iframe"
    UNKNOWN = "unknown"


class InteractionType(Enum):
    """Unified interaction type enumeration"""
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    HOVER = "hover"
    DRAG = "drag"
    DROP = "drop"
    SCROLL = "scroll"
    WAIT = "wait"
    ASSERT = "assert"
    NAVIGATE = "navigate"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    CLEAR = "clear"
    FOCUS = "focus"
    BLUR = "blur"
    SUBMIT = "submit"
    RESET = "reset"
    NONE = "none"


class SelectorGenerator:
    """Consolidated selector generation utilities"""
    
    @staticmethod
    def generate_css_selector(element: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate multiple CSS selector strategies for an element"""
        selectors = []
        attributes = element.get('attributes', {})
        tag_name = element.get('tag_name', '').lower()
        
        # ID selector (highest priority)
        if element_id := attributes.get('id'):
            if SelectorGenerator._is_valid_id(element_id):
                selectors.append({
                    'type': 'css',
                    'selector': f"#{element_id}",
                    'score': 1.0,
                    'strategy': 'id'
                })
        
        # Unique class combinations
        if classes := attributes.get('class'):
            class_list = classes.split() if isinstance(classes, str) else classes
            if unique_combo := SelectorGenerator._find_unique_class_combination(class_list, tag_name):
                selectors.append({
                    'type': 'css',
                    'selector': unique_combo,
                    'score': 0.8,
                    'strategy': 'class'
                })
        
        # Data attributes
        for attr, value in attributes.items():
            if attr.startswith('data-') and value:
                selector = f"{tag_name}[{attr}='{value}']"
                selectors.append({
                    'type': 'css',
                    'selector': selector,
                    'score': 0.7,
                    'strategy': 'data-attribute'
                })
        
        # ARIA attributes
        if aria_label := attributes.get('aria-label'):
            selector = f"{tag_name}[aria-label='{aria_label}']"
            selectors.append({
                'type': 'css',
                'selector': selector,
                'score': 0.75,
                'strategy': 'aria'
            })
        
        # Name attribute for form elements
        if name := attributes.get('name'):
            selector = f"{tag_name}[name='{name}']"
            selectors.append({
                'type': 'css',
                'selector': selector,
                'score': 0.65,
                'strategy': 'name'
            })
        
        # Position-based fallback
        if 'position' in element:
            nth = element['position'] + 1
            selector = f"{tag_name}:nth-of-type({nth})"
            selectors.append({
                'type': 'css',
                'selector': selector,
                'score': 0.3,
                'strategy': 'position'
            })
        
        return selectors
    
    @staticmethod
    def generate_xpath_selector(element: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate XPath selectors for an element"""
        selectors = []
        attributes = element.get('attributes', {})
        tag_name = element.get('tag_name', '').lower()
        text = element.get('text', '').strip()
        
        # ID-based XPath
        if element_id := attributes.get('id'):
            if SelectorGenerator._is_valid_id(element_id):
                selectors.append({
                    'type': 'xpath',
                    'selector': f"//*[@id='{element_id}']",
                    'score': 0.95,
                    'strategy': 'id'
                })
        
        # Text-based XPath
        if text and len(text) < 100:
            escaped_text = text.replace("'", "\\'")
            selectors.append({
                'type': 'xpath',
                'selector': f"//{tag_name}[contains(text(), '{escaped_text}')]",
                'score': 0.6,
                'strategy': 'text'
            })
        
        # Attribute-based XPath
        for attr, value in attributes.items():
            if attr not in ['id', 'class'] and value:
                selector = f"//{tag_name}[@{attr}='{value}']"
                selectors.append({
                    'type': 'xpath',
                    'selector': selector,
                    'score': 0.5,
                    'strategy': f'attribute-{attr}'
                })
        
        return selectors
    
    @staticmethod
    def _is_valid_id(element_id: str) -> bool:
        """Check if an ID is likely to be stable and not auto-generated"""
        if not element_id:
            return False
        
        # Check for common patterns of auto-generated IDs
        auto_generated_patterns = [
            r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',  # UUID
            r'^[a-f0-9]{24}$',  # MongoDB ObjectId
            r'^ember\d+$',  # Ember.js
            r'^react-select-\d+-',  # React Select
            r'^\d+$',  # Pure numbers
            r'^ng-',  # Angular
            r'^vue-',  # Vue.js
            r'^svelte-',  # Svelte
            r'^__next',  # Next.js
            r'^gatsby-',  # Gatsby
        ]
        
        for pattern in auto_generated_patterns:
            if re.match(pattern, element_id, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def _find_unique_class_combination(classes: List[str], tag_name: str) -> Optional[str]:
        """Find a unique combination of classes for selection"""
        if not classes:
            return None
        
        # Filter out common utility classes
        utility_classes = {
            'active', 'disabled', 'hidden', 'visible', 'selected',
            'hover', 'focus', 'error', 'success', 'warning', 'info',
            'sm', 'md', 'lg', 'xl', 'xs', 'small', 'medium', 'large',
            'col', 'row', 'container', 'wrapper', 'inner', 'outer'
        }
        
        meaningful_classes = [c for c in classes if c.lower() not in utility_classes]
        
        if meaningful_classes:
            # Try single meaningful class first
            if len(meaningful_classes) == 1:
                return f"{tag_name}.{meaningful_classes[0]}"
            
            # Try combination of first two meaningful classes
            return f"{tag_name}.{'.'.join(meaningful_classes[:2])}"
        
        # Fallback to first class
        return f"{tag_name}.{classes[0]}" if classes else None


class ElementTypeDetector:
    """Consolidated element type detection logic"""
    
    @staticmethod
    def determine_element_type(tag_name: str, attributes: Dict[str, Any]) -> ElementType:
        """Determine the type of an element based on tag and attributes"""
        tag_name = tag_name.lower()
        
        # Direct tag mappings
        tag_type_map = {
            'button': ElementType.BUTTON,
            'a': ElementType.LINK,
            'img': ElementType.IMAGE,
            'video': ElementType.VIDEO,
            'audio': ElementType.AUDIO,
            'canvas': ElementType.CANVAS,
            'iframe': ElementType.IFRAME,
            'form': ElementType.FORM,
            'table': ElementType.TABLE,
            'nav': ElementType.NAVIGATION,
            'header': ElementType.HEADER,
            'footer': ElementType.FOOTER,
            'dialog': ElementType.DIALOG,
            'textarea': ElementType.TEXTAREA,
            'select': ElementType.DROPDOWN,
        }
        
        if tag_name in tag_type_map:
            return tag_type_map[tag_name]
        
        # Input type-specific detection
        if tag_name == 'input':
            input_type = attributes.get('type', 'text').lower()
            input_type_map = {
                'button': ElementType.BUTTON,
                'submit': ElementType.BUTTON,
                'reset': ElementType.BUTTON,
                'checkbox': ElementType.CHECKBOX,
                'radio': ElementType.RADIO,
                'file': ElementType.INPUT,
                'image': ElementType.BUTTON,
            }
            return input_type_map.get(input_type, ElementType.INPUT)
        
        # Role-based detection
        role = attributes.get('role', '').lower()
        role_type_map = {
            'button': ElementType.BUTTON,
            'link': ElementType.LINK,
            'navigation': ElementType.NAVIGATION,
            'checkbox': ElementType.CHECKBOX,
            'radio': ElementType.RADIO,
            'textbox': ElementType.INPUT,
            'combobox': ElementType.DROPDOWN,
            'listbox': ElementType.LIST,
            'dialog': ElementType.DIALOG,
            'form': ElementType.FORM,
        }
        
        if role in role_type_map:
            return role_type_map[role]
        
        # List detection
        if tag_name in ['ul', 'ol', 'dl']:
            return ElementType.LIST
        
        # Generic text elements
        if tag_name in ['p', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return ElementType.TEXT
        
        return ElementType.UNKNOWN
    
    @staticmethod
    def determine_interaction_type(element_type: ElementType, attributes: Dict[str, Any]) -> List[InteractionType]:
        """Determine possible interaction types for an element"""
        interactions = []
        
        # Type-based interactions
        type_interactions = {
            ElementType.BUTTON: [InteractionType.CLICK],
            ElementType.LINK: [InteractionType.CLICK, InteractionType.NAVIGATE],
            ElementType.INPUT: [InteractionType.TYPE, InteractionType.CLEAR, InteractionType.FOCUS],
            ElementType.TEXTAREA: [InteractionType.TYPE, InteractionType.CLEAR, InteractionType.FOCUS],
            ElementType.DROPDOWN: [InteractionType.SELECT, InteractionType.CLICK],
            ElementType.CHECKBOX: [InteractionType.CLICK],
            ElementType.RADIO: [InteractionType.CLICK],
            ElementType.FORM: [InteractionType.SUBMIT, InteractionType.RESET],
            ElementType.IMAGE: [InteractionType.CLICK],
            ElementType.VIDEO: [InteractionType.CLICK],
        }
        
        if element_type in type_interactions:
            interactions.extend(type_interactions[element_type])
        
        # Event handler-based interactions
        event_handlers = ['onclick', 'onmousedown', 'onmouseup', 'onchange', 'oninput', 'onsubmit']
        for handler in event_handlers:
            if handler in attributes:
                if 'click' in handler or 'mouse' in handler:
                    interactions.append(InteractionType.CLICK)
                elif 'change' in handler or 'input' in handler:
                    interactions.append(InteractionType.TYPE)
                elif 'submit' in handler:
                    interactions.append(InteractionType.SUBMIT)
        
        # Draggable elements
        if attributes.get('draggable') == 'true':
            interactions.extend([InteractionType.DRAG, InteractionType.DROP])
        
        # Hover interactions for elements with titles or tooltips
        if 'title' in attributes or 'data-tooltip' in attributes:
            interactions.append(InteractionType.HOVER)
        
        # Remove duplicates and return
        return list(set(interactions)) if interactions else [InteractionType.NONE]


class ConfidenceCalculator:
    """Consolidated confidence scoring logic"""
    
    @staticmethod
    def calculate_element_confidence(
        selectors: List[Dict[str, Any]],
        properties: Dict[str, Any],
        element_type: ElementType
    ) -> float:
        """Calculate confidence score for an extracted element"""
        confidence = 0.0
        
        # Selector quality score
        if selectors:
            best_selector_score = max(s.get('score', 0) for s in selectors)
            confidence += best_selector_score * 0.4
        
        # Element type confidence
        if element_type != ElementType.UNKNOWN:
            confidence += 0.2
        
        # Properties completeness
        required_props = ['tag_name', 'text', 'attributes']
        present_props = sum(1 for prop in required_props if prop in properties and properties[prop])
        confidence += (present_props / len(required_props)) * 0.2
        
        # Interactability score
        if properties.get('is_visible') and properties.get('is_enabled'):
            confidence += 0.1
        
        # Accessibility score
        attrs = properties.get('attributes', {})
        if any(attr in attrs for attr in ['aria-label', 'aria-describedby', 'role', 'alt']):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    @staticmethod
    def calculate_stability_score(element: Dict[str, Any]) -> float:
        """Calculate stability score indicating how likely the element is to remain consistent"""
        score = 0.0
        attributes = element.get('attributes', {})
        
        # Stable ID
        if element_id := attributes.get('id'):
            if SelectorGenerator._is_valid_id(element_id):
                score += 0.3
        
        # Stable classes
        if classes := attributes.get('class'):
            class_list = classes.split() if isinstance(classes, str) else classes
            if class_list and not any('generated' in c or 'random' in c for c in class_list):
                score += 0.2
        
        # Data attributes (usually stable)
        data_attrs = [k for k in attributes.keys() if k.startswith('data-')]
        if data_attrs:
            score += min(len(data_attrs) * 0.1, 0.2)
        
        # ARIA attributes (usually stable)
        aria_attrs = [k for k in attributes.keys() if k.startswith('aria-')]
        if aria_attrs:
            score += min(len(aria_attrs) * 0.05, 0.15)
        
        # Semantic HTML (more stable than divs/spans)
        tag_name = element.get('tag_name', '').lower()
        semantic_tags = {
            'header', 'footer', 'nav', 'main', 'article', 'section',
            'aside', 'button', 'form', 'input', 'select', 'textarea'
        }
        if tag_name in semantic_tags:
            score += 0.15
        
        return min(score, 1.0)


class ElementValidator:
    """Consolidated element validation utilities"""
    
    @staticmethod
    def is_interactive_element(element: Dict[str, Any]) -> bool:
        """Check if an element is interactive"""
        tag_name = element.get('tag_name', '').lower()
        attributes = element.get('attributes', {})
        
        # Interactive tags
        interactive_tags = {
            'a', 'button', 'input', 'select', 'textarea', 'video', 'audio',
            'details', 'dialog', 'embed', 'iframe', 'object'
        }
        
        if tag_name in interactive_tags:
            return True
        
        # Interactive roles
        interactive_roles = {
            'button', 'link', 'checkbox', 'radio', 'slider', 'switch',
            'textbox', 'combobox', 'listbox', 'menu', 'menuitem', 'tab'
        }
        
        if attributes.get('role') in interactive_roles:
            return True
        
        # Has event handlers
        event_attrs = ['onclick', 'onmousedown', 'onchange', 'oninput', 'onsubmit']
        if any(attr in attributes for attr in event_attrs):
            return True
        
        # Has tabindex (keyboard accessible)
        if 'tabindex' in attributes:
            try:
                tabindex = int(attributes['tabindex'])
                if tabindex >= 0:
                    return True
            except (ValueError, TypeError):
                pass
        
        # Contenteditable
        if attributes.get('contenteditable') == 'true':
            return True
        
        return False
    
    @staticmethod
    def is_visible_element(element: Dict[str, Any]) -> bool:
        """Check if an element is likely visible"""
        # Check computed styles if available
        if 'computed_style' in element:
            style = element['computed_style']
            
            # Check display
            if style.get('display') == 'none':
                return False
            
            # Check visibility
            if style.get('visibility') == 'hidden':
                return False
            
            # Check opacity
            try:
                if float(style.get('opacity', 1)) == 0:
                    return False
            except (ValueError, TypeError):
                pass
        
        # Check inline styles
        if style_attr := element.get('attributes', {}).get('style'):
            if 'display: none' in style_attr or 'visibility: hidden' in style_attr:
                return False
        
        # Check aria-hidden
        if element.get('attributes', {}).get('aria-hidden') == 'true':
            return False
        
        # Check if element has dimensions
        if 'bounding_box' in element:
            bbox = element['bounding_box']
            if bbox.get('width', 0) <= 0 or bbox.get('height', 0) <= 0:
                return False
        
        return True
    
    @staticmethod
    def filter_duplicate_elements(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out duplicate elements based on various criteria"""
        seen_signatures = set()
        unique_elements = []
        
        for element in elements:
            # Create signature based on multiple attributes
            signature_parts = [
                element.get('tag_name', ''),
                element.get('attributes', {}).get('id', ''),
                element.get('attributes', {}).get('class', ''),
                str(element.get('bounding_box', {})),
                element.get('text', '')[:100]  # First 100 chars of text
            ]
            
            signature = hashlib.md5('|'.join(signature_parts).encode()).hexdigest()
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_elements.append(element)
        
        return unique_elements
    
    @staticmethod
    def validate_element_data(element: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate element data structure and return issues"""
        issues = []
        
        # Required fields
        required_fields = ['tag_name']
        for field in required_fields:
            if field not in element:
                issues.append(f"Missing required field: {field}")
        
        # Validate tag_name
        if 'tag_name' in element:
            if not element['tag_name'] or not isinstance(element['tag_name'], str):
                issues.append("Invalid tag_name")
        
        # Validate attributes
        if 'attributes' in element:
            if not isinstance(element['attributes'], dict):
                issues.append("Attributes must be a dictionary")
        
        # Validate selectors
        if 'selectors' in element:
            if not isinstance(element['selectors'], list):
                issues.append("Selectors must be a list")
            else:
                for selector in element['selectors']:
                    if not isinstance(selector, dict):
                        issues.append("Each selector must be a dictionary")
                        break
                    if 'selector' not in selector or 'type' not in selector:
                        issues.append("Selector missing required fields")
                        break
        
        # Validate bounding box
        if 'bounding_box' in element:
            bbox = element['bounding_box']
            if not isinstance(bbox, dict):
                issues.append("Bounding box must be a dictionary")
            else:
                required_bbox_fields = ['x', 'y', 'width', 'height']
                for field in required_bbox_fields:
                    if field not in bbox:
                        issues.append(f"Bounding box missing {field}")
        
        return len(issues) == 0, issues


class StealthUtilities:
    """Consolidated stealth and anti-detection utilities"""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    VIEWPORT_SIZES = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1440, "height": 900},
        {"width": 1536, "height": 864},
        {"width": 1680, "height": 1050}
    ]
    
    COOKIE_SELECTORS = [
        "button:has-text('Accept')",
        "button:has-text('Accept all')",
        "button:has-text('Accept cookies')",
        "button:has-text('I agree')",
        "button:has-text('OK')",
        "button:has-text('Got it')",
        "[class*='cookie'] button",
        "[id*='cookie'] button",
        "[class*='consent'] button",
        "[id*='consent'] button",
        ".cookie-banner button",
        "#cookie-banner button",
        "[aria-label*='accept']",
        "[aria-label*='cookie']"
    ]
    
    @staticmethod
    def get_random_user_agent() -> str:
        """Get a random user agent string"""
        import random
        return random.choice(StealthUtilities.USER_AGENTS)
    
    @staticmethod
    def get_random_viewport() -> Dict[str, int]:
        """Get random viewport dimensions"""
        import random
        return random.choice(StealthUtilities.VIEWPORT_SIZES)
    
    @staticmethod
    def calculate_human_delay(base_delay: float = 0.1) -> float:
        """Calculate human-like delay with randomization"""
        import random
        return base_delay + random.uniform(0, base_delay * 0.5)
    
    @staticmethod
    def get_stealth_browser_args() -> List[str]:
        """Get browser arguments for stealth mode"""
        return [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-accelerated-2d-canvas',
            '--disable-gpu',
            '--window-size=1920,1080',
            '--start-maximized',
            '--user-agent=' + StealthUtilities.get_random_user_agent()
        ]


class ExtractionMetrics:
    """Utilities for tracking extraction metrics and performance"""
    
    @staticmethod
    def calculate_extraction_stats(elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for extracted elements"""
        if not elements:
            return {
                'total_elements': 0,
                'interactive_elements': 0,
                'elements_by_type': {},
                'average_confidence': 0,
                'average_stability': 0
            }
        
        element_types = {}
        total_confidence = 0
        total_stability = 0
        interactive_count = 0
        
        for element in elements:
            # Count by type
            element_type = element.get('element_type', 'unknown')
            element_types[element_type] = element_types.get(element_type, 0) + 1
            
            # Sum confidence and stability
            total_confidence += element.get('confidence', 0)
            total_stability += element.get('stability_score', 0)
            
            # Count interactive
            if ElementValidator.is_interactive_element(element):
                interactive_count += 1
        
        return {
            'total_elements': len(elements),
            'interactive_elements': interactive_count,
            'elements_by_type': element_types,
            'average_confidence': total_confidence / len(elements),
            'average_stability': total_stability / len(elements),
            'extraction_quality': (total_confidence + total_stability) / (2 * len(elements))
        }