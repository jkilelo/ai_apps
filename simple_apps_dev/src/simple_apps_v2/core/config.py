"""
Application configuration using Pydantic settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix=""
    )

    # Application
    app_name: str = Field(default="Simple Apps v2")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=5175)
    api_reload: bool = Field(default=True)
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001"
        ]
    )
    
    # Browser Configuration
    browser_headless: bool = Field(default=True)
    browser_timeout: int = Field(default=30000)
    browser_viewport_width: int = Field(default=1920)
    browser_viewport_height: int = Field(default=1080)
    browser_user_agent: Optional[str] = Field(default=None)
    browser_executable_path: Optional[str] = Field(default=None)
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None)
    google_api_key: Optional[str] = Field(default=None)
    default_llm_provider: str = Field(default="openai")
    default_llm_model: str = Field(default="gpt-4")
    llm_max_tokens: int = Field(default=4000)
    llm_temperature: float = Field(default=0.7)
    
    # Paths Configuration
    test_output_dir: Path = Field(default=Path("test_output"))
    screenshot_dir: Path = Field(default=Path("screenshots"))
    
    # Logging Configuration
    log_level: str = Field(default="INFO")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Database Configuration (optional)
    database_url: Optional[str] = Field(default=None)
    redis_url: Optional[str] = Field(default=None)
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("test_output_dir", "screenshot_dir", mode="before")
    @classmethod
    def parse_paths(cls, v: Any) -> Path:
        """Parse path fields."""
        if isinstance(v, str):
            return Path(v)
        return v
    
    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.test_output_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration dictionary."""
        return {
            "provider": self.default_llm_provider,
            "model": self.default_llm_model,
            "max_tokens": self.llm_max_tokens,
            "temperature": self.llm_temperature,
            "openai_api_key": self.openai_api_key,
            "google_api_key": self.google_api_key,
        }
    
    @property
    def browser_config(self) -> Dict[str, Any]:
        """Get browser configuration dictionary."""
        config = {
            "headless": self.browser_headless,
            "timeout": self.browser_timeout,
            "viewport": {
                "width": self.browser_viewport_width,
                "height": self.browser_viewport_height,
            }
        }
        
        if self.browser_user_agent:
            config["user_agent"] = self.browser_user_agent
        if self.browser_executable_path:
            config["executable_path"] = self.browser_executable_path
            
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "app_name": self.app_name,
            "version": self.version,
            "debug": self.debug,
            "api": {
                "host": self.api_host,
                "port": self.api_port,
                "reload": self.api_reload,
            },
            "cors_origins": self.cors_origins,
            "browser": self.browser_config,
            "llm": self.llm_config,
            "paths": {
                "test_output": str(self.test_output_dir),
                "screenshots": str(self.screenshot_dir),
            },
            "logging": {
                "level": self.log_level,
                "format": self.log_format,
            },
            "database": {
                "url": self.database_url,
                "redis": self.redis_url,
            }
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    settings = Settings()
    settings.create_directories()
    return settings