"""
Configuration Management for Web Automation Pipeline
Senior Integration Engineer Pattern: Centralized Configuration
"""

import os
from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path
from enum import Enum

class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class LLMProvider(str, Enum):
    """Supported LLM providers"""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class Settings(BaseSettings):
    """
    Application settings with environment variable support
    Following 12-factor app principles
    """
    
    # Server Configuration
    app_name: str = "Web Automation Pipeline"
    app_version: str = "2.0.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = Field(default=True, env="DEBUG")
    
    # API Configuration
    api_host: str = Field(default="localhost", env="API_HOST")
    api_port: int = Field(default=5175, env="API_PORT")
    api_prefix: str = "/api/ui"
    api_key: Optional[str] = Field(default=None, env="API_KEY")
    
    # CORS Configuration
    cors_origins: list = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001"
        ],
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    # LLM Configuration
    llm_provider: LLMProvider = Field(default=LLMProvider.GEMINI, env="LLM_PROVIDER")
    llm_model: str = Field(default="gemini-2.5-flash", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=4096, env="LLM_MAX_TOKENS")
    llm_timeout: int = Field(default=30, env="LLM_TIMEOUT")
    
    # API Keys
    google_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Browser Configuration
    browser_headless: bool = Field(default=True, env="BROWSER_HEADLESS")
    browser_timeout: int = Field(default=30000, env="BROWSER_TIMEOUT")
    browser_viewport_width: int = Field(default=1920, env="BROWSER_WIDTH")
    browser_viewport_height: int = Field(default=1080, env="BROWSER_HEIGHT")
    
    # Pipeline Configuration
    pipeline_max_retries: int = Field(default=3, env="PIPELINE_MAX_RETRIES")
    pipeline_retry_delay: int = Field(default=2, env="PIPELINE_RETRY_DELAY")
    pipeline_timeout: int = Field(default=300, env="PIPELINE_TIMEOUT")
    pipeline_cache_enabled: bool = Field(default=True, env="PIPELINE_CACHE_ENABLED")
    pipeline_cache_ttl: int = Field(default=3600, env="PIPELINE_CACHE_TTL")
    
    # Session Management
    session_timeout: int = Field(default=3600, env="SESSION_TIMEOUT")
    session_cleanup_interval: int = Field(default=300, env="SESSION_CLEANUP_INTERVAL")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    log_json: bool = Field(default=False, env="LOG_JSON")
    
    # Monitoring Configuration
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    tracing_enabled: bool = Field(default=False, env="TRACING_ENABLED")
    tracing_endpoint: Optional[str] = Field(default=None, env="TRACING_ENDPOINT")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")
    
    # WebSocket Configuration
    websocket_enabled: bool = Field(default=True, env="WEBSOCKET_ENABLED")
    websocket_heartbeat: int = Field(default=30, env="WEBSOCKET_HEARTBEAT")
    websocket_max_connections: int = Field(default=100, env="WEBSOCKET_MAX_CONNECTIONS")
    
    # Storage Configuration
    temp_dir: str = Field(default="/tmp/web_automation", env="TEMP_DIR")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    
    # Security Configuration
    jwt_secret: Optional[str] = Field(default=None, env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration: int = Field(default=86400, env="JWT_EXPIRATION")
    
    # Feature Flags
    feature_real_execution: bool = Field(default=False, env="FEATURE_REAL_EXECUTION")
    feature_advanced_analytics: bool = Field(default=False, env="FEATURE_ANALYTICS")
    feature_export_enabled: bool = Field(default=True, env="FEATURE_EXPORT")
    
    class Config:
        # Use absolute path to the .env file
        env_file = r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from env
        
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration based on provider"""
        config = {
            "provider": self.llm_provider,
            "model": self.llm_model,
            "temperature": self.llm_temperature,
            "max_tokens": self.llm_max_tokens,
            "timeout": self.llm_timeout
        }
        
        if self.llm_provider == LLMProvider.GEMINI:
            config["api_key"] = self.google_api_key
        elif self.llm_provider == LLMProvider.OPENAI:
            config["api_key"] = self.openai_api_key
        elif self.llm_provider == LLMProvider.ANTHROPIC:
            config["api_key"] = self.anthropic_api_key
            
        return config
    
    def get_browser_config(self) -> Dict[str, Any]:
        """Get browser configuration"""
        return {
            "headless": self.browser_headless,
            "timeout": self.browser_timeout,
            "viewport": {
                "width": self.browser_viewport_width,
                "height": self.browser_viewport_height
            }
        }
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration"""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_allow_credentials,
            "allow_methods": self.cors_allow_methods,
            "allow_headers": self.cors_allow_headers
        }
    
    def validate_configuration(self) -> bool:
        """Validate critical configuration"""
        errors = []
        
        # Check LLM API key
        if self.llm_provider == LLMProvider.GEMINI and not self.google_api_key:
            errors.append("GOOGLE_API_KEY is required for Gemini provider")
        elif self.llm_provider == LLMProvider.OPENAI and not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required for OpenAI provider")
        elif self.llm_provider == LLMProvider.ANTHROPIC and not self.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY is required for Anthropic provider")
        
        # Check paths
        temp_path = Path(self.temp_dir)
        if not temp_path.exists():
            try:
                temp_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create temp directory: {e}")
        
        if errors:
            for error in errors:
                print(f"Configuration Error: {error}")
            return False
        
        return True
    
    def display_configuration(self):
        """Display current configuration (for debugging)"""
        print("\n" + "="*60)
        print("Web Automation Pipeline Configuration")
        print("="*60)
        print(f"Environment: {self.environment}")
        print(f"API: http://{self.api_host}:{self.api_port}{self.api_prefix}")
        print(f"LLM: {self.llm_provider} / {self.llm_model}")
        print(f"Debug Mode: {self.debug}")
        print(f"WebSocket: {'Enabled' if self.websocket_enabled else 'Disabled'}")
        print(f"Rate Limiting: {'Enabled' if self.rate_limit_enabled else 'Disabled'}")
        print("="*60 + "\n")

# Singleton instance
settings = Settings()

# Validate on import
if not settings.validate_configuration():
    print("WARNING: Configuration validation failed. Some features may not work.")

# Export commonly used configurations
API_PORT = settings.api_port
API_PREFIX = settings.api_prefix
LLM_MODEL = settings.llm_model
DEBUG = settings.debug