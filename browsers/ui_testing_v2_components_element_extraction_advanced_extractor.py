"""
Advanced Element Extraction Module
The most comprehensive web element extractor combining cutting-edge techniques
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urlparse

import numpy as np
from playwright.async_api import Browser, BrowserContext, ElementHandle, Page

from ...core.config import Config
from ...models.database import ExtractedElement, ElementInteractionType
from ...models.common import ElementType
from ...services.ai_services import AIServiceFactory
from ...services.cache import CacheService

logger = logging.getLogger(__name__)


class ExtractionStrategy(str, Enum):
    """Available extraction strategies"""
    DOM_ANALYSIS = "dom_analysis"
    VISUAL_DETECTION = "visual_detection"
    SEMANTIC_UNDERSTANDING = "semantic_understanding"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    ACCESSIBILITY_MAPPING = "accessibility_mapping"
    SHADOW_DOM_TRAVERSAL = "shadow_dom_traversal"
    DYNAMIC_CONTENT_TRACKING = "dynamic_content_tracking"
    ML_CLASSIFICATION = "ml_classification"
    RELATIONSHIP_MAPPING = "relationship_mapping"


class ConfidenceLevel(float, Enum):
    """Confidence levels for element detection"""
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


@dataclass
class ExtractionContext:
    """Context for element extraction"""
    url: str
    page: Page
    browser_context: BrowserContext
    viewport_size: Dict[str, int]
    device_info: Dict[str, Any]
    session_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ElementCandidate:
    """Candidate element during extraction process"""
    element: ElementHandle
    confidence: float
    strategies_used: Set[ExtractionStrategy]
    attributes: Dict[str, Any]
    selectors: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def merge_confidence(self, new_confidence: float, strategy: ExtractionStrategy):
        """Merge confidence scores from multiple strategies"""
        # Weighted average with strategy count
        total_strategies = len(self.strategies_used) + 1
        self.confidence = (self.confidence * len(self.strategies_used) + new_confidence) / total_strategies
        self.strategies_used.add(strategy)


class ExtractionStrategyBase(ABC):
    """Base class for extraction strategies"""
    
    def __init__(self, config: Config, ai_service_factory: Optional[AIServiceFactory] = None):
        self.config = config
        self.ai_service_factory = ai_service_factory
        self.strategy_name = self.__class__.__name__
        
    @abstractmethod
    async def extract(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Extract elements using this strategy"""
        pass
    
    @abstractmethod
    def get_confidence_boost(self) -> float:
        """Get confidence boost factor for this strategy"""
        pass
    
    async def validate_element(self, element: ElementHandle) -> bool:
        """Validate if element should be included"""
        try:
            # Check if element is visible
            is_visible = await element.is_visible()
            if not is_visible and not await self._is_hidden_but_important(element):
                return False
            
            # Check if element has minimum size
            box = await element.bounding_box()
            if box and (box['width'] < 1 or box['height'] < 1):
                return False
            
            return True
        except Exception:
            return False
    
    async def _is_hidden_but_important(self, element: ElementHandle) -> bool:
        """Check if hidden element is still important (e.g., for accessibility)"""
        try:
            # Check for screen reader only elements
            aria_hidden = await element.get_attribute('aria-hidden')
            if aria_hidden == 'false':
                return True
            
            # Check for visually hidden but accessible elements
            classes = await element.get_attribute('class') or ''
            if any(cls in classes for cls in ['sr-only', 'visually-hidden', 'screen-reader-only']):
                return True
            
            return False
        except Exception:
            return False


class AdvancedElementExtractor:
    """
    The most advanced element extractor combining multiple strategies
    and cutting-edge techniques for comprehensive element detection
    """
    
    def __init__(
        self,
        config: Config,
        ai_service_factory: AIServiceFactory,
        cache_service: CacheService
    ):
        self.config = config
        self.ai_service_factory = ai_service_factory
        self.cache_service = cache_service
        
        # Initialize strategies
        self.strategies: Dict[ExtractionStrategy, ExtractionStrategyBase] = {}
        self._initialize_strategies()
        
        # Extraction state
        self._extraction_stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'strategies_performance': {strategy: {'used': 0, 'successful': 0} for strategy in ExtractionStrategy}
        }
        
        logger.info("Advanced Element Extractor initialized with %d strategies", len(self.strategies))
    
    def _initialize_strategies(self):
        """Initialize all extraction strategies"""
        # Import strategy implementations
        from .strategies.dom_strategy import DOMAnalysisStrategy
        from .strategies.visual_strategy import VisualDetectionStrategy
        from .strategies.semantic_strategy import SemanticUnderstandingStrategy
        from .strategies.behavioral_strategy import BehavioralAnalysisStrategy
        from .strategies.accessibility_strategy import AccessibilityMappingStrategy
        from .strategies.shadow_dom_strategy import ShadowDOMTraversalStrategy
        from .strategies.dynamic_strategy import DynamicContentTrackingStrategy
        from .strategies.ml_strategy import MLClassificationStrategy
        from .strategies.relationship_strategy import RelationshipMappingStrategy
        
        # Initialize each strategy
        strategy_classes = {
            ExtractionStrategy.DOM_ANALYSIS: DOMAnalysisStrategy,
            ExtractionStrategy.VISUAL_DETECTION: VisualDetectionStrategy,
            ExtractionStrategy.SEMANTIC_UNDERSTANDING: SemanticUnderstandingStrategy,
            ExtractionStrategy.BEHAVIORAL_ANALYSIS: BehavioralAnalysisStrategy,
            ExtractionStrategy.ACCESSIBILITY_MAPPING: AccessibilityMappingStrategy,
            ExtractionStrategy.SHADOW_DOM_TRAVERSAL: ShadowDOMTraversalStrategy,
            ExtractionStrategy.DYNAMIC_CONTENT_TRACKING: DynamicContentTrackingStrategy,
            ExtractionStrategy.ML_CLASSIFICATION: MLClassificationStrategy,
            ExtractionStrategy.RELATIONSHIP_MAPPING: RelationshipMappingStrategy
        }
        
        for strategy_type, strategy_class in strategy_classes.items():
            try:
                self.strategies[strategy_type] = strategy_class(self.config, self.ai_service_factory)
                logger.info(f"Initialized strategy: {strategy_type.value}")
            except Exception as e:
                logger.error(f"Failed to initialize strategy {strategy_type.value}: {e}")
    
    async def extract_elements(
        self,
        url: str,
        page: Page,
        browser_context: BrowserContext,
        session_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> List[ExtractedElement]:
        """
        Extract elements from a web page using all available strategies
        
        Args:
            url: The URL of the page
            page: Playwright page object
            browser_context: Browser context
            session_id: Session ID for tracking
            options: Extraction options
            
        Returns:
            List of extracted elements with comprehensive metadata
        """
        start_time = datetime.now(timezone.utc)
        self._extraction_stats['total_extractions'] += 1
        
        try:
            # Create extraction context
            viewport = await page.viewport_size()
            context = ExtractionContext(
                url=url,
                page=page,
                browser_context=browser_context,
                viewport_size=viewport or {'width': 1920, 'height': 1080},
                device_info=await self._get_device_info(page),
                session_id=session_id,
                options=options or {}
            )
            
            logger.info(f"Starting advanced element extraction for {url}")
            
            # Phase 1: Parallel strategy execution
            extraction_tasks = []
            enabled_strategies = self._get_enabled_strategies(options)
            
            for strategy_type in enabled_strategies:
                if strategy_type in self.strategies:
                    strategy = self.strategies[strategy_type]
                    extraction_tasks.append(self._execute_strategy(strategy, context, strategy_type))
            
            # Execute all strategies in parallel
            strategy_results = await asyncio.gather(*extraction_tasks, return_exceptions=True)
            
            # Phase 2: Merge and deduplicate results
            all_candidates: Dict[str, ElementCandidate] = {}
            
            for strategy_type, result in zip(enabled_strategies, strategy_results):
                if isinstance(result, Exception):
                    logger.error(f"Strategy {strategy_type.value} failed: {result}")
                    self._extraction_stats['strategies_performance'][strategy_type]['used'] += 1
                    continue
                
                self._extraction_stats['strategies_performance'][strategy_type]['used'] += 1
                self._extraction_stats['strategies_performance'][strategy_type]['successful'] += 1
                
                # Merge candidates
                for candidate in result:
                    element_id = await self._generate_element_id(candidate)
                    
                    if element_id in all_candidates:
                        # Merge with existing candidate
                        existing = all_candidates[element_id]
                        existing.merge_confidence(candidate.confidence, strategy_type)
                        existing.attributes.update(candidate.attributes)
                        existing.selectors.extend(candidate.selectors)
                        existing.metadata.update(candidate.metadata)
                    else:
                        all_candidates[element_id] = candidate
            
            # Phase 3: Filter and rank candidates
            filtered_candidates = await self._filter_and_rank_candidates(list(all_candidates.values()), context)
            
            # Phase 4: Convert to ExtractedElement objects
            extracted_elements = await self._convert_to_extracted_elements(filtered_candidates, context)
            
            # Phase 5: Post-processing
            extracted_elements = await self._post_process_elements(extracted_elements, context)
            
            # Update statistics
            self._extraction_stats['successful_extractions'] += 1
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            logger.info(
                f"Extraction completed: {len(extracted_elements)} elements found in {duration:.2f}s "
                f"using {len(enabled_strategies)} strategies"
            )
            
            return extracted_elements
            
        except Exception as e:
            logger.error(f"Element extraction failed: {e}")
            self._extraction_stats['failed_extractions'] += 1
            raise
    
    async def _execute_strategy(
        self,
        strategy: ExtractionStrategyBase,
        context: ExtractionContext,
        strategy_type: ExtractionStrategy
    ) -> List[ElementCandidate]:
        """Execute a single extraction strategy"""
        try:
            logger.debug(f"Executing strategy: {strategy_type.value}")
            candidates = await strategy.extract(context)
            logger.debug(f"Strategy {strategy_type.value} found {len(candidates)} candidates")
            return candidates
        except Exception as e:
            logger.error(f"Strategy {strategy_type.value} failed: {e}")
            raise
    
    def _get_enabled_strategies(self, options: Optional[Dict[str, Any]]) -> List[ExtractionStrategy]:
        """Get list of enabled strategies based on options"""
        if not options:
            return list(ExtractionStrategy)
        
        # Check for specific strategy configuration
        if 'strategies' in options:
            enabled = []
            for strategy_name in options['strategies']:
                try:
                    enabled.append(ExtractionStrategy(strategy_name))
                except ValueError:
                    logger.warning(f"Unknown strategy: {strategy_name}")
            return enabled
        
        # Check for strategy exclusions
        if 'exclude_strategies' in options:
            excluded = set(options['exclude_strategies'])
            return [s for s in ExtractionStrategy if s.value not in excluded]
        
        # Default: use all strategies
        return list(ExtractionStrategy)
    
    async def _generate_element_id(self, candidate: ElementCandidate) -> str:
        """Generate unique ID for element deduplication"""
        try:
            # Get element properties for ID generation
            tag_name = await candidate.element.evaluate('el => el.tagName.toLowerCase()')
            
            # Try to get a stable identifier
            el_id = await candidate.element.get_attribute('id')
            if el_id:
                return f"{tag_name}#{el_id}"
            
            # Use position and content as fallback
            box = await candidate.element.bounding_box()
            text_content = await candidate.element.text_content()
            
            if box:
                position_key = f"{int(box['x'])}_{int(box['y'])}_{int(box['width'])}_{int(box['height'])}"
            else:
                position_key = "no_position"
            
            if text_content:
                content_key = text_content[:50].strip().replace(' ', '_')
            else:
                content_key = "no_content"
            
            return f"{tag_name}_{position_key}_{content_key}"
            
        except Exception as e:
            logger.debug(f"Failed to generate element ID: {e}")
            return f"unknown_{id(candidate)}"
    
    async def _filter_and_rank_candidates(
        self,
        candidates: List[ElementCandidate],
        context: ExtractionContext
    ) -> List[ElementCandidate]:
        """Filter and rank element candidates"""
        # Apply confidence threshold
        min_confidence = context.options.get('min_confidence', ConfidenceLevel.LOW.value)
        filtered = [c for c in candidates if c.confidence >= min_confidence]
        
        # Sort by confidence and strategy count
        filtered.sort(
            key=lambda c: (c.confidence, len(c.strategies_used)),
            reverse=True
        )
        
        # Apply element limit if specified
        max_elements = context.options.get('max_elements', 1000)
        if len(filtered) > max_elements:
            logger.info(f"Limiting elements from {len(filtered)} to {max_elements}")
            filtered = filtered[:max_elements]
        
        return filtered
    
    async def _convert_to_extracted_elements(
        self,
        candidates: List[ElementCandidate],
        context: ExtractionContext
    ) -> List[ExtractedElement]:
        """Convert candidates to ExtractedElement objects"""
        elements = []
        
        for i, candidate in enumerate(candidates):
            try:
                # Get element properties
                tag_name = await candidate.element.evaluate('el => el.tagName.toLowerCase()')
                text = await candidate.element.text_content()
                is_visible = await candidate.element.is_visible()
                bounding_box = await candidate.element.bounding_box()
                
                # Determine element type
                element_type = self._determine_element_type(tag_name, candidate.attributes)
                interaction_type = self._determine_interaction_type(element_type, candidate.attributes)
                
                # Create ExtractedElement
                element = ExtractedElement(
                    session_id=context.session_id,
                    element_index=i,
                    tag_name=tag_name,
                    element_type=element_type,
                    interaction_type=interaction_type,
                    text=text[:500] if text else None,  # Limit text length
                    css_selector=self._get_best_selector(candidate.selectors, 'css'),
                    xpath=self._get_best_selector(candidate.selectors, 'xpath'),
                    attributes=candidate.attributes,
                    bounding_box=bounding_box,
                    is_visible=is_visible,
                    is_interactable=await self._check_interactable(candidate.element),
                    confidence_score=candidate.confidence,
                    extraction_method=','.join(s.value for s in candidate.strategies_used),
                    ai_analysis=candidate.metadata.get('ai_analysis'),
                    stability_score=candidate.metadata.get('stability_score', 0.5),
                    created_at=context.timestamp
                )
                
                elements.append(element)
                
            except Exception as e:
                logger.error(f"Failed to convert candidate to ExtractedElement: {e}")
                continue
        
        return elements
    
    def _determine_element_type(self, tag_name: str, attributes: Dict[str, Any]) -> ElementType:
        """Determine element type from tag and attributes"""
        # Direct tag mapping
        tag_type_mapping = {
            'button': ElementType.BUTTON,
            'input': ElementType.INPUT,
            'textarea': ElementType.TEXTAREA,
            'select': ElementType.SELECT,
            'a': ElementType.LINK,
            'img': ElementType.IMAGE,
            'video': ElementType.VIDEO,
            'form': ElementType.FORM,
            'table': ElementType.TABLE,
            'nav': ElementType.NAVIGATION,
            'header': ElementType.HEADER,
            'footer': ElementType.FOOTER,
            'main': ElementType.CONTAINER,
            'section': ElementType.CONTAINER,
            'article': ElementType.CONTAINER,
            'aside': ElementType.CONTAINER
        }
        
        if tag_name in tag_type_mapping:
            return tag_type_mapping[tag_name]
        
        # Check role attribute
        role = attributes.get('role', '').lower()
        role_type_mapping = {
            'button': ElementType.BUTTON,
            'link': ElementType.LINK,
            'navigation': ElementType.NAVIGATION,
            'search': ElementType.INPUT,
            'tab': ElementType.TAB,
            'tablist': ElementType.TAB,
            'dialog': ElementType.MODAL,
            'alert': ElementType.ALERT,
            'tooltip': ElementType.TOOLTIP
        }
        
        if role in role_type_mapping:
            return role_type_mapping[role]
        
        # Check for specific classes or attributes
        classes = attributes.get('class', '').lower()
        if any(btn in classes for btn in ['btn', 'button']):
            return ElementType.BUTTON
        if any(modal in classes for modal in ['modal', 'dialog', 'popup']):
            return ElementType.MODAL
        
        # Default
        return ElementType.OTHER
    
    def _determine_interaction_type(
        self,
        element_type: ElementType,
        attributes: Dict[str, Any]
    ) -> ElementInteractionType:
        """Determine interaction type for element"""
        # Type-based mapping
        type_interaction_mapping = {
            ElementType.BUTTON: ElementInteractionType.CLICK,
            ElementType.LINK: ElementInteractionType.CLICK,
            ElementType.INPUT: ElementInteractionType.TYPE,
            ElementType.TEXTAREA: ElementInteractionType.TYPE,
            ElementType.SELECT: ElementInteractionType.SELECT,
            ElementType.CHECKBOX: ElementInteractionType.CHECK,
            ElementType.RADIO: ElementInteractionType.CHECK
        }
        
        if element_type in type_interaction_mapping:
            return type_interaction_mapping[element_type]
        
        # Check if element has click handlers
        if any(attr.startswith('on') for attr in attributes):
            return ElementInteractionType.CLICK
        
        return ElementInteractionType.NONE
    
    def _get_best_selector(self, selectors: List[Dict[str, Any]], selector_type: str) -> Optional[str]:
        """Get the best selector of a specific type"""
        type_selectors = [s for s in selectors if s.get('type') == selector_type]
        if not type_selectors:
            return None
        
        # Sort by score/confidence
        type_selectors.sort(key=lambda s: s.get('score', 0), reverse=True)
        return type_selectors[0].get('value')
    
    async def _check_interactable(self, element: ElementHandle) -> bool:
        """Check if element is interactable"""
        try:
            # Check if element is enabled
            is_enabled = await element.is_enabled()
            if not is_enabled:
                return False
            
            # Check if element is visible
            is_visible = await element.is_visible()
            if not is_visible:
                return False
            
            # Check if element has pointer events
            pointer_events = await element.evaluate('el => getComputedStyle(el).pointerEvents')
            if pointer_events == 'none':
                return False
            
            return True
        except Exception:
            return False
    
    async def _post_process_elements(
        self,
        elements: List[ExtractedElement],
        context: ExtractionContext
    ) -> List[ExtractedElement]:
        """Post-process extracted elements"""
        # Remove duplicates based on position and content
        unique_elements = []
        seen_positions = set()
        
        for element in elements:
            if element.bounding_box:
                # Create position key
                pos_key = (
                    int(element.bounding_box['x']),
                    int(element.bounding_box['y']),
                    int(element.bounding_box['width']),
                    int(element.bounding_box['height']),
                    element.text[:50] if element.text else ''
                )
                
                if pos_key not in seen_positions:
                    seen_positions.add(pos_key)
                    unique_elements.append(element)
            else:
                # Include elements without position (might be important hidden elements)
                unique_elements.append(element)
        
        logger.info(f"Post-processing: {len(elements)} -> {len(unique_elements)} unique elements")
        
        return unique_elements
    
    async def _get_device_info(self, page: Page) -> Dict[str, Any]:
        """Get device information from page"""
        try:
            device_info = await page.evaluate('''() => {
                return {
                    userAgent: navigator.userAgent,
                    platform: navigator.platform,
                    vendor: navigator.vendor,
                    language: navigator.language,
                    screenResolution: {
                        width: screen.width,
                        height: screen.height
                    },
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    },
                    devicePixelRatio: window.devicePixelRatio
                };
            }''')
            return device_info
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return {}
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get extraction statistics"""
        return {
            'total_extractions': self._extraction_stats['total_extractions'],
            'successful_extractions': self._extraction_stats['successful_extractions'],
            'failed_extractions': self._extraction_stats['failed_extractions'],
            'success_rate': (
                self._extraction_stats['successful_extractions'] / 
                max(self._extraction_stats['total_extractions'], 1)
            ),
            'strategies_performance': self._extraction_stats['strategies_performance']
        }