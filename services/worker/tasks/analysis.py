"""Gap analysis and summarization tasks."""

import logging
import uuid
from typing import Dict, Any, List
from celery import current_task
from sqlalchemy.orm import Session
from citrature.celery_app import celery_app
from citrature.database import SessionLocal
from citrature.models import Collection, Paper, PaperSummary, GapInsight, Chunk
from citrature.services.embeddings import EmbeddingService
from citrature.services.openrouter import OpenRouterService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="citrature.tasks.analysis.gap_analysis_task")
def gap_analysis_task(self, collection_id: str) -> Dict[str, Any]:
    """Perform gap analysis on a collection.
    
    Args:
        collection_id: UUID of the collection
        
    Returns:
        Dictionary with gap analysis results
    """
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Starting gap analysis"})
        
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
            
            self.update_state(state="PROGRESS", meta={"status": f"Analyzing {len(papers)} papers..."})
            
            # Initialize services
            embedding_service = EmbeddingService()
            openrouter_service = OpenRouterService()
            
            # Perform gap analysis
            gap_analyzer = GapAnalyzer(db, embedding_service, openrouter_service)
            insights = gap_analyzer.analyze_collection(collection, papers)
            
            # Save insights to database
            for insight_data in insights:
                insight = GapInsight(
                    id=str(uuid.uuid4()),
                    collection_id=collection_id,
                    **insight_data
                )
                db.add(insight)
            
            db.commit()
            
            return {
                "status": "success",
                "insights_created": len(insights),
                "papers_analyzed": len(papers),
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        logger.error(f"Gap analysis failed: {exc}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={"status": "failed", "error": str(exc)}
        )
        raise


@celery_app.task(bind=True, name="citrature.tasks.analysis.summarize_paper_task")
def summarize_paper_task(self, paper_id: str) -> Dict[str, Any]:
    """Generate summaries for a paper.
    
    Args:
        paper_id: UUID of the paper
        
    Returns:
        Dictionary with summarization results
    """
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Starting paper summarization"})
        
        # Get database session
        db = SessionLocal()
        try:
            # Get paper
            paper = db.query(Paper).filter(Paper.id == paper_id).first()
            if not paper:
                raise ValueError(f"Paper {paper_id} not found")
            
            # Get paper chunks by section
            chunks = db.query(Chunk).filter(Chunk.paper_id == paper_id).all()
            
            # Group chunks by section
            sections = {}
            for chunk in chunks:
                section = chunk.section
                if section not in sections:
                    sections[section] = []
                sections[section].append(chunk.text)
            
            self.update_state(state="PROGRESS", meta={"status": "Generating summaries..."})
            
            # Initialize services
            openrouter_service = OpenRouterService()
            
            # Generate summaries
            summarizer = PaperSummarizer(openrouter_service)
            summaries = summarizer.generate_summaries(sections)
            
            # Save or update paper summary
            existing_summary = db.query(PaperSummary).filter(PaperSummary.paper_id == paper_id).first()
            if existing_summary:
                for key, value in summaries.items():
                    if value:
                        setattr(existing_summary, key, value)
            else:
                summary = PaperSummary(
                    paper_id=paper_id,
                    **summaries
                )
                db.add(summary)
            
            db.commit()
            
            return {
                "status": "success",
                "summaries_generated": len([s for s in summaries.values() if s]),
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        logger.error(f"Paper summarization failed: {exc}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={"status": "failed", "error": str(exc)}
        )
        raise


class GapAnalyzer:
    """Analyzer for identifying research gaps."""
    
    def __init__(self, db: Session, embedding_service: EmbeddingService, openrouter_service: OpenRouterService):
        """Initialize gap analyzer."""
        self.db = db
        self.embedding_service = embedding_service
        self.openrouter_service = openrouter_service
    
    def analyze_collection(self, collection: Collection, papers: List[Paper]) -> List[Dict[str, Any]]:
        """Analyze collection for research gaps."""
        # Extract text for analysis (prefer abstracts, fallback to titles)
        texts = []
        paper_ids = []
        
        for paper in papers:
            if paper.abstract:
                texts.append(paper.abstract)
            elif paper.title:
                texts.append(paper.title)
            else:
                continue
            paper_ids.append(paper.id)
        
        if len(texts) < 3:
            return []  # Need at least 3 papers for meaningful analysis
        
        # Generate embeddings
        embeddings = self.embedding_service.generate_embeddings_batch(texts)
        
        # Perform clustering analysis
        clusters = self._cluster_papers(embeddings, texts, paper_ids)
        
        # Calculate metrics
        metrics = self._calculate_metrics(papers, clusters)
        
        # Generate insights
        insights = self._generate_insights(metrics, clusters, papers)
        
        return insights
    
    def _cluster_papers(self, embeddings: List[List[float]], texts: List[str], paper_ids: List[str]) -> List[Dict[str, Any]]:
        """Cluster papers based on embeddings."""
        try:
            from sklearn.cluster import KMeans
            import numpy as np
            
            # Determine number of clusters (heuristic)
            n_clusters = min(max(2, len(embeddings) // 3), 8)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            # Group papers by cluster
            clusters = []
            for i in range(n_clusters):
                cluster_papers = []
                for j, label in enumerate(cluster_labels):
                    if label == i:
                        cluster_papers.append({
                            "paper_id": paper_ids[j],
                            "text": texts[j],
                            "embedding": embeddings[j]
                        })
                
                if cluster_papers:
                    clusters.append({
                        "id": i,
                        "papers": cluster_papers,
                        "centroid": kmeans.cluster_centers_[i].tolist()
                    })
            
            return clusters
            
        except Exception as exc:
            logger.error(f"Clustering failed: {exc}", exc_info=True)
            return []
    
    def _calculate_metrics(self, papers: List[Paper], clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate research metrics."""
        metrics = {
            "total_papers": len(papers),
            "clusters": len(clusters),
            "coverage": 0.0,
            "novelty": 0.0,
            "trajectory_growth": 0.0,
            "method_diversity": 0.0,
        }
        
        if not papers or not clusters:
            return metrics
        
        # Calculate coverage (papers per cluster)
        metrics["coverage"] = len(papers) / len(clusters)
        
        # Calculate novelty (inverse of cluster density)
        total_embeddings = []
        for cluster in clusters:
            for paper in cluster["papers"]:
                total_embeddings.append(paper["embedding"])
        
        if total_embeddings:
            # Calculate average distance between papers
            import numpy as np
            embeddings_array = np.array(total_embeddings)
            distances = []
            for i in range(len(embeddings_array)):
                for j in range(i + 1, len(embeddings_array)):
                    dist = np.linalg.norm(embeddings_array[i] - embeddings_array[j])
                    distances.append(dist)
            
            if distances:
                metrics["novelty"] = 1.0 / (np.mean(distances) + 1e-6)
        
        # Calculate trajectory growth (recent papers vs older)
        years = [p.year for p in papers if p.year]
        if years:
            recent_years = [y for y in years if y >= 2020]
            metrics["trajectory_growth"] = len(recent_years) / len(years)
        
        # Calculate method diversity (venue diversity)
        venues = [p.venue for p in papers if p.venue]
        if venues:
            unique_venues = len(set(venues))
            metrics["method_diversity"] = unique_venues / len(venues)
        
        return metrics
    
    def _generate_insights(self, metrics: Dict[str, Any], clusters: List[Dict[str, Any]], papers: List[Paper]) -> List[Dict[str, Any]]:
        """Generate gap insights based on metrics."""
        insights = []
        
        # Generate insights based on different criteria
        if metrics["coverage"] < 2.0:
            insights.append({
                "insight": f"Low coverage detected: only {metrics['coverage']:.1f} papers per research cluster. Consider expanding literature in underrepresented areas.",
                "score": 0.8,
                "evidence": {
                    "metric": "coverage",
                    "value": metrics["coverage"],
                    "clusters": len(clusters)
                }
            })
        
        if metrics["novelty"] > 0.5:
            insights.append({
                "insight": f"High novelty potential detected (score: {metrics['novelty']:.2f}). Research areas show significant conceptual gaps that could be explored.",
                "score": 0.7,
                "evidence": {
                    "metric": "novelty",
                    "value": metrics["novelty"]
                }
            })
        
        if metrics["trajectory_growth"] < 0.3:
            insights.append({
                "insight": f"Limited recent research activity: only {metrics['trajectory_growth']:.1%} of papers are from 2020 or later. Recent developments may be underrepresented.",
                "score": 0.6,
                "evidence": {
                    "metric": "trajectory_growth",
                    "value": metrics["trajectory_growth"]
                }
            })
        
        if metrics["method_diversity"] < 0.5:
            insights.append({
                "insight": f"Low methodological diversity: only {metrics['method_diversity']:.1%} unique venues. Consider exploring interdisciplinary approaches.",
                "score": 0.5,
                "evidence": {
                    "metric": "method_diversity",
                    "value": metrics["method_diversity"]
                }
            })
        
        # Sort by score and return top 5
        insights.sort(key=lambda x: x["score"], reverse=True)
        return insights[:5]


class PaperSummarizer:
    """Summarizer for research papers."""
    
    def __init__(self, openrouter_service: OpenRouterService):
        """Initialize summarizer."""
        self.openrouter_service = openrouter_service
    
    def generate_summaries(self, sections: Dict[str, List[str]]) -> Dict[str, str]:
        """Generate summaries for paper sections."""
        summaries = {}
        
        # Generate abstract summary
        if "abstract" in sections:
            abstract_text = " ".join(sections["abstract"])
            summaries["abstract_summary"] = self._summarize_text(abstract_text, "abstract")
        
        # Generate introduction summary
        if "introduction" in sections:
            intro_text = " ".join(sections["introduction"])
            summaries["intro_summary"] = self._summarize_text(intro_text, "introduction")
        
        # Generate conclusion summary
        if "conclusion" in sections:
            conclusion_text = " ".join(sections["conclusion"])
            summaries["conclusion_summary"] = self._summarize_text(conclusion_text, "conclusion")
        
        # Generate TL;DR
        all_text = " ".join([" ".join(texts) for texts in sections.values()])
        summaries["tldr"] = self._generate_tldr(all_text)
        
        return summaries
    
    def _summarize_text(self, text: str, section_type: str) -> str:
        """Summarize a section of text."""
        if len(text) < 100:
            return text  # Too short to summarize
        
        prompt = f"""Summarize the following {section_type} section from a research paper in 2-3 sentences:

{text[:2000]}  # Truncate if too long

Summary:"""
        
        try:
            response = self.openrouter_service.generate_text(prompt)
            return response.strip()
        except Exception as exc:
            logger.error(f"Summarization failed for {section_type}: {exc}", exc_info=True)
            return text[:200] + "..." if len(text) > 200 else text
    
    def _generate_tldr(self, text: str) -> str:
        """Generate a TL;DR for the entire paper."""
        if len(text) < 200:
            return text
        
        prompt = f"""Generate a concise TL;DR (2-3 sentences) for this research paper:

{text[:3000]}  # Truncate if too long

TL;DR:"""
        
        try:
            response = self.openrouter_service.generate_text(prompt)
            return response.strip()
        except Exception as exc:
            logger.error(f"TL;DR generation failed: {exc}", exc_info=True)
            return text[:300] + "..." if len(text) > 300 else text
