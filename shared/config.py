"""Centralized configuration management for Citrature platform.

This module implements a robust, centralized configuration system that loads all
environment variables at application startup, validates their presence, and stores
them as immutable settings objects. This establishes a definitive contract that
governs the entire distributed system.
"""

import logging
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    This class defines the complete configuration contract for the Citrature platform.
    All required environment variables must be present at startup, preventing runtime
    errors caused by missing configuration.
    """
    
    # API Configuration
    api_origin: str = Field(..., env="API_ORIGIN")
    web_origin: str = Field(..., env="WEB_ORIGIN")
    
    # Database Configuration
    postgres_dsn: str = Field(..., env="POSTGRES_DSN")
    pgvector_dimension: int = Field(default=768, env="PGVECTOR_DIMENSION")
    
    # Message Queue Configuration
    rabbitmq_url: str = Field(..., env="RABBITMQ_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    
    # External APIs - OpenRouter
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")
    openrouter_api_key: str = Field(..., env="OPENROUTER_API_KEY")
    
    # External APIs - Crossref
    crossref_base_url: str = Field(default="https://api.crossref.org", env="CROSSREF_BASE_URL")
    crossref_mailto: str = Field(..., env="CROSSREF_MAILTO")
    
    # Google OAuth Configuration
    google_client_id: str = Field(..., env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(..., env="GOOGLE_REDIRECT_URI")
    
    # GROBID Service Configuration
    grobid_base_url: str = Field(default="http://grobid:8070", env="GROBID_BASE_URL")
    
    # Google Cloud Storage Configuration
    gcs_bucket_name: str = Field(..., env="GCS_BUCKET_NAME")
    gcs_project_id: str = Field(..., env="GCS_PROJECT_ID")
    gcs_credentials_json: Optional[str] = Field(default=None, env="GCS_CREDENTIALS_JSON")
    
    # Usage Limits and Quotas
    max_topic_papers: int = Field(default=30, env="MAX_TOPIC_PAPERS")
    max_graph_depth: int = Field(default=3, env="MAX_GRAPH_DEPTH")
    max_collections_per_user: int = Field(default=1, env="MAX_COLLECTIONS_PER_USER")
    monthly_chat_quota: int = Field(default=100, env="MONTHLY_CHAT_QUOTA")
    
    # Upload Limits
    max_upload_size_mb: int = Field(default=50, env="MAX_UPLOAD_SIZE_MB")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    @property
    def database_url(self) -> str:
        """Alias for postgres_dsn to maintain compatibility."""
        return self.postgres_dsn
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.max_upload_size_mb * 1024 * 1024
    
    @property
    def allowed_mime_types(self) -> List[str]:
        """Get allowed MIME types for file uploads."""
        return ["application/pdf"]
    
    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic."""
        return self.postgres_dsn.replace("postgresql://", "postgresql+psycopg2://")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance - immutable after initialization
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance.
    
    Returns:
        Settings: The immutable global settings object.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def initialize_settings() -> Settings:
    """Initialize settings and validate all required environment variables.
    
    This function should be called at application startup to ensure all
    required configuration is present before any services are initialized.
    
    Returns:
        Settings: The validated settings object.
        
    Raises:
        ValidationError: If any required environment variables are missing.
    """
    logger.info("🔧 Initializing Citrature configuration...")
    settings = get_settings()
    
    # Log successful configuration load (without sensitive values)
    logger.info(f"✅ API Origin: {settings.api_origin}")
    logger.info(f"✅ Web Origin: {settings.web_origin}")
    logger.info(f"✅ Database configured: {settings.postgres_dsn.split('@')[0]}@***")
    logger.info(f"✅ PGVector Dimension: {settings.pgvector_dimension}")
    logger.info(f"✅ RabbitMQ configured: {settings.rabbitmq_url.split('@')[0]}@***")
    logger.info(f"✅ Redis configured: {settings.redis_url.split('//')[0]}//***/")
    logger.info(f"✅ OpenRouter Base URL: {settings.openrouter_base_url}")
    logger.info(f"✅ Crossref Base URL: {settings.crossref_base_url}")
    logger.info(f"✅ Crossref Mailto: {settings.crossref_mailto}")
    logger.info(f"✅ GROBID Base URL: {settings.grobid_base_url}")
    logger.info(f"✅ GCS Bucket: {settings.gcs_bucket_name}")
    logger.info(f"✅ GCS Project ID: {settings.gcs_project_id}")
    logger.info(f"✅ Google OAuth Client ID configured: {settings.google_client_id[:20]}...")
    logger.info(f"✅ Usage Limits - Topic Papers: {settings.max_topic_papers}")
    logger.info(f"✅ Usage Limits - Graph Depth: {settings.max_graph_depth}")
    logger.info(f"✅ Usage Limits - Collections Per User: {settings.max_collections_per_user}")
    logger.info(f"✅ Usage Limits - Monthly Chat Quota: {settings.monthly_chat_quota}")
    logger.info("✅ All required environment variables loaded successfully")
    
    return settings
