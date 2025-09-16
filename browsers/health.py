"""System health monitoring and diagnostics"""
import asyncio
import psutil
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

from loguru import logger


@dataclass
class SystemHealth:
    """System health status"""
    healthy: bool
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_free_gb: float
    uptime_seconds: float
    active_processes: int
    details: Dict[str, Any]


@dataclass
class ComponentHealth:
    """Individual component health status"""
    name: str
    healthy: bool
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    last_check: Optional[datetime] = None
    metadata: Dict[str, Any] = None


class HealthMonitor:
    """Comprehensive health monitoring system"""
    
    def __init__(self):
        self.start_time = time.time()
        self.component_checks = {}
        self.health_history = []
        self.max_history = 1000
        
        # System thresholds
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
        
        logger.info("Health monitor initialized")
    
    def register_component(self, name: str, check_func, interval: int = 60):
        """Register a component health check"""
        self.component_checks[name] = {
            "check_func": check_func,
            "interval": interval,
            "last_check": 0,
            "last_result": None
        }
        logger.info(f"Registered health check for component: {name}")
    
    async def check_system_health(self) -> SystemHealth:
        """Check overall system health"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_free_gb = disk.free / (1024**3)
            disk_used_percent = (disk.used / disk.total) * 100
            
            # System uptime
            uptime_seconds = time.time() - self.start_time
            
            # Process count
            active_processes = len(psutil.pids())
            
            # Health determination
            healthy = (
                cpu_percent < self.cpu_threshold and
                memory_percent < self.memory_threshold and
                disk_used_percent < self.disk_threshold
            )
            
            health = SystemHealth(
                healthy=healthy,
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_gb=memory_available_gb,
                disk_free_gb=disk_free_gb,
                uptime_seconds=uptime_seconds,
                active_processes=active_processes,
                details={
                    "disk_used_percent": disk_used_percent,
                    "cpu_count": psutil.cpu_count(),
                    "memory_total_gb": memory.total / (1024**3),
                    "disk_total_gb": disk.total / (1024**3)
                }
            )
            
            # Store in history
            self.health_history.append(health)
            if len(self.health_history) > self.max_history:
                self.health_history = self.health_history[-self.max_history:]
            
            return health
            
        except Exception as e:
            logger.error(f"Failed to check system health: {e}")
            return SystemHealth(
                healthy=False,
                timestamp=datetime.now(),
                cpu_percent=0,
                memory_percent=0,
                memory_available_gb=0,
                disk_free_gb=0,
                uptime_seconds=0,
                active_processes=0,
                details={"error": str(e)}
            )
    
    async def check_browser_health(self) -> ComponentHealth:
        """Check browser component health"""
        try:
            # This would be implemented based on your browser manager
            # For now, return a placeholder
            return ComponentHealth(
                name="browser",
                healthy=True,
                response_time_ms=50.0,
                last_check=datetime.now(),
                metadata={"status": "active", "contexts": 1}
            )
        except Exception as e:
            return ComponentHealth(
                name="browser",
                healthy=False,
                error_message=str(e),
                last_check=datetime.now()
            )
    
    async def check_memory_layers_health(self) -> Dict[str, ComponentHealth]:
        """Check health of all memory layers"""
        results = {}
        
        # Session memory (SQLite)
        try:
            import sqlite3
            db_path = Path(".claude/memory/session.db")
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                
                results["session_memory"] = ComponentHealth(
                    name="session_memory",
                    healthy=True,
                    response_time_ms=10.0,
                    last_check=datetime.now(),
                    metadata={"database_tables": table_count, "file_size_mb": db_path.stat().st_size / (1024*1024)}
                )
            else:
                results["session_memory"] = ComponentHealth(
                    name="session_memory",
                    healthy=False,
                    error_message="Database file not found",
                    last_check=datetime.now()
                )
        except Exception as e:
            results["session_memory"] = ComponentHealth(
                name="session_memory",
                healthy=False,
                error_message=str(e),
                last_check=datetime.now()
            )
        
        # Semantic memory (Qdrant) - check if container is running
        try:
            # This would check your Qdrant container
            # For now, assume it's healthy if container is accessible
            results["semantic_memory"] = ComponentHealth(
                name="semantic_memory",
                healthy=True,  # Would check actual connection
                response_time_ms=100.0,
                last_check=datetime.now(),
                metadata={"collections": [], "vectors": 0}
            )
        except Exception as e:
            results["semantic_memory"] = ComponentHealth(
                name="semantic_memory",
                healthy=False,
                error_message=str(e),
                last_check=datetime.now()
            )
        
        # Knowledge graph (FalkorDB) - check if container is running
        try:
            # This would check your FalkorDB container on port 6379
            results["knowledge_graph"] = ComponentHealth(
                name="knowledge_graph",
                healthy=True,  # Would check actual connection
                response_time_ms=80.0,
                last_check=datetime.now(),
                metadata={"nodes": 0, "relationships": 0}
            )
        except Exception as e:
            results["knowledge_graph"] = ComponentHealth(
                name="knowledge_graph",
                healthy=False,
                error_message=str(e),
                last_check=datetime.now()
            )
        
        return results
    
    async def check_llm_providers_health(self) -> Dict[str, ComponentHealth]:
        """Check health of LLM providers"""
        results = {}
        
        providers = ["openai", "anthropic", "google"]
        
        for provider in providers:
            try:
                # This would make a simple API call to check provider health
                # For now, simulate based on API key availability
                api_key_env = f"{provider.upper()}_API_KEY"
                import os
                has_key = os.getenv(api_key_env) is not None
                
                results[provider] = ComponentHealth(
                    name=f"llm_{provider}",
                    healthy=has_key,
                    response_time_ms=200.0 if has_key else None,
                    error_message=None if has_key else f"No API key found for {api_key_env}",
                    last_check=datetime.now(),
                    metadata={"api_key_configured": has_key}
                )
            except Exception as e:
                results[provider] = ComponentHealth(
                    name=f"llm_{provider}",
                    healthy=False,
                    error_message=str(e),
                    last_check=datetime.now()
                )
        
        return results
    
    async def check_container_health(self) -> Dict[str, ComponentHealth]:
        """Check health of containerized services"""
        results = {}
        
        # Check if containers are running via podman
        try:
            import subprocess
            result = subprocess.run(
                ["podman", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                containers = json.loads(result.stdout) if result.stdout.strip() else []
                
                # Check for specific containers
                container_map = {
                    "falkordb": {"port": 6379, "service": "knowledge_graph"},
                    "meilisearch": {"port": 7700, "service": "search"},
                    "qdrant": {"port": 6333, "service": "vector_db"}
                }
                
                running_containers = {c.get("Names", [""])[0]: c for c in containers}
                
                for name, config in container_map.items():
                    if any(name in container_name for container_name in running_containers.keys()):
                        container = next(c for c_name, c in running_containers.items() if name in c_name)
                        results[name] = ComponentHealth(
                            name=name,
                            healthy=container.get("State") == "running",
                            last_check=datetime.now(),
                            metadata={
                                "status": container.get("Status"),
                                "port": config["port"],
                                "service": config["service"]
                            }
                        )
                    else:
                        results[name] = ComponentHealth(
                            name=name,
                            healthy=False,
                            error_message="Container not found",
                            last_check=datetime.now()
                        )
            else:
                # Podman not available or error
                for name in ["falkordb", "meilisearch", "qdrant"]:
                    results[name] = ComponentHealth(
                        name=name,
                        healthy=False,
                        error_message="Podman not accessible",
                        last_check=datetime.now()
                    )
        
        except Exception as e:
            logger.error(f"Failed to check container health: {e}")
            for name in ["falkordb", "meilisearch", "qdrant"]:
                results[name] = ComponentHealth(
                    name=name,
                    healthy=False,
                    error_message=str(e),
                    last_check=datetime.now()
                )
        
        return results
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check of all components"""
        start_time = time.time()
        
        # Run all health checks concurrently
        system_health_task = asyncio.create_task(self.check_system_health())
        browser_health_task = asyncio.create_task(self.check_browser_health())
        memory_health_task = asyncio.create_task(self.check_memory_layers_health())
        llm_health_task = asyncio.create_task(self.check_llm_providers_health())
        container_health_task = asyncio.create_task(self.check_container_health())
        
        # Wait for all checks to complete
        system_health = await system_health_task
        browser_health = await browser_health_task
        memory_health = await memory_health_task
        llm_health = await llm_health_task
        container_health = await container_health_task
        
        check_duration = (time.time() - start_time) * 1000  # ms
        
        # Aggregate results
        all_components = {
            "browser": browser_health,
            **memory_health,
            **llm_health,
            **container_health
        }
        
        healthy_components = sum(1 for c in all_components.values() if c.healthy)
        total_components = len(all_components)
        overall_healthy = system_health.healthy and healthy_components == total_components
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_healthy": overall_healthy,
            "check_duration_ms": check_duration,
            "system": {
                "healthy": system_health.healthy,
                "cpu_percent": system_health.cpu_percent,
                "memory_percent": system_health.memory_percent,
                "memory_available_gb": system_health.memory_available_gb,
                "disk_free_gb": system_health.disk_free_gb,
                "uptime_seconds": system_health.uptime_seconds,
                "active_processes": system_health.active_processes
            },
            "components": {
                name: {
                    "healthy": comp.healthy,
                    "response_time_ms": comp.response_time_ms,
                    "error_message": comp.error_message,
                    "last_check": comp.last_check.isoformat() if comp.last_check else None,
                    "metadata": comp.metadata or {}
                }
                for name, comp in all_components.items()
            },
            "summary": {
                "healthy_components": healthy_components,
                "total_components": total_components,
                "health_percentage": (healthy_components / total_components) * 100
            }
        }
    
    async def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trends over specified period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_health = [h for h in self.health_history if h.timestamp > cutoff_time]
        
        if not recent_health:
            return {"error": "No health data available for specified period"}
        
        # Calculate averages
        avg_cpu = sum(h.cpu_percent for h in recent_health) / len(recent_health)
        avg_memory = sum(h.memory_percent for h in recent_health) / len(recent_health)
        
        # Calculate health percentage over time
        healthy_checks = sum(1 for h in recent_health if h.healthy)
        health_percentage = (healthy_checks / len(recent_health)) * 100
        
        return {
            "period_hours": hours,
            "data_points": len(recent_health),
            "health_percentage": health_percentage,
            "averages": {
                "cpu_percent": avg_cpu,
                "memory_percent": avg_memory
            },
            "peaks": {
                "max_cpu": max(h.cpu_percent for h in recent_health),
                "max_memory": max(h.memory_percent for h in recent_health),
                "min_disk_free": min(h.disk_free_gb for h in recent_health)
            }
        }
    
    def export_health_report(self, filepath: Optional[Path] = None) -> Path:
        """Export comprehensive health report"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = Path(f".claude/monitoring/health_report_{timestamp}.json")
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # This would be called asynchronously in practice
        import json
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "system_info": {
                "uptime_hours": (time.time() - self.start_time) / 3600,
                "python_version": f"{psutil.version_info}",
                "platform": f"{psutil.version_info}"
            },
            "recent_health": [
                {
                    "timestamp": h.timestamp.isoformat(),
                    "healthy": h.healthy,
                    "cpu_percent": h.cpu_percent,
                    "memory_percent": h.memory_percent,
                    "memory_available_gb": h.memory_available_gb
                }
                for h in self.health_history[-100:]  # Last 100 checks
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Health report exported to {filepath}")
        return filepath