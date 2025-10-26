"""GROBID service for PDF processing and TEI extraction."""

import logging
import fitz  # PyMuPDF
from typing import Dict, Any, Optional, List
from grobid_client.client import ApiClient
from citrature.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GROBIDService:
    """Service for processing PDFs with GROBID."""
    
    def __init__(self):
        """Initialize GROBID client."""
        self.client = ApiClient(
            base_url=settings.grobid_base_url,
            timeout=60
        )
    
    def process_pdf(self, pdf_data: bytes) -> Optional[Dict[str, Any]]:
        """Process PDF with GROBID and extract TEI XML.
        
        Args:
            pdf_data: PDF file content as bytes
            
        Returns:
            Dictionary with extracted data or None if failed
        """
        try:
            # Process with GROBID
            result = self.client.process_pdf(
                "processFulltextDocument",
                pdf_data,
                generateIDs=True,
                consolidate_header=True,
                consolidate_citations=True,
                include_raw_citations=True,
                include_raw_affiliations=True,
                tei_coordinates=True,
                segment_sentences=True
            )
            
            if not result:
                return None
            
            # Parse TEI XML to extract structured data
            return self._parse_tei_xml(result)
            
        except Exception as exc:
            logger.error(f"GROBID processing failed: {exc}", exc_info=True)
            return None
    
    def process_pdf_fallback(self, pdf_data: bytes) -> Optional[Dict[str, Any]]:
        """Fallback PDF processing using PyMuPDF.
        
        Args:
            pdf_data: PDF file content as bytes
            
        Returns:
            Dictionary with extracted data or None if failed
        """
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            
            # Extract text and basic metadata
            text = ""
            for page in doc:
                text += page.get_text()
            
            # Extract basic metadata
            metadata = doc.metadata
            
            # Simple section detection (heuristic-based)
            sections = self._detect_sections(text)
            
            # Create minimal TEI-like structure
            tei_xml = self._create_minimal_tei(metadata, text, sections)
            
            # Parse the minimal TEI
            return self._parse_tei_xml(tei_xml)
            
        except Exception as exc:
            logger.error(f"PyMuPDF fallback processing failed: {exc}", exc_info=True)
            return None
    
    def _detect_sections(self, text: str) -> List[Dict[str, Any]]:
        """Detect sections in text using heuristics.
        
        Args:
            text: Full text content
            
        Returns:
            List of section dictionaries
        """
        sections = []
        lines = text.split('\n')
        
        current_section = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers (simple heuristics)
            if self._is_section_header(line):
                if current_section:
                    sections.append({
                        "name": current_section,
                        "text": '\n'.join(current_text)
                    })
                
                current_section = self._normalize_section_name(line)
                current_text = []
            else:
                current_text.append(line)
        
        # Add final section
        if current_section and current_text:
            sections.append({
                "name": current_section,
                "text": '\n'.join(current_text)
            })
        
        return sections
    
    def _is_section_header(self, line: str) -> bool:
        """Check if a line is likely a section header."""
        line_lower = line.lower()
        
        # Common section headers
        section_indicators = [
            "abstract", "introduction", "methodology", "methods",
            "results", "discussion", "conclusion", "references",
            "acknowledgments", "appendix"
        ]
        
        for indicator in section_indicators:
            if indicator in line_lower and len(line) < 100:
                return True
        
        return False
    
    def _normalize_section_name(self, line: str) -> str:
        """Normalize section name to standard format."""
        line_lower = line.lower()
        
        if "abstract" in line_lower:
            return "abstract"
        elif "introduction" in line_lower:
            return "introduction"
        elif "method" in line_lower:
            return "methods"
        elif "result" in line_lower:
            return "results"
        elif "discussion" in line_lower:
            return "discussion"
        elif "conclusion" in line_lower:
            return "conclusion"
        elif "reference" in line_lower:
            return "references"
        else:
            return "other"
    
    def _create_minimal_tei(self, metadata: Dict, text: str, sections: List[Dict]) -> str:
        """Create minimal TEI XML structure."""
        # This is a simplified TEI structure for fallback
        # In a real implementation, you'd want more sophisticated parsing
        
        title = metadata.get("title", "Unknown Title")
        authors = metadata.get("author", "").split(";") if metadata.get("author") else []
        
        tei_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title>{title}</title>
                {"".join([f"<author>{author.strip()}</author>" for author in authors])}
            </titleStmt>
        </fileDesc>
    </teiHeader>
    <text>
        <body>
            {"".join([f'<div type="section" n="{section["name"]}">{section["text"]}</div>' for section in sections])}
        </body>
    </text>
</TEI>"""
        
        return tei_xml
    
    def _parse_tei_xml(self, tei_xml: str) -> Dict[str, Any]:
        """Parse TEI XML and extract structured data.
        
        Args:
            tei_xml: TEI XML content as string
            
        Returns:
            Dictionary with extracted data
        """
        # This is a simplified parser
        # In a real implementation, you'd use proper XML parsing
        
        import re
        
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', tei_xml, re.DOTALL)
        title = title_match.group(1).strip() if title_match else "Unknown Title"
        
        # Extract authors
        author_matches = re.findall(r'<author>(.*?)</author>', tei_xml, re.DOTALL)
        authors = [{"name": author.strip()} for author in author_matches]
        
        # Extract sections
        section_matches = re.findall(r'<div type="section" n="([^"]*)"[^>]*>(.*?)</div>', tei_xml, re.DOTALL)
        sections = []
        for section_name, section_text in section_matches:
            sections.append({
                "section": section_name,
                "text": section_text.strip()
            })
        
        # Create chunks from sections
        chunks = []
        for i, section in enumerate(sections):
            if section["text"]:
                chunks.append({
                    "section": section["section"],
                    "text": section["text"]
                })
        
        return {
            "tei_xml": tei_xml,
            "metadata": {
                "title": title,
                "year": None,  # Would need more sophisticated parsing
                "venue": None,
                "doi": None,
            },
            "authors": authors,
            "citations": [],  # Would need citation extraction
            "chunks": chunks
        }
