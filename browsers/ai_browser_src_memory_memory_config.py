"""Production-ready memory system configuration and optimization"""
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from enum import Enum
import os


class MemoryTierConfig(BaseModel):
    """Configuration for individual memory tiers"""
    enabled: bool = True
    host: str = "localhost"
    port: int
    timeout_seconds: int = 30
    retry_attempts: int = 3
    connection_pool_size: int = 10


class CacheConfig(BaseModel):
    """Cache configuration"""
    max_size: int = 10000
    default_ttl: int = 300  # 5 minutes
    strategy: str = "adaptive"  # lru, lfu, ttl, adaptive
    eviction_threshold: float = 0.9
    warming_enabled: bool = True


class RetentionPolicy(BaseModel):
    """Data retention policies for each tier"""
    session_hours: int = 24
    semantic_days: int = 30
    knowledge_days: int = 90
    cleanup_interval_hours: int = 6


class PerformanceConfig(BaseModel):
    """Performance and optimization settings"""
    enable_intelligent_routing: bool = True
    enable_caching: bool = True
    enable_preloading: bool = True
    batch_size: int = 100
    concurrent_operations: int = 5
    health_check_interval: int = 300  # 5 minutes
    performance_monitoring: bool = True


class SecurityConfig(BaseModel):
    """Security and privacy settings"""
    encrypt_sensitive_data: bool = True
    anonymize_personal_data: bool = True
    audit_logging: bool = True
    data_retention_compliance: bool = True


class ProductionMemoryConfig(BaseModel):
    """Production memory system configuration"""
    
    # Environment
    environment: str = Field(default="production", description="Deployment environment")
    debug_mode: bool = Field(default=False, description="Enable debug logging")
    
    # Database paths and connections
    session_db_path: str = Field(default=".claude/memory/session.db", description="SQLite database path")
    memory_data_dir: str = Field(default=".claude/memory", description="Memory data directory")
    
    # Memory tier configurations
    session_memory: MemoryTierConfig = MemoryTierConfig(port=0)  # SQLite doesn't use port
    semantic_memory: MemoryTierConfig = MemoryTierConfig(port=6333)
    knowledge_graph: MemoryTierConfig = MemoryTierConfig(port=6380)
    
    # Caching configuration
    cache: CacheConfig = CacheConfig()
    
    # Data retention
    retention: RetentionPolicy = RetentionPolicy()
    
    # Performance settings
    performance: PerformanceConfig = PerformanceConfig()
    
    # Security settings
    security: SecurityConfig = SecurityConfig()
    
    # Resource limits
    max_memory_usage_mb: int = Field(default=2048, description="Maximum memory usage in MB")
    max_disk_usage_mb: int = Field(default=10240, description="Maximum disk usage in MB")
    max_concurrent_requests: int = Field(default=100, description="Maximum concurrent memory requests")
    
    class Config:
        env_prefix = "MEMORY_"
        
    @classmethod
    def from_environment(cls) -> "ProductionMemoryConfig":
        """Create configuration from environment variables"""
        return cls()
    
    @classmethod
    def for_development(cls) -> "ProductionMemoryConfig":
        """Create development-optimized configuration"""
        config = cls()
        config.environment = "development"
        config.debug_mode = True
        config.cache.max_size = 1000
        config.retention.session_hours = 4
        config.retention.semantic_days = 7
        config.retention.knowledge_days = 14
        config.performance.health_check_interval = 60
        return config
    
    @classmethod
    def for_testing(cls) -> "ProductionMemoryConfig":
        """Create testing-optimized configuration"""
        config = cls()
        config.environment = "testing"
        config.debug_mode = True
        config.session_db_path = ":memory:"  # In-memory SQLite for tests
        config.cache.max_size = 100
        config.retention.session_hours = 1
        config.retention.semantic_days = 1
        config.retention.knowledge_days = 1
        config.performance.health_check_interval = 30
        return config
    
    @classmethod
    def for_production(cls) -> "ProductionMemoryConfig":
        """Create production-optimized configuration"""
        config = cls()
        config.environment = "production"
        config.debug_mode = False
        config.cache.max_size = 50000
        config.retention.session_hours = 48
        config.retention.semantic_days = 90
        config.retention.knowledge_days = 365
        config.performance.concurrent_operations = 10
        config.performance.health_check_interval = 900  # 15 minutes
        config.max_memory_usage_mb = 8192
        config.max_disk_usage_mb = 102400  # 100GB
        return config
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        Path(self.memory_data_dir).mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        for subdir in ["session", "semantic", "knowledge", "cache", "logs"]:
            Path(self.memory_data_dir, subdir).mkdir(parents=True, exist_ok=True)
    
    def get_database_url(self, tier: str) -> str:
        """Get database connection URL for tier"""
        if tier == "session":
            if self.session_db_path == ":memory:":
                return "sqlite:///:memory:"
            return f"sqlite:///{self.session_db_path}"
        elif tier == "semantic":
            return f"qdrant://{self.semantic_memory.host}:{self.semantic_memory.port}"
        elif tier == "knowledge":
            return f"falkor://{self.knowledge_graph.host}:{self.knowledge_graph.port}"
        
        raise ValueError(f"Unknown memory tier: {tier}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for memory manager"""
        return {
            "session_db_path": self.session_db_path,
            "qdrant_host": self.semantic_memory.host,
            "qdrant_port": self.semantic_memory.port,
            "qdrant_collection": "browser_memory",
            "falkordb_host": self.knowledge_graph.host,
            "falkordb_port": self.knowledge_graph.port,
            "falkordb_graph": "browser_knowledge",
            "cache_size": self.cache.max_size,
            "debug_mode": self.debug_mode,
            "environment": self.environment
        }


class MemoryOptimizer:
    """Memory system optimization utilities"""
    
    def __init__(self, config: ProductionMemoryConfig):
        self.config = config
    
    def calculate_optimal_cache_size(self, available_memory_mb: int) -> int:
        """Calculate optimal cache size based on available memory"""
        # Use 10% of available memory for caching, with limits
        optimal_size = int((available_memory_mb * 0.1) * 100)  # Approximate entries per MB
        
        # Apply bounds
        min_size = 1000
        max_size = self.config.max_memory_usage_mb * 10
        
        return max(min_size, min(optimal_size, max_size))
    
    def calculate_optimal_batch_size(self, operation_type: str) -> int:
        """Calculate optimal batch size for different operations"""
        batch_sizes = {
            "embedding_operations": 50,
            "graph_operations": 20,
            "session_operations": 100,
            "cleanup_operations": 1000
        }
        
        return batch_sizes.get(operation_type, self.config.performance.batch_size)
    
    def get_retention_cutoff(self, tier: str) -> int:
        """Get retention cutoff time for tier"""
        if tier == "session":
            return self.config.retention.session_hours * 3600
        elif tier == "semantic":
            return self.config.retention.semantic_days * 24 * 3600
        elif tier == "knowledge":
            return self.config.retention.knowledge_days * 24 * 3600
        
        return 24 * 3600  # Default to 24 hours
    
    def should_enable_feature(self, feature: str) -> bool:
        """Determine if a performance feature should be enabled"""
        features = {
            "intelligent_routing": self.config.performance.enable_intelligent_routing,
            "caching": self.config.performance.enable_caching,
            "preloading": self.config.performance.enable_preloading,
            "performance_monitoring": self.config.performance.performance_monitoring
        }
        
        return features.get(feature, True)
    
    def get_connection_config(self, tier: str) -> Dict[str, Any]:
        """Get connection configuration for memory tier"""
        if tier == "semantic":
            return {
                "host": self.config.semantic_memory.host,
                "port": self.config.semantic_memory.port,
                "timeout": self.config.semantic_memory.timeout_seconds,
                "retry_attempts": self.config.semantic_memory.retry_attempts
            }
        elif tier == "knowledge":
            return {
                "host": self.config.knowledge_graph.host,
                "port": self.config.knowledge_graph.port,
                "timeout": self.config.knowledge_graph.timeout_seconds,
                "retry_attempts": self.config.knowledge_graph.retry_attempts
            }
        
        return {}


def create_memory_config(environment: str = None) -> ProductionMemoryConfig:
    """Create memory configuration based on environment"""
    
    # Detect environment if not specified
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        return ProductionMemoryConfig.for_production()
    elif environment == "testing":
        return ProductionMemoryConfig.for_testing()
    else:
        return ProductionMemoryConfig.for_development()


# Default configurations
DEFAULT_CONFIG = ProductionMemoryConfig.for_development()
PRODUCTION_CONFIG = ProductionMemoryConfig.for_production()
TEST_CONFIG = ProductionMemoryConfig.for_testing()