"""Ingestion endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from citrature.database import get_db
from citrature.models import User, Collection
from citrature.api.auth import get_current_user
from citrature.tasks.ingest import ingest_pdf_task, ingest_topic_task
from citrature.storage import get_gcs_client
from citrature.config_simple import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


@router.post("/pdf/{collection_id}")
async def upload_pdf(
    collection_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a PDF file for ingestion."""
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
    
    # Validate file
    if file.content_type not in settings.allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed"
        )
    
    if file.size > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB"
        )
    
    try:
        # Upload to GCS
        gcs_client = get_gcs_client()
        object_key = gcs_client.upload_pdf(collection_id, file.file, file.content_type)
        
        # Queue ingestion task
        task = ingest_pdf_task.delay(collection_id, object_key)
        
        return {
            "message": "PDF uploaded successfully",
            "task_id": task.id,
            "object_key": object_key
        }
        
    except Exception as exc:
        logger.error(f"PDF upload failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF upload failed"
        )


@router.post("/topic/{collection_id}")
async def ingest_topic(
    collection_id: str,
    query: str,
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ingest papers from a topic search."""
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
    
    # Apply limit cap
    limit = min(limit, settings.max_topic_papers)
    
    try:
        # Queue topic ingestion task
        task = ingest_topic_task.delay(collection_id, query, limit)
        
        return {
            "message": "Topic ingestion started",
            "task_id": task.id,
            "query": query,
            "limit": limit
        }
        
    except Exception as exc:
        logger.error(f"Topic ingestion failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Topic ingestion failed"
        )
