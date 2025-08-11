"""
Configuration management for UI Testing Framework v2
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings  # Fallback for older versions


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    
    url: str = Field(default="sqlite:///./ui_testing_v2.db", env="DATABASE_URL")
    echo: bool = Field(default=False, env="DATABASE_ECHO")
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    class Config:
        env_prefix = "DATABASE_"


class CacheConfig(BaseSettings):
    """Cache configuration"""
    
    backend: str = Field(default="redis", env="CACHE_BACKEND")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    redis_ttl: int = Field(default=3600, env="REDIS_TTL")
    
    # Memory cache fallback settings
    max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")
    ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # Specific cache TTL settings
    element_analysis_ttl: int = Field(default=7200, env="CACHE_ELEMENT_ANALYSIS_TTL")  # 2 hours
    test_generation_ttl: int = Field(default=3600, env="CACHE_TEST_GENERATION_TTL")   # 1 hour
    ai_analysis_ttl: int = Field(default=1800, env="CACHE_AI_ANALYSIS_TTL")           # 30 minutes
    
    class Config:
        env_prefix = "CACHE_"


class StorageConfig(BaseSettings):
    """Storage configuration"""
    
    backend: str = Field(default="filesystem", env="STORAGE_BACKEND")
    base_path: str = Field(default="./data", env="STORAGE_BASE_PATH")
    max_file_size: str = Field(default="100MB", env="STORAGE_MAX_FILE_SIZE")
    
    # AWS S3 settings (if using S3 storage)
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_s3_bucket: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    aws_s3_region: Optional[str] = Field(default="us-east-1", env="AWS_S3_REGION")
    
    class Config:
        env_prefix = "STORAGE_"


class AIConfig(BaseSettings):
    """AI/LLM service configuration"""
    
    # Provider settings
    default_provider: str = Field(default="openai", env="AI_DEFAULT_PROVIDER")
    enable_vision: bool = Field(default=True, env="AI_ENABLE_VISION")
    enable_caching: bool = Field(default=True, env="AI_ENABLE_CACHING")
    cache_ttl: int = Field(default=3600, env="AI_CACHE_TTL")
    
    # OpenAI settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_vision_model: str = Field(default="gpt-4-vision-preview", env="OPENAI_VISION_MODEL")
    openai_organization: Optional[str] = Field(default=None, env="OPENAI_ORGANIZATION")
    openai_max_tokens: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    openai_timeout: int = Field(default=60, env="OPENAI_TIMEOUT")
    
    # Anthropic settings
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(default=4000, env="ANTHROPIC_MAX_TOKENS")
    anthropic_temperature: float = Field(default=0.7, env="ANTHROPIC_TEMPERATURE")
    anthropic_timeout: int = Field(default=60, env="ANTHROPIC_TIMEOUT")
    
    # Prompt management
    max_context_length: int = Field(default=8000, env="AI_MAX_CONTEXT_LENGTH")
    enable_context_memory: bool = Field(default=True, env="AI_ENABLE_CONTEXT_MEMORY")
    context_memory_size: int = Field(default=10, env="AI_CONTEXT_MEMORY_SIZE")
    
class BrowserConfig(BaseSettings):
    """Browser configuration"""
    
    default_browser: str = Field(default="chromium", env="DEFAULT_BROWSER")
    headless: bool = Field(default=True, env="BROWSER_HEADLESS")
    timeout: int = Field(default=30000, env="BROWSER_TIMEOUT")
    screenshot_on_failure: bool = Field(default=True, env="BROWSER_SCREENSHOT_ON_FAILURE")
    
    # Browser executable paths (optional)
    chromium_executable_path: Optional[str] = Field(default=None, env="CHROMIUM_EXECUTABLE_PATH")
    firefox_executable_path: Optional[str] = Field(default=None, env="FIREFOX_EXECUTABLE_PATH")
    webkit_executable_path: Optional[str] = Field(default=None, env="WEBKIT_EXECUTABLE_PATH")
    
    class Config:
        env_prefix = "BROWSER_"


class APIConfig(BaseSettings):
    """API server configuration"""
    
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="API_DEBUG")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="API_CORS_ORIGINS"
    )
    max_request_size: str = Field(default="50MB", env="API_MAX_REQUEST_SIZE")
    
    # Authentication (if enabled)
    jwt_secret_key: Optional[str] = Field(default=None, env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration: int = Field(default=3600, env="JWT_EXPIRATION")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_prefix = "API_"


class LoggingConfig(BaseSettings):
    """Logging configuration"""
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="detailed", env="LOG_FORMAT")
    file: Optional[str] = Field(default="./logs/ui_testing_v2.log", env="LOG_FILE")
    max_size: str = Field(default="10MB", env="LOG_MAX_SIZE")
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    class Config:
        env_prefix = "LOG_"


class TestingConfig(BaseSettings):
    """Testing framework configuration"""
    
    timeout: int = Field(default=300, env="TEST_TIMEOUT")
    parallel_workers: int = Field(default=4, env="TEST_PARALLEL_WORKERS")
    retry_attempts: int = Field(default=3, env="TEST_RETRY_ATTEMPTS")
    retry_delay: int = Field(default=1, env="TEST_RETRY_DELAY")
    
    # Test data generation
    faker_locale: str = Field(default="en_US", env="TEST_DATA_FAKER_LOCALE")
    random_seed: Optional[int] = Field(default=42, env="TEST_DATA_RANDOM_SEED")
    
    class Config:
        env_prefix = "TEST_"


class PerformanceConfig(BaseSettings):
    """Performance and resource limits"""
    
    # Rate limiting
    rate_limit_requests_per_minute: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_burst_size: int = Field(default=10, env="RATE_LIMIT_BURST_SIZE")
    
    # Resource limits
    max_concurrent_extractions: int = Field(default=5, env="MAX_CONCURRENT_EXTRACTIONS")
    max_concurrent_test_executions: int = Field(default=3, env="MAX_CONCURRENT_TEST_EXECUTIONS")
    max_elements_per_page: int = Field(default=500, env="MAX_ELEMENTS_PER_PAGE")
    
    class Config:
        env_prefix = "PERFORMANCE_"


class SecurityConfig(BaseSettings):
    """Security configuration"""
    
    # Security headers
    hsts_enabled: bool = Field(default=True, env="SECURITY_HSTS_ENABLED")
    content_type_nosniff: bool = Field(default=True, env="SECURITY_CONTENT_TYPE_NOSNIFF")
    frame_options: str = Field(default="DENY", env="SECURITY_FRAME_OPTIONS")
    
    # Input validation
    max_url_length: int = Field(default=2048, env="MAX_URL_LENGTH")
    max_selector_length: int = Field(default=500, env="MAX_SELECTOR_LENGTH")
    max_prompt_length: int = Field(default=10000, env="MAX_PROMPT_LENGTH")
    
    class Config:
        env_prefix = "SECURITY_"


class MonitoringConfig(BaseSettings):
    """Monitoring and metrics configuration"""
    
    # Health checks
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    health_check_timeout: int = Field(default=10, env="HEALTH_CHECK_TIMEOUT")
    
    # Metrics collection
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_endpoint: str = Field(default="/metrics", env="METRICS_ENDPOINT")
    
    class Config:
        env_prefix = "MONITORING_"


class FeatureFlags(BaseSettings):
    """Feature flags for experimental features"""
    
    # Experimental features
    advanced_ai_analysis: bool = Field(default=True, env="FEATURE_ADVANCED_AI_ANALYSIS")
    visual_testing: bool = Field(default=True, env="FEATURE_VISUAL_TESTING")
    accessibility_testing: bool = Field(default=True, env="FEATURE_ACCESSIBILITY_TESTING")
    performance_testing: bool = Field(default=False, env="FEATURE_PERFORMANCE_TESTING")
    
    # UI features
    dark_mode: bool = Field(default=True, env="FEATURE_DARK_MODE")
    real_time_updates: bool = Field(default=True, env="FEATURE_REAL_TIME_UPDATES")
    export_formats: List[str] = Field(
        default=["json", "html", "pdf"],
        env="FEATURE_EXPORT_FORMATS"
    )
    
    @validator("export_formats", pre=True)
    def parse_export_formats(cls, v):
        if isinstance(v, str):
            return [fmt.strip() for fmt in v.split(",")]
        return v
    
    class Config:
        env_prefix = "FEATURE_"


class Config(BaseSettings):
    """Main application configuration"""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    development_mode: bool = Field(default=True, env="DEVELOPMENT_MODE")
    
    # Component configurations
    database: DatabaseConfig = DatabaseConfig()
    cache: CacheConfig = CacheConfig()
    storage: StorageConfig = StorageConfig()
    ai: AIConfig = AIConfig()
    browser: BrowserConfig = BrowserConfig()
    api: APIConfig = APIConfig()
    logging: LoggingConfig = LoggingConfig()
    testing: TestingConfig = TestingConfig()
    performance: PerformanceConfig = PerformanceConfig()
    security: SecurityConfig = SecurityConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    features: FeatureFlags = FeatureFlags()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == "development" or self.development_mode
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production"


@lru_cache()
def get_config() -> Config:
    """Get cached configuration instance"""
    return Config()


# Convenience functions for component configs
@lru_cache()
def get_database_config() -> DatabaseConfig:
    """Get database configuration"""
    return get_config().database


@lru_cache()
def get_cache_config() -> CacheConfig:
    """Get cache configuration"""
    return get_config().cache


@lru_cache()
def get_ai_config() -> AIConfig:
    """Get AI configuration"""
    return get_config().ai


@lru_cache()
def get_storage_config() -> StorageConfig:
    """Get storage configuration"""
    return get_config().storage

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class ExtractionConfig(BaseModel):
    """Element extraction configuration"""
    strategies: List[str] = Field(
        default=["auto", "manual", "ai"], 
        description="Extraction strategies to use"
    )
    timeout: int = Field(default=30, gt=0, description="Page load timeout in seconds")
    max_elements: int = Field(default=500, gt=0, description="Maximum elements to extract")
    include_invisible: bool = Field(default=False, description="Include invisible elements")
    min_confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Minimum confidence score")
    screenshot: bool = Field(default=True, description="Take screenshots during extraction")
    full_page_screenshot: bool = Field(default=False, description="Take full page screenshots")
    
    @validator("strategies")
    def validate_strategies(cls, v: List[str]) -> List[str]:
        allowed = ["auto", "manual", "ai", "visual", "accessibility"]
        for strategy in v:
            if strategy not in allowed:
                raise ValueError(f"Strategy '{strategy}' not in allowed: {allowed}")
        return v
    
    @validator("timeout")
    def validate_timeout(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v
    
    @validator("max_elements")
    def validate_max_elements(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Max elements must be positive")
        return v
    
    @validator("min_confidence")
    def validate_min_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class GenerationConfig(BaseModel):
    """Test generation configuration"""
    ai_provider: str = Field(default="openai", description="AI provider for test generation")
    model: str = Field(default="gpt-4", description="AI model to use")
    test_types: List[str] = Field(
        default=["functional", "ui", "accessibility"],
        description="Types of tests to generate"
    )
    max_test_cases: int = Field(default=100, gt=0, description="Maximum test cases to generate")
    include_negative_tests: bool = Field(default=True, description="Include negative test cases")
    include_edge_cases: bool = Field(default=True, description="Include edge case tests")
    complexity_level: str = Field(default="medium", description="Test complexity level")
    
    @validator("ai_provider")
    def validate_ai_provider(cls, v: str) -> str:
        allowed = ["openai", "anthropic", "local"]
        if v not in allowed:
            raise ValueError(f"AI provider must be one of {allowed}")
        return v
    
    @validator("complexity_level")
    def validate_complexity_level(cls, v: str) -> str:
        allowed = ["simple", "medium", "complex"]
        if v not in allowed:
            raise ValueError(f"Complexity level must be one of {allowed}")
        return v
    
    @validator("max_test_cases")
    def validate_max_test_cases(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Max test cases must be positive")
        return v


class ExecutionConfig(BaseModel):
    """Test execution configuration"""
    timeout: int = Field(default=60, gt=0, description="Test execution timeout")
    parallel: bool = Field(default=True, description="Enable parallel execution")
    max_workers: int = Field(default=4, gt=0, description="Maximum parallel workers")
    retry_attempts: int = Field(default=3, ge=0, description="Number of retry attempts")
    retry_delay: float = Field(default=1.0, ge=0.0, description="Delay between retries")
    headless: bool = Field(default=True, description="Run browsers in headless mode")
    screenshot_on_failure: bool = Field(default=True, description="Take screenshots on failure")
    video_recording: bool = Field(default=False, description="Record test execution videos")
    
    @validator("timeout")
    def validate_timeout(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v
    
    @validator("max_workers")
    def validate_max_workers(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Max workers must be positive")
        return v
    
    @validator("retry_attempts")
    def validate_retry_attempts(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Retry attempts cannot be negative")
        return v


class StorageConfig(BaseModel):
    """Storage configuration"""
    backend: str = Field(default="filesystem", description="Storage backend type")
    base_path: str = Field(default="./data", description="Base storage path")
    connection_string: str = Field(default="", description="Database connection string")
    encryption: bool = Field(default=False, description="Enable encryption")
    compression: bool = Field(default=True, description="Enable compression")
    retention_days: int = Field(default=30, ge=1, description="Data retention period in days")
    
    @validator("backend")
    def validate_backend(cls, v: str) -> str:
        allowed = ["filesystem", "database", "s3", "azure", "gcs"]
        if v not in allowed:
            raise ValueError(f"Storage backend must be one of {allowed}")
        return v


class CacheConfig(BaseModel):
    """Cache configuration"""
    backend: str = Field(default="memory", description="Cache backend type")
    ttl: int = Field(default=3600, gt=0, description="Time to live in seconds")
    max_size: int = Field(default=1000, gt=0, description="Maximum cache size")
    connection_string: str = Field(default="", description="Cache connection string")
    serialization: str = Field(default="json", description="Serialization format")
    
    @validator("backend")
    def validate_backend(cls, v: str) -> str:
        allowed = ["memory", "redis", "memcached", "disk"]
        if v not in allowed:
            raise ValueError(f"Cache backend must be one of {allowed}")
        return v
    
    @validator("ttl")
    def validate_ttl(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("TTL must be positive")
        return v
    
    @validator("max_size")
    def validate_max_size(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Max size must be positive")
        return v


class AIConfig(BaseModel):
    """AI service configuration"""
    
    # Provider settings
    default_provider: str = Field(default="openai", description="Default AI provider")
    
    # OpenAI settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_organization: Optional[str] = Field(default=None, env="OPENAI_ORGANIZATION")
    
    # Anthropic settings
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    
    # General AI settings
    max_tokens: int = Field(default=4000, ge=100, le=32000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    timeout: int = Field(default=60, ge=10, le=300)
    retry_attempts: int = Field(default=3, ge=1, le=10)
    
    # Computer vision settings
    enable_vision: bool = Field(default=True)
    vision_model: str = Field(default="gpt-4-vision-preview")
    
    # Prompt management
    prompt_templates_dir: str = Field(default="./prompts")
    enable_context_memory: bool = Field(default=True)
    max_context_length: int = Field(default=10000, ge=1000, le=50000)


class Settings(BaseSettings):
    """Main settings configuration"""
    
    # Application settings
    app_name: str = "ui_testing_v2"
    version: str = "2.0.0"
    debug: bool = False
    
    # Component configurations
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


@lru_cache()
def get_settings(_reload: bool = False) -> Settings:
    """Get cached settings instance"""
    if _reload:
        get_settings.cache_clear()
    return Settings()


def get_config_from_env() -> Settings:
    """Get fresh settings from environment"""
    return Settings()
