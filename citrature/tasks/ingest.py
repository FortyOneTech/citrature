"""PDF and topic ingestion tasks."""

import uuid
import logging
from typing import List, Dict, Any, Optional
from celery import current_task
from sqlalchemy.orm import Session
from citrature.celery_app import celery_app
from citrature.database import SessionLocal
from citrature.models import Collection, Paper, Author, PaperAuthor, Chunk, ChunkEmbedding
from citrature.storage import get_gcs_client
from citrature.services.grobid import GROBIDService
from citrature.services.crossref import CrossrefService
from citrature.services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="citrature.tasks.ingest.ingest_pdf_task")
def ingest_pdf_task(self, collection_id: str, object_key: str) -> Dict[str, Any]:
    """Ingest a PDF file and extract metadata, text, and citations.
    
    Args:
        collection_id: UUID of the collection
        object_key: GCS object key for the PDF file
        
    Returns:
        Dictionary with ingestion results
    """
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Starting PDF ingestion"})
        
        # Get database session
        db = SessionLocal()
        try:
            # Verify collection exists
            collection = db.query(Collection).filter(Collection.id == collection_id).first()
            if not collection:
                raise ValueError(f"Collection {collection_id} not found")
            
            # Download PDF from GCS
            gcs_client = get_gcs_client()
            pdf_data = gcs_client.download_file(object_key)
            
            self.update_state(state="PROGRESS", meta={"status": "Processing PDF with GROBID"})
            
            # Process with GROBID
            grobid_service = GROBIDService()
            tei_result = grobid_service.process_pdf(pdf_data)
            
            if not tei_result:
                # Fallback to PyMuPDF
                self.update_state(state="PROGRESS", meta={"status": "Using PyMuPDF fallback"})
                tei_result = grobid_service.process_pdf_fallback(pdf_data)
            
            if not tei_result:
                raise ValueError("Failed to process PDF with both GROBID and PyMuPDF")
            
            # Store TEI XML in GCS
            paper_id = str(uuid.uuid4())
            tei_key = gcs_client.upload_tei(collection_id, paper_id, tei_result["tei_xml"])
            
            self.update_state(state="PROGRESS", meta={"status": "Extracting metadata and text"})
            
            # Extract paper metadata
            paper_data = tei_result["metadata"]
            paper_data.update({
                "id": paper_id,
                "collection_id": collection_id,
                "source": "upload",
                "added_via": "upload",
                "pdf_url": f"gs://{gcs_client.bucket.name}/{object_key}",
            })
            
            # Create paper record
            paper = Paper(**paper_data)
            db.add(paper)
            db.flush()
            
            # Process authors
            for i, author_data in enumerate(tei_result["authors"]):
                author = Author(**author_data)
                db.add(author)
                db.flush()
                
                # Link author to paper
                paper_author = PaperAuthor(
                    paper_id=paper.id,
                    author_id=author.id,
                    author_order=i
                )
                db.add(paper_author)
            
            # Process citations
            for citation_data in tei_result["citations"]:
                citation_data["src_paper_id"] = paper.id
                # Citations will be processed later in graph building
            
            # Process chunks
            embedding_service = EmbeddingService()
            for i, chunk_data in enumerate(tei_result["chunks"]):
                chunk = Chunk(
                    id=str(uuid.uuid4()),
                    paper_id=paper.id,
                    **chunk_data,
                    ord=i
                )
                db.add(chunk)
                db.flush()
                
                # Generate embedding
                self.update_state(state="PROGRESS", meta={"status": f"Generating embeddings for chunk {i+1}"})
                embedding = embedding_service.generate_embedding(chunk.text)
                
                chunk_embedding = ChunkEmbedding(
                    chunk_id=chunk.id,
                    embedding=embedding
                )
                db.add(chunk_embedding)
            
            db.commit()
            
            return {
                "status": "success",
                "paper_id": paper.id,
                "title": paper.title,
                "chunks_created": len(tei_result["chunks"]),
                "authors_created": len(tei_result["authors"]),
                "citations_found": len(tei_result["citations"]),
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        logger.error(f"PDF ingestion failed: {exc}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={"status": "failed", "error": str(exc)}
        )
        raise


@celery_app.task(bind=True, name="citrature.tasks.ingest.ingest_topic_task")
def ingest_topic_task(self, collection_id: str, query: str, limit: int = 30) -> Dict[str, Any]:
    """Ingest papers from a topic search via Crossref.
    
    Args:
        collection_id: UUID of the collection
        query: Search query string
        limit: Maximum number of papers to fetch
        
    Returns:
        Dictionary with ingestion results
    """
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Starting topic ingestion"})
        
        # Get database session
        db = SessionLocal()
        try:
            # Verify collection exists
            collection = db.query(Collection).filter(Collection.id == collection_id).first()
            if not collection:
                raise ValueError(f"Collection {collection_id} not found")
            
            # Search Crossref
            crossref_service = CrossrefService()
            search_results = crossref_service.search_works(query, limit)
            
            self.update_state(state="PROGRESS", meta={"status": f"Found {len(search_results)} papers, processing..."})
            
            papers_created = 0
            papers_updated = 0
            chunks_created = 0
            
            embedding_service = EmbeddingService()
            
            for i, work_data in enumerate(search_results):
                self.update_state(
                    state="PROGRESS", 
                    meta={"status": f"Processing paper {i+1}/{len(search_results)}"}
                )
                
                # Check if paper already exists (by DOI or title+year)
                existing_paper = None
                if work_data.get("doi"):
                    existing_paper = db.query(Paper).filter(
                        Paper.collection_id == collection_id,
                        Paper.doi == work_data["doi"]
                    ).first()
                
                if not existing_paper and work_data.get("title") and work_data.get("year"):
                    existing_paper = db.query(Paper).filter(
                        Paper.collection_id == collection_id,
                        Paper.title == work_data["title"],
                        Paper.year == work_data["year"]
                    ).first()
                
                if existing_paper:
                    # Update existing paper
                    for key, value in work_data.items():
                        if hasattr(existing_paper, key) and value is not None:
                            setattr(existing_paper, key, value)
                    papers_updated += 1
                    paper = existing_paper
                else:
                    # Create new paper
                    paper_data = {
                        "id": str(uuid.uuid4()),
                        "collection_id": collection_id,
                        "source": "crossref",
                        "added_via": "topic",
                        "raw_json": work_data,
                        **work_data
                    }
                    paper = Paper(**paper_data)
                    db.add(paper)
                    db.flush()
                    papers_created += 1
                
                # Create abstract chunk if available
                if work_data.get("abstract"):
                    chunk = Chunk(
                        id=str(uuid.uuid4()),
                        paper_id=paper.id,
                        section="abstract",
                        ord=0,
                        text=work_data["abstract"]
                    )
                    db.add(chunk)
                    db.flush()
                    
                    # Generate embedding
                    embedding = embedding_service.generate_embedding(chunk.text)
                    chunk_embedding = ChunkEmbedding(
                        chunk_id=chunk.id,
                        embedding=embedding
                    )
                    db.add(chunk_embedding)
                    chunks_created += 1
            
            db.commit()
            
            return {
                "status": "success",
                "papers_created": papers_created,
                "papers_updated": papers_updated,
                "chunks_created": chunks_created,
                "total_found": len(search_results),
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        logger.error(f"Topic ingestion failed: {exc}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={"status": "failed", "error": str(exc)}
        )
        raise
