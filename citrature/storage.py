"""Google Cloud Storage integration for file management."""

import uuid
from typing import Optional, BinaryIO
from google.cloud import storage
from google.cloud.exceptions import NotFound
from citrature.config_simple import get_settings

settings = get_settings()


class GCSClient:
    """Google Cloud Storage client for file operations."""
    
    def __init__(self):
        """Initialize GCS client with credentials."""
        if settings.gcs_credential_path:
            self.client = storage.Client.from_service_account_json(
                settings.gcs_credential_path,
                project=settings.gcs_project_id
            )
        else:
            # Use default credentials (e.g., from environment)
            self.client = storage.Client(project=settings.gcs_project_id)
        
        self.bucket = self.client.bucket(settings.gcs_bucket_name)
    
    def upload_pdf(self, collection_id: str, file_data: BinaryIO, content_type: str = "application/pdf") -> str:
        """Upload a PDF file to GCS.
        
        Args:
            collection_id: UUID of the collection
            file_data: File-like object containing PDF data
            content_type: MIME type of the file
            
        Returns:
            Object key for the uploaded file
        """
        file_id = str(uuid.uuid4())
        object_key = f"collections/{collection_id}/uploads/{file_id}.pdf"
        
        blob = self.bucket.blob(object_key)
        blob.upload_from_file(
            file_data,
            content_type=content_type
        )
        
        return object_key
    
    def upload_tei(self, collection_id: str, paper_id: str, tei_data: str) -> str:
        """Upload TEI XML data to GCS.
        
        Args:
            collection_id: UUID of the collection
            paper_id: UUID of the paper
            tei_data: TEI XML content as string
            
        Returns:
            Object key for the uploaded file
        """
        object_key = f"collections/{collection_id}/derived/{paper_id}/tei.xml"
        
        blob = self.bucket.blob(object_key)
        blob.upload_from_string(
            tei_data,
            content_type="application/xml"
        )
        
        return object_key
    
    def upload_export(self, collection_id: str, export_data: str, timestamp: str) -> str:
        """Upload graph export data to GCS.
        
        Args:
            collection_id: UUID of the collection
            export_data: JSON export data as string
            timestamp: Timestamp for the export
            
        Returns:
            Object key for the uploaded file
        """
        object_key = f"collections/{collection_id}/exports/{timestamp}/graph.json"
        
        blob = self.bucket.blob(object_key)
        blob.upload_from_string(
            export_data,
            content_type="application/json"
        )
        
        return object_key
    
    def get_signed_url(self, object_key: str, expiration_minutes: int = 60) -> str:
        """Generate a signed URL for temporary access to an object.
        
        Args:
            object_key: GCS object key
            expiration_minutes: URL expiration time in minutes
            
        Returns:
            Signed URL for accessing the object
        """
        blob = self.bucket.blob(object_key)
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration_minutes * 60,  # Convert to seconds
            method="GET"
        )
        
        return url
    
    def download_file(self, object_key: str) -> bytes:
        """Download a file from GCS.
        
        Args:
            object_key: GCS object key
            
        Returns:
            File content as bytes
            
        Raises:
            NotFound: If the object doesn't exist
        """
        blob = self.bucket.blob(object_key)
        
        if not blob.exists():
            raise NotFound(f"Object {object_key} not found")
        
        return blob.download_as_bytes()
    
    def delete_file(self, object_key: str) -> bool:
        """Delete a file from GCS.
        
        Args:
            object_key: GCS object key
            
        Returns:
            True if deleted, False if not found
        """
        blob = self.bucket.blob(object_key)
        
        try:
            blob.delete()
            return True
        except NotFound:
            return False
    
    def list_collection_files(self, collection_id: str, prefix: str = "") -> list[str]:
        """List files in a collection.
        
        Args:
            collection_id: UUID of the collection
            prefix: Optional prefix to filter files
            
        Returns:
            List of object keys
        """
        collection_prefix = f"collections/{collection_id}/"
        if prefix:
            collection_prefix += prefix
        
        blobs = self.client.list_blobs(
            settings.gcs_bucket_name,
            prefix=collection_prefix
        )
        
        return [blob.name for blob in blobs]


# Global GCS client instance
_gcs_client: Optional[GCSClient] = None


def get_gcs_client() -> GCSClient:
    """Get the global GCS client instance."""
    global _gcs_client
    if _gcs_client is None:
        _gcs_client = GCSClient()
    return _gcs_client
