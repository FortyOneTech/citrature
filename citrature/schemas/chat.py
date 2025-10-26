"""Chat schemas."""

from typing import List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str
    k: Optional[int] = 5


class Citation(BaseModel):
    """Citation schema."""
    paper_id: str
    chunk_id: Optional[str] = None
    title: str
    year: Optional[int] = None
    venue: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response schema."""
    answer: str
    citations: List[Citation]
