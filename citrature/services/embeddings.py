"""Embedding service for generating vector embeddings."""

import logging
import httpx
from typing import List, Optional
from citrature.config_simple import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    """Service for generating embeddings using OpenRouter API."""
    
    def __init__(self):
        """Initialize embedding service."""
        self.base_url = settings.openrouter_base_url
        self.api_key = settings.openrouter_api_key
        self.model = "text-embedding-3-small"  # 1536 dimensions
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            # Truncate text if too long (most embedding models have limits)
            if len(text) > 8000:  # Conservative limit
                text = text[:8000]
            
            response = self.client.post(
                "/embeddings",
                json={
                    "model": self.model,
                    "input": text
                }
            )
            response.raise_for_status()
            
            data = response.json()
            embedding = data["data"][0]["embedding"]
            
            return embedding
            
        except Exception as exc:
            logger.error(f"Embedding generation failed: {exc}", exc_info=True)
            # Return zero vector as fallback
            return [0.0] * settings.vector_dimension
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Truncate texts if too long
            processed_texts = []
            for text in texts:
                if len(text) > 8000:
                    text = text[:8000]
                processed_texts.append(text)
            
            response = self.client.post(
                "/embeddings",
                json={
                    "model": self.model,
                    "input": processed_texts
                }
            )
            response.raise_for_status()
            
            data = response.json()
            embeddings = [item["embedding"] for item in data["data"]]
            
            return embeddings
            
        except Exception as exc:
            logger.error(f"Batch embedding generation failed: {exc}", exc_info=True)
            # Return zero vectors as fallback
            return [[0.0] * settings.vector_dimension for _ in texts]
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
