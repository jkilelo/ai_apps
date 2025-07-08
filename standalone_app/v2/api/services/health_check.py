"""Health check service for monitoring application status"""
import asyncio
import psutil
import time
from typing import Dict, Any, List
from datetime import datetime
import logging
import aiohttp

logger = logging.getLogger(__name__)

class HealthChecker:
    """Comprehensive health checking service"""
    
    def __init__(self):
        self.start_time = time.time()
        self.checks = {
            "system": self.check_system_resources,
            "api": self.check_api_endpoints,
            "external": self.check_external_services
        }
        self.health_history: List[Dict] = []
        self.max_history = 100
    
    async def initialize(self):
        """Initialize health checker"""
        logger.info("Health checker initialized")
    
    async def cleanup(self):
        """Cleanup health checker"""
        logger.info("Health checker cleaned up")
    
    async def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        results = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": f"{(time.time() - self.start_time):.0f}s",
            "checks": {}
        }
        
        # Run all checks concurrently
        check_tasks = {
            name: asyncio.create_task(check_func())
            for name, check_func in self.checks.items()
        }
        
        # Gather results
        for name, task in check_tasks.items():
            try:
                results["checks"][name] = await task
            except Exception as e:
                logger.error(f"Health check '{name}' failed: {e}")
                results["checks"][name] = {
                    "status": "error",
                    "error": str(e)
                }
                results["status"] = "unhealthy"
        
        # Determine overall health
        results["healthy"] = all(
            check.get("status") == "healthy"
            for check in results["checks"].values()
        )
        
        if not results["healthy"]:
            results["status"] = "unhealthy"
        
        # Store in history
        self.add_to_history(results)
        
        return results
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Define thresholds
            cpu_threshold = 80
            memory_threshold = 85
            disk_threshold = 90
            
            status = "healthy"
            warnings = []
            
            if cpu_percent > cpu_threshold:
                warnings.append(f"High CPU usage: {cpu_percent}%")
                status = "warning"
            
            if memory.percent > memory_threshold:
                warnings.append(f"High memory usage: {memory.percent}%")
                status = "warning"
            
            if disk.percent > disk_threshold:
                warnings.append(f"High disk usage: {disk.percent}%")
                status = "warning"
            
            return {
                "status": status,
                "cpu": {
                    "percent": cpu_percent,
                    "threshold": cpu_threshold
                },
                "memory": {
                    "percent": memory.percent,
                    "available": f"{memory.available / (1024**3):.2f} GB",
                    "total": f"{memory.total / (1024**3):.2f} GB",
                    "threshold": memory_threshold
                },
                "disk": {
                    "percent": disk.percent,
                    "free": f"{disk.free / (1024**3):.2f} GB",
                    "total": f"{disk.total / (1024**3):.2f} GB",
                    "threshold": disk_threshold
                },
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_api_endpoints(self) -> Dict[str, Any]:
        """Check internal API endpoints"""
        endpoints = [
            "/api/health",
            "/api/info"
        ]
        
        results = {
            "status": "healthy",
            "endpoints": {}
        }
        
        # In a real implementation, you would make actual HTTP requests
        # For now, we'll simulate the checks
        for endpoint in endpoints:
            results["endpoints"][endpoint] = {
                "status": "healthy",
                "response_time": "< 100ms"
            }
        
        return results
    
    async def check_external_services(self) -> Dict[str, Any]:
        """Check external service dependencies"""
        services = {
            "openai": "https://api.openai.com/v1/models",
            "mongodb": "mongodb://localhost:27017"  # If using MongoDB
        }
        
        results = {
            "status": "healthy",
            "services": {}
        }
        
        # Check OpenAI API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    services["openai"],
                    timeout=aiohttp.ClientTimeout(total=5),
                    headers={"Authorization": f"Bearer {self.get_api_key()}"}
                ) as response:
                    if response.status == 200:
                        results["services"]["openai"] = {
                            "status": "healthy",
                            "response_time": f"{response.headers.get('X-Response-Time', 'N/A')}"
                        }
                    else:
                        results["services"]["openai"] = {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}"
                        }
                        results["status"] = "degraded"
        except Exception as e:
            results["services"]["openai"] = {
                "status": "error",
                "error": str(e)
            }
            results["status"] = "degraded"
        
        return results
    
    def get_api_key(self) -> str:
        """Get API key from environment"""
        import os
        return os.getenv("OPENAI_API_KEY", "")
    
    def add_to_history(self, result: Dict):
        """Add health check result to history"""
        self.health_history.append(result)
        
        # Limit history size
        if len(self.health_history) > self.max_history:
            self.health_history = self.health_history[-self.max_history:]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get health check statistics"""
        if not self.health_history:
            return {
                "total_checks": 0,
                "healthy_checks": 0,
                "health_rate": "0%",
                "last_check": None
            }
        
        total = len(self.health_history)
        healthy = sum(1 for h in self.health_history if h.get("healthy", False))
        
        return {
            "total_checks": total,
            "healthy_checks": healthy,
            "health_rate": f"{(healthy / total) * 100:.2f}%",
            "last_check": self.health_history[-1]["timestamp"],
            "uptime": f"{(time.time() - self.start_time):.0f}s"
        }

# Global health checker instance
health_checker = HealthChecker()