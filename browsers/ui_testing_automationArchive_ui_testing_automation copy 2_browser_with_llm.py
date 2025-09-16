#!/usr/bin/env python3
"""
Browser with LLM Integration - Definitive Production Module
===========================================================

This module combines the power of:
1. browser.py - Ultimate stealth browser with anti-detection
2. llm.py - Single source of truth for LLM operations  
3. prompts.py - Advanced prompt engineering strategies

This is the DEFINITIVE starting point for any module requiring browser + LLM + prompts.
All browser-based modules that need LLM should inherit from or use this module.

Architecture:
- Layer 0: browser.py, llm.py, prompts.py (independent base modules)
- Layer 1: THIS MODULE (integration layer)
- Layer 2+: Domain-specific modules (element extraction, test generation, etc.)

Author: Senior Software Integration Engineer (30+ years experience)
Date: 2024
Version: 1.0.0 Production
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime

# ============================================================================
# BASE MODULE IMPORTS (Layer 0)
# ============================================================================

# Import browser capabilities (no LLM dependencies)
from browser import (
    UltimateStealthBrowser,
    StealthConfig,
    StealthLevel,
    BrowserProfile,
    BrowserError,
    NavigationError,
    ExtractionError,
    ElementData,
    ExtractionResult as BrowserExtractionResult
)

# Import LLM capabilities (single source of truth)
from llm import call_default_llm, query_llm

# Import prompt engineering capabilities
from prompts import (
    PromptEngine,
    PromptStrategy,
    PromptRequest,
    StrategyOrchestrator,
    TaskType,
    ComplexityLevel
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# ENHANCED DATA MODELS (Integration Layer)
# ============================================================================

@dataclass
class LLMAnalysisResult:
    """Result from LLM analysis of browser content"""
    content: str
    confidence: float = 0.0
    strategy_used: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    analysis_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SemanticContext:
    """Semantic understanding of the page"""
    page_type: Optional[str] = None  # e-commerce, blog, form, etc.
    page_purpose: Optional[str] = None
    main_functionality: List[str] = field(default_factory=list)
    user_journey_stage: Optional[str] = None
    key_interactions: List[str] = field(default_factory=list)
    business_domain: Optional[str] = None
    technical_stack: List[str] = field(default_factory=list)
    accessibility_features: List[str] = field(default_factory=list)

@dataclass
class ElementWithLLMContext:
    """Enhanced element with LLM-derived context"""
    element_data: ElementData  # From browser.py
    semantic_role: Optional[str] = None
    functional_purpose: Optional[str] = None
    test_priority: float = 0.0
    test_suggestions: List[str] = field(default_factory=list)
    accessibility_score: float = 0.0
    interaction_patterns: List[str] = field(default_factory=list)
    llm_confidence: float = 0.0

@dataclass
class BrowserWithLLMConfig:
    """Configuration for browser with LLM integration"""
    # Browser configuration
    stealth_config: StealthConfig = field(default_factory=StealthConfig)
    
    # LLM configuration
    enable_llm_analysis: bool = True
    llm_provider: str = "default"  # Uses default from llm.py
    max_tokens: int = 4000
    temperature: float = 0.3
    
    # Prompt configuration
    enable_prompt_optimization: bool = True
    prompt_strategy: Optional[PromptStrategy] = None
    task_type: TaskType = TaskType.ANALYTICAL
    complexity_level: ComplexityLevel = ComplexityLevel.MODERATE
    
    # Analysis configuration
    analyze_semantics: bool = True
    analyze_accessibility: bool = True
    analyze_security: bool = True
    generate_test_suggestions: bool = True
    
    # Performance configuration
    cache_llm_results: bool = True
    parallel_analysis: bool = True
    max_concurrent_analyses: int = 3
    timeout: int = 30000

@dataclass
class ExtractionWithLLMResult:
    """Complete extraction result with LLM analysis"""
    url: str
    browser_result: BrowserExtractionResult  # From browser.py
    elements_with_context: List[ElementWithLLMContext] = field(default_factory=list)
    semantic_context: Optional[SemanticContext] = None
    llm_analysis: Optional[LLMAnalysisResult] = None
    page_insights: Dict[str, Any] = field(default_factory=dict)
    test_scenarios: List[Dict[str, Any]] = field(default_factory=list)
    success: bool = True
    errors: List[str] = field(default_factory=list)
    extraction_time: float = 0.0
    analysis_time: float = 0.0
    total_time: float = 0.0

# ============================================================================
# MAIN INTEGRATION CLASS
# ============================================================================

class BrowserWithLLM:
    """
    Definitive browser with LLM integration.
    
    This class combines:
    - UltimateStealthBrowser from browser.py (anti-detection, stealth)
    - LLM capabilities from llm.py (AI analysis)
    - Prompt strategies from prompts.py (optimized prompting)
    
    All modules requiring browser + LLM should use this as their foundation.
    """
    
    def __init__(self, config: Optional[BrowserWithLLMConfig] = None):
        """Initialize browser with LLM capabilities"""
        self.config = config or BrowserWithLLMConfig()
        
        # Initialize browser (from browser.py)
        self.browser = UltimateStealthBrowser(self.config.stealth_config)
        
        # Initialize prompt engine (from prompts.py)
        self.prompt_engine = PromptEngine() if self.config.enable_prompt_optimization else None
        self.strategy_orchestrator = StrategyOrchestrator() if self.config.enable_prompt_optimization else None
        
        # LLM response cache
        self._llm_cache: Dict[str, LLMAnalysisResult] = {}
        
        # Metrics tracking
        self.metrics = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'llm_analyses': 0,
            'cache_hits': 0,
            'total_elements_analyzed': 0,
            'average_extraction_time': 0.0,
            'average_analysis_time': 0.0
        }
        
        logger.info(f"BrowserWithLLM initialized with config: {self.config}")
    
    async def initialize(self) -> bool:
        """Initialize browser and validate LLM connection"""
        try:
            # Initialize browser
            await self.browser.initialize()
            
            # Test LLM connection
            if self.config.enable_llm_analysis:
                test_response = await self._test_llm_connection()
                if not test_response:
                    logger.warning("LLM connection test failed, continuing without LLM")
                    self.config.enable_llm_analysis = False
            
            logger.info("BrowserWithLLM initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    async def _test_llm_connection(self) -> bool:
        """Test LLM connection"""
        try:
            messages = [{"role": "user", "content": "Reply with 'OK'"}]
            response = await asyncio.to_thread(call_default_llm, messages)
            return bool(response)
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False
    
    async def extract_and_analyze(
        self,
        url: str,
        wait_for: str = 'domcontentloaded',
        extract_selectors: Optional[List[str]] = None
    ) -> ExtractionWithLLMResult:
        """
        Extract elements from URL and analyze with LLM.
        
        This is the main entry point for browser + LLM operations.
        """
        start_time = time.time()
        
        # Create placeholder browser result for initialization
        placeholder_browser_result = BrowserExtractionResult(
            url=url,
            success=False,
            elements=[],
            page_title="",
            extraction_time=0.0,
            errors=[],
            metadata={}
        )
        
        result = ExtractionWithLLMResult(url=url, browser_result=placeholder_browser_result)
        
        try:
            # Step 1: Browser extraction (using browser.py)
            extraction_start = time.time()
            browser_result = await self.browser.extract_elements(
                url=url
            )
            result.browser_result = browser_result
            result.extraction_time = time.time() - extraction_start
            
            if not browser_result.success:
                result.success = False
                result.errors.extend(browser_result.errors)
                return result
            
            # Step 2: LLM Analysis (if enabled)
            if self.config.enable_llm_analysis:
                analysis_start = time.time()
                
                # Analyze page semantics
                if self.config.analyze_semantics:
                    # Use page title as content for now, or could extract page text
                    page_content = browser_result.page_title or "No page content available"
                    result.semantic_context = await self._analyze_page_semantics(
                        page_content,
                        browser_result.metadata
                    )
                
                # Analyze individual elements with LLM
                result.elements_with_context = await self._analyze_elements_with_llm(
                    browser_result.elements
                )
                
                # Generate page insights
                result.page_insights = await self._generate_page_insights(
                    browser_result,
                    result.semantic_context
                )
                
                # Generate test scenarios
                if self.config.generate_test_suggestions:
                    result.test_scenarios = await self._generate_test_scenarios(
                        result.elements_with_context,
                        result.semantic_context
                    )
                
                result.analysis_time = time.time() - analysis_start
            
            # Update metrics
            self._update_metrics(result)
            
            result.total_time = time.time() - start_time
            result.success = True
            
            logger.info(f"Extraction and analysis complete for {url} in {result.total_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Extraction and analysis failed: {e}")
            result.success = False
            result.errors.append(str(e))
        
        return result
    
    async def _analyze_page_semantics(
        self,
        page_content: str,
        metadata: Dict[str, Any]
    ) -> SemanticContext:
        """Analyze page semantics with LLM"""
        try:
            # Create optimized prompt using prompts.py
            prompt = self._create_semantic_analysis_prompt(page_content, metadata)
            
            # Query LLM
            messages = [
                {"role": "system", "content": "You are a web page analyzer expert."},
                {"role": "user", "content": prompt}
            ]
            
            response = await asyncio.to_thread(call_default_llm, messages)
            
            # Parse response into SemanticContext
            context = self._parse_semantic_response(response)
            
            return context
            
        except Exception as e:
            logger.error(f"Semantic analysis failed: {e}")
            return SemanticContext()
    
    async def _analyze_elements_with_llm(
        self,
        elements: List[ElementData]
    ) -> List[ElementWithLLMContext]:
        """Analyze elements with LLM for enhanced context"""
        analyzed_elements = []
        
        # Batch elements for efficient LLM analysis
        batch_size = 10
        for i in range(0, len(elements), batch_size):
            batch = elements[i:i+batch_size]
            
            try:
                # Create batch analysis prompt
                prompt = self._create_element_analysis_prompt(batch)
                
                messages = [
                    {"role": "system", "content": "You are a UI testing expert."},
                    {"role": "user", "content": prompt}
                ]
                
                response = await asyncio.to_thread(call_default_llm, messages)
                
                # Parse and create enhanced elements
                analyzed_batch = self._parse_element_analysis(batch, response)
                analyzed_elements.extend(analyzed_batch)
                
            except Exception as e:
                logger.error(f"Element batch analysis failed: {e}")
                # Fallback: create basic enhanced elements without LLM
                for element in batch:
                    analyzed_elements.append(ElementWithLLMContext(element_data=element))
        
        return analyzed_elements
    
    async def _generate_page_insights(
        self,
        browser_result: BrowserExtractionResult,
        semantic_context: Optional[SemanticContext]
    ) -> Dict[str, Any]:
        """Generate comprehensive page insights"""
        insights = {
            'total_elements': len(browser_result.elements),
            'interactive_elements': 0,
            'forms_detected': 0,
            'navigation_elements': 0,
            'accessibility_score': 0.0,
            'performance_metrics': browser_result.metadata.get('performance_metrics', {}) if hasattr(browser_result, 'metadata') else {},
            'security_findings': [],
            'improvement_suggestions': []
        }
        
        if not self.config.enable_llm_analysis:
            return insights
        
        try:
            # Create comprehensive analysis prompt
            prompt = self._create_insights_prompt(browser_result, semantic_context)
            
            messages = [
                {"role": "system", "content": "You are a web quality assurance expert."},
                {"role": "user", "content": prompt}
            ]
            
            response = await asyncio.to_thread(call_default_llm, messages)
            
            # Parse insights from LLM response
            llm_insights = self._parse_insights_response(response)
            insights.update(llm_insights)
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
        
        return insights
    
    async def _generate_test_scenarios(
        self,
        elements: List[ElementWithLLMContext],
        semantic_context: Optional[SemanticContext]
    ) -> List[Dict[str, Any]]:
        """Generate test scenarios using LLM"""
        scenarios = []
        
        if not elements:
            return scenarios
        
        try:
            # Use prompt optimization from prompts.py
            if self.prompt_engine:
                request = PromptRequest(
                    task="Generate comprehensive test scenarios",
                    task_type=TaskType.CREATIVE,
                    complexity=self.config.complexity_level,
                    context={"elements": len(elements), "page_type": semantic_context.page_type if semantic_context else "unknown"}
                )
                optimized_prompt = self.prompt_engine.enhance(request)
                prompt = optimized_prompt.enhanced_prompt
            else:
                prompt = self._create_test_scenarios_prompt(elements, semantic_context)
            
            messages = [
                {"role": "system", "content": "You are a test automation expert."},
                {"role": "user", "content": prompt}
            ]
            
            response = await asyncio.to_thread(call_default_llm, messages)
            
            # Parse test scenarios
            scenarios = self._parse_test_scenarios(response)
            
        except Exception as e:
            logger.error(f"Test scenario generation failed: {e}")
        
        return scenarios
    
    # ========================================================================
    # PROMPT CREATION METHODS
    # ========================================================================
    
    def _create_semantic_analysis_prompt(self, page_content: str, metadata: Dict[str, Any]) -> str:
        """Create prompt for semantic analysis"""
        # Truncate content if too long
        max_content_length = 3000
        truncated_content = page_content[:max_content_length] if len(page_content) > max_content_length else page_content
        
        prompt = f"""
        Analyze this web page and provide semantic understanding:
        
        URL: {metadata.get('url', 'unknown')}
        Title: {metadata.get('title', 'unknown')}
        
        Page Content (truncated):
        {truncated_content}
        
        Please identify:
        1. Page type (e-commerce, blog, form, dashboard, etc.)
        2. Main purpose of the page
        3. Key functionalities available
        4. User journey stage (landing, browse, interact, checkout, etc.)
        5. Business domain
        6. Technical indicators (framework, libraries if detectable)
        
        Respond in JSON format:
        {{
            "page_type": "...",
            "page_purpose": "...",
            "main_functionality": [...],
            "user_journey_stage": "...",
            "business_domain": "...",
            "technical_stack": [...]
        }}
        """
        
        return prompt
    
    def _create_element_analysis_prompt(self, elements: List[ElementData]) -> str:
        """Create prompt for element analysis"""
        elements_info = []
        for elem in elements[:10]:  # Limit to prevent token overflow
            elements_info.append({
                'tag': elem.tag_name,
                'text': elem.text_content[:50] if hasattr(elem, 'text_content') and elem.text_content else '',
                'attributes': dict(list(elem.attributes.items())[:5])  # Limit attributes
            })
        
        prompt = f"""
        Analyze these UI elements for testing purposes:
        
        Elements:
        {json.dumps(elements_info, indent=2)}
        
        For each element, provide:
        1. Semantic role (navigation, form_input, action_button, etc.)
        2. Functional purpose
        3. Test priority (0-1)
        4. Test suggestions
        5. Accessibility considerations
        
        Respond in JSON format with an array of analyses.
        """
        
        return prompt
    
    def _create_insights_prompt(
        self,
        browser_result: BrowserExtractionResult,
        semantic_context: Optional[SemanticContext]
    ) -> str:
        """Create prompt for page insights"""
        context_info = asdict(semantic_context) if semantic_context else {}
        
        prompt = f"""
        Generate comprehensive insights for this web page:
        
        Page Context:
        {json.dumps(context_info, indent=2)}
        
        Statistics:
        - Total elements: {len(browser_result.elements)}
        - Page load time: {browser_result.metadata.get('performance_metrics', {}).get('page_load_time', 'unknown') if hasattr(browser_result, 'metadata') else 'unknown'}
        
        Provide insights on:
        1. Accessibility score and issues
        2. Security findings
        3. Performance improvements
        4. UX improvements
        5. Testing recommendations
        
        Respond in JSON format.
        """
        
        return prompt
    
    def _create_test_scenarios_prompt(
        self,
        elements: List[ElementWithLLMContext],
        semantic_context: Optional[SemanticContext]
    ) -> str:
        """Create prompt for test scenario generation"""
        # Select most important elements for test generation
        important_elements = sorted(
            elements,
            key=lambda x: x.test_priority,
            reverse=True
        )[:20]
        
        elements_summary = []
        for elem in important_elements:
            elements_summary.append({
                'tag': elem.element_data.tag_name,
                'role': elem.semantic_role,
                'purpose': elem.functional_purpose
            })
        
        prompt = f"""
        Generate test scenarios for this web page:
        
        Page Type: {semantic_context.page_type if semantic_context else 'unknown'}
        Key Elements:
        {json.dumps(elements_summary, indent=2)}
        
        Generate 5-10 test scenarios covering:
        1. Happy path user flows
        2. Edge cases
        3. Error handling
        4. Accessibility tests
        5. Security validations
        
        For each scenario provide:
        - Name
        - Description
        - Steps
        - Expected outcome
        - Priority (high/medium/low)
        
        Respond in JSON format.
        """
        
        return prompt
    
    # ========================================================================
    # PARSING METHODS
    # ========================================================================
    
    def _parse_semantic_response(self, response: str) -> SemanticContext:
        """Parse LLM response into SemanticContext"""
        try:
            data = json.loads(response)
            return SemanticContext(
                page_type=data.get('page_type'),
                page_purpose=data.get('page_purpose'),
                main_functionality=data.get('main_functionality', []),
                user_journey_stage=data.get('user_journey_stage'),
                business_domain=data.get('business_domain'),
                technical_stack=data.get('technical_stack', [])
            )
        except Exception as e:
            logger.error(f"Failed to parse semantic response: {e}")
            return SemanticContext()
    
    def _parse_element_analysis(
        self,
        elements: List[ElementData],
        response: str
    ) -> List[ElementWithLLMContext]:
        """Parse LLM element analysis response"""
        analyzed = []
        
        try:
            analyses = json.loads(response)
            if not isinstance(analyses, list):
                analyses = [analyses]
            
            for i, element in enumerate(elements):
                if i < len(analyses):
                    analysis = analyses[i]
                    analyzed.append(ElementWithLLMContext(
                        element_data=element,
                        semantic_role=analysis.get('semantic_role'),
                        functional_purpose=analysis.get('functional_purpose'),
                        test_priority=float(analysis.get('test_priority', 0.5)),
                        test_suggestions=analysis.get('test_suggestions', []),
                        accessibility_score=float(analysis.get('accessibility_score', 0.0)),
                        llm_confidence=0.8
                    ))
                else:
                    analyzed.append(ElementWithLLMContext(element_data=element))
                    
        except Exception as e:
            logger.error(f"Failed to parse element analysis: {e}")
            # Fallback: return elements without LLM enhancement
            analyzed = [ElementWithLLMContext(element_data=elem) for elem in elements]
        
        return analyzed
    
    def _parse_insights_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM insights response"""
        try:
            return json.loads(response)
        except Exception:
            return {}
    
    def _parse_test_scenarios(self, response: str) -> List[Dict[str, Any]]:
        """Parse test scenarios from LLM response"""
        try:
            scenarios = json.loads(response)
            if not isinstance(scenarios, list):
                scenarios = [scenarios]
            return scenarios
        except Exception:
            return []
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _update_metrics(self, result: ExtractionWithLLMResult):
        """Update performance metrics"""
        self.metrics['total_extractions'] += 1
        if result.success:
            self.metrics['successful_extractions'] += 1
        if result.llm_analysis:
            self.metrics['llm_analyses'] += 1
        self.metrics['total_elements_analyzed'] += len(result.elements_with_context)
        
        # Update averages
        n = self.metrics['total_extractions']
        self.metrics['average_extraction_time'] = (
            (self.metrics['average_extraction_time'] * (n-1) + result.extraction_time) / n
        )
        self.metrics['average_analysis_time'] = (
            (self.metrics['average_analysis_time'] * (n-1) + result.analysis_time) / n
        )
    
    async def navigate(self, url: str, wait_for: str = 'domcontentloaded') -> bool:
        """Navigate to URL (delegates to browser)"""
        return await self.browser.navigate(url, wait_for)
    
    async def cleanup(self):
        """Clean up browser and resources"""
        await self.browser.cleanup()
        self._llm_cache.clear()
        logger.info("BrowserWithLLM cleanup complete")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.metrics.copy()
    
    # ========================================================================
    # ADVANCED FEATURES
    # ========================================================================
    
    async def extract_with_strategy(
        self,
        url: str,
        strategy: PromptStrategy,
        custom_instructions: Optional[str] = None
    ) -> ExtractionWithLLMResult:
        """
        Extract using a specific prompt strategy from prompts.py
        """
        # Temporarily override strategy
        original_strategy = self.config.prompt_strategy
        self.config.prompt_strategy = strategy
        
        try:
            result = await self.extract_and_analyze(url)
            
            # Add custom analysis if provided
            if custom_instructions and result.success:
                additional_analysis = await self._custom_llm_analysis(
                    result,
                    custom_instructions,
                    strategy
                )
                result.page_insights['custom_analysis'] = additional_analysis
            
            return result
            
        finally:
            self.config.prompt_strategy = original_strategy
    
    async def _custom_llm_analysis(
        self,
        result: ExtractionWithLLMResult,
        instructions: str,
        strategy: PromptStrategy
    ) -> Dict[str, Any]:
        """Perform custom LLM analysis with specific instructions"""
        try:
            # Use prompt engine with specified strategy
            if self.prompt_engine:
                request = PromptRequest(
                    task=instructions,
                    task_type=TaskType.ANALYTICAL,
                    complexity=self.config.complexity_level,
                    strategy_override=strategy
                )
                enhanced = self.prompt_engine.enhance(request)
                prompt = enhanced.enhanced_prompt
            else:
                prompt = instructions
            
            messages = [
                {"role": "system", "content": "You are an expert analyst."},
                {"role": "user", "content": f"{prompt}\n\nPage URL: {result.url}\nElements found: {len(result.elements_with_context)}"}
            ]
            
            response = await asyncio.to_thread(call_default_llm, messages)
            
            try:
                return json.loads(response)
            except:
                return {"analysis": response}
                
        except Exception as e:
            logger.error(f"Custom analysis failed: {e}")
            return {"error": str(e)}
    
    async def parallel_extract_and_analyze(
        self,
        urls: List[str],
        max_concurrent: int = 3
    ) -> List[ExtractionWithLLMResult]:
        """
        Extract and analyze multiple URLs in parallel
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def extract_with_limit(url: str) -> ExtractionWithLLMResult:
            async with semaphore:
                return await self.extract_and_analyze(url)
        
        tasks = [extract_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create placeholder browser result for error case
                placeholder_browser_result = BrowserExtractionResult(
                    url=urls[i],
                    success=False,
                    elements=[],
                    page_title="",
                    extraction_time=0.0,
                    errors=[str(result)],
                    metadata={}
                )
                error_result = ExtractionWithLLMResult(url=urls[i], browser_result=placeholder_browser_result)
                error_result.success = False
                error_result.errors.append(str(result))
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def quick_extract_and_analyze(url: str) -> ExtractionWithLLMResult:
    """
    Quick extraction and analysis with default configuration
    """
    browser_llm = BrowserWithLLM()
    await browser_llm.initialize()
    
    try:
        result = await browser_llm.extract_and_analyze(url)
        return result
    finally:
        await browser_llm.cleanup()

async def extract_with_custom_config(
    url: str,
    stealth_level: StealthLevel = StealthLevel.MODERATE,
    enable_llm: bool = True,
    generate_tests: bool = True
) -> ExtractionWithLLMResult:
    """
    Extract with custom configuration
    """
    config = BrowserWithLLMConfig(
        stealth_config=StealthConfig(level=stealth_level),
        enable_llm_analysis=enable_llm,
        generate_test_suggestions=generate_tests
    )
    
    browser_llm = BrowserWithLLM(config)
    await browser_llm.initialize()
    
    try:
        result = await browser_llm.extract_and_analyze(url)
        return result
    finally:
        await browser_llm.cleanup()

# ============================================================================
# MAIN EXAMPLE
# ============================================================================

async def main():
    """Demonstration of integrated browser with LLM capabilities"""
    
    print("=" * 80)
    print("BROWSER WITH LLM - DEFINITIVE PRODUCTION MODULE")
    print("Combining: browser.py + llm.py + prompts.py")
    print("=" * 80)
    
    # Configure with stealth and LLM
    config = BrowserWithLLMConfig(
        stealth_config=StealthConfig(
            level=StealthLevel.MODERATE,
            headless=True,
            block_webrtc=True,
            spoof_canvas=True
        ),
        enable_llm_analysis=True,
        enable_prompt_optimization=True,
        analyze_semantics=True,
        generate_test_suggestions=True
    )
    
    # Initialize browser with LLM
    browser_llm = BrowserWithLLM(config)
    await browser_llm.initialize()
    
    try:
        # Test on example.com
        url = "https://example.com"
        print(f"\n[1] Extracting and analyzing: {url}")
        
        result = await browser_llm.extract_and_analyze(url)
        
        if result.success:
            print(f"✓ Extraction successful")
            print(f"  - Elements found: {len(result.browser_result.elements)}")
            print(f"  - Elements with LLM context: {len(result.elements_with_context)}")
            
            if result.semantic_context:
                print(f"  - Page type: {result.semantic_context.page_type}")
                print(f"  - Page purpose: {result.semantic_context.page_purpose}")
            
            if result.test_scenarios:
                print(f"  - Test scenarios generated: {len(result.test_scenarios)}")
            
            print(f"  - Extraction time: {result.extraction_time:.2f}s")
            print(f"  - Analysis time: {result.analysis_time:.2f}s")
            print(f"  - Total time: {result.total_time:.2f}s")
        else:
            print(f"✗ Extraction failed: {result.errors}")
        
        # Test with specific prompt strategy
        print(f"\n[2] Testing with Tree of Thoughts strategy")
        
        tot_result = await browser_llm.extract_with_strategy(
            url,
            PromptStrategy.TREE_OF_THOUGHTS,
            "Analyze the page for potential security vulnerabilities"
        )
        
        if tot_result.success and 'custom_analysis' in tot_result.page_insights:
            print(f"✓ Custom analysis completed")
            print(f"  - Security findings: {tot_result.page_insights['custom_analysis']}")
        
        # Show metrics
        print(f"\n[3] Performance Metrics")
        metrics = browser_llm.get_metrics()
        for key, value in metrics.items():
            print(f"  - {key}: {value}")
        
    finally:
        await browser_llm.cleanup()
    
    print("\n" + "=" * 80)
    print("INTEGRATION COMPLETE - Module ready for production use")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())