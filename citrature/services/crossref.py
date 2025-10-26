"""Crossref API service for paper discovery."""

import logging
import httpx
from typing import List, Dict, Any, Optional
from citrature.config_simple import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CrossrefService:
    """Service for interacting with Crossref API."""
    
    def __init__(self):
        """Initialize Crossref client."""
        self.base_url = settings.crossref_base_url
        self.mailto = settings.crossref_mailto
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "User-Agent": f"Citrature/1.0 (mailto:{self.mailto})",
                "Accept": "application/json"
            },
            timeout=30
        )
    
    def search_works(self, query: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Search for works using Crossref API.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of work dictionaries
        """
        try:
            params = {
                "query": query,
                "rows": min(limit, 100),  # Crossref max is 100
                "sort": "relevance",
                "order": "desc"
            }
            
            response = self.client.get("/works", params=params)
            response.raise_for_status()
            
            data = response.json()
            works = data.get("message", {}).get("items", [])
            
            # Process and normalize work data
            processed_works = []
            for work in works:
                processed_work = self._process_work(work)
                if processed_work:
                    processed_works.append(processed_work)
            
            return processed_works[:limit]
            
        except Exception as exc:
            logger.error(f"Crossref search failed: {exc}", exc_info=True)
            return []
    
    def get_work_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """Get a specific work by DOI.
        
        Args:
            doi: DOI string
            
        Returns:
            Work dictionary or None if not found
        """
        try:
            # Normalize DOI
            doi = self._normalize_doi(doi)
            
            response = self.client.get(f"/works/{doi}")
            response.raise_for_status()
            
            data = response.json()
            work = data.get("message", {})
            
            return self._process_work(work)
            
        except Exception as exc:
            logger.error(f"Crossref DOI lookup failed for {doi}: {exc}", exc_info=True)
            return None
    
    def _process_work(self, work: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process and normalize a work from Crossref.
        
        Args:
            work: Raw work data from Crossref
            
        Returns:
            Processed work dictionary or None if invalid
        """
        try:
            # Extract basic metadata
            title = self._extract_title(work)
            if not title:
                return None
            
            # Extract DOI
            doi = self._extract_doi(work)
            
            # Extract authors
            authors = self._extract_authors(work)
            
            # Extract publication info
            year = self._extract_year(work)
            venue = self._extract_venue(work)
            
            # Extract abstract
            abstract = self._extract_abstract(work)
            
            # Extract URLs
            url = self._extract_url(work)
            
            return {
                "title": title,
                "doi": doi,
                "abstract": abstract,
                "year": year,
                "venue": venue,
                "url": url,
                "authors": authors,
                "raw_json": work
            }
            
        except Exception as exc:
            logger.error(f"Work processing failed: {exc}", exc_info=True)
            return None
    
    def _extract_title(self, work: Dict[str, Any]) -> Optional[str]:
        """Extract title from work data."""
        title = work.get("title", [])
        if title and len(title) > 0:
            return title[0]
        return None
    
    def _extract_doi(self, work: Dict[str, Any]) -> Optional[str]:
        """Extract DOI from work data."""
        doi = work.get("DOI")
        if doi:
            return self._normalize_doi(doi)
        return None
    
    def _extract_authors(self, work: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract authors from work data."""
        authors = []
        author_list = work.get("author", [])
        
        for author in author_list:
            author_data = {}
            
            # Extract name
            given = author.get("given", "")
            family = author.get("family", "")
            if given and family:
                author_data["name"] = f"{given} {family}"
            elif family:
                author_data["name"] = family
            elif given:
                author_data["name"] = given
            else:
                continue
            
            # Extract affiliation
            affiliation = author.get("affiliation", [])
            if affiliation and len(affiliation) > 0:
                author_data["affiliation"] = affiliation[0].get("name", "")
            
            # Extract ORCID
            orcid = author.get("ORCID")
            if orcid:
                author_data["orcid"] = orcid
            
            authors.append(author_data)
        
        return authors
    
    def _extract_year(self, work: Dict[str, Any]) -> Optional[int]:
        """Extract publication year from work data."""
        published_date = work.get("published-print") or work.get("published-online")
        if published_date:
            date_parts = published_date.get("date-parts", [])
            if date_parts and len(date_parts) > 0:
                year = date_parts[0][0]
                if isinstance(year, int) and 1900 <= year <= 2030:
                    return year
        return None
    
    def _extract_venue(self, work: Dict[str, Any]) -> Optional[str]:
        """Extract venue/journal name from work data."""
        container_title = work.get("container-title", [])
        if container_title and len(container_title) > 0:
            return container_title[0]
        return None
    
    def _extract_abstract(self, work: Dict[str, Any]) -> Optional[str]:
        """Extract abstract from work data."""
        abstract = work.get("abstract")
        if abstract:
            # Remove HTML tags if present
            import re
            clean_abstract = re.sub(r'<[^>]+>', '', abstract)
            return clean_abstract.strip()
        return None
    
    def _extract_url(self, work: Dict[str, Any]) -> Optional[str]:
        """Extract URL from work data."""
        link = work.get("link", [])
        if link and len(link) > 0:
            return link[0].get("URL")
        return None
    
    def _normalize_doi(self, doi: str) -> str:
        """Normalize DOI string."""
        if not doi:
            return ""
        
        # Remove common prefixes
        doi = doi.replace("https://doi.org/", "")
        doi = doi.replace("http://dx.doi.org/", "")
        doi = doi.replace("doi:", "")
        
        # Convert to lowercase
        doi = doi.lower().strip()
        
        return doi
