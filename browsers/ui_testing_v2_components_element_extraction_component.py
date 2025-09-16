"""
Main element extraction component that orchestrates browser automation,
element extraction, and AI-powered analysis using the unified extraction system.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from ui_testing_v2.components.browser_manager import BrowserManager, ElementInteractionManager
from ui_testing_v2.components.element_extraction.unified_extractor import (
    UnifiedElementExtractor, 
    UnifiedExtractionConfig,
    ExtractionMode
)
from ui_testing_v2.components.element_analysis import ElementAnalysisService
from ui_testing_v2.models.database import ExtractedElement, TestSession
from ui_testing_v2.services.ai_services import AIServiceFactory
from ui_testing_v2.services.cache import CacheService
from ui_testing_v2.services.database import DatabaseManager
from ui_testing_v2.core.config import Config

logger = logging.getLogger(__name__)


class ElementExtractionComponent:
    """
    Main component for comprehensive element extraction and analysis.
    Orchestrates browser automation, element extraction using unified system, and AI analysis.
    """
    
    def __init__(
        self,
        config: Config,
        database_manager: DatabaseManager,
        ai_service_factory: AIServiceFactory,
        cache_service: CacheService
    ):
        self.config = config
        self.database_manager = database_manager
        self.ai_service_factory = ai_service_factory
        self.cache_service = cache_service
        
        # Initialize core components with unified extractor
        self.browser_manager = BrowserManager(config)
        
        # Configure unified extractor based on config
        extraction_config = self._create_extraction_config()
        self.element_extractor = UnifiedElementExtractor(
            config=extraction_config,
            ai_service=ai_service_factory.get_ai_service() if ai_service_factory else None,
            cache_service=cache_service,
            database_service=database_manager
        )
        
        self.element_analyzer = ElementAnalysisService(config, ai_service_factory, cache_service)
        self.interaction_manager = ElementInteractionManager(self.browser_manager)
        
        # Component state
        self._active_sessions = {}
        self._extraction_stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'total_elements_extracted': 0,
            'extraction_times': [],
            'strategies_used': {}
        }
        
        logger.info("ElementExtractionComponent initialized with UnifiedElementExtractor")
    
    def _create_extraction_config(self) -> UnifiedExtractionConfig:
        """Create unified extraction config from component config"""
        # Determine extraction mode based on config
        mode = ExtractionMode.BALANCED  # Default
        if hasattr(self.config, 'extraction_mode'):
            mode_map = {
                'fast': ExtractionMode.FAST,
                'balanced': ExtractionMode.BALANCED,
                'comprehensive': ExtractionMode.COMPREHENSIVE,
                'custom': ExtractionMode.CUSTOM
            }
            mode = mode_map.get(self.config.extraction_mode, ExtractionMode.BALANCED)
        
        # Build extraction config
        config = UnifiedExtractionConfig(
            mode=mode,
            max_elements=getattr(self.config, 'max_elements', 1000),
            extraction_timeout=getattr(self.config.browser, 'timeout', 30000),
            enable_caching=True,
            enable_ai_analysis=bool(self.ai_service_factory),
            enable_parallel_extraction=getattr(self.config, 'parallel_extraction', True),
            filter_invisible=True,
            filter_duplicates=True,
            filter_non_interactive=False,
            min_confidence=getattr(self.config, 'min_confidence', 0.3),
            enable_stealth=getattr(self.config, 'enable_stealth', False),
            handle_cookie_consent=True,
            randomize_extraction_order=False,
            aggregation_method=getattr(self.config, 'aggregation_method', 'weighted_fusion')
        )
        
        # Add strategy-specific configs if available
        if hasattr(self.config, 'dom_config'):
            config.dom_config = self.config.dom_config
        if hasattr(self.config, 'visual_config'):
            config.visual_config = self.config.visual_config
            
        return config
    
    async def extract_and_analyze_page(
        self,
        url: str,
        session_id: str,
        extraction_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete page extraction and analysis workflow using unified extraction
        
        Args:
            url: URL to extract elements from
            session_id: Session ID for tracking
            extraction_config: Optional configuration for extraction
            
        Returns:
            Comprehensive extraction and analysis results
        """
        start_time = datetime.now(timezone.utc)
        extraction_id = f"{session_id}_{int(start_time.timestamp())}"
        
        try:
            logger.info(f"Starting element extraction and analysis for {url}")
            self._extraction_stats['total_extractions'] += 1
            
            # Override extraction config if provided
            if extraction_config:
                self._apply_extraction_config(extraction_config)
            
            # Launch browser and navigate
            async with self._browser_context() as (browser, page):
                # Navigate to URL
                await page.goto(url, wait_until='networkidle')
                
                # Extract elements using unified extractor
                elements = await self.element_extractor.extract_playwright(page)
                
                # Get extraction statistics
                extraction_stats = self.element_extractor.get_extraction_stats()
                
                # Update component stats
                self._update_stats(extraction_stats, len(elements))
                
                # Analyze extracted elements if configured
                analysis_results = None
                if self.element_analyzer and elements:
                    analysis_results = await self.element_analyzer.analyze_elements(
                        elements[:50],  # Limit AI analysis
                        url=url,
                        context={'session_id': session_id}
                    )
                
                # Store results in database
                if self.database_manager:
                    await self._store_extraction_results(
                        session_id, url, elements, analysis_results
                    )
                
                # Prepare response
                result = {
                    'extraction_id': extraction_id,
                    'url': url,
                    'session_id': session_id,
                    'timestamp': start_time.isoformat(),
                    'duration': (datetime.now(timezone.utc) - start_time).total_seconds(),
                    'elements': {
                        'total': len(elements),
                        'interactive': extraction_stats.get('interactive_elements', 0),
                        'by_type': extraction_stats.get('elements_by_type', {}),
                        'data': elements[:100]  # Limit response size
                    },
                    'extraction_stats': extraction_stats,
                    'analysis': analysis_results,
                    'strategies_used': extraction_stats.get('enabled_strategies', []),
                    'extraction_mode': extraction_stats.get('mode', 'unknown'),
                    'success': True
                }
                
                self._extraction_stats['successful_extractions'] += 1
                logger.info(f"Successfully extracted {len(elements)} elements from {url}")
                
                return result
                
        except Exception as e:
            logger.error(f"Error during extraction and analysis: {e}", exc_info=True)
            self._extraction_stats['failed_extractions'] += 1
            
            return {
                'extraction_id': extraction_id,
                'url': url,
                'session_id': session_id,
                'timestamp': start_time.isoformat(),
                'duration': (datetime.now(timezone.utc) - start_time).total_seconds(),
                'success': False,
                'error': str(e)
            }
    
    def _apply_extraction_config(self, config: Dict[str, Any]):
        """Apply custom extraction configuration"""
        if 'mode' in config:
            mode_map = {
                'fast': ExtractionMode.FAST,
                'balanced': ExtractionMode.BALANCED,
                'comprehensive': ExtractionMode.COMPREHENSIVE,
                'custom': ExtractionMode.CUSTOM
            }
            mode = mode_map.get(config['mode'], ExtractionMode.BALANCED)
            self.element_extractor.set_mode(mode)
        
        if 'max_elements' in config:
            self.element_extractor.config.max_elements = config['max_elements']
        
        if 'enable_stealth' in config:
            self.element_extractor.config.enable_stealth = config['enable_stealth']
        
        if 'strategies' in config:
            self.element_extractor.config.enabled_strategies = config['strategies']
    
    def _update_stats(self, extraction_stats: Dict[str, Any], element_count: int):
        """Update component statistics"""
        self._extraction_stats['total_elements_extracted'] += element_count
        
        # Track extraction times
        if 'extraction_time' in extraction_stats:
            self._extraction_stats['extraction_times'].append(extraction_stats['extraction_time'])
            # Keep only last 100 times
            if len(self._extraction_stats['extraction_times']) > 100:
                self._extraction_stats['extraction_times'] = self._extraction_stats['extraction_times'][-100:]
        
        # Track strategy usage
        for strategy in extraction_stats.get('enabled_strategies', []):
            if strategy not in self._extraction_stats['strategies_used']:
                self._extraction_stats['strategies_used'][strategy] = 0
            self._extraction_stats['strategies_used'][strategy] += 1
    
    @asynccontextmanager
    async def _browser_context(self):
        """Context manager for browser lifecycle"""
        browser = None
        page = None
        try:
            # Use Playwright by default for unified extractor
            browser = await self.browser_manager.get_playwright_browser()
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            yield browser, page
        finally:
            if page:
                await page.close()
            if browser:
                await browser.close()
    
    async def _store_extraction_results(
        self,
        session_id: str,
        url: str,
        elements: List[Dict[str, Any]],
        analysis_results: Optional[Dict[str, Any]]
    ):
        """Store extraction results in database"""
        try:
            # Convert elements to database models
            db_elements = []
            for element in elements[:100]:  # Limit database storage
                db_element = ExtractedElement(
                    session_id=session_id,
                    tag_name=element.get('tag_name', 'unknown'),
                    element_type=element.get('element_type', 'unknown'),
                    css_selector=element.get('selectors', [{}])[0].get('selector') if element.get('selectors') else None,
                    text_content=element.get('text', '')[:500],
                    attributes=element.get('attributes', {}),
                    is_visible=element.get('is_visible', True),
                    is_clickable=element.get('is_clickable', False),
                    confidence_score=element.get('confidence', 0.5),
                    extraction_strategy=element.get('extraction_method', 'unified'),
                    ai_description=analysis_results.get(element.get('id'), {}).get('description') if analysis_results else None
                )
                db_elements.append(db_element)
            
            # Bulk insert elements
            if db_elements:
                await self.database_manager.bulk_insert_elements(db_elements)
                
        except Exception as e:
            logger.error(f"Error storing extraction results: {e}")
    
    async def extract_with_custom_strategy(
        self,
        url: str,
        strategies: List[str],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract elements using specific strategies
        
        Args:
            url: URL to extract from
            strategies: List of strategy names to use
            session_id: Optional session ID
            
        Returns:
            Extraction results
        """
        # Configure for custom mode with specific strategies
        self.element_extractor.config.mode = ExtractionMode.CUSTOM
        self.element_extractor.config.enabled_strategies = strategies
        
        session_id = session_id or f"custom_{int(datetime.now().timestamp())}"
        
        return await self.extract_and_analyze_page(url, session_id)
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get component extraction statistics"""
        stats = self._extraction_stats.copy()
        
        # Calculate averages
        if stats['extraction_times']:
            stats['avg_extraction_time'] = sum(stats['extraction_times']) / len(stats['extraction_times'])
        else:
            stats['avg_extraction_time'] = 0
        
        if stats['successful_extractions'] > 0:
            stats['avg_elements_per_extraction'] = (
                stats['total_elements_extracted'] / stats['successful_extractions']
            )
        else:
            stats['avg_elements_per_extraction'] = 0
        
        # Success rate
        total = stats['total_extractions']
        if total > 0:
            stats['success_rate'] = stats['successful_extractions'] / total
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def set_extraction_mode(self, mode: str):
        """
        Set the extraction mode
        
        Args:
            mode: One of 'fast', 'balanced', 'comprehensive', 'custom'
        """
        mode_map = {
            'fast': ExtractionMode.FAST,
            'balanced': ExtractionMode.BALANCED,
            'comprehensive': ExtractionMode.COMPREHENSIVE,
            'custom': ExtractionMode.CUSTOM
        }
        
        if mode in mode_map:
            self.element_extractor.set_mode(mode_map[mode])
            logger.info(f"Extraction mode set to: {mode}")
        else:
            logger.warning(f"Invalid extraction mode: {mode}")
    
    async def close(self):
        """Clean up resources"""
        try:
            # Close browser manager
            if self.browser_manager:
                await self.browser_manager.close()
            
            # Clear cache if needed
            if self.cache_service:
                await self.cache_service.clear_expired()
                
            logger.info("ElementExtractionComponent closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing ElementExtractionComponent: {e}")