"""
ML Classification Strategy - Machine learning-based element classification
"""

import json
import logging
from typing import Any, Dict, List, Optional
import numpy as np
from playwright.async_api import ElementHandle

from ..advanced_extractor import (
    ElementCandidate,
    ExtractionContext,
    ExtractionStrategy,
    ExtractionStrategyBase,
)

logger = logging.getLogger(__name__)


class MLClassificationStrategy(ExtractionStrategyBase):
    """
    Machine learning strategy for intelligent element classification
    using pre-trained models and feature engineering
    """
    
    def __init__(self, config, ai_service_factory=None):
        super().__init__(config, ai_service_factory)
        
        # Feature extraction configuration
        self.feature_config = {
            'use_visual_features': True,
            'use_text_features': True,
            'use_structural_features': True,
            'use_attribute_features': True
        }
        
        # Element importance weights (simulated ML model weights)
        self.importance_weights = {
            'tag_scores': {
                'button': 0.9,
                'a': 0.85,
                'input': 0.8,
                'select': 0.75,
                'textarea': 0.7,
                'form': 0.65,
                'nav': 0.6,
                'img': 0.4,
                'div': 0.3,
                'span': 0.25
            },
            'attribute_scores': {
                'onclick': 0.8,
                'href': 0.7,
                'type=submit': 0.85,
                'type=button': 0.8,
                'role=button': 0.75,
                'data-action': 0.7,
                'ng-click': 0.7,
                'v-on:click': 0.7
            },
            'position_scores': {
                'above_fold': 0.3,
                'center_aligned': 0.2,
                'prominent_size': 0.25
            }
        }
    
    async def extract(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Extract elements using ML classification"""
        candidates = []
        
        try:
            # Get all potential elements
            elements = await self._get_all_elements(context)
            logger.info(f"ML Strategy: Analyzing {len(elements)} elements")
            
            # Extract features for each element
            element_features = []
            valid_elements = []
            
            for element in elements:
                features = await self._extract_features(element, context)
                if features:
                    element_features.append(features)
                    valid_elements.append(element)
            
            # Classify elements using ML
            predictions = self._classify_elements(element_features)
            
            # Create candidates for high-confidence predictions
            for i, (element, prediction) in enumerate(zip(valid_elements, predictions)):
                if prediction['confidence'] > 0.5:
                    candidate = await self._create_ml_candidate(
                        element,
                        prediction,
                        element_features[i]
                    )
                    if candidate:
                        candidates.append(candidate)
            
            logger.info(f"ML Strategy: Found {len(candidates)} high-confidence candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"ML classification failed: {e}")
            return candidates
    
    def get_confidence_boost(self) -> float:
        """ML classification provides moderate confidence boost"""
        return 0.15
    
    async def _get_all_elements(self, context: ExtractionContext) -> List[ElementHandle]:
        """Get all elements for ML analysis"""
        # Query for all potentially interactive elements
        # Split into individual selectors to avoid issues with complex queries
        selectors = [
            "button",
            "a",
            "input",
            "select",
            "textarea",
            "[onclick]",
            '[role="button"]',
            '[role="link"]',
            "[data-action]",
            "[ng-click]",
            '[v-on\\:click]',
            "form",
            "nav",
            '[role="navigation"]',
            "img[alt]",
            "video",
            "audio",
            '[tabindex]:not([tabindex="-1"])'
        ]
        
        all_elements = []
        element_ids = set()
        
        try:
            # Query each selector separately and merge results
            for selector in selectors:
                try:
                    elements = await context.page.query_selector_all(selector)
                    for element in elements:
                        # Get element's unique identifier to avoid duplicates
                        try:
                            element_id = await element.evaluate('el => el.outerHTML.substring(0, 100)')
                            if element_id not in element_ids:
                                element_ids.add(element_id)
                                all_elements.append(element)
                        except:
                            # If we can't get ID, include the element anyway
                            all_elements.append(element)
                except Exception as e:
                    logger.debug(f"Selector '{selector}' failed: {e}")
                    continue
            
            logger.info(f"ML Strategy: Collected {len(all_elements)} unique elements from {len(selectors)} selectors")
            return all_elements
            
        except Exception as e:
            logger.error(f"Failed to get elements for ML: {e}")
            return []
    
    async def _extract_features(
        self,
        element: ElementHandle,
        context: ExtractionContext
    ) -> Optional[Dict[str, Any]]:
        """Extract ML features from element"""
        try:
            features = {}
            
            # Basic properties
            properties = await element.evaluate('''el => ({
                tag: el.tagName.toLowerCase(),
                text: el.textContent?.trim() || '',
                isVisible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length),
                position: el.getBoundingClientRect(),
                computedStyle: {
                    display: getComputedStyle(el).display,
                    visibility: getComputedStyle(el).visibility,
                    cursor: getComputedStyle(el).cursor,
                    fontSize: parseFloat(getComputedStyle(el).fontSize),
                    fontWeight: getComputedStyle(el).fontWeight,
                    backgroundColor: getComputedStyle(el).backgroundColor,
                    color: getComputedStyle(el).color
                }
            })''')
            
            # Skip invisible elements
            if not properties['isVisible']:
                return None
            
            # Extract different feature types
            if self.feature_config['use_structural_features']:
                features['structural'] = await self._extract_structural_features(element, properties)
            
            if self.feature_config['use_text_features']:
                features['text'] = self._extract_text_features(properties['text'])
            
            if self.feature_config['use_visual_features']:
                features['visual'] = self._extract_visual_features(properties)
            
            if self.feature_config['use_attribute_features']:
                features['attributes'] = await self._extract_attribute_features(element)
            
            features['properties'] = properties
            
            return features
            
        except Exception as e:
            logger.debug(f"Feature extraction failed: {e}")
            return None
    
    async def _extract_structural_features(
        self,
        element: ElementHandle,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract structural features of element"""
        structural = await element.evaluate('''el => {
            // Get element depth in DOM
            let depth = 0;
            let parent = el.parentElement;
            while (parent && depth < 20) {
                depth++;
                parent = parent.parentElement;
            }
            
            // Get sibling information
            const siblings = el.parentElement ? el.parentElement.children : [];
            const siblingIndex = Array.from(siblings).indexOf(el);
            
            // Check if element is in common containers
            const inForm = !!el.closest('form');
            const inNav = !!el.closest('nav');
            const inHeader = !!el.closest('header');
            const inFooter = !!el.closest('footer');
            const inList = !!el.closest('ul, ol');
            const inTable = !!el.closest('table');
            
            // Get child element count
            const childCount = el.children.length;
            const hasText = (el.textContent?.trim().length || 0) > 0;
            
            return {
                depth: depth,
                siblingCount: siblings.length,
                siblingIndex: siblingIndex,
                childCount: childCount,
                hasText: hasText,
                inForm: inForm,
                inNav: inNav,
                inHeader: inHeader,
                inFooter: inFooter,
                inList: inList,
                inTable: inTable
            };
        }''')
        
        return structural
    
    def _extract_text_features(self, text: str) -> Dict[str, Any]:
        """Extract text-based features"""
        text = text.strip()
        
        return {
            'length': len(text),
            'word_count': len(text.split()) if text else 0,
            'has_action_words': any(word in text.lower() for word in [
                'click', 'submit', 'save', 'delete', 'edit', 'view',
                'download', 'upload', 'search', 'login', 'register'
            ]),
            'is_uppercase': text.isupper() if text else False,
            'has_numbers': any(c.isdigit() for c in text),
            'is_single_word': len(text.split()) == 1 if text else False
        }
    
    def _extract_visual_features(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Extract visual features"""
        position = properties['position']
        style = properties['computedStyle']
        viewport = {'width': 1920, 'height': 1080}  # Default viewport
        
        return {
            'position': {
                'x': position['x'],
                'y': position['y'],
                'width': position['width'],
                'height': position['height'],
                'area': position['width'] * position['height'],
                'aspect_ratio': position['width'] / position['height'] if position['height'] > 0 else 0,
                'center_x': position['x'] + position['width'] / 2,
                'center_y': position['y'] + position['height'] / 2,
                'above_fold': position['y'] < viewport['height'],
                'prominence': min(position['width'] * position['height'] / (viewport['width'] * viewport['height']), 1.0)
            },
            'style': {
                'font_size': style['fontSize'],
                'is_bold': style['fontWeight'] == 'bold' or int(style['fontWeight'] or 400) >= 600,
                'has_pointer_cursor': style['cursor'] == 'pointer',
                'is_hidden': style['display'] == 'none' or style['visibility'] == 'hidden'
            }
        }
    
    async def _extract_attribute_features(self, element: ElementHandle) -> Dict[str, Any]:
        """Extract attribute-based features"""
        attributes = await element.evaluate('''el => {
            const attrs = {};
            const importantAttrs = [
                'id', 'class', 'name', 'type', 'role', 'href',
                'onclick', 'data-action', 'data-event', 'data-testid',
                'aria-label', 'title', 'placeholder', 'value'
            ];
            
            for (const attr of importantAttrs) {
                const value = el.getAttribute(attr);
                if (value) {
                    attrs[attr] = value;
                }
            }
            
            // Check for event listeners
            attrs.hasOnclick = !!el.onclick;
            attrs.hasHref = !!el.href;
            
            // Check for data attributes
            attrs.hasDataAttributes = Array.from(el.attributes).some(
                attr => attr.name.startsWith('data-')
            );
            
            return attrs;
        }''')
        
        return attributes
    
    def _classify_elements(self, features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify elements using ML (simulated with rule-based scoring)"""
        predictions = []
        
        for features in features_list:
            # Calculate importance score
            score = 0.0
            
            # Tag-based scoring
            tag = features['properties']['tag']
            score += self.importance_weights['tag_scores'].get(tag, 0.1)
            
            # Attribute-based scoring
            attrs = features.get('attributes', {})
            for attr_pattern, attr_score in self.importance_weights['attribute_scores'].items():
                if '=' in attr_pattern:
                    attr_name, attr_value = attr_pattern.split('=')
                    if attrs.get(attr_name) == attr_value:
                        score += attr_score
                else:
                    if attr_pattern in attrs:
                        score += attr_score
            
            # Position-based scoring
            visual = features.get('visual', {})
            if visual.get('position', {}).get('above_fold'):
                score += self.importance_weights['position_scores']['above_fold']
            
            if visual.get('position', {}).get('prominence', 0) > 0.01:
                score += self.importance_weights['position_scores']['prominent_size']
            
            # Text-based scoring
            text_features = features.get('text', {})
            if text_features.get('has_action_words'):
                score += 0.2
            
            # Structural scoring
            structural = features.get('structural', {})
            if structural.get('inForm'):
                score += 0.1
            if structural.get('inNav'):
                score += 0.1
            
            # Normalize score to confidence
            confidence = min(score, 1.0)
            
            # Predict element type based on features
            element_type = self._predict_element_type(features)
            
            predictions.append({
                'confidence': confidence,
                'element_type': element_type,
                'importance_score': score,
                'is_interactive': confidence > 0.5
            })
        
        return predictions
    
    def _predict_element_type(self, features: Dict[str, Any]) -> str:
        """Predict element type from features"""
        tag = features['properties']['tag']
        attrs = features.get('attributes', {})
        
        # Direct mappings
        if tag == 'button' or attrs.get('type') == 'button':
            return 'button'
        elif tag == 'a' and 'href' in attrs:
            return 'link'
        elif tag == 'input':
            input_type = attrs.get('type', 'text')
            if input_type in ['submit', 'button']:
                return 'button'
            elif input_type in ['text', 'email', 'password', 'search']:
                return 'text_input'
            elif input_type == 'checkbox':
                return 'checkbox'
            elif input_type == 'radio':
                return 'radio'
            else:
                return 'input'
        elif tag == 'select':
            return 'dropdown'
        elif tag == 'textarea':
            return 'textarea'
        elif tag == 'form':
            return 'form'
        elif tag == 'nav' or attrs.get('role') == 'navigation':
            return 'navigation'
        else:
            # Check for interactive divs/spans
            if attrs.get('onclick') or attrs.get('role') == 'button':
                return 'button'
            elif attrs.get('role') == 'link':
                return 'link'
            else:
                return 'other'
    
    async def _create_ml_candidate(
        self,
        element: ElementHandle,
        prediction: Dict[str, Any],
        features: Dict[str, Any]
    ) -> Optional[ElementCandidate]:
        """Create candidate from ML prediction"""
        try:
            # Generate ML-based selectors
            selectors = await self._generate_ml_selectors(element, features, prediction)
            
            # Get attributes
            attributes = await element.evaluate('''el => {
                const attrs = {};
                for (const attr of el.attributes) {
                    attrs[attr.name] = attr.value;
                }
                return attrs;
            }''')
            
            # Calculate final confidence
            confidence = prediction['confidence']
            
            # Boost confidence if multiple signals agree
            if len(selectors) > 2:
                confidence = min(confidence * 1.1, 0.95)
            
            candidate = ElementCandidate(
                element=element,
                confidence=confidence,
                strategies_used={ExtractionStrategy.ML_CLASSIFICATION},
                attributes=attributes,
                selectors=selectors,
                metadata={
                    'ml_prediction': prediction,
                    'ml_features': {
                        'structural': features.get('structural', {}),
                        'visual': features.get('visual', {}),
                        'text': features.get('text', {}),
                        'tag': features['properties']['tag']
                    },
                    'element_type': prediction['element_type'],
                    'importance_score': prediction['importance_score']
                }
            )
            
            return candidate
            
        except Exception as e:
            logger.debug(f"Failed to create ML candidate: {e}")
            return None
    
    async def _generate_ml_selectors(
        self,
        element: ElementHandle,
        features: Dict[str, Any],
        prediction: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate selectors based on ML analysis"""
        selectors = []
        attrs = features.get('attributes', {})
        
        # High-confidence selectors based on ML insights
        if attrs.get('id'):
            selectors.append({
                'type': 'css',
                'value': f"#{attrs['id']}",
                'score': 0.95,
                'strategy': 'ml-id'
            })
        
        if attrs.get('data-testid'):
            selectors.append({
                'type': 'css',
                'value': f"[data-testid='{attrs['data-testid']}']",
                'score': 0.9,
                'strategy': 'ml-testid'
            })
        
        # Type-specific selectors
        tag = features['properties']['tag']
        if prediction['element_type'] == 'button':
            if features['properties']['text']:
                selectors.append({
                    'type': 'xpath',
                    'value': f"//button[contains(text(), '{features['properties']['text'][:20]}')]",
                    'score': 0.7,
                    'strategy': 'ml-text'
                })
        
        # Feature-based selector
        if features.get('structural', {}).get('inForm') and attrs.get('name'):
            selectors.append({
                'type': 'css',
                'value': f"form {tag}[name='{attrs['name']}']",
                'score': 0.75,
                'strategy': 'ml-context'
            })
        
        # Visual prominence selector
        if features.get('visual', {}).get('position', {}).get('prominence', 0) > 0.05:
            # Generate selector for prominent elements
            classes = attrs.get('class', '').split()
            if classes:
                primary_class = classes[0]
                selectors.append({
                    'type': 'css',
                    'value': f".{primary_class}",
                    'score': 0.5,
                    'strategy': 'ml-visual'
                })
        
        return selectors