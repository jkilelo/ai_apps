"""
Components package for UI Testing Framework v2.
Contains all major components for test automation.
"""

"""
Components package for UI Testing Framework v2.
Contains all major components for test automation.
"""

# Phase 1 Day 4 - Element Extraction Components
from .browser_manager import BrowserManager, ElementInteractionManager
from .element_extraction.unified_extractor import UnifiedElementExtractor as ElementExtractor
from .element_extraction.optimized_extractor_v2 import UnifiedElementExtractor as ElementExtractorV2
from .element_analysis import ElementAnalysisService
from .element_extraction_component import ElementExtractionComponent

# Phase 1 Day 5 - Test Case Generation Components
from .test_case_generator import TestCaseGenerationService, TestCaseGenerationComponent

# Future components will be added here
# from .test_executor import TestExecutor
# from .results_analyzer import ResultsAnalyzer

__all__ = [
    # Phase 1 Day 4 - Element Extraction
    'BrowserManager',
    'ElementInteractionManager', 
    'ElementExtractor',
    'ElementExtractorV2',
    'ElementAnalysisService',
    'ElementExtractionComponent',
    
    # Phase 1 Day 5 - Test Case Generation
    'TestCaseGenerationService',
    'TestCaseGenerationComponent',
    
    # Future components
    # 'TestExecutor',
    # 'ResultsAnalyzer'
]
