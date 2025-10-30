"""Simple configuration for migrations and utilities.

This module provides a simpler settings class that doesn't use Pydantic validation,
making it suitable for use in Alembic migrations and other scenarios where
validation overhead should be minimal.
"""

import os
from typing import List, Optional


class SimpleSettings:
    """Simple settings for migrations that don't require complex validation.
    
    This class provides the same configuration interface as the main Settings class
    but uses simple environment variable lookups with sensible defaults.
    """
    
    def __init__(self):
        # Core Configuration
        self.api_origin = os.getenv("API_ORIGIN", "http://localhost:8000")
        self.web_origin = os.getenv("WEB_ORIGIN", "http://localhost:3000")
        
        # Database (support both POSTGRES_DSN and DATABASE_URL for compatibility)
        self.postgres_dsn = os.getenv("POSTGRES_DSN", os.getenv("DATABASE_URL", "postgresql://citrature:password@db:5432/citrature"))
        self.pgvector_dimension = int(os.getenv("PGVECTOR_DIMENSION", "768"))
        
        # Message Queue
        self.rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        
        # External APIs
        self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "placeholder")
        self.crossref_base_url = os.getenv("CROSSREF_BASE_URL", "https://api.crossref.org")
        self.crossref_mailto = os.getenv("CROSSREF_MAILTO", "test@example.com")
        
        # Google OAuth
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID", "placeholder")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "placeholder")
        self.google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        
        # GROBID
        self.grobid_base_url = os.getenv("GROBID_BASE_URL", "http://grobid:8070")
        
        # Google Cloud Storage
        self.gcs_bucket_name = os.getenv("GCS_BUCKET_NAME", "citrature-papers")
        self.gcs_project_id = os.getenv("GCS_PROJECT_ID", "placeholder")
        self.gcs_credentials_json = os.getenv("GCS_CREDENTIALS_JSON")
        
        # Usage Limits
        self.max_topic_papers = int(os.getenv("MAX_TOPIC_PAPERS", "30"))
        self.max_graph_depth = int(os.getenv("MAX_GRAPH_DEPTH", "3"))
        self.max_collections_per_user = int(os.getenv("MAX_COLLECTIONS_PER_USER", "1"))
        self.monthly_chat_quota = int(os.getenv("MONTHLY_CHAT_QUOTA", "100"))
        self.max_upload_size_mb = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
        
        # Security
        self.secret_key = os.getenv("SECRET_KEY", "placeholder_secret_key_min_32_chars")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Derived values
        self.allowed_mime_types = ["application/pdf"]
    
    @property
    def database_url(self) -> str:
        """Alias for postgres_dsn to maintain compatibility."""
        return self.postgres_dsn
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.max_upload_size_mb * 1024 * 1024
    
    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic."""
        return self.postgres_dsn.replace("postgresql://", "postgresql+psycopg2://")


# Global settings instance
_settings: Optional[SimpleSettings] = None


def get_settings() -> SimpleSettings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = SimpleSettings()
    return _settings
