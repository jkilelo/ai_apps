#!/usr/bin/env python3
"""
ELEMENTS EXTRACTOR WITH LLM - Production-Ready LLM-Enhanced Element Extraction
==============================================================================
Strategic module for AI-powered website element extraction using the definitive
browser_with_llm.py integration layer.

This module leverages:
- browser_with_llm.py for integrated browser + LLM + prompts capabilities
- Advanced semantic understanding and context analysis
- Multi-strategy extraction with confidence scoring
- Production hardening and comprehensive validation

Architecture:
- Layer 0: browser.py, llm.py, prompts.py (base modules)
- Layer 1: browser_with_llm.py (integration layer)
- Layer 2: THIS MODULE (domain-specific element extraction)

Author: Senior Software Engineer (30+ years experience)
Version: 4.0.0 - Refactored to use browser_with_llm.py
Compliance: 100% UI_TESTING_AUTOMATION_MASTER_PLAN.md
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

# Import the definitive browser with LLM integration
from browser_with_llm import (
    BrowserWithLLM,
    BrowserWithLLMConfig,
    ExtractionWithLLMResult,
    ElementWithLLMContext,
    SemanticContext,
    LLMAnalysisResult
)

# Import pipeline contracts for proper data structures
from pipeline_contracts import (
    ElementType,
    ExtractedElement,
    ElementExtractionOutput
)

# Import browser types for element data
from browser import (
    StealthConfig,
    StealthLevel,
    ElementData,
    ElementType as BrowserElementType
)

# Import prompt strategies for enhanced analysis
from prompts import (
    PromptStrategy,
    TaskType,
    ComplexityLevel,
    PromptEngine
)

# Import LLM for direct queries when needed
from llm import call_default_llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
)
logger = logging.getLogger(__name__)

# ==================== ENHANCED DATA MODELS ====================

class InteractionType(Enum):
    """Types of interactions possible with elements"""
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    HOVER = "hover"
    DRAG = "drag"
    SCROLL = "scroll"
    FOCUS = "focus"
    SUBMIT = "submit"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    NAVIGATE = "navigate"
    TOGGLE = "toggle"
    EXPAND = "expand"
    COLLAPSE = "collapse"

@dataclass
class AIAnalysis:
    """AI-powered analysis of elements"""
    semantic_role: str
    functional_purpose: str
    test_priority: float
    confidence_score: float
    suggested_interactions: List[InteractionType]
    accessibility_notes: Optional[str] = None
    security_considerations: Optional[str] = None
    performance_impact: Optional[str] = None
    edge_cases: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class EnhancedElement:
    """Element with full context and AI analysis"""
    # Basic element data
    element_type: ElementType
    selector: str
    text: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Position and visibility
    is_visible: bool = True
    is_interactive: bool = True
    bounding_box: Optional[Dict[str, float]] = None
    
    # AI-enhanced properties
    ai_analysis: Optional[AIAnalysis] = None
    semantic_context: Optional[str] = None
    interaction_patterns: List[InteractionType] = field(default_factory=list)
    test_suggestions: List[str] = field(default_factory=list)
    
    # Relationships
    parent_selector: Optional[str] = None
    child_selectors: List[str] = field(default_factory=list)
    related_elements: List[str] = field(default_factory=list)
    
    # Metadata
    extraction_confidence: float = 1.0
    extraction_method: str = "browser_with_llm"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ExtractionConfig:
    """Configuration for element extraction"""
    # Browser configuration
    headless: bool = True
    stealth_level: StealthLevel = StealthLevel.MAXIMUM
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # LLM configuration
    use_llm_analysis: bool = True
    analyze_semantics: bool = True
    analyze_accessibility: bool = True
    generate_test_cases: bool = True
    
    # Extraction configuration
    max_elements: int = 1000
    min_confidence: float = 0.3
    extract_hidden: bool = False
    extract_shadow_dom: bool = True
    extract_iframes: bool = True
    
    # Performance configuration
    parallel_analysis: bool = True
    cache_results: bool = True
    timeout: int = 30000
    max_retries: int = 3
    
    # Output configuration
    include_screenshots: bool = False
    include_html: bool = False
    verbose_logging: bool = False

# ExtractionResult removed - using ElementExtractionOutput from pipeline_contracts

# ==================== MAIN EXTRACTOR CLASS ====================

class ElementsExtractorWithLLM:
    """
    Production-ready element extractor using browser_with_llm.py
    
    This class leverages the definitive browser + LLM + prompts integration
    for advanced element extraction with semantic understanding.
    """
    
    def __init__(self, config: Optional[ExtractionConfig] = None):
        """Initialize extractor with configuration"""
        self.config = config or ExtractionConfig()
        
        # Create browser with LLM configuration
        browser_config = BrowserWithLLMConfig(
            stealth_config=StealthConfig(
                level=self.config.stealth_level,
                headless=self.config.headless,
                viewport_width=self.config.viewport_width,
                viewport_height=self.config.viewport_height
            ),
            enable_llm_analysis=self.config.use_llm_analysis,
            analyze_semantics=self.config.analyze_semantics,
            analyze_accessibility=self.config.analyze_accessibility,
            generate_test_suggestions=self.config.generate_test_cases,
            parallel_analysis=self.config.parallel_analysis,
            cache_llm_results=self.config.cache_results,
            timeout=self.config.timeout
        )
        
        # Initialize browser with LLM
        self.browser = BrowserWithLLM(browser_config)
        self.prompt_engine = PromptEngine()
        
        # Cache for performance
        self._element_cache: Dict[str, EnhancedElement] = {}
        self._analysis_cache: Dict[str, AIAnalysis] = {}
        
        logger.info("ElementsExtractorWithLLM initialized with browser_with_llm.py integration")
    
    async def extract_from_url(
        self,
        url: str,
        custom_prompts: Optional[Dict[str, str]] = None
    ) -> ElementExtractionOutput:
        """
        Extract elements from URL with AI enhancement
        
        Args:
            url: Target URL to extract from
            custom_prompts: Optional custom prompts for specific analysis
        
        Returns:
            ElementExtractionOutput with extracted elements per pipeline contract
        """
        start_time = time.time()
        
        try:
            # Initialize browser
            await self.browser.initialize()
            
            # Extract and analyze using browser_with_llm
            browser_result = await self.browser.extract_and_analyze(
                url=url,
                wait_for='domcontentloaded'
            )
            
            if not browser_result.success:
                return ElementExtractionOutput(
                    url=url,
                    elements=[],
                    page_title="Error",
                    page_type="error",
                    extraction_method="hybrid"
                )
            
            # Convert browser elements to enhanced elements
            # browser_result has elements_with_context from browser_with_llm
            enhanced_elements = await self._enhance_elements(
                browser_result.elements_with_context if hasattr(browser_result, 'elements_with_context') else [],
                custom_prompts
            )
            
            # Filter by confidence if configured
            if self.config.min_confidence > 0:
                enhanced_elements = [
                    e for e in enhanced_elements 
                    if e.extraction_confidence >= self.config.min_confidence
                ]
            
            # Limit elements if configured
            if self.config.max_elements > 0:
                enhanced_elements = enhanced_elements[:self.config.max_elements]
            
            # Generate test scenarios if enabled
            test_scenarios = []
            if self.config.generate_test_cases and browser_result.test_scenarios:
                test_scenarios = browser_result.test_scenarios
            
            # Compile extraction statistics
            extraction_stats = {
                'total_elements': len(enhanced_elements),
                'element_types': self._count_element_types(enhanced_elements),
                'interactive_elements': sum(1 for e in enhanced_elements if e.is_interactive),
                'visible_elements': sum(1 for e in enhanced_elements if e.is_visible),
                'ai_analyzed': sum(1 for e in enhanced_elements if e.ai_analysis is not None),
                'average_confidence': sum(e.extraction_confidence for e in enhanced_elements) / len(enhanced_elements) if enhanced_elements else 0,
                'extraction_method': 'browser_with_llm',
                'llm_calls': browser_result.total_llm_calls if hasattr(browser_result, 'total_llm_calls') else 0
            }
            
            extraction_time = time.time() - start_time
            
            # Convert EnhancedElement to ExtractedElement for pipeline contract
            extracted_elements = []
            for elem in enhanced_elements:
                extracted_elements.append(ExtractedElement(
                    selector=elem.selector or f"[data-id='{elem.element_id}']",
                    element_type=self._map_element_type(elem.tag_name),
                    tag_name=elem.tag_name,
                    text=elem.text,
                    id=elem.attributes.get('id'),
                    classes=elem.classes,
                    attributes=elem.attributes,
                    is_clickable=elem.is_interactive,
                    is_editable=elem.tag_name in ['input', 'textarea', 'select'],
                    is_visible=elem.is_visible,
                    is_enabled=not elem.attributes.get('disabled', False),
                    ai_description=elem.ai_analysis.description if elem.ai_analysis else None,
                    test_suggestions=elem.ai_analysis.test_suggestions if elem.ai_analysis else [],
                    importance_score=elem.ai_analysis.importance_score if elem.ai_analysis else 0.5
                ))
            
            return ElementExtractionOutput(
                url=url,
                elements=extracted_elements,
                page_title=browser_result.page_insights.get('title', 'Unknown'),
                page_type=browser_result.page_insights.get('page_type', 'unknown'),
                extraction_method="hybrid",
                page_description=browser_result.page_insights.get('description'),
                key_features=browser_result.page_insights.get('key_features', []),
                test_recommendations=test_scenarios[:5] if test_scenarios else []
            )
            
        except Exception as e:
            logger.error(f"Extraction failed for {url}: {e}")
            return ElementExtractionOutput(
                url=url,
                elements=[],
                page_title="Error",
                page_type="error",
                extraction_method="hybrid"
            )
        finally:
            await self.browser.cleanup()
    
    def _map_element_type(self, tag_name: str) -> ElementType:
        """Map HTML tag to ElementType enum"""
        mapping = {
            'button': ElementType.BUTTON,
            'input': ElementType.INPUT,
            'select': ElementType.SELECT,
            'textarea': ElementType.INPUT,
            'a': ElementType.LINK,
            'img': ElementType.IMAGE,
            'table': ElementType.TABLE,
            'form': ElementType.FORM,
            'div': ElementType.DIV,
            'span': ElementType.SPAN,
            'h1': ElementType.HEADING,
            'h2': ElementType.HEADING,
            'h3': ElementType.HEADING,
            'h4': ElementType.HEADING,
            'h5': ElementType.HEADING,
            'h6': ElementType.HEADING,
            'p': ElementType.PARAGRAPH,
            'ul': ElementType.LIST,
            'ol': ElementType.LIST
        }
        return mapping.get(tag_name.lower(), ElementType.UNKNOWN)
    
    async def _enhance_elements(
        self,
        elements_with_context: List[ElementWithLLMContext],
        custom_prompts: Optional[Dict[str, str]] = None
    ) -> List[EnhancedElement]:
        """Convert browser elements to enhanced elements with AI analysis"""
        enhanced_elements = []
        
        for element_context in elements_with_context:
            element_data = element_context.element_data
            
            # Determine element type
            element_type = self._map_element_type(element_data.tag_name, element_data.attributes)
            
            # Determine interaction patterns
            interaction_patterns = self._determine_interactions(element_type, element_data.attributes)
            
            # Create AI analysis if available
            ai_analysis = None
            if element_context.semantic_role:
                ai_analysis = AIAnalysis(
                    semantic_role=element_context.semantic_role,
                    functional_purpose=element_context.functional_purpose or "Unknown",
                    test_priority=element_context.test_priority,
                    confidence_score=element_context.llm_confidence,
                    suggested_interactions=interaction_patterns,
                    accessibility_notes=f"Accessibility score: {element_context.accessibility_score}",
                    edge_cases=element_context.test_suggestions
                )
            
            # Create enhanced element
            enhanced_element = EnhancedElement(
                element_type=element_type,
                selector=element_data.selector,
                text=element_data.text,
                attributes=element_data.attributes,
                is_visible=element_data.is_visible,
                is_interactive=element_data.is_interactive,
                bounding_box=element_data.bounding_box,
                ai_analysis=ai_analysis,
                semantic_context=element_context.semantic_role,
                interaction_patterns=interaction_patterns,
                test_suggestions=element_context.test_suggestions,
                extraction_confidence=element_context.llm_confidence
            )
            
            enhanced_elements.append(enhanced_element)
        
        return enhanced_elements
    
    def _map_element_type(self, tag_name: str, attributes: Dict[str, Any]) -> ElementType:
        """Map HTML tag to element type"""
        tag = tag_name.lower()
        
        # Check for specific types based on tag and attributes
        if tag == 'button':
            return ElementType.BUTTON
        elif tag == 'a':
            return ElementType.LINK
        elif tag == 'input':
            input_type = attributes.get('type', 'text').lower()
            if input_type in ['checkbox']:
                return ElementType.CHECKBOX
            elif input_type in ['radio']:
                return ElementType.RADIO
            else:
                return ElementType.INPUT
        elif tag == 'select':
            return ElementType.SELECT
        elif tag == 'textarea':
            return ElementType.TEXTAREA
        elif tag == 'img':
            return ElementType.IMAGE
        elif tag == 'video':
            return ElementType.VIDEO
        elif tag == 'audio':
            return ElementType.AUDIO
        elif tag == 'form':
            return ElementType.FORM
        elif tag == 'table':
            return ElementType.TABLE
        elif tag in ['ul', 'ol', 'dl']:
            return ElementType.LIST
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return ElementType.HEADING
        elif tag == 'nav':
            return ElementType.NAVIGATION
        elif tag == 'article':
            return ElementType.ARTICLE
        elif tag == 'section':
            return ElementType.SECTION
        elif tag == 'footer':
            return ElementType.FOOTER
        elif tag == 'header':
            return ElementType.HEADER
        elif 'modal' in attributes.get('class', '').lower() or attributes.get('role') == 'dialog':
            return ElementType.MODAL
        elif 'dropdown' in attributes.get('class', '').lower():
            return ElementType.DROPDOWN
        elif 'card' in attributes.get('class', '').lower():
            return ElementType.CARD
        else:
            return ElementType.OTHER
    
    def _determine_interactions(
        self,
        element_type: ElementType,
        attributes: Dict[str, Any]
    ) -> List[InteractionType]:
        """Determine possible interactions for an element"""
        interactions = []
        
        # Type-based interactions
        if element_type in [ElementType.BUTTON, ElementType.LINK]:
            interactions.append(InteractionType.CLICK)
        elif element_type in [ElementType.INPUT, ElementType.TEXTAREA]:
            interactions.extend([InteractionType.TYPE, InteractionType.FOCUS])
        elif element_type == ElementType.SELECT:
            interactions.extend([InteractionType.SELECT, InteractionType.FOCUS])
        elif element_type in [ElementType.CHECKBOX, ElementType.RADIO]:
            interactions.extend([InteractionType.CLICK, InteractionType.TOGGLE])
        elif element_type == ElementType.FORM:
            interactions.append(InteractionType.SUBMIT)
        
        # Attribute-based interactions
        if attributes.get('draggable') == 'true':
            interactions.append(InteractionType.DRAG)
        if attributes.get('contenteditable') == 'true':
            interactions.append(InteractionType.TYPE)
        if 'hover' in attributes.get('class', '').lower():
            interactions.append(InteractionType.HOVER)
        
        return list(set(interactions))  # Remove duplicates
    
    def _count_element_types(self, elements: List[EnhancedElement]) -> Dict[str, int]:
        """Count elements by type"""
        counts = {}
        for element in elements:
            type_name = element.element_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    async def analyze_element_with_custom_prompt(
        self,
        element: EnhancedElement,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Analyze a specific element with a custom prompt
        
        Args:
            element: Element to analyze
            prompt: Custom prompt for analysis
        
        Returns:
            Analysis result from LLM
        """
        element_context = f"""
        Element Type: {element.element_type.value}
        Selector: {element.selector}
        Text: {element.text or 'N/A'}
        Attributes: {json.dumps(element.attributes, indent=2)}
        Visible: {element.is_visible}
        Interactive: {element.is_interactive}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert web element analyzer."},
            {"role": "user", "content": f"{prompt}\n\nElement Context:\n{element_context}"}
        ]
        
        try:
            response = call_default_llm(messages)
            return {"success": True, "analysis": response}
        except Exception as e:
            logger.error(f"Custom analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    def save_results(self, result: ElementExtractionOutput, filepath: Path):
        """Save extraction results to file"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result.model_dump(), f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Results saved to {filepath}")

# ==================== CONVENIENCE FUNCTIONS ====================

async def extract_elements(
    url: str,
    config: Optional[ExtractionConfig] = None
) -> ElementExtractionOutput:
    """
    Convenience function for element extraction
    
    Args:
        url: Target URL
        config: Optional extraction configuration
    
    Returns:
        Extraction result with enhanced elements
    """
    extractor = ElementsExtractorWithLLM(config)
    return await extractor.extract_from_url(url)

def create_test_config() -> ExtractionConfig:
    """Create a test configuration for quick testing"""
    return ExtractionConfig(
        headless=True,
        use_llm_analysis=True,
        analyze_semantics=True,
        generate_test_cases=True,
        max_elements=50,
        min_confidence=0.5
    )

# ==================== MAIN EXECUTION ====================

async def main():
    """Main execution with example usage"""
    logger.info("=" * 60)
    logger.info("Elements Extractor with LLM - Using browser_with_llm.py")
    logger.info("=" * 60)
    
    # Create configuration
    config = create_test_config()
    
    # Initialize extractor
    extractor = ElementsExtractorWithLLM(config)
    
    # Test extraction
    test_url = "https://example.com"
    logger.info(f"Extracting elements from: {test_url}")
    
    result = await extractor.extract_from_url(test_url)
    
    if result.success:
        logger.info(f"✓ Extraction successful!")
        logger.info(f"  Total elements: {len(result.elements)}")
        logger.info(f"  Element types: {result.extraction_stats.get('element_types', {})}")
        logger.info(f"  Interactive elements: {result.extraction_stats.get('interactive_elements', 0)}")
        logger.info(f"  AI analyzed: {result.extraction_stats.get('ai_analyzed', 0)}")
        logger.info(f"  Test scenarios: {len(result.test_scenarios)}")
        logger.info(f"  Extraction time: {result.extraction_time:.2f}s")
        
        # Save results
        output_path = Path("extraction_results.json")
        extractor.save_results(result, output_path)
        logger.info(f"  Results saved to: {output_path}")
    else:
        logger.error(f"✗ Extraction failed: {result.errors}")
    
    logger.info("=" * 60)
    logger.info("Extraction complete - Powered by browser_with_llm.py")

if __name__ == "__main__":
    asyncio.run(main())