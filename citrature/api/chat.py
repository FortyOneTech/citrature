"""Chat endpoints."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from citrature.database import get_db
from citrature.models import User, Collection
from citrature.api.auth import get_current_user
from citrature.services.openrouter import OpenRouterService
from citrature.services.embeddings import EmbeddingService
from citrature.schemas.chat import ChatRequest, ChatResponse, Citation

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{collection_id}", response_model=ChatResponse)
async def chat(
    collection_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with the research collection."""
    # Verify collection exists and belongs to user
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    try:
        # Initialize services
        openrouter_service = OpenRouterService()
        embedding_service = EmbeddingService()
        
        # Retrieve relevant chunks using hybrid search
        relevant_chunks = await _retrieve_relevant_chunks(
            collection_id, request.message, request.k or 5, db, embedding_service
        )
        
        # Build context
        context = _build_context(relevant_chunks)
        
        # Generate response
        messages = [
            {"role": "user", "content": request.message}
        ]
        
        response_text = openrouter_service.generate_chat_response(messages, context)
        
        # Extract citations
        citations = openrouter_service.extract_citations(response_text, relevant_chunks)
        
        return ChatResponse(
            answer=response_text,
            citations=citations
        )
        
    except Exception as exc:
        logger.error(f"Chat failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat failed"
        )


async def _retrieve_relevant_chunks(collection_id: str, query: str, k: int, db: Session, embedding_service: EmbeddingService) -> List[dict]:
    """Retrieve relevant chunks using hybrid search."""
    # This is a simplified implementation
    # In a real implementation, you'd use BM25 + vector search
    
    # Get all chunks in the collection
    chunks = db.query(collection.chunks).all()
    
    if not chunks:
        return []
    
    # Generate query embedding
    query_embedding = embedding_service.generate_embedding(query)
    
    # Calculate similarity scores (simplified)
    scored_chunks = []
    for chunk in chunks:
        if chunk.chunk_embeddings:
            # Calculate cosine similarity
            similarity = _cosine_similarity(query_embedding, chunk.chunk_embeddings.embedding)
            scored_chunks.append({
                "chunk": chunk,
                "score": similarity
            })
    
    # Sort by score and return top k
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    
    return [item["chunk"] for item in scored_chunks[:k]]


def _build_context(chunks: List[dict]) -> str:
    """Build context string from chunks."""
    context_parts = []
    
    for chunk in chunks:
        context_parts.append(f"Section: {chunk.section}\n{chunk.text}\n")
    
    return "\n".join(context_parts)


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    import numpy as np
    
    a = np.array(a)
    b = np.array(b)
    
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)
