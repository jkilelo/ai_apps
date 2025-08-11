"""
Semantic Understanding Strategy - NLP and AI-based element understanding
"""

import logging
import re
from typing import Any, Dict, List, Optional
from playwright.async_api import ElementHandle

from ..advanced_extractor import (
    ElementCandidate,
    ExtractionContext,
    ExtractionStrategy,
    ExtractionStrategyBase,
)

logger = logging.getLogger(__name__)


class SemanticUnderstandingStrategy(ExtractionStrategyBase):
    """
    Semantic understanding strategy using NLP and AI to understand
    element purpose and context
    """
    
    def __init__(self, config, ai_service_factory=None):
        super().__init__(config, ai_service_factory)
        
        # Semantic patterns for element identification
        self.action_keywords = {
            'submit': ['submit', 'send', 'save', 'confirm', 'ok', 'apply', 'create', 'update'],
            'cancel': ['cancel', 'close', 'dismiss', 'back', 'return'],
            'delete': ['delete', 'remove', 'trash', 'discard'],
            'navigation': ['next', 'previous', 'prev', 'forward', 'back', 'home', 'menu'],
            'auth': ['login', 'signin', 'logout', 'signout', 'register', 'signup'],
            'search': ['search', 'find', 'filter', 'query'],
            'edit': ['edit', 'modify', 'change', 'update'],
            'view': ['view', 'show', 'display', 'details', 'more'],
            'download': ['download', 'export', 'save as'],
            'upload': ['upload', 'import', 'attach', 'browse']
        }
        
        # Input field patterns
        self.input_patterns = {
            'email': [r'email', r'e-mail', r'mail'],
            'password': [r'password', r'pwd', r'passcode'],
            'username': [r'username', r'user', r'login'],
            'phone': [r'phone', r'tel', r'mobile', r'contact'],
            'name': [r'name', r'full.?name', r'first.?name', r'last.?name'],
            'address': [r'address', r'street', r'city', r'zip', r'postal'],
            'date': [r'date', r'calendar', r'when', r'schedule'],
            'quantity': [r'quantity', r'qty', r'amount', r'number'],
            'search': [r'search', r'find', r'query'],
            'comment': [r'comment', r'message', r'feedback', r'note']
        }
        
        # Form field relationships
        self.label_patterns = [
            r'for\s*=\s*["\']([^"\']+)["\']',  # label for attribute
            r'aria-labelledby\s*=\s*["\']([^"\']+)["\']',
            r'aria-describedby\s*=\s*["\']([^"\']+)["\']'
        ]
    
    async def extract(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Extract elements using semantic understanding"""
        candidates = []
        
        try:
            # Phase 1: Extract elements with semantic significance
            semantic_elements = await self._extract_semantic_elements(context)
            
            # Phase 2: Analyze context and relationships
            for element in semantic_elements:
                candidate = await self._analyze_semantic_element(element, context)
                if candidate:
                    candidates.append(candidate)
            
            # Phase 3: Find form field relationships
            form_candidates = await self._analyze_form_semantics(context)
            candidates.extend(form_candidates)
            
            # Phase 4: AI-enhanced understanding (if available)
            if self.ai_service_factory:
                ai_candidates = await self._ai_semantic_analysis(context)
                candidates.extend(ai_candidates)
            
            logger.info(f"Semantic Strategy: Found {len(candidates)} candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Semantic understanding failed: {e}")
            return candidates
    
    def get_confidence_boost(self) -> float:
        """Semantic understanding provides good confidence boost"""
        return 0.25
    
    async def _extract_semantic_elements(self, context: ExtractionContext) -> List[ElementHandle]:
        """Extract elements with semantic significance"""
        elements = []
        
        # Elements with explicit semantic meaning
        semantic_selectors = [
            # Buttons with meaningful text
            'button:not(:empty)',
            'input[type="submit"]',
            'input[type="button"]',
            '[role="button"]:not(:empty)',
            
            # Links with text
            'a[href]:not(:empty)',
            '[role="link"]:not(:empty)',
            
            # Form elements with labels
            'label > input',
            'label > select',
            'label > textarea',
            'input[aria-label]',
            'input[placeholder]',
            'select[aria-label]',
            'textarea[aria-label]',
            
            # Navigation elements
            'nav a',
            'nav button',
            '[role="navigation"] a',
            '[role="menuitem"]',
            '[role="tab"]',
            
            # Content with actions
            '[onclick]:not(:empty)',
            '[data-action]',
            '[data-event]'
        ]
        
        for selector in semantic_selectors:
            try:
                found_elements = await context.page.query_selector_all(selector)
                elements.extend(found_elements)
            except Exception:
                continue
        
        # Deduplicate
        unique_elements = []
        seen = set()
        
        for element in elements:
            try:
                # Create unique key
                tag = await element.evaluate('el => el.tagName')
                text = await element.text_content()
                key = f"{tag}_{text[:50] if text else 'empty'}"
                
                if key not in seen:
                    seen.add(key)
                    unique_elements.append(element)
            except:
                continue
        
        return unique_elements
    
    async def _analyze_semantic_element(
        self,
        element: ElementHandle,
        context: ExtractionContext
    ) -> Optional[ElementCandidate]:
        """Analyze element for semantic meaning"""
        try:
            # Get element text and context
            text = await element.text_content() or ""
            text = text.strip().lower()
            
            # Get surrounding context
            context_text = await self._get_element_context(element)
            
            # Analyze semantic purpose
            semantic_type = self._classify_semantic_type(text, context_text)
            
            if not semantic_type:
                return None
            
            # Get element properties
            properties = await element.evaluate('''el => ({
                tag: el.tagName.toLowerCase(),
                type: el.type || null,
                role: el.getAttribute('role'),
                ariaLabel: el.getAttribute('aria-label'),
                placeholder: el.placeholder || null,
                title: el.title || null,
                value: el.value || null,
                href: el.href || null
            })''')
            
            # Generate semantic selectors
            selectors = await self._generate_semantic_selectors(element, text, properties)
            
            # Calculate confidence
            confidence = self._calculate_semantic_confidence(semantic_type, text, context_text)
            
            # Get attributes
            attributes = await element.evaluate('''el => {
                const attrs = {};
                for (const attr of el.attributes) {
                    attrs[attr.name] = attr.value;
                }
                return attrs;
            }''')
            
            candidate = ElementCandidate(
                element=element,
                confidence=confidence,
                strategies_used={ExtractionStrategy.SEMANTIC_UNDERSTANDING},
                attributes=attributes,
                selectors=selectors,
                metadata={
                    'semantic_type': semantic_type,
                    'semantic_text': text,
                    'context_text': context_text,
                    'element_properties': properties
                }
            )
            
            return candidate
            
        except Exception as e:
            logger.debug(f"Failed to analyze semantic element: {e}")
            return None
    
    async def _get_element_context(self, element: ElementHandle) -> str:
        """Get surrounding context of element"""
        try:
            context = await element.evaluate('''el => {
                let context = '';
                
                // Get parent text
                const parent = el.parentElement;
                if (parent) {
                    const parentText = parent.textContent || '';
                    context += parentText.substring(0, 100);
                }
                
                // Get label if exists
                const labels = el.labels || [];
                for (const label of labels) {
                    context += ' ' + (label.textContent || '');
                }
                
                // Get aria-describedby text
                const describedBy = el.getAttribute('aria-describedby');
                if (describedBy) {
                    const descriptor = document.getElementById(describedBy);
                    if (descriptor) {
                        context += ' ' + (descriptor.textContent || '');
                    }
                }
                
                // Get nearby headings
                let sibling = el.previousElementSibling;
                while (sibling && !sibling.matches('h1,h2,h3,h4,h5,h6')) {
                    sibling = sibling.previousElementSibling;
                }
                if (sibling) {
                    context += ' ' + (sibling.textContent || '');
                }
                
                return context.trim();
            }''')
            
            return context
            
        except Exception:
            return ""
    
    def _classify_semantic_type(self, text: str, context: str) -> Optional[str]:
        """Classify semantic type of element"""
        combined_text = f"{text} {context}".lower()
        
        # Check against action keywords
        for action_type, keywords in self.action_keywords.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return f"action_{action_type}"
        
        # Check against input patterns
        for input_type, patterns in self.input_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    return f"input_{input_type}"
        
        # General classification
        if any(word in combined_text for word in ['click', 'tap', 'press']):
            return "interactive"
        
        if any(word in combined_text for word in ['enter', 'input', 'type', 'fill']):
            return "input_field"
        
        return None
    
    async def _generate_semantic_selectors(
        self,
        element: ElementHandle,
        text: str,
        properties: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate selectors based on semantic properties"""
        selectors = []
        
        # Text-based selector for buttons and links
        if text and properties['tag'] in ['button', 'a']:
            selectors.append({
                'type': 'xpath',
                'value': f"//{properties['tag']}[contains(text(), '{text[:30]}')]",
                'score': 0.7,
                'strategy': 'semantic-text'
            })
        
        # Aria-label selector
        if properties.get('ariaLabel'):
            selectors.append({
                'type': 'css',
                'value': f"[aria-label='{properties['ariaLabel']}']",
                'score': 0.8,
                'strategy': 'semantic-aria'
            })
        
        # Placeholder selector for inputs
        if properties.get('placeholder'):
            selectors.append({
                'type': 'css',
                'value': f"[placeholder='{properties['placeholder']}']",
                'score': 0.6,
                'strategy': 'semantic-placeholder'
            })
        
        # Role-based selector
        if properties.get('role'):
            selectors.append({
                'type': 'css',
                'value': f"[role='{properties['role']}']",
                'score': 0.5,
                'strategy': 'semantic-role'
            })
        
        return selectors
    
    def _calculate_semantic_confidence(
        self,
        semantic_type: str,
        text: str,
        context: str
    ) -> float:
        """Calculate confidence based on semantic clarity"""
        confidence = 0.6  # Base confidence
        
        # Boost for clear action types
        if semantic_type.startswith('action_'):
            confidence += 0.2
        
        # Boost for specific input types
        if semantic_type.startswith('input_') and semantic_type != 'input_field':
            confidence += 0.15
        
        # Boost for rich context
        if len(context) > 50:
            confidence += 0.1
        
        # Boost for clear, meaningful text
        if len(text) > 3 and not text.isdigit():
            confidence += 0.05
        
        return min(confidence, 0.95)
    
    async def _analyze_form_semantics(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Analyze form fields and their semantic relationships"""
        candidates = []
        
        try:
            # Find all forms
            forms = await context.page.query_selector_all('form')
            
            for form in forms:
                # Analyze form purpose
                form_purpose = await self._analyze_form_purpose(form)
                
                # Get form fields
                fields = await form.query_selector_all('input, select, textarea')
                
                for field in fields:
                    # Find associated label
                    label_text = await self._find_field_label(field)
                    
                    if label_text:
                        candidate = await self._create_form_field_candidate(
                            field,
                            label_text,
                            form_purpose
                        )
                        if candidate:
                            candidates.append(candidate)
            
            # Also find fields outside forms but with labels
            labeled_fields = await context.page.query_selector_all(
                'label input, label select, label textarea'
            )
            
            for field in labeled_fields:
                label_text = await self._find_field_label(field)
                if label_text:
                    candidate = await self._create_form_field_candidate(
                        field,
                        label_text,
                        'standalone'
                    )
                    if candidate:
                        candidates.append(candidate)
            
        except Exception as e:
            logger.error(f"Form semantic analysis failed: {e}")
        
        return candidates
    
    async def _analyze_form_purpose(self, form: ElementHandle) -> str:
        """Analyze the purpose of a form"""
        try:
            # Get form text content
            form_text = await form.text_content() or ""
            form_text = form_text.lower()
            
            # Check for common form types
            if any(word in form_text for word in ['login', 'sign in', 'authenticate']):
                return 'login'
            elif any(word in form_text for word in ['register', 'sign up', 'create account']):
                return 'registration'
            elif any(word in form_text for word in ['search', 'find', 'query']):
                return 'search'
            elif any(word in form_text for word in ['contact', 'message', 'feedback']):
                return 'contact'
            elif any(word in form_text for word in ['payment', 'checkout', 'purchase']):
                return 'payment'
            else:
                return 'general'
                
        except Exception:
            return 'unknown'
    
    async def _find_field_label(self, field: ElementHandle) -> Optional[str]:
        """Find label associated with a field"""
        try:
            label_text = await field.evaluate('''field => {
                // Method 1: Direct label
                const labels = field.labels;
                if (labels && labels.length > 0) {
                    return labels[0].textContent?.trim();
                }
                
                // Method 2: Aria-label
                const ariaLabel = field.getAttribute('aria-label');
                if (ariaLabel) {
                    return ariaLabel;
                }
                
                // Method 3: Placeholder
                if (field.placeholder) {
                    return field.placeholder;
                }
                
                // Method 4: Previous sibling text
                let sibling = field.previousElementSibling;
                while (sibling) {
                    const text = sibling.textContent?.trim();
                    if (text && text.length > 2) {
                        return text;
                    }
                    sibling = sibling.previousElementSibling;
                }
                
                // Method 5: Parent label
                const parent = field.parentElement;
                if (parent && parent.tagName === 'LABEL') {
                    return parent.textContent?.trim();
                }
                
                return null;
            }''')
            
            return label_text
            
        except Exception:
            return None
    
    async def _create_form_field_candidate(
        self,
        field: ElementHandle,
        label_text: str,
        form_purpose: str
    ) -> Optional[ElementCandidate]:
        """Create candidate for form field with semantic understanding"""
        try:
            # Classify field type based on label
            field_type = self._classify_field_type(label_text)
            
            # Get field properties
            properties = await field.evaluate('''field => ({
                tag: field.tagName.toLowerCase(),
                type: field.type || null,
                name: field.name || null,
                id: field.id || null,
                required: field.required || false,
                pattern: field.pattern || null
            })''')
            
            # Generate semantic selectors
            selectors = []
            
            if properties['id']:
                selectors.append({
                    'type': 'css',
                    'value': f"#{properties['id']}",
                    'score': 0.9,
                    'strategy': 'semantic-id'
                })
            
            if properties['name']:
                selectors.append({
                    'type': 'css',
                    'value': f"[name='{properties['name']}']",
                    'score': 0.7,
                    'strategy': 'semantic-name'
                })
            
            # Label-based selector
            selectors.append({
                'type': 'xpath',
                'value': f"//label[contains(text(), '{label_text[:20]}')]//input",
                'score': 0.6,
                'strategy': 'semantic-label'
            })
            
            # Get attributes
            attributes = await field.evaluate('''el => {
                const attrs = {};
                for (const attr of el.attributes) {
                    attrs[attr.name] = attr.value;
                }
                return attrs;
            }''')
            
            candidate = ElementCandidate(
                element=field,
                confidence=0.85,  # High confidence for labeled fields
                strategies_used={ExtractionStrategy.SEMANTIC_UNDERSTANDING},
                attributes=attributes,
                selectors=selectors,
                metadata={
                    'semantic_type': f"form_field_{field_type}",
                    'label_text': label_text,
                    'form_purpose': form_purpose,
                    'field_properties': properties
                }
            )
            
            return candidate
            
        except Exception as e:
            logger.debug(f"Failed to create form field candidate: {e}")
            return None
    
    def _classify_field_type(self, label_text: str) -> str:
        """Classify field type based on label text"""
        label_lower = label_text.lower()
        
        for field_type, patterns in self.input_patterns.items():
            for pattern in patterns:
                if re.search(pattern, label_lower, re.IGNORECASE):
                    return field_type
        
        return 'general'
    
    async def _ai_semantic_analysis(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Use AI service for advanced semantic analysis"""
        candidates = []
        
        if not self.ai_service_factory:
            return candidates
        
        try:
            # Get page content for AI analysis
            page_content = await context.page.content()
            
            # Prepare AI prompt
            ai_prompt = self._prepare_ai_prompt(page_content)
            
            # Get AI service
            ai_service = await self.ai_service_factory.get_service('openai')
            if not ai_service:
                return candidates
            
            # Analyze with AI
            ai_response = await ai_service.analyze_elements(ai_prompt)
            
            if ai_response and ai_response.get('success'):
                # Process AI insights
                insights = ai_response.get('analysis', {})
                
                # Create candidates based on AI insights
                # (This would need to be implemented based on actual AI response format)
                
        except Exception as e:
            logger.error(f"AI semantic analysis failed: {e}")
        
        return candidates
    
    def _prepare_ai_prompt(self, page_content: str) -> str:
        """Prepare prompt for AI analysis"""
        # Truncate content to reasonable length
        max_length = 5000
        if len(page_content) > max_length:
            page_content = page_content[:max_length] + "..."
        
        return f"""
        Analyze this web page HTML and identify interactive elements with their semantic purpose:
        
        {page_content}
        
        For each interactive element found, provide:
        1. Element selector (CSS or XPath)
        2. Semantic purpose (what the element does)
        3. User-facing label or text
        4. Importance level (high/medium/low)
        5. Suggested test scenarios
        
        Focus on buttons, links, form fields, and other interactive elements.
        """