"""Collections schemas."""

from datetime import datetime
from pydantic import BaseModel


class CollectionCreate(BaseModel):
    """Collection creation schema."""
    title: str


class CollectionResponse(BaseModel):
    """Collection response schema."""
    id: str
    title: str
    created_at: datetime
    paper_count: int
    
    class Config:
        from_attributes = True


class CollectionListResponse(BaseModel):
    """Collection list response schema."""
    id: str
    title: str
    created_at: datetime
    paper_count: int
    
    class Config:
        from_attributes = True
