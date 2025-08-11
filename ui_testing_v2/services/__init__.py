"""
Service initialization and dependency injection for UI Testing Framework v2
"""

import logging
from typing import Optional

from ..core.config import get_config, Config
from ..core.events import EventBus
from ..services.database import DatabaseManager
from ..services.cache import CacheService
from ..services.state_manager import StateManager
from ..services.migrations import MigrationManager
from ..ai_services import AIServiceFactory, PromptManager, ReasoningEngine

logger = logging.getLogger(__name__)


class ServiceContainer:
    """Service container for dependency injection"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        
        # Core services
        self.event_bus: Optional[EventBus] = None
        self.database_manager: Optional[DatabaseManager] = None
        self.cache_service: Optional[CacheService] = None
        self.migration_manager: Optional[MigrationManager] = None
        self.state_manager: Optional[StateManager] = None
        
        # AI services
        self.ai_service_factory: Optional[AIServiceFactory] = None
        self.prompt_manager: Optional[PromptManager] = None
        self.reasoning_engine: Optional[ReasoningEngine] = None
        
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all services"""
        if self._initialized:
            return
        
        logger.info("Initializing service container...")
        
        try:
            # Initialize core services in dependency order
            await self._initialize_event_bus()
            await self._initialize_database()
            await self._initialize_cache()
            await self._initialize_migrations()
            await self._initialize_state_manager()
            
            # Initialize AI services
            await self._initialize_ai_services()
            
            self._initialized = True
            logger.info("Service container initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize service container: {e}")
            await self.cleanup()
            raise
    
    async def _initialize_event_bus(self) -> None:
        """Initialize event bus"""
        self.event_bus = EventBus()
        await self.event_bus.initialize()
        logger.debug("Event bus initialized")
    
    async def _initialize_database(self) -> None:
        """Initialize database manager"""
        self.database_manager = DatabaseManager(self.config.database)
        await self.database_manager.initialize()
        logger.debug("Database manager initialized")
    
    async def _initialize_cache(self) -> None:
        """Initialize cache service"""
        self.cache_service = CacheService(self.config.cache)
        await self.cache_service.initialize()
        logger.debug("Cache service initialized")
    
    async def _initialize_migrations(self) -> None:
        """Initialize migration manager and ensure database is up to date"""
        self.migration_manager = MigrationManager(self.config.database)
        
        # Ensure database schema is current
        await self.migration_manager.async_ensure_current()
        logger.debug("Migration manager initialized")
    
    async def _initialize_state_manager(self) -> None:
        """Initialize state manager"""
        self.state_manager = StateManager(
            self.database_manager,
            self.event_bus
        )
        await self.state_manager.initialize()
        logger.debug("State manager initialized")
    
    async def _initialize_ai_services(self) -> None:
        """Initialize AI services"""
        # AI Service Factory
        self.ai_service_factory = AIServiceFactory(
            openai_config=self.config.ai.dict(),
            anthropic_config=self.config.ai.dict(),
            cache_service=self.cache_service
        )
        await self.ai_service_factory.initialize()
        
        # Prompt Manager
        self.prompt_manager = PromptManager(
            ai_config=self.config.ai,
            cache_service=self.cache_service
        )
        
        # Reasoning Engine
        self.reasoning_engine = ReasoningEngine(
            ai_service_factory=self.ai_service_factory,
            prompt_manager=self.prompt_manager,
            config=self.config.ai.dict()
        )
        
        logger.debug("AI services initialized")
    
    async def health_check(self) -> dict:
        """Check health of all services"""
        health = {
            "service_container": "healthy" if self._initialized else "not_initialized",
            "services": {}
        }
        
        if not self._initialized:
            return health
        
        # Check event bus
        if self.event_bus:
            health["services"]["event_bus"] = await self.event_bus.health_check()
        
        # Check database
        if self.database_manager:
            health["services"]["database"] = await self.database_manager.health_check()
        
        # Check cache
        if self.cache_service:
            health["services"]["cache"] = await self.cache_service.health_check()
        
        # Check state manager
        if self.state_manager:
            health["services"]["state_manager"] = await self.state_manager.health_check()
        
        # Check AI services
        if self.ai_service_factory:
            health["services"]["ai_services"] = await self.ai_service_factory.health_check()
        
        return health
    
    async def cleanup(self) -> None:
        """Cleanup all services"""
        logger.info("Cleaning up service container...")
        
        # Cleanup in reverse order of initialization
        if self.state_manager:
            await self.state_manager.cleanup()
        
        if self.cache_service:
            await self.cache_service.cleanup()
        
        if self.database_manager:
            await self.database_manager.cleanup()
        
        if self.event_bus:
            await self.event_bus.cleanup()
        
        if self.ai_service_factory:
            await self.ai_service_factory.cleanup()
        
        self._initialized = False
        logger.info("Service container cleaned up")
    
    # Convenience methods for getting services
    def get_database_manager(self) -> DatabaseManager:
        """Get database manager"""
        if not self.database_manager:
            raise RuntimeError("Database manager not initialized")
        return self.database_manager
    
    def get_cache_service(self) -> CacheService:
        """Get cache service"""
        if not self.cache_service:
            raise RuntimeError("Cache service not initialized")
        return self.cache_service
    
    def get_state_manager(self) -> StateManager:
        """Get state manager"""
        if not self.state_manager:
            raise RuntimeError("State manager not initialized")
        return self.state_manager
    
    def get_event_bus(self) -> EventBus:
        """Get event bus"""
        if not self.event_bus:
            raise RuntimeError("Event bus not initialized")
        return self.event_bus
    
    def get_ai_service_factory(self) -> AIServiceFactory:
        """Get AI service factory"""
        if not self.ai_service_factory:
            raise RuntimeError("AI service factory not initialized")
        return self.ai_service_factory
    
    def get_prompt_manager(self) -> PromptManager:
        """Get prompt manager"""
        if not self.prompt_manager:
            raise RuntimeError("Prompt manager not initialized")
        return self.prompt_manager
    
    def get_reasoning_engine(self) -> ReasoningEngine:
        """Get reasoning engine"""
        if not self.reasoning_engine:
            raise RuntimeError("Reasoning engine not initialized")
        return self.reasoning_engine


# Global service container instance
_service_container: Optional[ServiceContainer] = None


async def get_service_container() -> ServiceContainer:
    """Get the global service container instance"""
    global _service_container
    
    if _service_container is None:
        _service_container = ServiceContainer()
        await _service_container.initialize()
    
    return _service_container


async def initialize_services(config: Optional[Config] = None) -> ServiceContainer:
    """Initialize all services and return the container"""
    global _service_container
    
    if _service_container is not None:
        await _service_container.cleanup()
    
    _service_container = ServiceContainer(config)
    await _service_container.initialize()
    
    return _service_container


async def cleanup_services() -> None:
    """Cleanup all services"""
    global _service_container
    
    if _service_container is not None:
        await _service_container.cleanup()
        _service_container = None


# Convenience functions for getting individual services
async def get_database_manager() -> DatabaseManager:
    """Get database manager from service container"""
    container = await get_service_container()
    return container.get_database_manager()


async def get_cache_service() -> CacheService:
    """Get cache service from service container"""
    container = await get_service_container()
    return container.get_cache_service()


async def get_state_manager() -> StateManager:
    """Get state manager from service container"""
    container = await get_service_container()
    return container.get_state_manager()


async def get_event_bus() -> EventBus:
    """Get event bus from service container"""
    container = await get_service_container()
    return container.get_event_bus()


async def get_ai_service_factory() -> AIServiceFactory:
    """Get AI service factory from service container"""
    container = await get_service_container()
    return container.get_ai_service_factory()


async def get_prompt_manager() -> PromptManager:
    """Get prompt manager from service container"""
    container = await get_service_container()
    return container.get_prompt_manager()


async def get_reasoning_engine() -> ReasoningEngine:
    """Get reasoning engine from service container"""
    container = await get_service_container()
    return container.get_reasoning_engine()
