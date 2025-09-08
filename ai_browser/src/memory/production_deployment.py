"""Production deployment utilities for multi-tier memory system"""
import asyncio
import sys
import signal
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from contextlib import asynccontextmanager

from loguru import logger
from .memory_manager import MemoryManager
from .memory_config import ProductionMemoryConfig, create_memory_config


class MemorySystemDeployment:
    """Production deployment manager for memory system"""
    
    def __init__(self, config: Optional[ProductionMemoryConfig] = None):
        self.config = config or create_memory_config("production")
        self.memory_manager: Optional[MemoryManager] = None
        self._shutdown_event = asyncio.Event()
        self._maintenance_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> bool:
        """Initialize memory system for production"""
        try:
            logger.info("Initializing production memory system...")
            
            # Ensure directories exist
            self.config.ensure_directories()
            
            # Initialize memory manager
            self.memory_manager = MemoryManager(self.config.to_dict())
            success = await self.memory_manager.initialize()
            
            if not success:
                logger.error("Failed to initialize memory manager")
                return False
            
            # Start maintenance tasks
            await self._start_maintenance_tasks()
            
            # Setup graceful shutdown
            self._setup_signal_handlers()
            
            logger.info("Production memory system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize production memory system: {e}")
            return False
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())
        
        if sys.platform != "win32":  # Unix systems
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
    
    async def _start_maintenance_tasks(self):
        """Start background maintenance tasks"""
        if not self.memory_manager:
            return
        
        self._maintenance_task = asyncio.create_task(self._maintenance_loop())
        logger.info("Started memory system maintenance tasks")
    
    async def _maintenance_loop(self):
        """Background maintenance loop"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.retention.cleanup_interval_hours * 3600)
                
                if self._shutdown_event.is_set():
                    break
                
                logger.info("Starting scheduled maintenance...")
                
                # Perform cleanup
                await self.memory_manager.cleanup_old_data(
                    session_hours=self.config.retention.session_hours,
                    semantic_days=self.config.retention.semantic_days,
                    graph_days=self.config.retention.knowledge_days
                )
                
                # Optimize performance
                if self.memory_manager.router:
                    await self.memory_manager.router.optimize_performance()
                
                # Health check
                health = await self.memory_manager.health_check()
                logger.info(f"Memory system health: {health}")
                
                logger.info("Scheduled maintenance completed")
                
            except Exception as e:
                logger.error(f"Maintenance task error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        if not self.memory_manager:
            return {"status": "error", "message": "Memory manager not initialized"}
        
        try:
            # Basic health check
            health = await self.memory_manager.health_check()
            
            # Get statistics
            stats = await self.memory_manager.get_memory_statistics()
            
            # Performance metrics
            performance = {}
            if self.memory_manager.router:
                performance = self.memory_manager.router.get_performance_report()
            
            return {
                "status": "healthy" if all(health.values()) else "degraded",
                "tier_health": health,
                "statistics": stats,
                "performance": performance,
                "config": {
                    "environment": self.config.environment,
                    "cache_size": self.config.cache.max_size,
                    "retention_policy": {
                        "session_hours": self.config.retention.session_hours,
                        "semantic_days": self.config.retention.semantic_days,
                        "knowledge_days": self.config.retention.knowledge_days
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics for monitoring"""
        if not self.memory_manager:
            return {}
        
        try:
            # Memory statistics
            stats = await self.memory_manager.get_memory_statistics()
            
            # Performance metrics
            performance_report = {}
            if self.memory_manager.router:
                performance_report = self.memory_manager.router.get_performance_report()
            
            # System metrics
            import psutil
            process = psutil.Process()
            
            return {
                "memory_stats": stats,
                "performance": performance_report,
                "system": {
                    "memory_usage_mb": process.memory_info().rss / 1024 / 1024,
                    "cpu_percent": process.cpu_percent(),
                    "open_connections": len(process.connections()),
                    "uptime_seconds": (asyncio.get_event_loop().time() - process.create_time())
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e)}
    
    async def backup_data(self, backup_path: str) -> bool:
        """Backup memory data"""
        try:
            logger.info(f"Starting data backup to {backup_path}")
            
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup session database
            session_db = Path(self.config.session_db_path)
            if session_db.exists():
                import shutil
                shutil.copy2(session_db, backup_dir / "session.db")
                logger.info("Session database backed up")
            
            # TODO: Implement semantic memory and knowledge graph backups
            # This would require tier-specific backup methods
            
            logger.info("Data backup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    async def shutdown(self):
        """Graceful shutdown of memory system"""
        logger.info("Starting graceful shutdown of memory system...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Stop maintenance tasks
        if self._maintenance_task and not self._maintenance_task.done():
            self._maintenance_task.cancel()
            try:
                await self._maintenance_task
            except asyncio.CancelledError:
                pass
        
        # Close memory manager
        if self.memory_manager:
            await self.memory_manager.close()
            self.memory_manager = None
        
        logger.info("Memory system shutdown completed")
    
    @asynccontextmanager
    async def managed_deployment(self):
        """Context manager for managed deployment lifecycle"""
        try:
            success = await self.initialize()
            if not success:
                raise RuntimeError("Failed to initialize memory system")
            
            yield self
            
        finally:
            await self.shutdown()


async def deploy_production_memory(config: Optional[ProductionMemoryConfig] = None) -> MemorySystemDeployment:
    """Deploy production memory system"""
    deployment = MemorySystemDeployment(config)
    
    success = await deployment.initialize()
    if not success:
        raise RuntimeError("Failed to deploy production memory system")
    
    return deployment


async def main():
    """Main entry point for production deployment"""
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )
    
    # Create production configuration
    config = create_memory_config("production")
    
    # Deploy memory system
    deployment = None
    try:
        async with MemorySystemDeployment(config).managed_deployment() as deployment:
            logger.info("Production memory system is running...")
            
            # Run health checks periodically
            while True:
                await asyncio.sleep(300)  # 5 minutes
                
                health = await deployment.health_check()
                if health["status"] != "healthy":
                    logger.warning(f"Memory system health: {health['status']}")
                else:
                    logger.info("Memory system healthy")
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Production deployment error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())