"""
Optimized Element Extraction System V2 - Production Implementation
Follows CODER strategy with comprehensive metadata for LLM test generation
"""

import asyncio
import hashlib
import json
import logging
import random
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urlparse

import numpy as np
from playwright.async_api import Page, ElementHandle, async_playwright
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class ElementType(Enum):
    """Enumeration of element types for classification."""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    FORM = "form"
    TABLE = "table"
    IMAGE = "image"
    VIDEO = "video"
    NAVIGATION = "navigation"
    DIALOG = "dialog"
    TEXT = "text"
    UNKNOWN = "unknown"


class InteractionType(Enum):
    """Possible interaction types with elements."""
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    CHECK = "check"
    HOVER = "hover"
    SCROLL = "scroll"
    UPLOAD = "upload"
    DRAG = "drag"
    SUBMIT = "submit"
    CLEAR = "clear"
    FOCUS = "focus"
    BLUR = "blur"


@dataclass
class ExtractionConfig:
    """Configuration for element extraction."""
    max_elements: int = 100
    enable_ai_analysis: bool = True
    parallel_strategies: bool = True
    extract_validation_rules: bool = True
    extract_relationships: bool = True
    generate_test_hints: bool = True
    timeout: int = 30
    min_confidence: float = 0.3
    enable_visual_extraction: bool = False  # Disabled for now
    enable_accessibility_extraction: bool = True
    stealth_mode: bool = True


@dataclass
class ElementMetadata:
    """Complete metadata for an extracted element."""
    # Identification
    element_id: str
    selectors: Dict[str, str]
    test_id: Optional[str] = None
    
    # Basic Properties
    tag_name: str = ""
    element_type: str = "unknown"
    text_content: Optional[str] = None
    inner_html: Optional[str] = None
    
    # Semantic Context
    aria_label: Optional[str] = None
    aria_role: Optional[str] = None
    semantic_purpose: str = ""
    business_context: Optional[str] = None
    
    # Interaction Capabilities
    possible_interactions: List[str] = field(default_factory=list)
    is_interactive: bool = False
    is_clickable: bool = False
    is_editable: bool = False
    accepts_input: bool = False
    
    # State Information
    is_visible: bool = True
    is_enabled: bool = True
    is_required: bool = False
    current_value: Optional[Any] = None
    default_value: Optional[Any] = None
    
    # Validation Rules
    validation_pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    allowed_values: Optional[List[str]] = None
    
    # Relationships
    parent_element_id: Optional[str] = None
    child_element_ids: List[str] = field(default_factory=list)
    sibling_element_ids: List[str] = field(default_factory=list)
    form_id: Optional[str] = None
    label_element_id: Optional[str] = None
    
    # Visual Context
    position: Dict[str, float] = field(default_factory=dict)
    z_index: Optional[int] = None
    is_above_fold: bool = True
    visual_hierarchy_level: int = 0
    
    # Test Generation Hints
    test_priority: int = 3
    suggested_test_scenarios: List[str] = field(default_factory=list)
    expected_behaviors: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    
    # Metadata
    extraction_confidence: float = 0.5
    extraction_strategy: str = ""
    extraction_timestamp: str = ""
    page_context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for LLM consumption."""
        return {
            'element_id': self.element_id,
            'selectors': self.selectors,
            'test_id': self.test_id,
            'tag_name': self.tag_name,
            'element_type': self.element_type,
            'text_content': self.text_content,
            'aria_label': self.aria_label,
            'aria_role': self.aria_role,
            'semantic_purpose': self.semantic_purpose,
            'business_context': self.business_context,
            'possible_interactions': self.possible_interactions,
            'is_interactive': self.is_interactive,
            'is_clickable': self.is_clickable,
            'is_editable': self.is_editable,
            'accepts_input': self.accepts_input,
            'is_visible': self.is_visible,
            'is_enabled': self.is_enabled,
            'is_required': self.is_required,
            'current_value': self.current_value,
            'validation_pattern': self.validation_pattern,
            'min_length': self.min_length,
            'max_length': self.max_length,
            'allowed_values': self.allowed_values,
            'form_id': self.form_id,
            'position': self.position,
            'test_priority': self.test_priority,
            'suggested_test_scenarios': self.suggested_test_scenarios,
            'expected_behaviors': self.expected_behaviors,
            'extraction_confidence': self.extraction_confidence,
            'extraction_strategy': self.extraction_strategy,
            'page_context': self.page_context
        }


# ============================================================================
# Extraction Strategies
# ============================================================================

class ExtractionStrategy(ABC):
    """Abstract base class for extraction strategies."""
    
    @abstractmethod
    async def extract(self, page: Page) -> List[ElementMetadata]:
        """Extract elements using this strategy."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name."""
        pass


class DOMExtractionStrategy(ExtractionStrategy):
    """DOM-based extraction strategy."""
    
    @property
    def name(self) -> str:
        return "dom"
    
    async def extract(self, page: Page) -> List[ElementMetadata]:
        """Extract elements from DOM."""
        elements = []
        
        # JavaScript to extract comprehensive DOM information
        extraction_script = """
        () => {
            const elements = [];
            
            function generateId(element, index) {
                return element.id || 
                       element.dataset?.testid || 
                       `${element.tagName.toLowerCase()}_${index}`;
            }
            
            function getSelectors(element) {
                const selectors = {};
                
                // ID selector
                if (element.id) {
                    selectors.id = `#${element.id}`;
                }
                
                // Data-testid selector
                if (element.dataset?.testid) {
                    selectors.testid = `[data-testid="${element.dataset.testid}"]`;
                }
                
                // Class selector
                if (element.className && typeof element.className === 'string') {
                    const classes = element.className.split(' ').filter(c => c);
                    if (classes.length) {
                        selectors.css = `${element.tagName.toLowerCase()}.${classes.join('.')}`;
                    }
                }
                
                // XPath
                selectors.xpath = getXPath(element);
                
                return selectors;
            }
            
            function getXPath(element) {
                if (element.id) return `//*[@id="${element.id}"]`;
                if (element === document.body) return '/html/body';
                
                let ix = 0;
                const siblings = element.parentNode?.childNodes;
                if (siblings) {
                    for (let i = 0; i < siblings.length; i++) {
                        const sibling = siblings[i];
                        if (sibling === element) {
                            return getXPath(element.parentNode) + '/' + 
                                   element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                }
                return '';
            }
            
            function getValidationRules(element) {
                const rules = {};
                
                if (element.pattern) rules.pattern = element.pattern;
                if (element.minLength !== undefined && element.minLength !== -1) rules.minLength = element.minLength;
                if (element.maxLength !== undefined && element.maxLength !== -1) rules.maxLength = element.maxLength;
                if (element.min !== undefined) rules.min = element.min;
                if (element.max !== undefined) rules.max = element.max;
                if (element.required) rules.required = true;
                if (element.type === 'email') rules.pattern = rules.pattern || '[^@]+@[^@]+\\.[^@]+';
                
                return rules;
            }
            
            function getElementType(element) {
                const tag = element.tagName.toLowerCase();
                const type = element.type?.toLowerCase();
                const role = element.getAttribute('role');
                
                if (tag === 'button' || type === 'button' || type === 'submit' || role === 'button') {
                    return 'button';
                } else if (tag === 'input') {
                    if (type === 'checkbox') return 'checkbox';
                    if (type === 'radio') return 'radio';
                    if (type === 'file') return 'input';
                    return 'input';
                } else if (tag === 'a') {
                    return 'link';
                } else if (tag === 'select') {
                    return 'dropdown';
                } else if (tag === 'textarea') {
                    return 'textarea';
                } else if (tag === 'form') {
                    return 'form';
                } else if (tag === 'table') {
                    return 'table';
                } else if (tag === 'img') {
                    return 'image';
                } else if (tag === 'video') {
                    return 'video';
                } else if (role === 'navigation' || tag === 'nav') {
                    return 'navigation';
                } else if (role === 'dialog') {
                    return 'dialog';
                }
                
                return 'unknown';
            }
            
            function getPossibleInteractions(element) {
                const interactions = [];
                const tag = element.tagName.toLowerCase();
                const type = element.type?.toLowerCase();
                
                if (element.onclick || element.getAttribute('onclick')) {
                    interactions.push('click');
                }
                
                if (tag === 'input' || tag === 'textarea') {
                    interactions.push('type', 'clear', 'focus', 'blur');
                }
                
                if (tag === 'select') {
                    interactions.push('select');
                }
                
                if (type === 'checkbox' || type === 'radio') {
                    interactions.push('check', 'click');
                }
                
                if (tag === 'button' || type === 'submit') {
                    interactions.push('click');
                    if (element.form) interactions.push('submit');
                }
                
                if (tag === 'a') {
                    interactions.push('click');
                }
                
                if (type === 'file') {
                    interactions.push('upload');
                }
                
                return [...new Set(interactions)];
            }
            
            // Get all interactive elements
            const selector = 'input, button, a, select, textarea, [role="button"], [role="link"], [onclick], [data-testid], form';
            const allElements = document.querySelectorAll(selector);
            
            allElements.forEach((element, index) => {
                const rect = element.getBoundingClientRect();
                const styles = window.getComputedStyle(element);
                const validationRules = getValidationRules(element);
                
                // Find associated label
                let labelText = null;
                let labelId = null;
                if (element.id) {
                    const label = document.querySelector(`label[for="${element.id}"]`);
                    if (label) {
                        labelText = label.textContent?.trim();
                        labelId = label.id || `label_${element.id}`;
                    }
                }
                
                // Find parent form
                const form = element.closest('form');
                
                // Get select options if dropdown
                let options = null;
                if (element.tagName === 'SELECT') {
                    options = Array.from(element.options || []).map(o => o.value);
                }
                
                elements.push({
                    element_id: generateId(element, index),
                    selectors: getSelectors(element),
                    test_id: element.dataset?.testid || null,
                    tag_name: element.tagName.toLowerCase(),
                    element_type: getElementType(element),
                    text_content: element.textContent?.trim().substring(0, 200),
                    aria_label: element.getAttribute('aria-label'),
                    aria_role: element.getAttribute('role'),
                    possible_interactions: getPossibleInteractions(element),
                    is_interactive: true,
                    is_clickable: element.tagName === 'BUTTON' || element.tagName === 'A' || !!element.onclick,
                    is_editable: element.tagName === 'INPUT' || element.tagName === 'TEXTAREA',
                    accepts_input: element.tagName === 'INPUT' || element.tagName === 'TEXTAREA' || element.tagName === 'SELECT',
                    is_visible: rect.width > 0 && rect.height > 0 && styles.display !== 'none' && styles.visibility !== 'hidden',
                    is_enabled: !element.disabled,
                    is_required: element.required || element.getAttribute('aria-required') === 'true',
                    current_value: element.value || null,
                    default_value: element.defaultValue || null,
                    validation_pattern: validationRules.pattern || null,
                    min_length: validationRules.minLength || null,
                    max_length: validationRules.maxLength || null,
                    min_value: validationRules.min || null,
                    max_value: validationRules.max || null,
                    allowed_values: options,
                    form_id: form?.id || null,
                    label_element_id: labelId,
                    label_text: labelText,
                    position: {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    },
                    z_index: parseInt(styles.zIndex) || 0,
                    is_above_fold: rect.top < window.innerHeight,
                    visual_hierarchy_level: element.parentElement ? Array.from(element.parentElement.children).indexOf(element) : 0,
                    placeholder: element.placeholder || null,
                    title: element.title || null,
                    name: element.name || null,
                    className: element.className || null,
                    href: element.href || null
                });
            });
            
            return elements;
        }
        """
        
        try:
            raw_elements = await page.evaluate(extraction_script)
            
            for raw in raw_elements:
                element = ElementMetadata(
                    element_id=raw['element_id'],
                    selectors=raw['selectors'],
                    test_id=raw.get('test_id'),
                    tag_name=raw['tag_name'],
                    element_type=raw['element_type'],
                    text_content=raw.get('text_content'),
                    aria_label=raw.get('aria_label'),
                    aria_role=raw.get('aria_role'),
                    possible_interactions=raw.get('possible_interactions', []),
                    is_interactive=raw.get('is_interactive', False),
                    is_clickable=raw.get('is_clickable', False),
                    is_editable=raw.get('is_editable', False),
                    accepts_input=raw.get('accepts_input', False),
                    is_visible=raw.get('is_visible', True),
                    is_enabled=raw.get('is_enabled', True),
                    is_required=raw.get('is_required', False),
                    current_value=raw.get('current_value'),
                    validation_pattern=raw.get('validation_pattern'),
                    min_length=raw.get('min_length'),
                    max_length=raw.get('max_length'),
                    min_value=raw.get('min_value'),
                    max_value=raw.get('max_value'),
                    allowed_values=raw.get('allowed_values'),
                    form_id=raw.get('form_id'),
                    label_element_id=raw.get('label_element_id'),
                    position=raw.get('position', {}),
                    z_index=raw.get('z_index'),
                    is_above_fold=raw.get('is_above_fold', True),
                    visual_hierarchy_level=raw.get('visual_hierarchy_level', 0),
                    extraction_strategy='dom',
                    extraction_confidence=0.9,
                    extraction_timestamp=datetime.now().isoformat()
                )
                
                # Generate semantic purpose
                element.semantic_purpose = self._infer_semantic_purpose(element, raw)
                
                # Generate test hints
                element.suggested_test_scenarios = self._generate_test_scenarios(element)
                element.expected_behaviors = self._generate_expected_behaviors(element)
                element.test_priority = self._calculate_test_priority(element)
                
                elements.append(element)
                
        except Exception as e:
            logger.error(f"DOM extraction failed: {e}")
            
        return elements
    
    def _infer_semantic_purpose(self, element: ElementMetadata, raw_data: Dict) -> str:
        """Infer the semantic purpose of an element."""
        # Check for common patterns
        text = (element.text_content or '').lower()
        aria_label = (element.aria_label or '').lower()
        test_id = (element.test_id or '').lower()
        element_id = element.element_id.lower()
        placeholder = (raw_data.get('placeholder') or '').lower()
        name = (raw_data.get('name') or '').lower()
        href = (raw_data.get('href') or '').lower()
        
        combined_text = f"{text} {aria_label} {test_id} {element_id} {placeholder} {name}"
        
        # Authentication patterns
        if any(keyword in combined_text for keyword in ['login', 'signin', 'sign in', 'authenticate', 'logout', 'signout']):
            if element.element_type == 'button':
                return 'authentication_submit'
            elif element.element_type == 'input':
                if 'password' in combined_text:
                    return 'authentication_password'
                elif any(k in combined_text for k in ['email', 'username', 'user']):
                    return 'authentication_username'
        
        # Navigation patterns
        if element.element_type == 'link':
            if 'home' in text:
                return 'navigation_home'
            elif 'about' in text:
                return 'navigation_about'
            elif 'contact' in text:
                return 'navigation_contact'
            elif 'forgot' in text and 'password' in text:
                return 'authentication_recovery'
            elif href.startswith('http'):
                return 'navigation_external'
            else:
                return 'navigation_internal'
        
        # Form patterns
        if element.form_id:
            if 'email' in combined_text or (element.validation_pattern and '@' in element.validation_pattern):
                return 'form_email_input'
            elif 'phone' in combined_text or 'tel' in combined_text:
                return 'form_phone_input'
            elif 'name' in combined_text:
                if 'first' in combined_text:
                    return 'form_firstname_input'
                elif 'last' in combined_text:
                    return 'form_lastname_input'
                else:
                    return 'form_name_input'
            elif 'address' in combined_text:
                return 'form_address_input'
            elif 'city' in combined_text:
                return 'form_city_input'
            elif 'zip' in combined_text or 'postal' in combined_text:
                return 'form_zipcode_input'
            elif element.element_type == 'button' and element.is_clickable:
                if 'submit' in combined_text:
                    return 'form_submit'
                elif 'cancel' in combined_text:
                    return 'form_cancel'
                elif 'reset' in combined_text:
                    return 'form_reset'
        
        # Search patterns
        if 'search' in combined_text:
            if element.element_type == 'input':
                return 'search_input'
            elif element.element_type == 'button':
                return 'search_submit'
        
        # Shopping/E-commerce patterns
        if any(keyword in combined_text for keyword in ['cart', 'basket', 'checkout', 'buy', 'purchase', 'add to']):
            if element.element_type == 'button':
                if 'add' in combined_text:
                    return 'shopping_add_to_cart'
                elif 'checkout' in combined_text:
                    return 'shopping_checkout'
                elif 'buy' in combined_text:
                    return 'shopping_buy_now'
        
        # Social patterns
        if any(keyword in combined_text for keyword in ['share', 'like', 'comment', 'follow', 'tweet']):
            return f"social_{element.element_type}"
        
        # Media patterns
        if element.element_type in ['video', 'image']:
            return f"media_{element.element_type}"
        
        return f"{element.element_type}_generic"
    
    def _generate_test_scenarios(self, element: ElementMetadata) -> List[str]:
        """Generate test scenarios for an element."""
        scenarios = []
        
        if element.element_type == 'input':
            if element.is_required:
                scenarios.append("Test with empty value (required field validation)")
            
            if element.validation_pattern:
                scenarios.append("Test with valid format matching pattern")
                scenarios.append("Test with invalid format not matching pattern")
            
            if element.min_length:
                scenarios.append(f"Test with text shorter than {element.min_length} characters")
                scenarios.append(f"Test with exactly {element.min_length} characters")
            
            if element.max_length:
                scenarios.append(f"Test with text longer than {element.max_length} characters")
                scenarios.append(f"Test with exactly {element.max_length} characters")
            
            if 'email' in element.semantic_purpose:
                scenarios.append("Test with valid email format (user@domain.com)")
                scenarios.append("Test with invalid email format (missing @)")
                scenarios.append("Test with invalid email format (missing domain)")
                scenarios.append("Test with special characters in email")
            
            if 'password' in element.semantic_purpose:
                scenarios.append("Test with weak password (less than 8 chars)")
                scenarios.append("Test with strong password (uppercase, lowercase, numbers, special chars)")
                scenarios.append("Test password visibility toggle if available")
                scenarios.append("Test password copy/paste restrictions")
            
            if 'phone' in element.semantic_purpose:
                scenarios.append("Test with valid phone number format")
                scenarios.append("Test with international phone format")
                scenarios.append("Test with invalid phone number")
        
        elif element.element_type == 'button':
            scenarios.append("Test click interaction")
            scenarios.append("Test keyboard activation (Enter/Space)")
            if element.form_id:
                scenarios.append("Test form submission with valid data")
                scenarios.append("Test form submission with invalid data")
                scenarios.append("Test form validation trigger")
            if not element.is_enabled:
                scenarios.append("Test interaction when disabled")
            scenarios.append("Test double-click prevention")
        
        elif element.element_type == 'dropdown':
            scenarios.append("Test selection of each option")
            scenarios.append("Test default selection")
            scenarios.append("Test keyboard navigation")
            if element.is_required:
                scenarios.append("Test submission without selection")
            if element.allowed_values and len(element.allowed_values) > 0:
                scenarios.append(f"Test with {len(element.allowed_values)} available options")
        
        elif element.element_type == 'checkbox':
            scenarios.append("Test checking and unchecking")
            scenarios.append("Test default state")
            scenarios.append("Test keyboard interaction (Space)")
            if element.is_required:
                scenarios.append("Test submission when unchecked (required)")
        
        elif element.element_type == 'radio':
            scenarios.append("Test selection within radio group")
            scenarios.append("Test mutual exclusivity")
            scenarios.append("Test keyboard navigation (arrow keys)")
        
        elif element.element_type == 'link':
            scenarios.append("Test navigation to correct URL")
            scenarios.append("Test link opens in correct window/tab")
            scenarios.append("Test hover state")
            scenarios.append("Test keyboard navigation (Tab + Enter)")
            
        elif element.element_type == 'textarea':
            scenarios.append("Test multiline input")
            scenarios.append("Test character limit if applicable")
            scenarios.append("Test auto-resize behavior")
            
        return scenarios
    
    def _generate_expected_behaviors(self, element: ElementMetadata) -> List[str]:
        """Generate expected behaviors for an element."""
        behaviors = []
        
        if element.is_required:
            behaviors.append("Shows validation error when empty")
            behaviors.append("Prevents form submission when empty")
        
        if element.validation_pattern:
            behaviors.append("Validates input against pattern in real-time or on blur")
            behaviors.append("Shows error message for invalid format")
            behaviors.append("Clears error when valid input provided")
        
        if element.element_type == 'button' and element.form_id:
            behaviors.append("Submits form when clicked")
            behaviors.append("Shows loading state during submission")
            behaviors.append("Disabled during form processing")
        
        if element.is_clickable:
            behaviors.append("Responds to click events")
            behaviors.append("Shows visual feedback on interaction (hover/active states)")
            behaviors.append("Accessible via keyboard")
        
        if element.accepts_input:
            behaviors.append("Accepts user input")
            behaviors.append("Updates value on input")
            behaviors.append("Triggers input/change events")
            behaviors.append("Supports copy/paste operations")
        
        if element.element_type == 'link':
            behaviors.append("Navigates to target URL")
            behaviors.append("Shows visited state if applicable")
            behaviors.append("Updates browser history")
        
        if not element.is_enabled:
            behaviors.append("Does not respond to user interaction when disabled")
            behaviors.append("Shows disabled visual state")
        
        return behaviors
    
    def _calculate_test_priority(self, element: ElementMetadata) -> int:
        """Calculate test priority (1-5, 5 being highest)."""
        priority = 3  # Default
        
        # Critical functionality gets highest priority
        critical_purposes = ['authentication', 'payment', 'checkout', 'submit', 'buy']
        if any(purpose in element.semantic_purpose for purpose in critical_purposes):
            priority = 5
        
        # Form submission buttons
        elif element.element_type == 'button' and element.form_id:
            priority = 5
        
        # Required fields
        elif element.is_required:
            priority = max(priority, 4)
        
        # Navigation elements
        elif 'navigation' in element.semantic_purpose:
            priority = 4
        
        # Search functionality
        elif 'search' in element.semantic_purpose:
            priority = 4
        
        # Interactive elements
        elif element.is_interactive:
            priority = max(priority, 3)
        
        # Non-interactive elements
        else:
            priority = 2
        
        # Adjust based on visibility
        if not element.is_visible:
            priority = max(1, priority - 2)
        
        # Adjust based on enabled state
        if not element.is_enabled:
            priority = max(1, priority - 1)
        
        return priority


class AccessibilityExtractionStrategy(ExtractionStrategy):
    """Accessibility-focused extraction strategy."""
    
    @property
    def name(self) -> str:
        return "accessibility"
    
    async def extract(self, page: Page) -> List[ElementMetadata]:
        """Extract elements with accessibility focus."""
        elements = []
        
        # Extract accessibility tree
        accessibility_script = """
        () => {
            const elements = [];
            
            // Find all elements with ARIA attributes
            const ariaElements = document.querySelectorAll('[role], [aria-label], [aria-describedby], [aria-labelledby], [tabindex]');
            
            ariaElements.forEach((element, index) => {
                const rect = element.getBoundingClientRect();
                const styles = window.getComputedStyle(element);
                
                // Skip if already processed by DOM strategy (has standard interactive tags)
                const interactiveTags = ['INPUT', 'BUTTON', 'A', 'SELECT', 'TEXTAREA'];
                if (interactiveTags.includes(element.tagName)) {
                    return;
                }
                
                elements.push({
                    element_id: element.id || `aria_${index}`,
                    tag_name: element.tagName.toLowerCase(),
                    aria_role: element.getAttribute('role'),
                    aria_label: element.getAttribute('aria-label'),
                    aria_describedby: element.getAttribute('aria-describedby'),
                    aria_labelledby: element.getAttribute('aria-labelledby'),
                    aria_hidden: element.getAttribute('aria-hidden'),
                    aria_expanded: element.getAttribute('aria-expanded'),
                    aria_selected: element.getAttribute('aria-selected'),
                    aria_checked: element.getAttribute('aria-checked'),
                    aria_disabled: element.getAttribute('aria-disabled'),
                    aria_required: element.getAttribute('aria-required'),
                    tabindex: element.getAttribute('tabindex'),
                    is_focusable: element.tabIndex >= 0,
                    text_content: element.textContent?.trim().substring(0, 200),
                    position: {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    },
                    is_visible: rect.width > 0 && rect.height > 0 && styles.display !== 'none' && styles.visibility !== 'hidden'
                });
            });
            
            return elements;
        }
        """
        
        try:
            raw_elements = await page.evaluate(accessibility_script)
            
            for raw in raw_elements:
                if raw.get('aria_hidden') == 'true':
                    continue  # Skip hidden elements
                
                element = ElementMetadata(
                    element_id=raw['element_id'],
                    selectors={'aria': f"[role='{raw.get('aria_role')}']" if raw.get('aria_role') else f"#{raw['element_id']}"},
                    tag_name=raw['tag_name'],
                    text_content=raw.get('text_content'),
                    aria_label=raw.get('aria_label'),
                    aria_role=raw.get('aria_role'),
                    is_visible=raw.get('is_visible', True),
                    is_enabled=raw.get('aria_disabled') != 'true',
                    is_required=raw.get('aria_required') == 'true',
                    position=raw.get('position', {}),
                    extraction_strategy='accessibility',
                    extraction_confidence=0.85,
                    extraction_timestamp=datetime.now().isoformat()
                )
                
                # Set element type based on role
                element.element_type = self._role_to_element_type(raw.get('aria_role', ''))
                
                # Set interaction capabilities based on role
                element.possible_interactions = self._role_to_interactions(raw.get('aria_role', ''))
                element.is_interactive = len(element.possible_interactions) > 0
                element.is_clickable = 'click' in element.possible_interactions
                
                # Generate test hints
                element.test_priority = 3 if element.is_interactive else 2
                element.suggested_test_scenarios = self._generate_aria_test_scenarios(element)
                
                elements.append(element)
                
        except Exception as e:
            logger.error(f"Accessibility extraction failed: {e}")
            
        return elements
    
    def _role_to_element_type(self, role: str) -> str:
        """Map ARIA role to element type."""
        role_map = {
            'button': 'button',
            'link': 'link',
            'textbox': 'input',
            'checkbox': 'checkbox',
            'radio': 'radio',
            'combobox': 'dropdown',
            'listbox': 'dropdown',
            'navigation': 'navigation',
            'dialog': 'dialog',
            'form': 'form',
            'table': 'table',
            'img': 'image',
            'tab': 'navigation',
            'tablist': 'navigation',
            'menu': 'navigation',
            'menuitem': 'link'
        }
        return role_map.get(role, 'unknown')
    
    def _role_to_interactions(self, role: str) -> List[str]:
        """Map ARIA role to possible interactions."""
        interaction_map = {
            'button': ['click'],
            'link': ['click'],
            'textbox': ['type', 'clear', 'focus'],
            'checkbox': ['check', 'click'],
            'radio': ['check', 'click'],
            'combobox': ['select', 'type'],
            'listbox': ['select'],
            'tab': ['click'],
            'menuitem': ['click']
        }
        return interaction_map.get(role, [])
    
    def _generate_aria_test_scenarios(self, element: ElementMetadata) -> List[str]:
        """Generate test scenarios for ARIA elements."""
        scenarios = []
        
        if element.aria_role:
            scenarios.append(f"Test ARIA role '{element.aria_role}' behavior")
            scenarios.append("Test keyboard accessibility")
            scenarios.append("Test screen reader compatibility")
        
        if element.is_required:
            scenarios.append("Test required field announcement")
        
        if element.aria_label:
            scenarios.append("Test accessible label is announced")
        
        return scenarios


# ============================================================================
# Main Extractor
# ============================================================================

class UnifiedElementExtractor:
    """
    Unified element extractor that coordinates multiple strategies
    and produces optimized output for LLM test generation.
    """
    
    def __init__(self, config: Optional[ExtractionConfig] = None):
        """Initialize extractor with configuration."""
        self.config = config or ExtractionConfig()
        self.strategies = self._initialize_strategies()
        
    def _initialize_strategies(self) -> List[ExtractionStrategy]:
        """Initialize extraction strategies based on configuration."""
        strategies = [DOMExtractionStrategy()]
        
        if self.config.enable_accessibility_extraction:
            strategies.append(AccessibilityExtractionStrategy())
        
        return strategies
    
    async def extract_elements_for_test_generation(self, page: Page) -> List[Dict[str, Any]]:
        """
        Main extraction method that returns list of dictionaries
        optimized for LLM test case generation.
        
        Args:
            page: Playwright page object
            
        Returns:
            List of dictionaries containing comprehensive element metadata
        """
        start_time = time.time()
        
        try:
            # Extract page context
            page_context = await self._extract_page_context(page)
            
            # Run extraction strategies
            if self.config.parallel_strategies:
                all_elements = await self._run_strategies_parallel(page)
            else:
                all_elements = await self._run_strategies_sequential(page)
            
            # Aggregate and deduplicate results
            aggregated_elements = self._aggregate_results(all_elements)
            
            # Filter based on confidence
            filtered_elements = [
                e for e in aggregated_elements 
                if e.extraction_confidence >= self.config.min_confidence
            ]
            
            # Enrich with relationships
            if self.config.extract_relationships:
                self._extract_relationships(filtered_elements)
            
            # Generate test hints
            if self.config.generate_test_hints:
                for element in filtered_elements:
                    self._enhance_test_hints(element)
            
            # Add page context to each element
            for element in filtered_elements:
                element.page_context = page_context
            
            # Sort by test priority
            filtered_elements.sort(key=lambda e: e.test_priority, reverse=True)
            
            # Limit to max elements
            final_elements = filtered_elements[:self.config.max_elements]
            
            # Convert to dictionaries
            result = [element.to_dict() for element in final_elements]
            
            extraction_time = time.time() - start_time
            logger.info(f"Extracted {len(result)} elements in {extraction_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Element extraction failed: {e}")
            raise
    
    async def _extract_page_context(self, page: Page) -> Dict[str, Any]:
        """Extract page-level context information."""
        return {
            'url': page.url,
            'title': await page.title(),
            'viewport': page.viewport_size,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _run_strategies_parallel(self, page: Page) -> Dict[str, List[ElementMetadata]]:
        """Run extraction strategies in parallel."""
        tasks = []
        for strategy in self.strategies:
            tasks.append(strategy.extract(page))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        strategy_results = {}
        for strategy, result in zip(self.strategies, results):
            if isinstance(result, Exception):
                logger.error(f"Strategy {strategy.name} failed: {result}")
                strategy_results[strategy.name] = []
            else:
                strategy_results[strategy.name] = result
        
        return strategy_results
    
    async def _run_strategies_sequential(self, page: Page) -> Dict[str, List[ElementMetadata]]:
        """Run extraction strategies sequentially."""
        strategy_results = {}
        
        for strategy in self.strategies:
            try:
                results = await strategy.extract(page)
                strategy_results[strategy.name] = results
            except Exception as e:
                logger.error(f"Strategy {strategy.name} failed: {e}")
                strategy_results[strategy.name] = []
        
        return strategy_results
    
    def _aggregate_results(self, strategy_results: Dict[str, List[ElementMetadata]]) -> List[ElementMetadata]:
        """Aggregate results from multiple strategies."""
        element_map = {}
        
        for strategy_name, elements in strategy_results.items():
            for element in elements:
                # Use element_id as key for aggregation
                key = element.element_id
                
                if key not in element_map:
                    element_map[key] = element
                else:
                    # Merge information from multiple strategies
                    existing = element_map[key]
                    
                    # Update confidence (weighted average)
                    existing.extraction_confidence = max(
                        existing.extraction_confidence,
                        element.extraction_confidence
                    )
                    
                    # Merge selectors
                    existing.selectors.update(element.selectors)
                    
                    # Merge aria information
                    if element.aria_label and not existing.aria_label:
                        existing.aria_label = element.aria_label
                    if element.aria_role and not existing.aria_role:
                        existing.aria_role = element.aria_role
                    
                    # Merge interaction types
                    existing.possible_interactions = list(set(
                        existing.possible_interactions + element.possible_interactions
                    ))
                    
                    # Merge test scenarios
                    existing.suggested_test_scenarios = list(set(
                        existing.suggested_test_scenarios + element.suggested_test_scenarios
                    ))
                    
                    # Update extraction strategy to show multiple
                    if strategy_name not in existing.extraction_strategy:
                        existing.extraction_strategy += f",{strategy_name}"
        
        return list(element_map.values())
    
    def _extract_relationships(self, elements: List[ElementMetadata]):
        """Extract relationships between elements."""
        element_dict = {e.element_id: e for e in elements}
        
        for element in elements:
            # Find form relationships
            if element.form_id:
                form_elements = [
                    e.element_id for e in elements 
                    if e.form_id == element.form_id and e.element_id != element.element_id
                ]
                element.sibling_element_ids = form_elements[:5]  # Limit to 5
            
            # Find spatial relationships (elements at similar y-position)
            if element.position:
                y_pos = element.position.get('y', 0)
                nearby_elements = [
                    e.element_id for e in elements
                    if e.position and abs(e.position.get('y', 0) - y_pos) < 50
                    and e.element_id != element.element_id
                ]
                if nearby_elements and not element.sibling_element_ids:
                    element.sibling_element_ids = nearby_elements[:3]  # Limit to 3
    
    def _enhance_test_hints(self, element: ElementMetadata):
        """Enhance test generation hints for an element."""
        # Add business context based on semantic purpose
        context_map = {
            'authentication': "User authentication flow",
            'payment': "Payment processing flow",
            'search': "Search functionality",
            'navigation': "Site navigation",
            'form': "Data input form",
            'shopping': "E-commerce functionality",
            'social': "Social interaction features"
        }
        
        for key, context in context_map.items():
            if key in element.semantic_purpose:
                element.business_context = context
                break
        
        # Add common error messages based on element type and purpose
        if 'authentication' in element.semantic_purpose:
            element.error_messages.extend([
                "Invalid credentials",
                "Account locked",
                "Password expired"
            ])
        elif 'email' in element.semantic_purpose:
            element.error_messages.extend([
                "Invalid email format",
                "Email already registered"
            ])
        elif 'required' in str(element.is_required):
            element.error_messages.append("This field is required")
        
        # Enhance expected behaviors
        if element.element_type == 'button' and element.is_enabled:
            if "Changes appearance on hover" not in element.expected_behaviors:
                element.expected_behaviors.append("Changes appearance on hover")
        
        if element.accepts_input and element.is_required:
            if "Shows required indicator" not in element.expected_behaviors:
                element.expected_behaviors.append("Shows required indicator")


# ============================================================================
# Public API
# ============================================================================

async def extract_elements_for_test_generation(
    url: str,
    config: Optional[ExtractionConfig] = None
) -> List[Dict[str, Any]]:
    """
    Main public API for element extraction.
    
    Args:
        url: URL to extract elements from
        config: Optional extraction configuration
        
    Returns:
        List of dictionaries containing element metadata optimized for LLM test generation
    """
    config = config or ExtractionConfig()
    extractor = UnifiedElementExtractor(config)
    
    async with async_playwright() as p:
        # Enhanced stealth configuration
        browser_args = []
        if config.stealth_mode:
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-web-security',
                '--disable-features=CrossSiteDocumentBlockingIfIsolating',
                '--disable-features=CrossSiteDocumentBlockingAlways',
                '--disable-features=IsolateOrigins',
                '--disable-features=site-per-process',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--window-size=1920,1080',
                '--start-maximized'
            ]
        
        browser = await p.chromium.launch(
            headless=False if config.stealth_mode else True,  # Use headful for better stealth
            args=browser_args
        )
        
        # Randomize fingerprint for stealth
        import random
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=random.choice(user_agents) if config.stealth_mode else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation', 'notifications'] if config.stealth_mode else [],
            color_scheme='light',
            device_scale_factor=1.0,
            has_touch=False,
            java_script_enabled=True,
            bypass_csp=True if config.stealth_mode else False,
            ignore_https_errors=True if config.stealth_mode else False
        )
        
        page = await context.new_page()
        
        # Advanced stealth: Override navigator properties and add realistic behavior
        if config.stealth_mode:
            await page.add_init_script("""
                // Override navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override navigator.plugins to look realistic
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin}, description: "Portable Document Format", filename: "internal-pdf-viewer", length: 1, name: "Chrome PDF Plugin"},
                        {0: {type: "application/pdf", suffixes: "pdf", description: "", enabledPlugin: Plugin}, description: "", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", length: 1, name: "Chrome PDF Viewer"},
                        {0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable", enabledPlugin: Plugin}, 1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable", enabledPlugin: Plugin}, description: "", filename: "internal-nacl-plugin", length: 2, name: "Native Client"}
                    ]
                });
                
                // Override navigator.languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Override navigator.platform
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });
                
                // Add chrome object
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Add realistic window properties
                window.navigator.getBattery = () => Promise.resolve({
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: Infinity,
                    level: 1
                });
                
                // Override navigator.hardwareConcurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });
                
                // Override screen properties
                Object.defineProperty(screen, 'availWidth', {
                    get: () => 1920
                });
                Object.defineProperty(screen, 'availHeight', {
                    get: () => 1040
                });
                
                // Add WebGL vendor and renderer
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter(parameter);
                };
                
                // Override toString methods to avoid detection
                const nativeToString = Function.prototype.toString;
                Function.prototype.toString = function() {
                    if (this === window.navigator.permissions.query) {
                        return 'function query() { [native code] }';
                    }
                    return nativeToString.call(this);
                };
                
                // Disable automation indicators
                delete window.navigator.__proto__.webdriver;
                
                // Add realistic mouse movement
                document.addEventListener('DOMContentLoaded', () => {
                    const mouseEvent = new MouseEvent('mousemove', {
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        clientX: Math.random() * window.innerWidth,
                        clientY: Math.random() * window.innerHeight
                    });
                    document.dispatchEvent(mouseEvent);
                });
            """)
            
            # Add random delays for human-like behavior
            await page.wait_for_timeout(random.randint(100, 500))
        
        try:
            # Add pre-navigation for Cloudflare bypass
            if config.stealth_mode:
                # Set additional headers for Cloudflare bypass
                await page.set_extra_http_headers({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                })
                
                # Random delay before navigation
                await page.wait_for_timeout(random.randint(500, 1500))
            
            # Use domcontentloaded instead of networkidle for better compatibility
            # networkidle fails on sites with continuous activity (analytics, polling, etc.)
            wait_strategy = 'domcontentloaded'
            
            # First attempt with stealth mode
            try:
                await page.goto(url, wait_until=wait_strategy, timeout=config.timeout * 1000)
            except Exception as e:
                if config.stealth_mode and 'timeout' in str(e).lower():
                    # Retry with different strategy for problematic sites
                    logger.info(f"Retrying {url} with 'commit' strategy due to timeout")
                    wait_strategy = 'commit'
                    await page.goto(url, wait_until=wait_strategy, timeout=config.timeout * 1000)
                else:
                    raise
            
            # Handle Cloudflare challenge if detected
            if config.stealth_mode:
                page_content = await page.content()
                if 'cf-browser-verification' in page_content or 'checking your browser' in page_content.lower():
                    logger.info("Cloudflare challenge detected, waiting for bypass...")
                    # Wait for Cloudflare to pass
                    await page.wait_for_timeout(5000)
                    
                    # Check if challenge passed
                    try:
                        await page.wait_for_selector('body', timeout=10000)
                    except:
                        logger.warning("Cloudflare bypass may have failed")
                
                # Add human-like scrolling
                await page.evaluate("""
                    window.scrollTo({
                        top: 100,
                        behavior: 'smooth'
                    });
                """)
                await page.wait_for_timeout(random.randint(200, 500))
            results = await extractor.extract_elements_for_test_generation(page)
            return results
        finally:
            await browser.close()