"""
Service Container for UI Testing Framework v2
"""

import logging
from typing import Optional
from functools import lru_cache

from .ai_services import AIServiceFactory
from .cache import CacheService
from .database import DatabaseManager
from .state_manager import StateManager

logger = logging.getLogger(__name__)


class ServiceContainer:
    """Container for all framework services"""
    
    def __init__(self, config):
        self.config = config
        self._ai_service_factory = None
        self._cache_service = None
        self._database_manager = None
        self._state_manager = None
        logger.info("ServiceContainer initialized")
    
    def get_ai_service_factory(self) -> AIServiceFactory:
        """Get AI service factory instance"""
        if self._ai_service_factory is None:
            self._ai_service_factory = AIServiceFactory(self.config)
        return self._ai_service_factory
    
    def get_cache_service(self) -> CacheService:
        """Get cache service instance"""
        if self._cache_service is None:
            self._cache_service = CacheService(self.config)
        return self._cache_service
    
    def get_database_manager(self) -> DatabaseManager:
        """Get database manager instance"""
        if self._database_manager is None:
            self._database_manager = DatabaseManager(self.config)
        return self._database_manager
    
    def get_state_manager(self) -> StateManager:
        """Get state manager instance"""
        if self._state_manager is None:
            self._state_manager = StateManager(self.config)
        return self._state_manager
    
    async def shutdown(self):
        """Shutdown all services gracefully"""
        logger.info("Shutting down services...")
        
        # Add any cleanup logic here
        # For example, close database connections, save state, etc.
        
        logger.info("Services shutdown complete")


# Global service container instance
_service_container: Optional[ServiceContainer] = None


@lru_cache()
def get_service_container() -> ServiceContainer:
    """Get the global service container instance"""
    global _service_container
    
    if _service_container is None:
        from ..core.config import get_config
        config = get_config()
        _service_container = ServiceContainer(config)
    
    return _service_container


def reset_service_container():
    """Reset the service container (mainly for testing)"""
    global _service_container
    _service_container = None
    get_service_container.cache_clear()