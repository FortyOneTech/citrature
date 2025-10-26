"""OpenRouter API service for LLM interactions."""

import logging
import httpx
from typing import Dict, Any, Optional
from citrature.config_simple import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenRouterService:
    """Service for interacting with OpenRouter API."""
    
    def __init__(self):
        """Initialize OpenRouter client."""
        self.base_url = settings.openrouter_base_url
        self.api_key = settings.openrouter_api_key
        self.model = "anthropic/claude-3-haiku"  # Fast and cost-effective model
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=120
        )
    
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using OpenRouter API.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        try:
            response = self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "stream": False
                }
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            return content.strip()
            
        except Exception as exc:
            logger.error(f"Text generation failed: {exc}", exc_info=True)
            return ""
    
    def generate_chat_response(self, messages: list[Dict[str, str]], context: str = "") -> str:
        """Generate a chat response with context.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            context: Additional context to include
            
        Returns:
            Generated response
        """
        try:
            # Prepare messages with context
            system_message = {
                "role": "system",
                "content": f"""You are an AI research assistant for Citrature, a platform for analyzing research papers and citation graphs. 
                
You have access to a collection of research papers and can help users understand:
- Paper content and relationships
- Research gaps and opportunities
- Citation patterns and trends
- Summaries and insights

Context from relevant papers:
{context}

Please provide helpful, accurate, and well-reasoned responses based on the available information."""
            }
            
            all_messages = [system_message] + messages
            
            response = self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": all_messages,
                    "max_tokens": 2000,
                    "temperature": 0.7,
                    "stream": False
                }
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            return content.strip()
            
        except Exception as exc:
            logger.error(f"Chat response generation failed: {exc}", exc_info=True)
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."
    
    def extract_citations(self, text: str, available_papers: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """Extract citations from generated text.
        
        Args:
            text: Generated text to extract citations from
            available_papers: List of available papers with metadata
            
        Returns:
            List of citation dictionaries
        """
        try:
            # Simple citation extraction (in a real implementation, you'd use more sophisticated NLP)
            citations = []
            
            # Look for paper titles in the text
            for paper in available_papers:
                title = paper.get("title", "")
                if title and title.lower() in text.lower():
                    citations.append({
                        "paper_id": paper.get("id"),
                        "title": title,
                        "year": paper.get("year"),
                        "venue": paper.get("venue"),
                        "chunk_id": None,  # Would need more sophisticated matching
                    })
            
            return citations
            
        except Exception as exc:
            logger.error(f"Citation extraction failed: {exc}", exc_info=True)
            return []
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
