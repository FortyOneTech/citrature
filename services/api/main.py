"""FastAPI application for Citrature platform."""

import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from shared.config import initialize_settings
from services.api.routes import auth, collections, ingest, graph, chat, search
from shared.database import engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize and validate settings at startup
settings = initialize_settings()

# Create FastAPI app
app = FastAPI(
    title="Citrature API",
    description="AI-powered research paper analysis and citation graph platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", settings.api_origin.replace("http://", "").replace("https://", "")]
)

# Database tables are created by Alembic migrations
# Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(collections.router, prefix="/collections", tags=["collections"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingestion"])
app.include_router(graph.router, prefix="/graph", tags=["graph"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(search.router, prefix="/search", tags=["search"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Citrature API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "citrature.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
