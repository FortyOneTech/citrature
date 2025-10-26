"""Collections management endpoints."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from citrature.database import get_db
from citrature.models import User, Collection
from citrature.schemas.collections import CollectionCreate, CollectionResponse, CollectionListResponse
from citrature.api.auth import get_current_user
from citrature.config_simple import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


@router.post("/", response_model=CollectionResponse)
async def create_collection(
    collection: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new collection."""
    # Check collection limit for free plan
    existing_collections = db.query(Collection).filter(Collection.user_id == current_user.id).count()
    if existing_collections >= settings.max_collections_per_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Free plan limited to {settings.max_collections_per_user} collection(s)"
        )
    
    # Create collection
    db_collection = Collection(
        title=collection.title,
        user_id=current_user.id
    )
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    
    return CollectionResponse(
        id=str(db_collection.id),
        title=db_collection.title,
        created_at=db_collection.created_at,
        paper_count=0
    )


@router.get("/", response_model=List[CollectionListResponse])
async def list_collections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's collections."""
    collections = db.query(Collection).filter(Collection.user_id == current_user.id).all()
    
    result = []
    for collection in collections:
        paper_count = len(collection.papers)
        result.append(CollectionListResponse(
            id=str(collection.id),
            title=collection.title,
            created_at=collection.created_at,
            paper_count=paper_count
        ))
    
    return result


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific collection."""
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    paper_count = len(collection.papers)
    
    return CollectionResponse(
        id=str(collection.id),
        title=collection.title,
        created_at=collection.created_at,
        paper_count=paper_count
    )


@router.delete("/{collection_id}")
async def delete_collection(
    collection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a collection."""
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    db.delete(collection)
    db.commit()
    
    return {"message": "Collection deleted successfully"}
