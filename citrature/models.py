"""Database models for Citrature platform."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, 
    UniqueConstraint, Index, Numeric, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from citrature.database import Base


class User(Base):
    """User accounts."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    picture_url = Column(String(500), nullable=True)
    plan = Column(String(50), default="free", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    collections = relationship("Collection", back_populates="user", cascade="all, delete-orphan")


class Collection(Base):
    """Research paper collections."""
    __tablename__ = "collections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="collections")
    papers = relationship("Paper", back_populates="collection", cascade="all, delete-orphan")
    gap_insights = relationship("GapInsight", back_populates="collection", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_collections_user_id", "user_id"),
    )


class Author(Base):
    """Paper authors."""
    __tablename__ = "authors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    affiliation = Column(String(500), nullable=True)
    orcid = Column(String(50), nullable=True)
    
    # Relationships
    paper_authors = relationship("PaperAuthor", back_populates="author")


class Paper(Base):
    """Research papers."""
    __tablename__ = "papers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    doi = Column(String(255), nullable=True, index=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    venue = Column(String(255), nullable=True)
    url = Column(String(500), nullable=True)
    pdf_url = Column(String(500), nullable=True)
    source = Column(String(50), nullable=False)  # 'upload' or 'crossref'
    added_via = Column(String(50), nullable=False)  # 'upload' or 'topic'
    raw_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    collection = relationship("Collection", back_populates="papers")
    paper_authors = relationship("PaperAuthor", back_populates="paper", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="src_paper", foreign_keys="Citation.src_paper_id", cascade="all, delete-orphan")
    resolved_citations = relationship("Citation", back_populates="resolved_paper", foreign_keys="Citation.resolved_paper_id")
    chunks = relationship("Chunk", back_populates="paper", cascade="all, delete-orphan")
    paper_summaries = relationship("PaperSummary", back_populates="paper", cascade="all, delete-orphan", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_papers_collection_id", "collection_id"),
        Index("idx_papers_doi", "doi"),
    )


class PaperAuthor(Base):
    """Many-to-many relationship between papers and authors."""
    __tablename__ = "paper_authors"
    
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True)
    author_order = Column(Integer, nullable=False)
    
    # Relationships
    paper = relationship("Paper", back_populates="paper_authors")
    author = relationship("Author", back_populates="paper_authors")


class Citation(Base):
    """Citation relationships between papers."""
    __tablename__ = "citations"
    
    src_paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True)
    dst_doi = Column(String(255), nullable=True)
    resolved_paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=True)
    dst_title = Column(Text, nullable=True)
    dst_year = Column(Integer, nullable=True)
    
    # Relationships
    src_paper = relationship("Paper", back_populates="citations", foreign_keys=[src_paper_id])
    resolved_paper = relationship("Paper", back_populates="resolved_citations", foreign_keys=[resolved_paper_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_citations_src_paper_id", "src_paper_id"),
        Index("idx_citations_resolved_paper_id", "resolved_paper_id"),
        UniqueConstraint("src_paper_id", "dst_doi", name="uq_citations_src_dst"),
    )


class Chunk(Base):
    """Text chunks for embedding and retrieval."""
    __tablename__ = "chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    section = Column(String(100), nullable=False)  # normalized section label
    ord = Column(Integer, nullable=False)  # sequence within section
    text = Column(Text, nullable=False)
    
    # Relationships
    paper = relationship("Paper", back_populates="chunks")
    chunk_embeddings = relationship("ChunkEmbedding", back_populates="chunk", cascade="all, delete-orphan", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_chunks_paper_id_ord", "paper_id", "ord"),
    )


class ChunkEmbedding(Base):
    """Vector embeddings for chunks."""
    __tablename__ = "chunk_embeddings"
    
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("chunks.id", ondelete="CASCADE"), primary_key=True)
    embedding = Column(Vector(1536), nullable=False)  # dimension from config
    
    # Relationships
    chunk = relationship("Chunk", back_populates="chunk_embeddings")


class PaperSummary(Base):
    """AI-generated paper summaries."""
    __tablename__ = "paper_summaries"
    
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True)
    abstract_summary = Column(Text, nullable=True)
    intro_summary = Column(Text, nullable=True)
    conclusion_summary = Column(Text, nullable=True)
    tldr = Column(Text, nullable=True)
    
    # Relationships
    paper = relationship("Paper", back_populates="paper_summaries")


class GapInsight(Base):
    """Gap analysis insights."""
    __tablename__ = "gap_insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    insight = Column(Text, nullable=False)
    evidence = Column(JSONB, nullable=True)
    score = Column(Numeric(5, 4), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    collection = relationship("Collection", back_populates="gap_insights")
