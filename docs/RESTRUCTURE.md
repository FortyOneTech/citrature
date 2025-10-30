# Citrature Platform - Microservice Restructure

## ✅ Completed Restructuring

The project has been successfully reorganized into a clean microservice architecture with separate services, each having its own Dockerfile and requirements.

## New Structure

```
citrature/
├── frontend/                      # React Frontend Service
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   └── src/
│       └── components/
│
├── services/                      # Backend Microservices
│   ├── api/                      # FastAPI REST API
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── chat.py
│   │       ├── collections.py
│   │       ├── graph.py
│   │       ├── ingest.py
│   │       └── search.py
│   │
│   ├── worker/                   # Celery Worker
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── worker.py
│   │   └── tasks/
│   │       ├── analysis.py
│   │       ├── graph.py
│   │       └── ingest.py
│   │
│   └── beat/                     # Celery Beat Scheduler
│       ├── Dockerfile
│       ├── requirements.txt
│       └── beat.py
│
├── shared/                        # Shared Code & Utilities
│   ├── config.py                 # Centralized configuration
│   ├── config_simple.py          # Simple config for migrations
│   ├── database.py               # Database connection
│   ├── models.py                 # SQLAlchemy ORM models
│   ├── storage.py                # GCS storage utilities
│   ├── schemas/                  # Pydantic schemas (no __init__.py)
│   │   ├── auth.py
│   │   ├── chat.py
│   │   └── collections.py
│   ├── clients/                  # External service clients (no __init__.py)
│   │   ├── crossref.py
│   │   ├── embeddings.py
│   │   ├── grobid.py
│   │   └── openrouter.py
│   └── alembic/                  # Database migrations
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
│
├── scripts/
│   └── verify_startup.sh         # Startup verification script
│
├── .env.example
├── docker-compose.yml            # Orchestrates all 7 services
├── Makefile
└── README.md
```

## Key Changes

### 1. **Separate Dockerfiles per Service**

Each microservice now has its own optimized Dockerfile:

- **services/api/Dockerfile** - FastAPI service
- **services/worker/Dockerfile** - Celery worker
- **services/beat/Dockerfile** - Celery Beat scheduler  
- **frontend/Dockerfile** - React application

### 2. **Service-Specific Requirements**

Each service has its own `requirements.txt` with only the dependencies it needs:

- **API**: FastAPI, SQLAlchemy, authentication libs
- **Worker**: Celery, PDF processing, ML libs, embedding clients
- **Beat**: Celery, minimal dependencies for scheduling

### 3. **Shared Code Directory**

All shared utilities centralized in `shared/`:

- Database models and schemas
- Configuration management
- External service clients
- Alembic migrations

### 4. **No Unnecessary __init__.py Files**

Removed Python package markers from:
- `shared/clients/` - External service clients
- `shared/schemas/` - Pydantic schemas
- `services/api/routes/` - API routes
- `services/worker/tasks/` - Celery tasks

### 5. **Minimal Documentation**

Removed excessive markdown files, keeping only:
- `README.md` - Main project documentation
- `RESTRUCTURE.md` - This file
- `.env.example` - Configuration template

## Docker Compose Updates

The `docker-compose.yml` now uses service-specific build contexts:

```yaml
api:
  build:
    context: .
    dockerfile: services/api/Dockerfile

worker:
  build:
    context: .
    dockerfile: services/worker/Dockerfile

beat:
  build:
    context: .
    dockerfile: services/beat/Dockerfile

frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
```

## Import Path Changes

### Old Imports
```python
from citrature.config import get_settings
from citrature.database import Base
from citrature.models import User
from citrature.api import auth
```

### New Imports
```python
from shared.config import get_settings
from shared.database import Base
from shared.models import User
from services.api.routes import auth
```

## Benefits

1. **Clear Separation of Concerns** - Each service is self-contained
2. **Optimized Builds** - Only install needed dependencies per service
3. **Better Scalability** - Can deploy/scale services independently
4. **Easier Maintenance** - Changes isolated to specific services
5. **Faster Builds** - Docker cache optimization per service
6. **Cleaner Structure** - No nested package hierarchies

## Quick Start

```bash
# Initialize environment
make env

# Start all services
make dev

# Verify everything works
make verify
```

All services communicate via the shared `citrature-network` Docker network and share the `shared/` codebase through volume mounts in development.

## Production Deployment

For production:
1. Each service can be built and deployed independently
2. Shared code is copied into each service's Docker image
3. No volume mounts needed - all code baked into images
4. Can scale each service based on load

The restructuring is complete and maintains full compatibility with Step 1 implementation requirements!

