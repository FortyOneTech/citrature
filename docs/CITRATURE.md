# Citrature Platform Documentation

## Overview

Citrature is an AI-powered research paper analysis and citation graph platform that enables researchers to upload, discover, analyze, and visualize research papers. The platform combines PDF processing, semantic search, citation graph building, and AI-powered chat capabilities to provide comprehensive research assistance.

## Architecture

### Technology Stack

**Backend:**
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0 (ASGI)
- **Database**: PostgreSQL 16 with pgvector extension for vector similarity search
- **ORM**: SQLAlchemy 2.0.23
- **Migrations**: Alembic 1.13.1
- **Authentication**: JWT tokens via python-jose (HS256 algorithm)
- **Password Hashing**: bcrypt via passlib

**Message Queue & Task Processing:**
- **Broker**: RabbitMQ 3-management-alpine
- **Backend**: Redis 7-alpine
- **Task Queue**: Celery 5.3.4
- **Serialization**: JSON

**External Services:**
- **PDF Processing**: GROBID 0.8.0 (containerized)
- **Paper Discovery**: Crossref API
- **Embeddings**: OpenRouter API (text-embedding-3-small, 1536 dimensions)
- **LLM**: OpenRouter API (anthropic/claude-3-haiku)
- **Storage**: Google Cloud Storage

**Frontend:**
- **Framework**: React 18.2.0
- **Routing**: React Router DOM 6.8.1
- **HTTP Client**: Axios 1.3.4
- **Visualization**: React Force Graph 2D 1.25.0, Recharts 2.5.0
- **Styling**: Tailwind CSS 3.2.7
- **Markdown**: React Markdown 8.0.5
- **Icons**: Lucide React 0.263.1

**Development Tools:**
- **Build System**: Docker Compose 3.8
- **Python Version**: 3.11+
- **Package Management**: pip (requirements.txt), pyproject.toml
- **Code Formatting**: Black (88 char line length), isort
- **Type Checking**: mypy (Python 3.11)

## Database Schema

### Core Tables

**users**
- `id` (UUID, Primary Key)
- `email` (String(255), Unique, Indexed)
- `name` (String(255))
- `picture_url` (String(500), Nullable)
- `plan` (String(50), Default: "free")
- `created_at` (DateTime)

**collections**
- `id` (UUID, Primary Key)
- `title` (String(255))
- `user_id` (UUID, Foreign Key → users.id, CASCADE DELETE)
- `created_at` (DateTime)
- Index on `user_id`

**papers**
- `id` (UUID, Primary Key)
- `collection_id` (UUID, Foreign Key → collections.id, CASCADE DELETE)
- `doi` (String(255), Indexed, Nullable)
- `title` (Text)
- `abstract` (Text, Nullable)
- `year` (Integer, Nullable)
- `venue` (String(255), Nullable)
- `url` (String(500), Nullable)
- `pdf_url` (String(500), Nullable)
- `source` (String(50)) - 'upload' or 'crossref'
- `added_via` (String(50)) - 'upload', 'topic', or 'graph'
- `raw_json` (JSONB, Nullable)
- `created_at` (DateTime)
- Indexes on `collection_id` and `doi`

**authors**
- `id` (UUID, Primary Key)
- `name` (String(255))
- `email` (String(255), Nullable)
- `affiliation` (String(500), Nullable)
- `orcid` (String(50), Nullable)

**paper_authors**
- `paper_id` (UUID, Foreign Key → papers.id, CASCADE DELETE, Primary Key)
- `author_id` (UUID, Foreign Key → authors.id, CASCADE DELETE, Primary Key)
- `author_order` (Integer)

**citations**
- `src_paper_id` (UUID, Foreign Key → papers.id, CASCADE DELETE, Primary Key)
- `dst_doi` (String(255), Nullable)
- `resolved_paper_id` (UUID, Foreign Key → papers.id, CASCADE DELETE, Nullable)
- `dst_title` (Text, Nullable)
- `dst_year` (Integer, Nullable)
- Unique constraint on (`src_paper_id`, `dst_doi`)
- Indexes on `src_paper_id` and `resolved_paper_id`

**chunks**
- `id` (UUID, Primary Key)
- `paper_id` (UUID, Foreign Key → papers.id, CASCADE DELETE)
- `section` (String(100)) - normalized section label (abstract, introduction, methods, results, discussion, conclusion, references)
- `ord` (Integer) - sequence within section
- `text` (Text)
- Index on (`paper_id`, `ord`)

**chunk_embeddings**
- `chunk_id` (UUID, Foreign Key → chunks.id, CASCADE DELETE, Primary Key)
- `embedding` (Vector(1536)) - pgvector column

**paper_summaries**
- `paper_id` (UUID, Foreign Key → papers.id, CASCADE DELETE, Primary Key)
- `abstract_summary` (Text, Nullable)
- `intro_summary` (Text, Nullable)
- `conclusion_summary` (Text, Nullable)
- `tldr` (Text, Nullable)

**gap_insights**
- `id` (UUID, Primary Key)
- `collection_id` (UUID, Foreign Key → collections.id, CASCADE DELETE)
- `insight` (Text)
- `evidence` (JSONB, Nullable)
- `score` (Numeric(5, 4))
- `created_at` (DateTime)

### Database Extensions

- **pgvector**: PostgreSQL extension for vector similarity search (enabled in migration)

## API Endpoints

### Authentication (`/auth`)

**POST /auth/google**
- Authenticate with Google OAuth
- Request: `{ "id_token": string }`
- Response: `{ "access_token": string, "token_type": "bearer", "expires_in": number }`
- Creates new user if not exists, updates existing user info

**GET /auth/me**
- Get current authenticated user info
- Requires: Bearer token
- Response: User object with id, email, name, picture_url, plan, created_at

**POST /auth/logout**
- Logout user (clears token client-side)
- Requires: Bearer token
- Response: `{ "message": "Successfully logged out" }`

### Collections (`/collections`)

**POST /collections/**
- Create a new collection
- Requires: Bearer token
- Request: `{ "title": string }`
- Response: Collection object with id, title, created_at, paper_count
- Enforces `MAX_COLLECTIONS_PER_USER` limit (default: 1 for free plan)

**GET /collections/**
- List user's collections
- Requires: Bearer token
- Response: Array of Collection objects

**GET /collections/{collection_id}**
- Get specific collection details
- Requires: Bearer token
- Response: Collection object with paper_count

**DELETE /collections/{collection_id}**
- Delete a collection (cascades to papers, chunks, citations)
- Requires: Bearer token
- Response: `{ "message": "Collection deleted successfully" }`

### Ingestion (`/ingest`)

**POST /ingest/pdf/{collection_id}**
- Upload PDF file for ingestion
- Requires: Bearer token, multipart/form-data file upload
- Validates: Content type (application/pdf), file size (max 50MB)
- Uploads to GCS, queues Celery task `ingest_pdf_task`
- Response: `{ "message": string, "task_id": string, "object_key": string }`

**POST /ingest/topic/{collection_id}**
- Ingest papers from topic search via Crossref
- Requires: Bearer token
- Query parameters: `query` (string), `limit` (int, default: 30, max: MAX_TOPIC_PAPERS)
- Queues Celery task `ingest_topic_task`
- Response: `{ "message": string, "task_id": string, "query": string, "limit": number }`

### Graph (`/graph`)

**POST /graph/build/{collection_id}**
- Build citation graph for collection
- Requires: Bearer token
- Query parameters: `mode` (string, default: "bfs"), `depth` (int, default: 3, max: MAX_GRAPH_DEPTH)
- Queues Celery task `build_graph_task`
- Response: `{ "message": string, "task_id": string, "mode": string, "depth": number }`

**GET /graph/{collection_id}**
- Get current graph state
- Requires: Bearer token
- Response: `{ "nodes": Array, "edges": Array, "total_papers": number, "total_citations": number }`

### Chat (`/chat`)

**POST /chat/{collection_id}**
- Chat with research collection using AI
- Requires: Bearer token
- Request: `{ "message": string, "k": number (optional, default: 5) }`
- Uses hybrid search (BM25 + vector similarity) to retrieve relevant chunks
- Generates response via OpenRouter API with context
- Extracts citations from response
- Response: `{ "answer": string, "citations": Array<Citation> }`

### Search (`/search`)

**GET /search/{collection_id}**
- Search within collection
- Requires: Bearer token
- Query parameters: `q` (string), `k` (int, default: 10)
- Simplified text search implementation (case-insensitive substring matching)
- Response: `{ "query": string, "results": Array, "total": number }`

## Configuration

### Environment Variables

**Database**
- `DATABASE_URL`: PostgreSQL connection string (required)
- Format: `postgresql://user:password@host:port/database`

**Message Queue**
- `RABBITMQ_URL`: RabbitMQ connection string (required)
- Format: `amqp://user:password@host:port/`
- Default in docker-compose: `amqp://guest:guest@rabbitmq:5672/`

**Cache**
- `REDIS_URL`: Redis connection string (required)
- Format: `redis://host:port/db`
- Default in docker-compose: `redis://redis:6379/0`

**External APIs**
- `OPENROUTER_API_KEY`: OpenRouter API key (required)
- `OPENROUTER_BASE_URL`: OpenRouter API base URL (default: https://openrouter.ai/api/v1)
- `CROSSREF_MAILTO`: Email for Crossref API (required, for User-Agent header)
- `CROSSREF_BASE_URL`: Crossref API base URL (default: https://api.crossref.org)

**Google OAuth**
- `GOOGLE_CLIENT_ID`: Google OAuth client ID (required)
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret (required)
- `GOOGLE_REDIRECT_URI`: OAuth redirect URI (required)
- Default: `http://localhost:8000/auth/google/callback`

**PDF Processing**
- `GROBID_BASE_URL`: GROBID service URL (default: http://localhost:8070)

**Google Cloud Storage**
- `GCS_BUCKET_NAME`: GCS bucket name (required)
- `GCS_PROJECT_ID`: GCP project ID (required)
- `GCS_CREDENTIAL_PATH`: Path to GCS service account JSON file (required)

**Security**
- `SECRET_KEY`: JWT secret key (required)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

**Usage Limits**
- `MAX_TOPIC_PAPERS`: Maximum papers per topic search (default: 30)
- `MAX_GRAPH_DEPTH`: Maximum citation graph depth (default: 3)
- `MAX_COLLECTIONS_PER_USER`: Maximum collections per user (default: 1 for free plan)
- `MONTHLY_CHAT_QUOTA`: Monthly chat quota (default: 100)
- `MAX_UPLOAD_SIZE_MB`: Maximum PDF upload size in MB (default: 50)

**API Configuration**
- `API_ORIGIN`: API origin URL (default: http://localhost:8000)
- `WEB_ORIGIN`: Web frontend origin URL (default: http://localhost:3000)

**Frontend Environment Variables**
- `REACT_APP_API_URL`: API base URL (default: http://localhost:8000)
- `REACT_APP_GOOGLE_CLIENT_ID`: Google OAuth client ID for frontend (required)

### Configuration Files

**Backend Configuration**
- `citrature/config.py`: Main configuration using Pydantic Settings
- `citrature/config_simple.py`: Simplified configuration for migrations

**Alembic Configuration**
- `alembic.ini`: Alembic migration configuration
- `alembic/env.py`: Alembic environment setup
- `alembic/versions/3b2478be7244_initial_migration_with_pgvector_.py`: Initial migration

**Docker Configuration**
- `docker-compose.yml`: Multi-service Docker Compose setup
- `Dockerfile`: Backend API container (Python 3.11-slim)
- `frontend/Dockerfile`: Frontend React container

**Makefile**
- `make env`: Copy .env.example to .env
- `make dev`: Start development environment
- `make dev-down`: Stop development environment
- `make dev-destroy`: Destroy environment and volumes
- `make frontend`: Start only frontend service
- `make logs`: Show live logs
- `make status`: Show service status
- `make clean`: Clean up containers and volumes

## Services

### GROBID Service (`citrature/services/grobid.py`)

**GROBIDService**
- Processes PDFs with GROBID API
- Extracts TEI XML with structured metadata
- Fallback to PyMuPDF for basic text extraction
- Supports section detection, citation extraction, author parsing
- Methods:
  - `process_pdf(pdf_data: bytes) -> Dict`: Main processing with GROBID
  - `process_pdf_fallback(pdf_data: bytes) -> Dict`: Fallback with PyMuPDF
  - `_parse_tei_xml(tei_xml: str) -> Dict`: Parse TEI XML to structured data
  - `_detect_sections(text: str) -> List[Dict]`: Heuristic section detection
  - `_normalize_section_name(line: str) -> str`: Normalize section names

### Crossref Service (`citrature/services/crossref.py`)

**CrossrefService**
- Interfaces with Crossref API for paper discovery
- Supports work search and DOI lookup
- Normalizes and processes Crossref metadata
- Methods:
  - `search_works(query: str, limit: int) -> List[Dict]`: Search for papers
  - `get_work_by_doi(doi: str) -> Optional[Dict]`: Get paper by DOI
  - `_process_work(work: Dict) -> Optional[Dict]`: Process and normalize work data
  - `_extract_title/authors/year/venue/abstract/url(work: Dict)`: Extract metadata
  - `_normalize_doi(doi: str) -> str`: Normalize DOI strings

### Embedding Service (`citrature/services/embeddings.py`)

**EmbeddingService**
- Generates vector embeddings using OpenRouter API
- Model: text-embedding-3-small (1536 dimensions)
- Supports single and batch embedding generation
- Truncates text to 8000 characters if needed
- Methods:
  - `generate_embedding(text: str) -> List[float]`: Generate single embedding
  - `generate_embeddings_batch(texts: List[str]) -> List[List[float]]`: Batch generation

### OpenRouter Service (`citrature/services/openrouter.py`)

**OpenRouterService**
- Interfaces with OpenRouter API for LLM interactions
- Model: anthropic/claude-3-haiku (fast, cost-effective)
- Supports text generation, chat responses, citation extraction
- Methods:
  - `generate_text(prompt: str, max_tokens: int) -> str`: Generate text
  - `generate_chat_response(messages: List[Dict], context: str) -> str`: Chat with context
  - `extract_citations(text: str, papers: List[Dict]) -> List[Dict]`: Extract citations

### Storage Service (`citrature/storage.py`)

**GCSClient**
- Google Cloud Storage client for file operations
- Supports PDF uploads, TEI XML storage, graph exports
- Generates signed URLs for temporary access
- Methods:
  - `upload_pdf(collection_id: str, file_data: BinaryIO, content_type: str) -> str`: Upload PDF
  - `upload_tei(collection_id: str, paper_id: str, tei_data: str) -> str`: Upload TEI XML
  - `upload_export(collection_id: str, export_data: str, timestamp: str) -> str`: Upload export
  - `get_signed_url(object_key: str, expiration_minutes: int) -> str`: Generate signed URL
  - `download_file(object_key: str) -> bytes`: Download file
  - `delete_file(object_key: str) -> bool`: Delete file
  - `list_collection_files(collection_id: str, prefix: str) -> List[str]`: List files

## Celery Tasks

### Task Configuration (`citrature/celery_app.py`)

**Celery App**
- Broker: RabbitMQ
- Backend: Redis
- Serialization: JSON
- Timezone: UTC
- Task time limits: 1 hour hard limit, 50 minutes soft limit
- Task queues: default (all tasks)
- Rate limits configured per task type

**Task Modules**
- `citrature.tasks.ingest`: PDF and topic ingestion
- `citrature.tasks.graph`: Citation graph building
- `citrature.tasks.analysis`: Gap analysis and summarization

### Ingest Tasks (`citrature/tasks/ingest.py`)

**ingest_pdf_task**
- Processes PDF uploads
- Rate limit: 10/minute
- Time limit: 30 minutes (hard), 25 minutes (soft)
- Steps:
  1. Download PDF from GCS
  2. Process with GROBID (fallback to PyMuPDF)
  3. Store TEI XML in GCS
  4. Extract metadata and create Paper record
  5. Process authors and create Author records
  6. Process citations (stored for later graph building)
  7. Create chunks from sections
  8. Generate embeddings for chunks
  9. Store chunk embeddings
- Returns: `{ "status": "success", "paper_id": string, "title": string, "chunks_created": number, "authors_created": number, "citations_found": number }`

**ingest_topic_task**
- Ingests papers from Crossref topic search
- Rate limit: 5/minute
- Time limit: 10 minutes (hard), 8 minutes (soft)
- Steps:
  1. Search Crossref API
  2. For each work:
     - Check if paper exists (by DOI or title+year)
     - Create or update Paper record
     - Create abstract chunk if available
     - Generate embedding for abstract
  3. Commit batch
- Returns: `{ "status": "success", "papers_created": number, "papers_updated": number, "chunks_created": number, "total_found": number }`

### Graph Tasks (`citrature/tasks/graph.py`)

**build_graph_task**
- Builds citation graph for collection
- Rate limit: 2/minute
- Time limit: 1 hour (hard), 50 minutes (soft)
- Traversal modes: BFS (breadth-first) or DFS (depth-first)
- Depth limit: MAX_GRAPH_DEPTH (default: 3)
- Steps:
  1. Get all papers in collection
  2. Initialize CitationGraphBuilder
  3. Traverse citations (BFS or DFS)
  4. For each citation:
     - Try to resolve by DOI via Crossref
     - Fallback to resolution by title+year
     - Create Paper record if not exists
     - Create abstract chunk and embedding if available
     - Link citation to resolved paper
  5. Commit graph
- Returns: `{ "status": "success", "nodes_processed": number, "edges_created": number, "papers_added": number, "depth_reached": number }`

**CitationGraphBuilder**
- Helper class for graph building
- Tracks visited papers and DOIs
- Methods:
  - `build_bfs(seed_papers: List[Paper], max_depth: int) -> Dict`: Breadth-first traversal
  - `build_dfs(seed_papers: List[Paper], max_depth: int) -> Dict`: Depth-first traversal
  - `_process_citations(paper: Paper, depth: int) -> Tuple[int, List[Paper]]`: Process citations
  - `_resolve_by_doi(doi: str, collection_id: str) -> Optional[Paper]`: Resolve by DOI
  - `_resolve_by_title_year(title: str, year: int, collection_id: str) -> Optional[Paper]`: Resolve by title+year
  - `_create_abstract_chunk(paper: Paper, abstract: str)`: Create chunk and embedding

### Analysis Tasks (`citrature/tasks/analysis.py`)

**gap_analysis_task**
- Performs gap analysis on collection
- Rate limit: 1/minute
- Time limit: 30 minutes (hard), 25 minutes (soft)
- Steps:
  1. Get all papers in collection
  2. Extract texts (abstracts or titles)
  3. Generate embeddings
  4. Perform K-means clustering
  5. Calculate metrics (coverage, novelty, trajectory growth, method diversity)
  6. Generate insights using LLM
  7. Save GapInsight records
- Returns: `{ "status": "success", "insights_created": number, "papers_analyzed": number }`

**GapAnalyzer**
- Analyzes collections for research gaps
- Methods:
  - `analyze_collection(collection: Collection, papers: List[Paper]) -> List[Dict]`: Main analysis
  - `_cluster_papers(embeddings: List[List[float]], texts: List[str], paper_ids: List[str]) -> List[Dict]`: K-means clustering
  - `_calculate_metrics(papers: List[Paper], clusters: List[Dict]) -> Dict`: Calculate metrics
  - `_generate_insights(metrics: Dict, clusters: List[Dict], papers: List[Paper]) -> List[Dict]`: Generate insights

**summarize_paper_task**
- Generates summaries for a paper
- Steps:
  1. Get paper and chunks
  2. Group chunks by section
  3. Generate summaries for abstract, introduction, conclusion
  4. Generate TL;DR
  5. Save PaperSummary record
- Returns: `{ "status": "success", "summaries_generated": number }`

**PaperSummarizer**
- Generates paper summaries
- Methods:
  - `generate_summaries(sections: Dict[str, List[str]]) -> Dict[str, str]`: Generate all summaries
  - `_summarize_text(text: str, section_type: str) -> str`: Summarize section
  - `_generate_tldr(text: str) -> str`: Generate TL;DR

## Frontend Architecture

### React Application (`frontend/src/App.js`)

**Main App Component**
- Routes:
  - `/`: Landing page
  - `/login`: Login page
  - `/dashboard`: Dashboard (protected)
  - `/collection/:id`: Collection view (protected)
- Authentication state management
- Token storage in localStorage
- Axios configuration with base URL and Authorization header

### Components

**Landing** (`frontend/src/components/Landing.js`)
- Public landing page

**Login** (`frontend/src/components/Login.js`)
- Google OAuth sign-in integration
- Uses Google Identity Services
- Stores token in localStorage

**Dashboard** (`frontend/src/components/Dashboard.js`)
- Displays user collections
- Create new collection
- Navigate to collection view
- User profile display

**CollectionView** (`frontend/src/components/CollectionView.js`)
- Main collection interface
- PDF upload
- Topic search
- Graph visualization
- Chat interface
- Gap analysis view

**FileUpload** (`frontend/src/components/FileUpload.js`)
- PDF file upload with drag-and-drop
- Uses react-dropzone
- Validates file type and size

**TopicSearch** (`frontend/src/components/TopicSearch.js`)
- Search Crossref for papers
- Display results
- Add papers to collection

**GraphView** (`frontend/src/components/GraphView.js`)
- Citation graph visualization
- Uses react-force-graph-2d
- Interactive node/edge display
- Graph building controls

**ChatInterface** (`frontend/src/components/ChatInterface.js`)
- Chat with collection
- Message history
- Citation display
- Markdown rendering

**GapAnalysis** (`frontend/src/components/GapAnalysis.js`)
- Display gap insights
- Evidence visualization
- Metrics display

### Frontend Dependencies

**Core**
- react: 18.2.0
- react-dom: 18.2.0
- react-router-dom: 6.8.1
- react-scripts: 5.0.1

**HTTP & Data**
- axios: 1.3.4

**Visualization**
- recharts: 2.5.0
- react-force-graph-2d: 1.25.0

**UI Components**
- react-dropzone: 14.2.3
- react-markdown: 8.0.5
- lucide-react: 0.263.1
- clsx: 1.2.1

**Styling**
- tailwindcss: 3.2.7
- autoprefixer: 10.4.14
- postcss: 8.4.21

**Authentication**
- google-auth-library: 9.0.0
- @google-cloud/local-auth: 2.1.0

## Docker Compose Setup

### Services

**db** (PostgreSQL with pgvector)
- Image: `pgvector/pgvector:pg16`
- Port: 5432
- Database: citrature
- User: citrature
- Password: password
- Volume: postgres_data
- Health check: pg_isready

**redis** (Cache)
- Image: `redis:7-alpine`
- Port: 6379
- Volume: redis_data
- Health check: redis-cli ping

**rabbitmq** (Message Broker)
- Image: `rabbitmq:3-management-alpine`
- Ports: 5672 (AMQP), 15672 (Management UI)
- User: guest
- Password: guest
- Volume: rabbitmq_data
- Health check: rabbitmq-diagnostics ping

**grobid** (PDF Processing)
- Image: `lfoppiano/grobid:0.8.0`
- Platform: linux/amd64
- Port: 8070
- Java options: -Xmx2g
- Volume: grobid_data
- Health check: curl http://localhost:8070/api/isalive
- Start period: 300s (5 minutes for startup)

**api** (FastAPI Backend)
- Build: Dockerfile
- Port: 8000
- Command: Run migrations then uvicorn with reload
- Environment: All backend environment variables
- Volumes: Code mount, credentials.json (read-only), bm25_index
- Depends on: db, redis, rabbitmq (health checks)
- Health check: curl http://localhost:8000/health

**worker** (Celery Worker)
- Build: Dockerfile
- Command: celery worker
- Environment: Same as API
- Volumes: Code mount, credentials.json (read-only), bm25_index
- Depends on: db, redis, rabbitmq (health checks)

**beat** (Celery Beat)
- Build: Dockerfile
- Command: celery beat
- Environment: Same as API (without GROBID)
- Volumes: Code mount
- Depends on: db, redis, rabbitmq (health checks)

**frontend** (React Frontend)
- Build: frontend/Dockerfile
- Port: 3000
- Environment: REACT_APP_API_URL, REACT_APP_GOOGLE_CLIENT_ID
- Volumes: Code mount, node_modules exclusion
- Depends on: api (health check)

### Volumes

- `postgres_data`: PostgreSQL data persistence
- `redis_data`: Redis data persistence
- `rabbitmq_data`: RabbitMQ data persistence
- `grobid_data`: GROBID data persistence
- `bm25_index`: BM25 search index persistence

## Database Migrations

### Initial Migration (`3b2478be7244`)

**Upgrade Operations:**
1. Enable pgvector extension
2. Create users table
3. Create collections table
4. Create authors table
5. Create papers table
6. Create paper_authors junction table
7. Create citations table
8. Create chunks table
9. Create chunk_embeddings table (with Vector column)
10. Create paper_summaries table
11. Create gap_insights table

**Indexes Created:**
- `ix_users_email` on users.email
- `ix_collections_user_id` on collections.user_id
- `ix_papers_collection_id` on papers.collection_id
- `ix_papers_doi` on papers.doi
- `ix_citations_src_paper_id` on citations.src_paper_id
- `ix_citations_resolved_paper_id` on citations.resolved_paper_id
- `ix_chunks_paper_id_ord` on chunks(paper_id, ord)

**Unique Constraints:**
- `uq_citations_src_dst` on citations(src_paper_id, dst_doi)

**Downgrade Operations:**
- Drop all tables in reverse order
- Drop pgvector extension

## API Schemas

### Authentication Schemas (`citrature/schemas/auth.py`)

**UserCreate**
- `email`: EmailStr
- `name`: string
- `picture_url`: string (optional)

**UserResponse**
- `id`: string (UUID)
- `email`: string
- `name`: string
- `picture_url`: string (optional)
- `plan`: string
- `created_at`: datetime

**Token**
- `access_token`: string
- `token_type`: string (default: "bearer")
- `expires_in`: number (seconds)

**GoogleAuthRequest**
- `id_token`: string

### Collection Schemas (`citrature/schemas/collections.py`)

**CollectionCreate**
- `title`: string

**CollectionResponse**
- `id`: string (UUID)
- `title`: string
- `created_at`: datetime
- `paper_count`: number

**CollectionListResponse**
- Same as CollectionResponse

### Chat Schemas (`citrature/schemas/chat.py`)

**ChatRequest**
- `message`: string
- `k`: number (optional, default: 5)

**Citation**
- `paper_id`: string (UUID)
- `chunk_id`: string (UUID, optional)
- `title`: string
- `year`: number (optional)
- `venue`: string (optional)

**ChatResponse**
- `answer`: string
- `citations`: Array<Citation>

## Security

### Authentication Flow

1. User clicks Google Sign-In button
2. Frontend receives Google ID token
3. Frontend sends ID token to `/auth/google`
4. Backend verifies ID token with Google
5. Backend creates/updates User record
6. Backend generates JWT access token
7. Frontend stores token in localStorage
8. Frontend includes token in Authorization header for subsequent requests

### JWT Token Details

- Algorithm: HS256
- Secret: SECRET_KEY environment variable
- Expiration: ACCESS_TOKEN_EXPIRE_MINUTES (default: 30 minutes)
- Payload: `{ "sub": user_id, "exp": expiration_timestamp }`

### Authorization

- All protected endpoints require Bearer token in Authorization header
- `get_current_user` dependency verifies token and loads user
- User can only access their own collections and data

### CORS Configuration

- Allowed origins: WEB_ORIGIN (default: http://localhost:3000)
- Credentials: enabled
- Methods: all (*)
- Headers: all (*)

### Trusted Hosts

- Middleware validates host header
- Allowed hosts: localhost, 127.0.0.1, API_ORIGIN hostname

## File Storage

### Google Cloud Storage Structure

**PDF Uploads**
- Path: `collections/{collection_id}/uploads/{file_id}.pdf`
- Content type: application/pdf

**TEI XML**
- Path: `collections/{collection_id}/derived/{paper_id}/tei.xml`
- Content type: application/xml

**Graph Exports**
- Path: `collections/{collection_id}/exports/{timestamp}/graph.json`
- Content type: application/json

### GCS Credentials

- Service account JSON file required
- Path specified in `GCS_CREDENTIAL_PATH`
- Permissions needed: Storage Object Creator, Storage Object Viewer

## Usage Limits

### Free Plan Limits

- **Collections**: 1 collection per user (MAX_COLLECTIONS_PER_USER: 1)
- **Topic Papers**: 30 papers per topic search (MAX_TOPIC_PAPERS: 30)
- **Graph Depth**: Maximum depth 3 (MAX_GRAPH_DEPTH: 3)
- **Monthly Chat**: 100 chats per month (MONTHLY_CHAT_QUOTA: 100)
- **Upload Size**: 50MB per PDF (MAX_UPLOAD_SIZE_MB: 50)

### Supported Formats

- PDF only for uploads
- Content type validation: application/pdf

## Deployment

### Development Setup

1. **Clone repository**
2. **Create .env files**
   - Copy `.env.example` to `.env`
   - Copy `frontend/.env.example` to `frontend/.env`
   - Fill in all required values
3. **Set up Google OAuth**
   - Create OAuth client in Google Cloud Console
   - Configure authorized origins and redirect URIs
   - Add credentials to .env files
4. **Set up GCS**
   - Create GCS bucket
   - Create service account
   - Download credentials JSON
   - Place as `credentials.json` in project root
5. **Start services**
   - `docker-compose up -d`
6. **Run migrations**
   - `docker-compose exec api alembic upgrade head`
7. **Access application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - RabbitMQ Management: http://localhost:15672 (guest/guest)

### Production Considerations

1. **Environment Variables**: Use secure secret management (AWS Secrets Manager, HashiCorp Vault, etc.)
2. **Database**: Use managed PostgreSQL with pgvector (AWS RDS, Google Cloud SQL, etc.)
3. **Storage**: Configure GCS bucket with proper IAM and lifecycle policies
4. **Monitoring**: Add logging (structlog), metrics (Prometheus), and tracing
5. **Scaling**: Use multiple Celery workers, horizontal scaling for API
6. **Security**: Enable HTTPS, proper CORS origins, rate limiting, API key rotation
7. **Backup**: Regular database backups, GCS bucket versioning

## Known Issues & Limitations

### Search Implementation

- Current search endpoint uses simplified text matching
- BM25 + vector hybrid search not fully implemented
- Whoosh library included but not actively used

### Citation Resolution

- Citation extraction depends on GROBID quality
- Resolution by title+year may have false positives
- No duplicate detection for similar papers

### Frontend Components

- Some components may have incomplete implementations
- Graph visualization may need performance optimization for large graphs
- Chat interface may need streaming support for better UX

### Error Handling

- Some error messages may not be user-friendly
- Task failure recovery could be improved
- Retry logic for external API calls could be enhanced

### Performance

- Embedding generation is synchronous per chunk
- Could benefit from batch processing optimizations
- Graph building may be slow for large collections

## Development Workflow

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Local Development

1. Start infrastructure: `docker-compose up -d db redis rabbitmq grobid`
2. Run migrations: `alembic upgrade head`
3. Start API: `uvicorn citrature.main:app --reload`
4. Start Celery worker: `celery -A citrature.celery_app worker --loglevel=info`
5. Start frontend: `cd frontend && npm start`

### Testing

- No test suite currently configured
- Manual testing via API docs and frontend
- Integration testing needed for production readiness

## Project Structure

```
citrature/
├── alembic/                    # Database migrations
│   ├── env.py                  # Alembic environment
│   └── versions/               # Migration files
├── citrature/                  # Main application
│   ├── api/                    # API endpoints
│   │   ├── auth.py            # Authentication routes
│   │   ├── collections.py     # Collection routes
│   │   ├── ingest.py          # Ingestion routes
│   │   ├── graph.py           # Graph routes
│   │   ├── chat.py             # Chat routes
│   │   └── search.py           # Search routes
│   ├── services/               # External service integrations
│   │   ├── grobid.py          # GROBID service
│   │   ├── crossref.py        # Crossref service
│   │   ├── embeddings.py      # Embedding service
│   │   └── openrouter.py      # OpenRouter service
│   ├── tasks/                  # Celery tasks
│   │   ├── ingest.py          # Ingestion tasks
│   │   ├── graph.py           # Graph building tasks
│   │   └── analysis.py        # Analysis tasks
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py            # Auth schemas
│   │   ├── collections.py     # Collection schemas
│   │   └── chat.py             # Chat schemas
│   ├── database.py             # Database connection
│   ├── models.py               # SQLAlchemy models
│   ├── config.py               # Configuration (Pydantic)
│   ├── config_simple.py        # Simple configuration (migrations)
│   ├── celery_app.py           # Celery app configuration
│   ├── storage.py              # GCS storage client
│   └── main.py                 # FastAPI application
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── App.js              # Main app component
│   │   └── index.js            # Entry point
│   ├── public/                 # Static files
│   └── package.json            # Dependencies
├── alembic.ini                  # Alembic configuration
├── Dockerfile                   # Backend container
├── docker-compose.yml           # Docker Compose setup
├── Makefile                     # Development commands
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Python project config
├── .env.example                 # Environment variables template
├── GOOGLE_OAUTH_SETUP.md       # OAuth setup guide
└── README.md                    # Project README
```

## License

MIT License

