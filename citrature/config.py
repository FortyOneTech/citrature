"""Centralized configuration management for Citrature platform."""

import os
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_origin: str = Field(default="http://localhost:8000", env="API_ORIGIN")
    web_origin: str = Field(default="http://localhost:3000", env="WEB_ORIGIN")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    vector_dimension: int = Field(default=1536, env="VECTOR_DIMENSION")
    
    # Message Queue
    rabbitmq_url: str = Field(..., env="RABBITMQ_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    
    # External APIs
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")
    openrouter_api_key: str = Field(..., env="OPENROUTER_API_KEY")
    crossref_base_url: str = Field(default="https://api.crossref.org", env="CROSSREF_BASE_URL")
    crossref_mailto: str = Field(..., env="CROSSREF_MAILTO")
    
    # Google OAuth
    google_client_id: str = Field(..., env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(..., env="GOOGLE_REDIRECT_URI")
    
    # GROBID
    grobid_base_url: str = Field(default="http://localhost:8070", env="GROBID_BASE_URL")
    
    # Google Cloud Storage
    gcs_bucket_name: str = Field(..., env="GCS_BUCKET_NAME")
    gcs_project_id: str = Field(..., env="GCS_PROJECT_ID")
    gcs_credential_path: Optional[str] = Field(default=None, env="GCS_CREDENTIAL_PATH")
    
    # Usage Limits
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
        return self.database_url.replace("postgresql://", "postgresql+psycopg2://")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance - immutable after initialization
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def initialize_settings() -> Settings:
    """Initialize settings and return the instance."""
    return get_settings()
