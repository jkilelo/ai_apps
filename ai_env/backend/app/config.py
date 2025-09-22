"""
Configuration settings for FastAPI backend
Following AI-first design principles
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with AI-first configuration"""

    # Application
    APP_NAME: str = "Infrastructure Audit API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(False, env="DEBUG")

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI-Driven Infrastructure Audit System"

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database - PostgreSQL (AI-managed)
    POSTGRES_HOST: str = Field("127.0.0.1", env="POSTGRES_HOST")
    POSTGRES_PORT: str = Field("5433", env="POSTGRES_PORT")
    POSTGRES_USER: str = Field("ai_dba", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("AIDBAdmin2025Secure", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field("ai_control", env="POSTGRES_DB")

    # MCP Server Integration
    MCP_SERVER_URL: str = Field("http://localhost:8080", env="MCP_SERVER_URL")
    MCP_API_KEY: Optional[str] = Field(None, env="MCP_API_KEY")

    # AI/LLM Configuration (AI-first mandatory)
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    DEFAULT_LLM_PROVIDER: str = Field("gemini", env="DEFAULT_LLM_PROVIDER")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        ["http://localhost:3000", "http://localhost:3001"],
        env="BACKEND_CORS_ORIGINS"
    )

    # Redis for caching and background tasks
    REDIS_URL: str = Field("redis://localhost:6379", env="REDIS_URL")

    # Email (SendGrid)
    SENDGRID_API_KEY: Optional[str] = Field(None, env="SENDGRID_API_KEY")
    EMAIL_FROM: str = Field("noreply@ai-audit.com", env="EMAIL_FROM")

    # SMS (Plivo)
    PLIVO_AUTH_ID: Optional[str] = Field(None, env="PLIVO_AUTH_ID")
    PLIVO_AUTH_TOKEN: Optional[str] = Field(None, env="PLIVO_AUTH_TOKEN")

    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL database URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Construct sync PostgreSQL database URL for Alembic"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @validator("GEMINI_API_KEY", pre=True)
    def validate_ai_first(cls, v):
        """Ensure AI-first requirement is met"""
        if not v:
            raise ValueError("AI-first design requires at least one LLM API key (Gemini preferred)")
        return v

    class Config:
        env_file = Path(__file__).parent.parent.parent.parent / ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env file

# Create settings instance
settings = Settings()