"""
MongoDB configuration settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class MongoDBSettings(BaseSettings):
    """MongoDB configuration settings"""
    
    # Connection settings
    mongodb_connection_string: str = "mongodb://localhost:27017"
    mongodb_database: str = "ai_apps"
    
    # Connection pool settings
    mongodb_max_pool_size: int = 100
    mongodb_min_pool_size: int = 10
    mongodb_max_idle_time_ms: int = 30000
    
    # Write concern settings
    mongodb_write_concern: str = "majority"
    mongodb_retry_writes: bool = True
    
    # TTL settings (in days)
    metrics_ttl_days: int = 30
    artifacts_ttl_days: int = 90
    
    # GridFS settings
    gridfs_chunk_size_bytes: int = 261120  # 255KB
    max_artifact_size_mb: int = 16  # Max size before using GridFS
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
mongodb_settings = MongoDBSettings()


def get_mongodb_uri() -> str:
    """Get MongoDB connection URI"""
    return mongodb_settings.mongodb_connection_string


def get_database_name() -> str:
    """Get MongoDB database name"""
    return mongodb_settings.mongodb_database