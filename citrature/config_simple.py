"""Simple configuration for migrations."""

import os
from typing import List, Optional


class SimpleSettings:
    """Simple settings for migrations that don't require complex validation."""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://citrature:password@localhost:5432/citrature")
        self.vector_dimension = int(os.getenv("VECTOR_DIMENSION", "1536"))
        self.rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "placeholder")
        self.crossref_base_url = os.getenv("CROSSREF_BASE_URL", "https://api.crossref.org")
        self.crossref_mailto = os.getenv("CROSSREF_MAILTO", "test@example.com")
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID", "placeholder")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "placeholder")
        self.google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        self.grobid_base_url = os.getenv("GROBID_BASE_URL", "http://localhost:8070")
        self.gcs_bucket_name = os.getenv("GCS_BUCKET_NAME", "citrature-papers")
        self.gcs_project_id = os.getenv("GCS_PROJECT_ID", "placeholder")
        self.gcs_credential_path = os.getenv("GCS_CREDENTIAL_PATH")
        self.max_topic_papers = int(os.getenv("MAX_TOPIC_PAPERS", "30"))
        self.max_graph_depth = int(os.getenv("MAX_GRAPH_DEPTH", "3"))
        self.max_collections_per_user = int(os.getenv("MAX_COLLECTIONS_PER_USER", "1"))
        self.monthly_chat_quota = int(os.getenv("MONTHLY_CHAT_QUOTA", "100"))
        self.max_upload_size_mb = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
        self.allowed_mime_types = ["application/pdf"]  # Default value
        self.secret_key = os.getenv("SECRET_KEY", "placeholder_secret_key")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.max_upload_size_mb * 1024 * 1024
    
    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic."""
        return self.database_url.replace("postgresql://", "postgresql+psycopg2://")


# Global settings instance
_settings: Optional[SimpleSettings] = None


def get_settings() -> SimpleSettings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = SimpleSettings()
    return _settings
