"""
Unified Framework Core - Central orchestration and configuration
This creates a cohesive system from the individual components
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import yaml
import logging
from datetime import datetime


# ============================================================================
# CONFIGURATION SYSTEM
# ============================================================================

@dataclass
class BrowserConfig:
    """Browser configuration"""
    headless: bool = False
    max_instances: int = 3
    timeout: int = 30000
    shadow_dom_enabled: bool = True
    shadow_dom_max_depth: int = 5
    anti_bot_level: str = "maximum"


@dataclass
class ExtractionConfig:
    """Extraction configuration"""
    default_profile: str = "general"
    auto_profile: bool = True
    max_elements: int = 1000
    cache_enabled: bool = True
    cache_ttl: int = 3600


@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: str = "gemini"
    model: str = "gemini-2.5-pro"
    default_strategy: str = "qa_engineer_agent"
    max_tokens: int = 4000
    temperature: float = 0.7


@dataclass
class StorageConfig:
    """Storage configuration"""
    db_path: Path = field(default_factory=lambda: Path("extraction_history.db"))
    cleanup_days: int = 30
    deduplication: bool = True


@dataclass
class FrameworkConfig:
    """Complete framework configuration"""
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    extraction: ExtractionConfig = field(default_factory=ExtractionConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    
    @classmethod
    def from_yaml(cls, path: Path) -> 'FrameworkConfig':
        """Load configuration from YAML file"""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        return cls(
            browser=BrowserConfig(**data.get('browser', {})),
            extraction=ExtractionConfig(**data.get('extraction', {})),
            llm=LLMConfig(**data.get('llm', {})),
            storage=StorageConfig(**data.get('storage', {}))
        )
    
    def to_yaml(self, path: Path):
        """Save configuration to YAML file"""
        import dataclasses
        
        def to_dict(obj):
            if dataclasses.is_dataclass(obj):
                return {k: to_dict(v) for k, v in dataclasses.asdict(obj).items()}
            elif isinstance(obj, Path):
                return str(obj)
            return obj
        
        with open(path, 'w') as f:
            yaml.dump(to_dict(self), f, default_flow_style=False)


# ============================================================================
# EVENT SYSTEM
# ============================================================================

class EventType(str, Enum):
    """Standard event types"""
    EXTRACTION_START = "extraction.start"
    EXTRACTION_COMPLETE = "extraction.complete"
    EXTRACTION_ERROR = "extraction.error"
    
    FORMATTING_START = "formatting.start"
    FORMATTING_COMPLETE = "formatting.complete"
    
    TEST_GENERATION_START = "test_generation.start"
    TEST_GENERATION_COMPLETE = "test_generation.complete"
    
    BROWSER_INITIALIZED = "browser.initialized"
    BROWSER_CLOSED = "browser.closed"
    
    CACHE_HIT = "cache.hit"
    CACHE_MISS = "cache.miss"


class EventBus:
    """Central event system for component communication"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._logger = logging.getLogger(__name__)
    
    def on(self, event: str, handler: Callable):
        """Register event handler"""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
        self._logger.debug(f"Registered handler for {event}")
    
    def emit(self, event: str, data: Any = None):
        """Emit event to all listeners"""
        self._logger.debug(f"Emitting {event} with data: {data}")
        
        if event in self._handlers:
            for handler in self._handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(data))
                    else:
                        handler(data)
                except Exception as e:
                    self._logger.error(f"Error in handler for {event}: {e}")
    
    def off(self, event: str, handler: Callable):
        """Unregister event handler"""
        if event in self._handlers and handler in self._handlers[event]:
            self._handlers[event].remove(handler)


# ============================================================================
# BROWSER POOL MANAGER
# ============================================================================

class BrowserPoolManager:
    """Manage browser instances for parallel processing"""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
        self.pool: List[Any] = []
        self.available = asyncio.Queue(maxsize=config.max_instances)
        self.lock = asyncio.Lock()
        self._logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize browser pool"""
        from ..browser import UltimateStealthBrowser, StealthConfig
        
        for i in range(self.config.max_instances):
            browser_config = StealthConfig(
                headless=self.config.headless,
                shadow_dom_enabled=self.config.shadow_dom_enabled,
                shadow_dom_max_depth=self.config.shadow_dom_max_depth
            )
            browser = UltimateStealthBrowser(browser_config)
            await browser.initialize()
            self.pool.append(browser)
            await self.available.put(browser)
            self._logger.info(f"Initialized browser instance {i+1}/{self.config.max_instances}")
    
    async def acquire(self) -> Any:
        """Get available browser from pool"""
        browser = await self.available.get()
        self._logger.debug(f"Acquired browser from pool")
        return browser
    
    async def release(self, browser: Any):
        """Return browser to pool"""
        await self.available.put(browser)
        self._logger.debug(f"Released browser to pool")
    
    async def cleanup(self):
        """Clean up all browsers"""
        async with self.lock:
            for browser in self.pool:
                try:
                    await browser.cleanup()
                except Exception as e:
                    self._logger.error(f"Error cleaning up browser: {e}")
            self.pool.clear()


# ============================================================================
# UNIFIED PIPELINE
# ============================================================================

class WorkflowStep:
    """Single step in a workflow"""
    
    def __init__(self, name: str, func: Callable, **kwargs):
        self.name = name
        self.func = func
        self.kwargs = kwargs


@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    success: bool
    steps_completed: List[str]
    results: Dict[str, Any]
    errors: List[str]
    duration: float
    timestamp: datetime = field(default_factory=datetime.now)


class UnifiedPipeline:
    """Central orchestrator for all operations"""
    
    def __init__(self, config: FrameworkConfig):
        self.config = config
        self.event_bus = EventBus()
        self.browser_pool = BrowserPoolManager(config.browser)
        self._logger = logging.getLogger(__name__)
        
        # Component initialization deferred
        self._extractor = None
        self._formatter_registry = None
        self._test_generator = None
        self._storage = None
        self._cache = None
        
        # Setup event listeners
        self._setup_event_listeners()
    
    async def initialize(self):
        """Initialize all components"""
        # Initialize browser pool
        await self.browser_pool.initialize()
        
        # Initialize components
        from ..core.extractor import IntelligentExtractor
        from ..storage.sqlite_storage import SQLiteStorage
        from ..cache.memory_cache import MemoryCache
        from ..formatters import FORMATTERS
        from ..test_generation import LLMTestGenerator
        
        self._storage = SQLiteStorage(str(self.config.storage.db_path))
        self._cache = MemoryCache(default_ttl=self.config.extraction.cache_ttl)
        self._extractor = IntelligentExtractor(
            storage=self._storage,
            cache=self._cache if self.config.extraction.cache_enabled else None
        )
        self._formatter_registry = FORMATTERS
        self._test_generator = LLMTestGenerator(self.config.llm.default_strategy)
        
        self.event_bus.emit(EventType.BROWSER_INITIALIZED)
        self._logger.info("Unified pipeline initialized")
    
    def _setup_event_listeners(self):
        """Setup default event listeners"""
        # Log all major events
        self.event_bus.on(EventType.EXTRACTION_COMPLETE, 
                         lambda data: self._logger.info(f"Extraction complete: {data.get('element_count', 0)} elements"))
        self.event_bus.on(EventType.TEST_GENERATION_COMPLETE,
                         lambda data: self._logger.info(f"Test generation complete: {data.get('test_count', 0)} tests"))
        self.event_bus.on(EventType.EXTRACTION_ERROR,
                         lambda data: self._logger.error(f"Extraction error: {data}"))
    
    async def run_workflow(self, 
                          workflow_name: str,
                          **params) -> WorkflowResult:
        """Execute a named workflow"""
        
        workflows = {
            "extract_only": [
                WorkflowStep("extract", self._extract_step)
            ],
            "extract_and_format": [
                WorkflowStep("extract", self._extract_step),
                WorkflowStep("format", self._format_step)
            ],
            "extract_and_test": [
                WorkflowStep("extract", self._extract_step),
                WorkflowStep("format", self._format_step),
                WorkflowStep("generate_tests", self._generate_tests_step)
            ],
            "full_pipeline": [
                WorkflowStep("extract", self._extract_step),
                WorkflowStep("format", self._format_step),
                WorkflowStep("generate_tests", self._generate_tests_step),
                WorkflowStep("validate", self._validate_step)
            ]
        }
        
        if workflow_name not in workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow = workflows[workflow_name]
        results = {}
        steps_completed = []
        errors = []
        start_time = datetime.now()
        
        for step in workflow:
            try:
                self._logger.info(f"Executing step: {step.name}")
                result = await step.func(results, **params, **step.kwargs)
                results[step.name] = result
                steps_completed.append(step.name)
                self.event_bus.emit(f"{step.name}.complete", result)
            except Exception as e:
                error_msg = f"Error in step {step.name}: {str(e)}"
                self._logger.error(error_msg)
                errors.append(error_msg)
                self.event_bus.emit(f"{step.name}.error", {"error": str(e)})
                
                # Decide whether to continue or abort
                if step.name in ["extract"]:  # Critical steps
                    break
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return WorkflowResult(
            success=len(errors) == 0,
            steps_completed=steps_completed,
            results=results,
            errors=errors,
            duration=duration
        )
    
    async def _extract_step(self, context: Dict, **params) -> Dict[str, Any]:
        """Extraction workflow step"""
        url = params.get("url")
        profile = params.get("profile", self.config.extraction.default_profile)
        
        self.event_bus.emit(EventType.EXTRACTION_START, {"url": url, "profile": profile})
        
        # Get browser from pool
        browser = await self.browser_pool.acquire()
        
        try:
            # Use existing extraction logic
            # For now, simplified version
            await browser.navigate(url)
            page = browser.page
            
            # Extract elements (simplified)
            elements = []  # Would use actual extraction
            
            self.event_bus.emit(EventType.EXTRACTION_COMPLETE, {
                "element_count": len(elements),
                "url": url
            })
            
            return {
                "elements": elements,
                "url": url,
                "profile": profile
            }
        finally:
            await self.browser_pool.release(browser)
    
    async def _format_step(self, context: Dict, **params) -> Dict[str, Any]:
        """Formatting workflow step"""
        elements = context.get("extract", {}).get("elements", [])
        format_type = params.get("format_type", "llm_test")
        
        self.event_bus.emit(EventType.FORMATTING_START, {"format_type": format_type})
        
        from ..formatters import format_output
        formatted = format_output(elements, format_type, {"url": params.get("url")})
        
        self.event_bus.emit(EventType.FORMATTING_COMPLETE, {"format_type": format_type})
        
        return formatted
    
    async def _generate_tests_step(self, context: Dict, **params) -> Dict[str, Any]:
        """Test generation workflow step"""
        elements = context.get("extract", {}).get("elements", [])
        url = params.get("url")
        test_type = params.get("test_type", "comprehensive")
        
        self.event_bus.emit(EventType.TEST_GENERATION_START, {"test_type": test_type})
        
        tests = self._test_generator.generate_tests(elements, url, test_type)
        
        self.event_bus.emit(EventType.TEST_GENERATION_COMPLETE, {
            "test_count": len(tests.get("tests", []))
        })
        
        return tests
    
    async def _validate_step(self, context: Dict, **params) -> Dict[str, Any]:
        """Validation workflow step"""
        tests = context.get("generate_tests", {}).get("tests", [])
        elements = context.get("extract", {}).get("elements", [])
        
        # Validate generated tests
        validation_results = {
            "valid_selectors": 0,
            "invalid_selectors": 0,
            "total_tests": len(tests)
        }
        
        # Check if selectors in tests exist in elements
        element_selectors = {e.selector for e in elements}
        
        for test in tests:
            if isinstance(test, dict):
                test_selectors = test.get("selectors", [])
                for selector in test_selectors:
                    if selector in element_selectors:
                        validation_results["valid_selectors"] += 1
                    else:
                        validation_results["invalid_selectors"] += 1
        
        return validation_results
    
    async def cleanup(self):
        """Clean up all resources"""
        await self.browser_pool.cleanup()
        self.event_bus.emit(EventType.BROWSER_CLOSED)
        self._logger.info("Pipeline cleanup complete")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def create_unified_framework(config_path: Optional[Path] = None) -> UnifiedPipeline:
    """Create and initialize unified framework"""
    
    # Load or create config
    if config_path and config_path.exists():
        config = FrameworkConfig.from_yaml(config_path)
    else:
        config = FrameworkConfig()
    
    # Create pipeline
    pipeline = UnifiedPipeline(config)
    await pipeline.initialize()
    
    return pipeline


async def run_extraction_pipeline(url: str, 
                                 profile: str = "general",
                                 generate_tests: bool = True) -> WorkflowResult:
    """Simple function to run complete extraction pipeline"""
    
    pipeline = await create_unified_framework()
    
    try:
        workflow = "extract_and_test" if generate_tests else "extract_only"
        result = await pipeline.run_workflow(
            workflow,
            url=url,
            profile=profile
        )
        return result
    finally:
        await pipeline.cleanup()