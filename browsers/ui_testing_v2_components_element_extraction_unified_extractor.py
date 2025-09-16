"""
UnifiedElementExtractor - Main orchestrator for element extraction.
Implements strategy pattern with dynamic loading and result aggregation.
Consolidates functionality from multiple extractor implementations.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Type
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum

from playwright.async_api import Page, Browser
from selenium.webdriver.remote.webdriver import WebDriver

from .extraction_utils import (
    ElementType, InteractionType, ElementValidator,
    ExtractionMetrics, ConfidenceCalculator
)

logger = logging.getLogger(__name__)


class ExtractionMode(Enum):
    """Extraction mode configuration"""
    FAST = "fast"  # DOM only
    BALANCED = "balanced"  # DOM + key strategies
    COMPREHENSIVE = "comprehensive"  # All strategies
    CUSTOM = "custom"  # User-defined strategy selection


@dataclass
class UnifiedExtractionConfig:
    """Unified configuration for all extraction strategies"""
    mode: ExtractionMode = ExtractionMode.BALANCED
    enabled_strategies: List[str] = field(default_factory=lambda: [
        'dom', 'visual', 'accessibility', 'semantic'
    ])
    
    # Global settings
    max_elements: int = 1000
    extraction_timeout: int = 30000
    enable_caching: bool = True
    enable_ai_analysis: bool = True
    enable_parallel_extraction: bool = True
    
    # Filtering options
    filter_invisible: bool = True
    filter_duplicates: bool = True
    filter_non_interactive: bool = False
    min_confidence: float = 0.3
    
    # Stealth options
    enable_stealth: bool = False
    handle_cookie_consent: bool = True
    randomize_extraction_order: bool = False
    
    # Strategy-specific configurations
    dom_config: Optional[Dict[str, Any]] = None
    visual_config: Optional[Dict[str, Any]] = None
    accessibility_config: Optional[Dict[str, Any]] = None
    semantic_config: Optional[Dict[str, Any]] = None
    behavioral_config: Optional[Dict[str, Any]] = None
    dynamic_config: Optional[Dict[str, Any]] = None
    
    # Result aggregation
    aggregation_method: str = "weighted_fusion"  # or "voting", "confidence_based"
    strategy_weights: Dict[str, float] = field(default_factory=lambda: {
        'dom': 0.35,
        'visual': 0.20,
        'accessibility': 0.15,
        'semantic': 0.15,
        'behavioral': 0.10,
        'dynamic': 0.05
    })


class ExtractionStrategy(ABC):
    """Base class for all extraction strategies"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name"""
        pass
    
    @abstractmethod
    async def extract_playwright(self, page: Page, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract elements using Playwright"""
        pass
    
    @abstractmethod
    def extract_selenium(self, driver: WebDriver, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract elements using Selenium"""
        pass
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for this strategy"""
        return {}


class StrategyRegistry:
    """Registry for dynamically loading extraction strategies"""
    
    def __init__(self):
        self._strategies: Dict[str, ExtractionStrategy] = {}
        self._load_built_in_strategies()
    
    def _load_built_in_strategies(self):
        """Load built-in extraction strategies"""
        try:
            # Import and register built-in strategies
            from .strategies.unified_dom_strategy import UnifiedDOMStrategy, DOMExtractionConfig
            from .strategies.unified_visual_strategy import UnifiedVisualStrategy, VisualExtractionConfig
            
            # Create wrapper classes that implement ExtractionStrategy interface
            class DOMStrategyWrapper(ExtractionStrategy):
                def __init__(self):
                    self.strategy = UnifiedDOMStrategy()
                
                @property
                def name(self) -> str:
                    return "dom"
                
                async def extract_playwright(self, page: Page, config: Dict[str, Any]) -> List[Dict[str, Any]]:
                    dom_config = DOMExtractionConfig(**config) if config else DOMExtractionConfig()
                    self.strategy.config = dom_config
                    return await self.strategy.extract_playwright(page)
                
                def extract_selenium(self, driver: WebDriver, config: Dict[str, Any]) -> List[Dict[str, Any]]:
                    dom_config = DOMExtractionConfig(**config) if config else DOMExtractionConfig()
                    self.strategy.config = dom_config
                    return self.strategy.extract_selenium(driver)
            
            class VisualStrategyWrapper(ExtractionStrategy):
                def __init__(self):
                    self.strategy = UnifiedVisualStrategy()
                
                @property
                def name(self) -> str:
                    return "visual"
                
                async def extract_playwright(self, page: Page, config: Dict[str, Any]) -> List[Dict[str, Any]]:
                    visual_config = VisualExtractionConfig(**config) if config else VisualExtractionConfig()
                    self.strategy.config = visual_config
                    return await self.strategy.extract_playwright(page)
                
                def extract_selenium(self, driver: WebDriver, config: Dict[str, Any]) -> List[Dict[str, Any]]:
                    visual_config = VisualExtractionConfig(**config) if config else VisualExtractionConfig()
                    self.strategy.config = visual_config
                    return self.strategy.extract_selenium(driver)
            
            self.register_strategy(DOMStrategyWrapper())
            self.register_strategy(VisualStrategyWrapper())
            
            # Try to load other strategies if available
            self._load_optional_strategies()
            
        except ImportError as e:
            logger.warning(f"Could not load some strategies: {e}")
    
    def _load_optional_strategies(self):
        """Load optional strategies that may or may not be available"""
        optional_strategies = [
            ('accessibility', 'accessibility_strategy', 'AccessibilityMappingStrategy'),
            ('semantic', 'semantic_strategy', 'SemanticUnderstandingStrategy'),
            ('behavioral', 'behavioral_strategy', 'BehavioralAnalysisStrategy'),
            ('dynamic', 'dynamic_strategy', 'DynamicContentTrackingStrategy'),
            ('shadow_dom', 'shadow_dom_strategy', 'ShadowDOMTraversalStrategy'),
            ('ml', 'ml_strategy', 'MLClassificationStrategy'),
            ('relationship', 'relationship_strategy', 'RelationshipMappingStrategy')
        ]
        
        for name, module_name, class_name in optional_strategies:
            try:
                module = __import__(f'.strategies.{module_name}', fromlist=[class_name], package=__package__)
                strategy_class = getattr(module, class_name)
                
                # Create wrapper for the strategy
                class StrategyWrapper(ExtractionStrategy):
                    def __init__(self, strategy_instance, strategy_name):
                        self.strategy = strategy_instance
                        self._name = strategy_name
                    
                    @property
                    def name(self) -> str:
                        return self._name
                    
                    async def extract_playwright(self, page: Page, config: Dict[str, Any]) -> List[Dict[str, Any]]:
                        if hasattr(self.strategy, 'extract'):
                            return await self.strategy.extract(page, config)
                        return []
                    
                    def extract_selenium(self, driver: WebDriver, config: Dict[str, Any]) -> List[Dict[str, Any]]:
                        if hasattr(self.strategy, 'extract_selenium'):
                            return self.strategy.extract_selenium(driver, config)
                        return []
                
                wrapper = StrategyWrapper(strategy_class(), name)
                self.register_strategy(wrapper)
                logger.info(f"Loaded optional strategy: {name}")
                
            except (ImportError, AttributeError) as e:
                logger.debug(f"Optional strategy {name} not available: {e}")
    
    def register_strategy(self, strategy: ExtractionStrategy):
        """Register a new extraction strategy"""
        self._strategies[strategy.name] = strategy
        logger.info(f"Registered extraction strategy: {strategy.name}")
    
    def get_strategy(self, name: str) -> Optional[ExtractionStrategy]:
        """Get a strategy by name"""
        return self._strategies.get(name)
    
    def list_strategies(self) -> List[str]:
        """List all available strategies"""
        return list(self._strategies.keys())


class ResultAggregator:
    """Aggregates results from multiple extraction strategies"""
    
    def __init__(self, config: UnifiedExtractionConfig):
        self.config = config
        self.validator = ElementValidator()
        self.confidence_calculator = ConfidenceCalculator()
    
    def aggregate(self, strategy_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Aggregate results from multiple strategies"""
        if self.config.aggregation_method == "weighted_fusion":
            return self._weighted_fusion(strategy_results)
        elif self.config.aggregation_method == "voting":
            return self._voting_aggregation(strategy_results)
        elif self.config.aggregation_method == "confidence_based":
            return self._confidence_based_aggregation(strategy_results)
        else:
            # Default to simple merge
            return self._simple_merge(strategy_results)
    
    def _weighted_fusion(self, strategy_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Weighted fusion of results based on strategy importance"""
        element_groups = {}
        
        # Group similar elements across strategies
        for strategy_name, elements in strategy_results.items():
            strategy_weight = self.config.strategy_weights.get(strategy_name, 0.1)
            
            for element in elements:
                # Create element signature
                signature = self._create_element_signature(element)
                
                if signature not in element_groups:
                    element_groups[signature] = {
                        'elements': [],
                        'total_weight': 0,
                        'strategies': []
                    }
                
                # Add weighted element
                element['strategy_weight'] = strategy_weight
                element['source_strategy'] = strategy_name
                element_groups[signature]['elements'].append(element)
                element_groups[signature]['total_weight'] += strategy_weight
                element_groups[signature]['strategies'].append(strategy_name)
        
        # Merge groups into final elements
        final_elements = []
        for signature, group in element_groups.items():
            merged_element = self._merge_element_group(group['elements'])
            
            # Calculate final confidence
            merged_element['confidence'] = min(
                group['total_weight'],
                merged_element.get('confidence', 0.5) * (1 + len(group['strategies']) * 0.1)
            )
            merged_element['detected_by_strategies'] = group['strategies']
            merged_element['fusion_score'] = group['total_weight']
            
            final_elements.append(merged_element)
        
        # Sort by fusion score and confidence
        final_elements.sort(key=lambda x: (x['fusion_score'], x['confidence']), reverse=True)
        
        return final_elements
    
    def _voting_aggregation(self, strategy_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Aggregate using voting - elements detected by multiple strategies get higher scores"""
        element_votes = {}
        
        for strategy_name, elements in strategy_results.items():
            for element in elements:
                signature = self._create_element_signature(element)
                
                if signature not in element_votes:
                    element_votes[signature] = {
                        'element': element,
                        'votes': 0,
                        'strategies': []
                    }
                
                element_votes[signature]['votes'] += 1
                element_votes[signature]['strategies'].append(strategy_name)
                
                # Update element if this version has higher confidence
                if element.get('confidence', 0) > element_votes[signature]['element'].get('confidence', 0):
                    element_votes[signature]['element'] = element
        
        # Filter by minimum votes
        min_votes = max(1, len(strategy_results) // 3)  # At least 1/3 of strategies
        
        final_elements = []
        for signature, vote_data in element_votes.items():
            if vote_data['votes'] >= min_votes:
                element = vote_data['element'].copy()
                element['vote_count'] = vote_data['votes']
                element['detected_by_strategies'] = vote_data['strategies']
                final_elements.append(element)
        
        # Sort by vote count
        final_elements.sort(key=lambda x: (x['vote_count'], x.get('confidence', 0)), reverse=True)
        
        return final_elements
    
    def _confidence_based_aggregation(self, strategy_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Aggregate based on confidence scores"""
        all_elements = []
        
        for strategy_name, elements in strategy_results.items():
            for element in elements:
                element['source_strategy'] = strategy_name
                all_elements.append(element)
        
        # Sort by confidence
        all_elements.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Remove duplicates keeping highest confidence
        seen_signatures = set()
        final_elements = []
        
        for element in all_elements:
            signature = self._create_element_signature(element)
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                final_elements.append(element)
        
        return final_elements
    
    def _simple_merge(self, strategy_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Simple merge of all results with deduplication"""
        all_elements = []
        
        for strategy_name, elements in strategy_results.items():
            for element in elements:
                element['source_strategy'] = strategy_name
                all_elements.append(element)
        
        # Deduplicate
        return self.validator.filter_duplicate_elements(all_elements)
    
    def _create_element_signature(self, element: Dict[str, Any]) -> str:
        """Create a signature for element comparison"""
        # Use multiple attributes for signature
        parts = [
            element.get('tag_name', ''),
            str(element.get('bounding_box', {}).get('x', 0) // 10),
            str(element.get('bounding_box', {}).get('y', 0) // 10),
            element.get('element_type', ''),
            element.get('text', '')[:50]
        ]
        
        return '|'.join(parts)
    
    def _merge_element_group(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]]:
        """Merge a group of similar elements into one"""
        if not elements:
            return {}
        
        # Start with the element with highest confidence
        elements.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        merged = elements[0].copy()
        
        # Aggregate selectors
        all_selectors = []
        for element in elements:
            if 'selectors' in element:
                all_selectors.extend(element['selectors'])
        
        # Deduplicate selectors
        seen_selectors = set()
        unique_selectors = []
        for selector in all_selectors:
            sel_str = f"{selector.get('type')}:{selector.get('selector')}"
            if sel_str not in seen_selectors:
                seen_selectors.add(sel_str)
                unique_selectors.append(selector)
        
        merged['selectors'] = unique_selectors
        
        # Average confidence scores
        confidences = [e.get('confidence', 0) for e in elements]
        merged['confidence'] = sum(confidences) / len(confidences) if confidences else 0
        
        # Merge interaction types
        all_interactions = set()
        for element in elements:
            if 'interaction_types' in element:
                all_interactions.update(element['interaction_types'])
        merged['interaction_types'] = list(all_interactions)
        
        return merged


class UnifiedElementExtractor:
    """
    Main unified element extractor that orchestrates all strategies.
    Replaces multiple extractor implementations with a single, configurable system.
    """
    
    def __init__(
        self,
        config: Optional[UnifiedExtractionConfig] = None,
        ai_service: Optional[Any] = None,
        cache_service: Optional[Any] = None,
        database_service: Optional[Any] = None
    ):
        self.config = config or UnifiedExtractionConfig()
        self.ai_service = ai_service
        self.cache_service = cache_service
        self.database_service = database_service
        
        self.strategy_registry = StrategyRegistry()
        self.result_aggregator = ResultAggregator(self.config)
        self.validator = ElementValidator()
        
        self._extraction_stats = {}
        self._last_extraction_time = 0
        
        # Configure based on mode
        self._configure_for_mode()
    
    def _configure_for_mode(self):
        """Configure strategies based on extraction mode"""
        if self.config.mode == ExtractionMode.FAST:
            self.config.enabled_strategies = ['dom']
            self.config.enable_ai_analysis = False
        elif self.config.mode == ExtractionMode.BALANCED:
            self.config.enabled_strategies = ['dom', 'visual', 'accessibility', 'semantic']
        elif self.config.mode == ExtractionMode.COMPREHENSIVE:
            self.config.enabled_strategies = self.strategy_registry.list_strategies()
        # CUSTOM mode uses user-defined enabled_strategies
    
    async def extract_playwright(
        self,
        page: Page,
        url: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract elements from a page using Playwright"""
        start_time = time.time()
        
        try:
            # Navigate if URL provided
            if url:
                await page.goto(url, wait_until='networkidle')
            
            # Check cache if enabled
            if self.cache_service and self.config.enable_caching:
                cache_key = f"elements:{page.url}"
                cached = await self.cache_service.get(cache_key)
                if cached:
                    logger.info("Using cached extraction results")
                    return cached
            
            # Run extraction strategies
            strategy_results = {}
            
            if self.config.enable_parallel_extraction:
                # Run strategies in parallel
                tasks = []
                for strategy_name in self.config.enabled_strategies:
                    strategy = self.strategy_registry.get_strategy(strategy_name)
                    if strategy:
                        config = getattr(self.config, f"{strategy_name}_config", {})
                        tasks.append(self._run_strategy_async(strategy, page, config, strategy_name))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for strategy_name, result in zip(self.config.enabled_strategies, results):
                    if not isinstance(result, Exception):
                        strategy_results[strategy_name] = result
                    else:
                        logger.error(f"Strategy {strategy_name} failed: {result}")
            else:
                # Run strategies sequentially
                for strategy_name in self.config.enabled_strategies:
                    strategy = self.strategy_registry.get_strategy(strategy_name)
                    if strategy:
                        try:
                            config = getattr(self.config, f"{strategy_name}_config", {})
                            result = await strategy.extract_playwright(page, config)
                            strategy_results[strategy_name] = result
                        except Exception as e:
                            logger.error(f"Strategy {strategy_name} failed: {e}")
            
            # Aggregate results
            elements = self.result_aggregator.aggregate(strategy_results)
            
            # Apply AI analysis if enabled
            if self.config.enable_ai_analysis and self.ai_service:
                elements = await self._apply_ai_analysis(elements)
            
            # Apply filters
            elements = self._apply_filters(elements)
            
            # Limit to max elements
            elements = elements[:self.config.max_elements]
            
            # Calculate statistics
            self._extraction_stats = ExtractionMetrics.calculate_extraction_stats(elements)
            self._last_extraction_time = time.time() - start_time
            
            # Cache results if enabled
            if self.cache_service and self.config.enable_caching:
                await self.cache_service.set(cache_key, elements, ttl=300)
            
            # Store in database if available
            if self.database_service:
                await self._store_elements(elements, page.url)
            
            return elements
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return []
    
    def extract_selenium(
        self,
        driver: WebDriver,
        url: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract elements from a page using Selenium"""
        start_time = time.time()
        
        try:
            # Navigate if URL provided
            if url:
                driver.get(url)
            
            # Run extraction strategies
            strategy_results = {}
            
            for strategy_name in self.config.enabled_strategies:
                strategy = self.strategy_registry.get_strategy(strategy_name)
                if strategy:
                    try:
                        config = getattr(self.config, f"{strategy_name}_config", {})
                        result = strategy.extract_selenium(driver, config)
                        strategy_results[strategy_name] = result
                    except Exception as e:
                        logger.error(f"Strategy {strategy_name} failed: {e}")
            
            # Aggregate results
            elements = self.result_aggregator.aggregate(strategy_results)
            
            # Apply filters
            elements = self._apply_filters(elements)
            
            # Limit to max elements
            elements = elements[:self.config.max_elements]
            
            # Calculate statistics
            self._extraction_stats = ExtractionMetrics.calculate_extraction_stats(elements)
            self._last_extraction_time = time.time() - start_time
            
            return elements
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return []
    
    async def _run_strategy_async(
        self,
        strategy: ExtractionStrategy,
        page: Page,
        config: Dict[str, Any],
        strategy_name: str
    ) -> List[Dict[str, Any]]:
        """Run a strategy asynchronously with timeout"""
        try:
            return await asyncio.wait_for(
                strategy.extract_playwright(page, config),
                timeout=self.config.extraction_timeout / 1000
            )
        except asyncio.TimeoutError:
            logger.error(f"Strategy {strategy_name} timed out")
            return []
        except Exception as e:
            logger.error(f"Strategy {strategy_name} failed: {e}")
            return []
    
    async def _apply_ai_analysis(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply AI analysis to enhance element data"""
        if not self.ai_service:
            return elements
        
        try:
            # Batch analyze elements
            enhanced_elements = await self.ai_service.analyze_elements(elements)
            
            # Merge AI insights
            for original, enhanced in zip(elements, enhanced_elements):
                if 'ai_classification' in enhanced:
                    original['ai_classification'] = enhanced['ai_classification']
                if 'ai_confidence' in enhanced:
                    original['confidence'] = (
                        original.get('confidence', 0.5) * 0.7 +
                        enhanced['ai_confidence'] * 0.3
                    )
            
            return elements
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return elements
    
    def _apply_filters(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply configured filters to elements"""
        filtered = elements
        
        # Filter invisible elements
        if self.config.filter_invisible:
            filtered = [e for e in filtered if self.validator.is_visible_element(e)]
        
        # Filter duplicates
        if self.config.filter_duplicates:
            filtered = self.validator.filter_duplicate_elements(filtered)
        
        # Filter non-interactive
        if self.config.filter_non_interactive:
            filtered = [e for e in filtered if self.validator.is_interactive_element(e)]
        
        # Filter by minimum confidence
        if self.config.min_confidence > 0:
            filtered = [e for e in filtered if e.get('confidence', 0) >= self.config.min_confidence]
        
        return filtered
    
    async def _store_elements(self, elements: List[Dict[str, Any]], url: str):
        """Store extracted elements in database"""
        if not self.database_service:
            return
        
        try:
            await self.database_service.store_extraction_result({
                'url': url,
                'elements': elements,
                'extraction_time': self._last_extraction_time,
                'stats': self._extraction_stats,
                'config': {
                    'mode': self.config.mode.value,
                    'enabled_strategies': self.config.enabled_strategies
                }
            })
        except Exception as e:
            logger.error(f"Failed to store elements: {e}")
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get statistics from last extraction"""
        return {
            **self._extraction_stats,
            'extraction_time': self._last_extraction_time,
            'enabled_strategies': self.config.enabled_strategies,
            'mode': self.config.mode.value
        }
    
    def register_custom_strategy(self, strategy: ExtractionStrategy):
        """Register a custom extraction strategy"""
        self.strategy_registry.register_strategy(strategy)
    
    def set_mode(self, mode: ExtractionMode):
        """Change extraction mode"""
        self.config.mode = mode
        self._configure_for_mode()