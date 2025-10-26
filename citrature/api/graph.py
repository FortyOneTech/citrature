"""Graph building endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from citrature.database import get_db
from citrature.models import User, Collection
from citrature.api.auth import get_current_user
from citrature.tasks.graph import build_graph_task
from citrature.config_simple import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


@router.post("/build/{collection_id}")
async def build_graph(
    collection_id: str,
    mode: str = "bfs",
    depth: int = 3,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Build citation graph for a collection."""
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
    
    # Apply depth cap
    depth = min(depth, settings.max_graph_depth)
    
    try:
        # Queue graph building task
        task = build_graph_task.delay(collection_id, mode, depth)
        
        return {
            "message": "Graph building started",
            "task_id": task.id,
            "mode": mode,
            "depth": depth
        }
        
    except Exception as exc:
        logger.error(f"Graph building failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Graph building failed"
        )


@router.get("/{collection_id}")
async def get_graph(
    collection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current graph state for a collection."""
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
    
    # Get papers and citations
    papers = collection.papers
    citations = collection.citations
    
    # Format for frontend
    nodes = []
    for paper in papers:
        nodes.append({
            "id": paper.id,
            "title": paper.title,
            "year": paper.year,
            "venue": paper.venue,
            "doi": paper.doi
        })
    
    edges = []
    for citation in citations:
        if citation.resolved_paper_id:
            edges.append({
                "source": citation.src_paper_id,
                "target": citation.resolved_paper_id,
                "resolved": True
            })
        else:
            edges.append({
                "source": citation.src_paper_id,
                "target": citation.dst_doi or citation.dst_title,
                "resolved": False
            })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "total_papers": len(papers),
        "total_citations": len(citations)
    }
