"""Plugin system interfaces and base classes for the AI browser extensibility layer.

This module defines the core interfaces that all plugins must implement, including
specialized interfaces for different plugin types (stealth, analysis, optimization).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from playwright.async_api import BrowserContext, Page


class PluginState(Enum):
    """Plugin lifecycle states"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class PluginType(Enum):
    """Plugin categories"""
    STEALTH = "stealth"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    CUSTOM = "custom"


class PluginMetadata(BaseModel):
    """Plugin metadata and configuration"""
    name: str = Field(..., description="Unique plugin identifier")
    version: str = Field(..., description="Plugin version (semver)")
    author: str = Field(..., description="Plugin author")
    description: str = Field(..., description="Plugin description")
    plugin_type: PluginType = Field(..., description="Plugin category")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies")
    min_framework_version: str = Field(..., description="Minimum browser framework version")
    max_framework_version: Optional[str] = Field(None, description="Maximum framework version")
    priority: int = Field(50, description="Execution priority (lower = earlier)")
    enabled: bool = Field(True, description="Whether plugin is enabled by default")
    hot_reload: bool = Field(True, description="Whether plugin supports hot reloading")
    sandbox_permissions: Dict[str, bool] = Field(
        default_factory=lambda: {
            "network": False,
            "filesystem": False,
            "subprocess": False,
            "import_all": False
        },
        description="Sandbox permission requirements"
    )
    config_schema: Optional[Dict[str, Any]] = Field(None, description="Configuration schema")
    hooks: List[str] = Field(default_factory=list, description="Hook names this plugin listens to")


@dataclass
class PluginContext:
    """Context passed to plugins during execution"""
    plugin_name: str
    config: Dict[str, Any]
    browser_context: Optional[BrowserContext] = None
    page: Optional[Page] = None
    session_data: Dict[str, Any] = None
    shared_state: Dict[str, Any] = None


class PluginResult(BaseModel):
    """Result returned by plugin operations"""
    success: bool = Field(..., description="Whether operation succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    modified_context: Optional[Dict[str, Any]] = Field(None, description="Modified context data")
    continue_chain: bool = Field(True, description="Whether to continue plugin chain")


class IPlugin(ABC):
    """Base interface that all plugins must implement"""
    
    @abstractmethod
    async def initialize(self, context: PluginContext) -> PluginResult:
        """Initialize plugin with context and configuration
        
        Args:
            context: Plugin execution context
            
        Returns:
            PluginResult indicating success/failure of initialization
        """
        pass
    
    @abstractmethod
    async def execute(self, context: PluginContext, **kwargs) -> PluginResult:
        """Execute plugin main functionality
        
        Args:
            context: Plugin execution context
            **kwargs: Additional execution parameters
            
        Returns:
            PluginResult with execution results
        """
        pass
    
    @abstractmethod
    async def cleanup(self, context: PluginContext) -> PluginResult:
        """Cleanup plugin resources
        
        Args:
            context: Plugin execution context
            
        Returns:
            PluginResult indicating cleanup success
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata and configuration
        
        Returns:
            PluginMetadata object with plugin information
        """
        pass
    
    @abstractmethod
    def is_compatible(self, framework_version: str) -> bool:
        """Check if plugin is compatible with framework version
        
        Args:
            framework_version: Current framework version
            
        Returns:
            True if compatible, False otherwise
        """
        pass
    
    @abstractmethod
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if config is valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def on_hook(self, hook_name: str, context: PluginContext, data: Any) -> PluginResult:
        """Handle hook events
        
        Args:
            hook_name: Name of the triggered hook
            context: Plugin execution context
            data: Hook-specific data
            
        Returns:
            PluginResult with hook processing results
        """
        pass


class IStealthPlugin(IPlugin):
    """Interface for stealth/evasion plugins"""
    
    @abstractmethod
    async def apply_to_context(self, browser_context: BrowserContext, config: Dict[str, Any]) -> PluginResult:
        """Apply stealth modifications to browser context
        
        Args:
            browser_context: Playwright browser context
            config: Plugin configuration
            
        Returns:
            PluginResult indicating success/failure
        """
        pass
    
    @abstractmethod
    async def apply_to_page(self, page: Page, config: Dict[str, Any]) -> PluginResult:
        """Apply stealth modifications to specific page
        
        Args:
            page: Playwright page object
            config: Plugin configuration
            
        Returns:
            PluginResult indicating success/failure
        """
        pass
    
    @abstractmethod
    async def test_evasion(self, page: Page) -> Dict[str, Any]:
        """Test effectiveness of evasion techniques
        
        Args:
            page: Page to test on
            
        Returns:
            Dictionary with test results
        """
        pass
    
    @abstractmethod
    def get_evasion_techniques(self) -> List[str]:
        """Get list of evasion techniques implemented
        
        Returns:
            List of technique names
        """
        pass


class IAnalysisPlugin(IPlugin):
    """Interface for page analysis plugins"""
    
    @abstractmethod
    async def analyze_page(self, page: Page, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze page structure and content
        
        Args:
            page: Page to analyze
            config: Analysis configuration
            
        Returns:
            Analysis results dictionary
        """
        pass
    
    @abstractmethod
    async def extract_elements(self, page: Page, selector_strategy: str) -> List[Dict[str, Any]]:
        """Extract interactive elements from page
        
        Args:
            page: Page to extract from
            selector_strategy: Strategy for element selection
            
        Returns:
            List of element information dictionaries
        """
        pass
    
    @abstractmethod
    async def assess_complexity(self, page: Page) -> Dict[str, float]:
        """Assess page complexity metrics
        
        Args:
            page: Page to assess
            
        Returns:
            Complexity metrics dictionary
        """
        pass


class IOptimizationPlugin(IPlugin):
    """Interface for performance optimization plugins"""
    
    @abstractmethod
    async def optimize_page_load(self, context: BrowserContext, config: Dict[str, Any]) -> PluginResult:
        """Optimize page loading performance
        
        Args:
            context: Browser context to optimize
            config: Optimization configuration
            
        Returns:
            PluginResult with optimization results
        """
        pass
    
    @abstractmethod
    async def optimize_memory_usage(self) -> PluginResult:
        """Optimize memory usage
        
        Returns:
            PluginResult with memory optimization results
        """
        pass
    
    @abstractmethod
    async def get_performance_metrics(self, page: Page) -> Dict[str, float]:
        """Get performance metrics for page
        
        Args:
            page: Page to measure
            
        Returns:
            Performance metrics dictionary
        """
        pass


class IHookListener(ABC):
    """Interface for hook event listeners"""
    
    @abstractmethod
    async def on_hook_triggered(
        self,
        hook_name: str,
        context: PluginContext,
        data: Any
    ) -> Union[Any, Awaitable[Any]]:
        """Handle hook event
        
        Args:
            hook_name: Name of triggered hook
            context: Plugin context
            data: Hook data
            
        Returns:
            Modified data or result
        """
        pass
    
    @abstractmethod
    def get_hook_priority(self, hook_name: str) -> int:
        """Get priority for specific hook
        
        Args:
            hook_name: Hook name
            
        Returns:
            Priority value (lower = earlier execution)
        """
        pass


class PluginException(Exception):
    """Base exception for plugin errors"""
    
    def __init__(self, plugin_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.plugin_name = plugin_name
        self.message = message
        self.details = details or {}
        super().__init__(f"Plugin '{plugin_name}': {message}")


class PluginLoadError(PluginException):
    """Exception raised when plugin loading fails"""
    pass


class PluginExecutionError(PluginException):
    """Exception raised during plugin execution"""
    pass


class PluginValidationError(PluginException):
    """Exception raised when plugin validation fails"""
    pass


class PluginSandboxViolation(PluginException):
    """Exception raised when plugin violates sandbox restrictions"""
    pass


# Type aliases for convenience
PluginFactory = Callable[[], IPlugin]
HookCallback = Callable[[str, PluginContext, Any], Awaitable[Any]]