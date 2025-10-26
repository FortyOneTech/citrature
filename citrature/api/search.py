"""Search endpoints."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from citrature.database import get_db
from citrature.models import User, Collection
from citrature.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{collection_id}")
async def search_collection(
    collection_id: str,
    q: str,
    k: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search within a collection."""
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
    
    # This is a simplified search implementation
    # In a real implementation, you'd use BM25 + vector search
    
    # Get all chunks in the collection
    chunks = db.query(collection.chunks).all()
    
    # Simple text search (case-insensitive)
    matching_chunks = []
    query_lower = q.lower()
    
    for chunk in chunks:
        if query_lower in chunk.text.lower():
            matching_chunks.append({
                "chunk_id": chunk.id,
                "paper_id": chunk.paper_id,
                "section": chunk.section,
                "text": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                "score": 1.0  # Simplified scoring
            })
    
    # Sort by score and return top k
    matching_chunks.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "query": q,
        "results": matching_chunks[:k],
        "total": len(matching_chunks)
    }
