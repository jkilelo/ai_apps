"""
Base navigator abstraction module.

This module defines the abstract base class for navigation strategies,
handling different approaches to page loading and waiting.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from ..config import NavigationConfig
from ..core import (
    NavigationResult,
    NavigationStrategy,
    BrowserState,
    NavigationCallback,
    DEFAULT_TIMEOUT,
)


class BaseNavigator(ABC):
    """
    Abstract base class for navigation strategies.
    
    This class defines the contract for different navigation approaches,
    allowing for flexible navigation behavior based on page types and requirements.
    """
    
    def __init__(self, config: NavigationConfig) -> None:
        """Initialize the navigator with configuration."""
        self.config = config
        self._callbacks: List[NavigationCallback] = []
        self._metrics: Dict[str, Any] = {}
    
    # ============================================================================
    # CALLBACK MANAGEMENT
    # ============================================================================
    
    def add_callback(self, callback: NavigationCallback) -> None:
        """Add a navigation callback."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: NavigationCallback) -> None:
        """Remove a navigation callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    async def _trigger_callbacks(self, event: str, data: Dict[str, Any]) -> None:
        """Trigger navigation callbacks."""
        for callback in self._callbacks:
            try:
                await callback(event, data)
            except Exception as e:
                # Log error but don't stop other callbacks
                self._log_error(f"Callback error: {e}")
    
    # ============================================================================
    # CORE NAVIGATION METHODS
    # ============================================================================
    
    @abstractmethod
    async def navigate_to(self, url: str, **kwargs) -> NavigationResult:
        """Navigate to a URL with specific strategy."""
        pass
    
    @abstractmethod
    async def wait_for_load(self, timeout: Optional[int] = None) -> NavigationResult:
        """Wait for page to load based on strategy."""
        pass
    
    @abstractmethod
    async def wait_for_ready(self, timeout: Optional[int] = None) -> bool:
        """Wait for page to be ready for interaction."""
        pass
    
    @abstractmethod
    async def check_load_state(self) -> Dict[str, Any]:
        """Check current page load state."""
        pass
    
    # ============================================================================
    # STRATEGY-SPECIFIC METHODS
    # ============================================================================
    
    @abstractmethod
    async def wait_for_dom_content_loaded(self, timeout: Optional[int] = None) -> bool:
        """Wait for DOM content to be loaded."""
        pass
    
    @abstractmethod
    async def wait_for_network_idle(self, timeout: Optional[int] = None, idle_time: int = 500) -> bool:
        """Wait for network to be idle."""
        pass
    
    @abstractmethod
    async def wait_for_all_resources(self, timeout: Optional[int] = None) -> bool:
        """Wait for all resources to load."""
        pass
    
    @abstractmethod
    async def wait_for_custom_condition(self, condition: Callable, timeout: Optional[int] = None) -> bool:
        """Wait for a custom condition to be met."""
        pass
    
    # ============================================================================
    # PAGE STATE DETECTION
    # ============================================================================
    
    @abstractmethod
    async def detect_spa_navigation(self) -> bool:
        """Detect if this is a Single Page Application navigation."""
        pass
    
    @abstractmethod
    async def detect_lazy_loading(self) -> bool:
        """Detect if the page uses lazy loading."""
        pass
    
    @abstractmethod
    async def detect_infinite_scroll(self) -> bool:
        """Detect if the page has infinite scroll."""
        pass
    
    @abstractmethod
    async def detect_dynamic_content(self) -> bool:
        """Detect if the page loads content dynamically."""
        pass
    
    # ============================================================================
    # ERROR HANDLING AND RECOVERY
    # ============================================================================
    
    @abstractmethod
    async def handle_navigation_timeout(self, url: str, timeout: int) -> NavigationResult:
        """Handle navigation timeout with recovery strategies."""
        pass
    
    @abstractmethod
    async def handle_network_error(self, error: Exception) -> NavigationResult:
        """Handle network errors during navigation."""
        pass
    
    @abstractmethod
    async def retry_navigation(self, url: str, max_retries: int = 3) -> NavigationResult:
        """Retry navigation with exponential backoff."""
        pass
    
    # ============================================================================
    # PERFORMANCE MONITORING
    # ============================================================================
    
    @abstractmethod
    async def measure_performance(self) -> Dict[str, Any]:
        """Measure navigation performance metrics."""
        pass
    
    @abstractmethod
    async def get_timing_metrics(self) -> Dict[str, float]:
        """Get detailed timing metrics."""
        pass
    
    @abstractmethod
    async def get_resource_metrics(self) -> Dict[str, Any]:
        """Get resource loading metrics."""
        pass
    
    # ============================================================================
    # ADAPTIVE NAVIGATION
    # ============================================================================
    
    @abstractmethod
    async def select_optimal_strategy(self, url: str, page_type: Optional[str] = None) -> NavigationStrategy:
        """Select the optimal navigation strategy for the page."""
        pass
    
    @abstractmethod
    async def learn_from_navigation(self, url: str, result: NavigationResult) -> None:
        """Learn from navigation results to improve future decisions."""
        pass
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _get_timeout(self, timeout: Optional[int] = None) -> int:
        """Get timeout value, using config default if not provided."""
        return timeout or self.config.timeouts.navigation or DEFAULT_TIMEOUT
    
    def _log_metric(self, name: str, value: Any) -> None:
        """Log a navigation metric."""
        self._metrics[name] = value
    
    def _log_error(self, message: str) -> None:
        """Log an error message."""
        # Implementation would use proper logging
        print(f"Navigator Error: {message}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all recorded metrics."""
        return self._metrics.copy()
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self._metrics.clear()


class LoadNavigator(BaseNavigator):
    """Navigator that waits for the 'load' event."""
    
    async def navigate_to(self, url: str, **kwargs) -> NavigationResult:
        """Navigate using load strategy."""
        # Implementation would be in concrete classes
        pass
    
    async def wait_for_load(self, timeout: Optional[int] = None) -> NavigationResult:
        """Wait for load event."""
        # Implementation would be in concrete classes
        pass


class NetworkIdleNavigator(BaseNavigator):
    """Navigator that waits for network idle."""
    
    def __init__(self, config: NavigationConfig) -> None:
        super().__init__(config)
        self.idle_time = config.wait_strategy.network_idle_timeout
    
    async def navigate_to(self, url: str, **kwargs) -> NavigationResult:
        """Navigate using network idle strategy."""
        # Implementation would be in concrete classes
        pass
    
    async def wait_for_load(self, timeout: Optional[int] = None) -> NavigationResult:
        """Wait for network idle."""
        # Implementation would be in concrete classes
        pass


class DOMContentLoadedNavigator(BaseNavigator):
    """Navigator that waits for DOM content loaded."""
    
    async def navigate_to(self, url: str, **kwargs) -> NavigationResult:
        """Navigate using DOM content loaded strategy."""
        # Implementation would be in concrete classes
        pass
    
    async def wait_for_load(self, timeout: Optional[int] = None) -> NavigationResult:
        """Wait for DOM content loaded."""
        # Implementation would be in concrete classes
        pass


class AdaptiveNavigator(BaseNavigator):
    """Navigator that adapts strategy based on page characteristics."""
    
    def __init__(self, config: NavigationConfig) -> None:
        super().__init__(config)
        self._navigators = {
            NavigationStrategy.LOAD: LoadNavigator(config),
            NavigationStrategy.NETWORK_IDLE: NetworkIdleNavigator(config),
            NavigationStrategy.DOMCONTENTLOADED: DOMContentLoadedNavigator(config),
        }
        self._current_navigator: Optional[BaseNavigator] = None
    
    async def navigate_to(self, url: str, **kwargs) -> NavigationResult:
        """Navigate using adaptive strategy selection."""
        strategy = await self.select_optimal_strategy(url, kwargs.get('page_type'))
        self._current_navigator = self._navigators[strategy]
        
        await self._trigger_callbacks('strategy_selected', {
            'url': url,
            'strategy': strategy.value
        })
        
        return await self._current_navigator.navigate_to(url, **kwargs)
    
    async def select_optimal_strategy(self, url: str, page_type: Optional[str] = None) -> NavigationStrategy:
        """Select optimal strategy based on URL and page type."""
        # Simple heuristics - could be enhanced with ML
        if page_type == 'spa':
            return NavigationStrategy.NETWORK_IDLE
        elif 'ajax' in url.lower() or 'api' in url.lower():
            return NavigationStrategy.DOMCONTENTLOADED
        else:
            return NavigationStrategy.LOAD