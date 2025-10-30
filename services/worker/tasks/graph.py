"""Citation graph building tasks."""

import logging
from typing import Dict, Any, List, Set, Optional
from celery import current_task
from sqlalchemy.orm import Session
from citrature.celery_app import celery_app
from citrature.database import SessionLocal
from citrature.models import Collection, Paper, Citation, Chunk, ChunkEmbedding
from citrature.services.crossref import CrossrefService
from citrature.services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="citrature.tasks.graph.build_graph_task")
def build_graph_task(self, collection_id: str, mode: str = "bfs", depth: int = 3) -> Dict[str, Any]:
    """Build citation graph for a collection.
    
    Args:
        collection_id: UUID of the collection
        mode: Traversal mode ('bfs' or 'dfs')
        depth: Maximum depth to traverse
        
    Returns:
        Dictionary with graph building results
    """
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Starting graph building"})
        
        # Get database session
        db = SessionLocal()
        try:
            # Verify collection exists
            collection = db.query(Collection).filter(Collection.id == collection_id).first()
            if not collection:
                raise ValueError(f"Collection {collection_id} not found")
            
            # Get all papers in collection
            papers = db.query(Paper).filter(Paper.collection_id == collection_id).all()
            if not papers:
                raise ValueError("No papers found in collection")
            
            self.update_state(state="PROGRESS", meta={"status": f"Found {len(papers)} papers, building graph..."})
            
            # Initialize services
            crossref_service = CrossrefService()
            embedding_service = EmbeddingService()
            
            # Build citation graph
            graph_builder = CitationGraphBuilder(db, crossref_service, embedding_service)
            
            if mode == "bfs":
                result = graph_builder.build_bfs(papers, depth)
            else:
                result = graph_builder.build_dfs(papers, depth)
            
            db.commit()
            
            return {
                "status": "success",
                "nodes_processed": result["nodes_processed"],
                "edges_created": result["edges_created"],
                "papers_added": result["papers_added"],
                "depth_reached": result["depth_reached"],
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        logger.error(f"Graph building failed: {exc}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={"status": "failed", "error": str(exc)}
        )
        raise


class CitationGraphBuilder:
    """Builder for citation graphs."""
    
    def __init__(self, db: Session, crossref_service: CrossrefService, embedding_service: EmbeddingService):
        """Initialize graph builder."""
        self.db = db
        self.crossref_service = crossref_service
        self.embedding_service = embedding_service
        self.visited_papers: Set[str] = set()
        self.visited_dois: Set[str] = set()
    
    def build_bfs(self, seed_papers: List[Paper], max_depth: int) -> Dict[str, Any]:
        """Build graph using breadth-first search."""
        from collections import deque
        
        queue = deque([(paper, 0) for paper in seed_papers])
        nodes_processed = 0
        edges_created = 0
        papers_added = 0
        max_depth_reached = 0
        
        while queue:
            current_paper, current_depth = queue.popleft()
            
            if current_depth >= max_depth:
                continue
            
            if current_paper.id in self.visited_papers:
                continue
            
            self.visited_papers.add(current_paper.id)
            nodes_processed += 1
            
            # Process citations for current paper
            citations_processed, new_papers = self._process_citations(current_paper, current_depth)
            edges_created += citations_processed
            papers_added += len(new_papers)
            
            # Add new papers to queue
            for paper in new_papers:
                if paper.id not in self.visited_papers:
                    queue.append((paper, current_depth + 1))
                    max_depth_reached = max(max_depth_reached, current_depth + 1)
        
        return {
            "nodes_processed": nodes_processed,
            "edges_created": edges_created,
            "papers_added": papers_added,
            "depth_reached": max_depth_reached,
        }
    
    def build_dfs(self, seed_papers: List[Paper], max_depth: int) -> Dict[str, Any]:
        """Build graph using depth-first search."""
        nodes_processed = 0
        edges_created = 0
        papers_added = 0
        max_depth_reached = 0
        
        for paper in seed_papers:
            result = self._dfs_recursive(paper, 0, max_depth)
            nodes_processed += result["nodes_processed"]
            edges_created += result["edges_created"]
            papers_added += result["papers_added"]
            max_depth_reached = max(max_depth_reached, result["depth_reached"])
        
        return {
            "nodes_processed": nodes_processed,
            "edges_created": edges_created,
            "papers_added": papers_added,
            "depth_reached": max_depth_reached,
        }
    
    def _dfs_recursive(self, paper: Paper, current_depth: int, max_depth: int) -> Dict[str, Any]:
        """Recursive DFS implementation."""
        if current_depth >= max_depth or paper.id in self.visited_papers:
            return {"nodes_processed": 0, "edges_created": 0, "papers_added": 0, "depth_reached": current_depth}
        
        self.visited_papers.add(paper.id)
        nodes_processed = 1
        
        # Process citations for current paper
        citations_processed, new_papers = self._process_citations(paper, current_depth)
        edges_created = citations_processed
        papers_added = len(new_papers)
        max_depth_reached = current_depth
        
        # Recursively process new papers
        for new_paper in new_papers:
            result = self._dfs_recursive(new_paper, current_depth + 1, max_depth)
            nodes_processed += result["nodes_processed"]
            edges_created += result["edges_created"]
            papers_added += result["papers_added"]
            max_depth_reached = max(max_depth_reached, result["depth_reached"])
        
        return {
            "nodes_processed": nodes_processed,
            "edges_created": edges_created,
            "papers_added": papers_added,
            "depth_reached": max_depth_reached,
        }
    
    def _process_citations(self, paper: Paper, depth: int) -> tuple[int, List[Paper]]:
        """Process citations for a paper."""
        citations_processed = 0
        new_papers = []
        
        # Get existing citations for this paper
        existing_citations = self.db.query(Citation).filter(
            Citation.src_paper_id == paper.id
        ).all()
        
        # Process each citation
        for citation in existing_citations:
            if citation.resolved_paper_id:
                # Already resolved
                citations_processed += 1
                continue
            
            # Try to resolve by DOI
            if citation.dst_doi:
                resolved_paper = self._resolve_by_doi(citation.dst_doi, paper.collection_id)
                if resolved_paper:
                    citation.resolved_paper_id = resolved_paper.id
                    citations_processed += 1
                    if resolved_paper not in new_papers:
                        new_papers.append(resolved_paper)
                    continue
            
            # Try to resolve by title and year
            if citation.dst_title and citation.dst_year:
                resolved_paper = self._resolve_by_title_year(
                    citation.dst_title, citation.dst_year, paper.collection_id
                )
                if resolved_paper:
                    citation.resolved_paper_id = resolved_paper.id
                    citations_processed += 1
                    if resolved_paper not in new_papers:
                        new_papers.append(resolved_paper)
        
        return citations_processed, new_papers
    
    def _resolve_by_doi(self, doi: str, collection_id: str) -> Optional[Paper]:
        """Resolve a paper by DOI."""
        # Check if paper already exists in collection
        existing_paper = self.db.query(Paper).filter(
            Paper.collection_id == collection_id,
            Paper.doi == doi
        ).first()
        
        if existing_paper:
            return existing_paper
        
        # Try to fetch from Crossref
        work_data = self.crossref_service.get_work_by_doi(doi)
        if not work_data:
            return None
        
        # Create new paper
        paper = Paper(
            collection_id=collection_id,
            source="crossref",
            added_via="graph",
            **work_data
        )
        self.db.add(paper)
        self.db.flush()
        
        # Create abstract chunk and embedding if available
        if work_data.get("abstract"):
            self._create_abstract_chunk(paper, work_data["abstract"])
        
        return paper
    
    def _resolve_by_title_year(self, title: str, year: int, collection_id: str) -> Optional[Paper]:
        """Resolve a paper by title and year."""
        # Check if paper already exists in collection
        existing_paper = self.db.query(Paper).filter(
            Paper.collection_id == collection_id,
            Paper.title == title,
            Paper.year == year
        ).first()
        
        if existing_paper:
            return existing_paper
        
        # Try to search Crossref
        search_results = self.crossref_service.search_works(f"{title} {year}", limit=5)
        
        # Find best match
        for work_data in search_results:
            if (work_data.get("title", "").lower() == title.lower() and 
                work_data.get("year") == year):
                
                # Create new paper
                paper = Paper(
                    collection_id=collection_id,
                    source="crossref",
                    added_via="graph",
                    **work_data
                )
                self.db.add(paper)
                self.db.flush()
                
                # Create abstract chunk and embedding if available
                if work_data.get("abstract"):
                    self._create_abstract_chunk(paper, work_data["abstract"])
                
                return paper
        
        return None
    
    def _create_abstract_chunk(self, paper: Paper, abstract: str):
        """Create abstract chunk and embedding for a paper."""
        chunk = Chunk(
            paper_id=paper.id,
            section="abstract",
            ord=0,
            text=abstract
        )
        self.db.add(chunk)
        self.db.flush()
        
        # Generate embedding
        embedding = self.embedding_service.generate_embedding(abstract)
        chunk_embedding = ChunkEmbedding(
            chunk_id=chunk.id,
            embedding=embedding
        )
        self.db.add(chunk_embedding)
