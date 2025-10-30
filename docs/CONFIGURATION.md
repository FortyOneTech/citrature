# Citrature Platform - Configuration Guide

## Overview

This document provides comprehensive guidance on configuring the Citrature platform according to the **Microservice and Environment Configuration** specification from the Implementation Plan.

## Architecture

The Citrature platform consists of seven microservices orchestrated via Docker Compose:

### Foundational Services
1. **PostgreSQL (db)** - Database with pgvector extension
2. **RabbitMQ (rabbitmq)** - Message broker for task queuing
3. **Redis (redis)** - Result backend and caching
4. **GROBID (grobid)** - PDF processing service

### Application Services
5. **API (api)** - FastAPI application serving REST endpoints
6. **Worker (worker)** - Celery worker for background tasks
7. **Beat (beat)** - Celery beat scheduler for periodic tasks
8. **Frontend (frontend)** - React application

## Centralized Configuration System

The platform implements a **centralized configuration contract** where all environment variables are:
- Loaded at application startup
- Validated for presence and correctness
- Stored as immutable settings objects
- Logged on successful initialization (without exposing sensitive values)

This approach prevents runtime errors and ensures environmental consistency across the distributed system.

## Environment Variables Reference

### Core Configuration

| Variable | Description | Required | Default | Consumed By |
|----------|-------------|----------|---------|-------------|
| `API_ORIGIN` | Public-facing URL of the API service | Yes | - | api |
| `WEB_ORIGIN` | Public-facing URL of the React frontend | Yes | - | api |

### Database Configuration

| Variable | Description | Required | Default | Consumed By |
|----------|-------------|----------|---------|-------------|
| `POSTGRES_DSN` | PostgreSQL connection string | Yes | - | api, worker |
| `PGVECTOR_DIMENSION` | Vector dimensionality for embeddings | No | 768 | api, worker |

### Message Queue Configuration

| Variable | Description | Required | Default | Consumed By |
|----------|-------------|----------|---------|-------------|
| `RABBITMQ_URL` | RabbitMQ connection URL | Yes | - | api, worker |
| `REDIS_URL` | Redis connection URL | Yes | - | worker |

### External APIs - OpenRouter

| Variable | Description | Required | Default | Consumed By |
|----------|-------------|----------|---------|-------------|
| `OPENROUTER_BASE_URL` | OpenRouter API base URL | No | https://openrouter.ai/api/v1 | worker |
| `OPENROUTER_API_KEY` | OpenRouter API authentication key | Yes | - | worker |

### External APIs - Crossref

| Variable | Description | Required | Default | Consumed By |
|----------|-------------|----------|---------|-------------|
| `CROSSREF_BASE_URL` | Crossref API base URL | No | https://api.crossref.org | worker |
| `CROSSREF_MAILTO` | Email for Crossref "polite" pool | Yes | - | worker |

### Google OAuth Configuration

| Variable | Description | Required | Default | Consumed By |
|----------|-------------|----------|---------|-------------|
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 Client ID | Yes | - | api, frontend |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 Client Secret | Yes | - | api |
| `GOOGLE_REDIRECT_URI` | OAuth callback URI | Yes | - | api |

### GROBID Configuration

| Variable | Description | Required | Default | Consumed By |
|----------|-------------|----------|---------|-------------|
| `GROBID_BASE_URL` | GROBID service URL | No | http://grobid:8070 | worker |

### Google Cloud Storage Configuration

| Variable | Description | Required | Default | Consumed By |
|----------|-------------|----------|---------|-------------|
| `GCS_BUCKET_NAME` | GCS bucket name for file storage | Yes | - | api, worker |
| `GCS_PROJECT_ID` | Google Cloud project ID | Yes | - | api, worker |
| `GCS_CREDENTIALS_JSON` | GCS service account credentials | Yes | - | api, worker |

### Usage Limits and Quotas

| Variable | Description | Required | Default | Consumed By |
|----------|-------------|----------|---------|-------------|
| `MAX_TOPIC_PAPERS` | Max papers per topic ingestion | No | 30 | api, worker |
| `MAX_GRAPH_DEPTH` | Max citation graph traversal depth | No | 3 | api, worker |
| `MAX_COLLECTIONS_PER_USER` | Max collections per free-tier user | No | 1 | api |
| `MONTHLY_CHAT_QUOTA` | Max chat messages per user/month | No | 100 | api |
| `MAX_UPLOAD_SIZE_MB` | Max PDF upload size in MB | No | 50 | api |

### Security Configuration

| Variable | Description | Required | Default | Consumed By |
|----------|-------------|----------|---------|-------------|
| `SECRET_KEY` | JWT signing secret (min 32 chars) | Yes | - | api |
| `ALGORITHM` | JWT algorithm | No | HS256 | api |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiration time | No | 30 | api |

## Setup Instructions

### 1. Copy Environment File

```bash
cp .env.example .env
```

### 2. Configure Required Variables

Edit `.env` and set all required variables (marked with `...` in `.env.example`):

```bash
# Essential configuration
POSTGRES_DSN=postgresql://citrature:password@db:5432/citrature
API_ORIGIN=http://localhost:8000
WEB_ORIGIN=http://localhost:3000

# External API keys
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
CROSSREF_MAILTO=your-email@example.com

# Google OAuth (from Google Cloud Console)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret

# Google Cloud Storage
GCS_BUCKET_NAME=your-bucket-name
GCS_PROJECT_ID=your-project-id
GCS_CREDENTIALS_JSON='{"type":"service_account",...}'

# Security
SECRET_KEY=generate-a-secure-random-key-with-at-least-32-characters
```

### 3. Configure Frontend

```bash
cp frontend/.env.example frontend/.env
```

Edit `frontend/.env`:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

### 4. Start Services

```bash
docker-compose up --build
```

### 5. Verify Startup

Run the verification script:

```bash
chmod +x scripts/verify_startup.sh
./scripts/verify_startup.sh
```

## Docker Compose Architecture

### Shared Network

All services communicate via the `citrature-network` bridge network, enabling service discovery by container name.

### Startup Order

Services start in strict order enforced by health checks:

1. **Foundational services** (db, redis, rabbitmq, grobid) start and reach healthy state
2. **Application services** (api, worker, beat) start after dependencies are healthy
3. **Frontend** starts after API is healthy

### Persistent Volumes

| Volume | Purpose | Shared By |
|--------|---------|-----------|
| `citrature-pgdata` | PostgreSQL data persistence | db |
| `citrature-bm25-indices` | BM25 search indices | api, worker |
| `citrature-redis-data` | Redis persistence | redis |
| `citrature-rabbitmq-data` | RabbitMQ persistence | rabbitmq |
| `citrature-grobid-data` | GROBID model cache | grobid |

## Configuration Validation

### Startup Logs

The API and Worker services log configuration status on startup:

```
🔧 Initializing Citrature configuration...
✅ API Origin: http://localhost:8000
✅ Web Origin: http://localhost:3000
✅ Database configured: postgresql://citrature@***
✅ PGVector Dimension: 768
✅ RabbitMQ configured: amqp://guest@***
✅ Redis configured: redis://***/
✅ OpenRouter Base URL: https://openrouter.ai/api/v1
✅ Crossref Base URL: https://api.crossref.org
✅ Crossref Mailto: hello@citrature.com
✅ GROBID Base URL: http://grobid:8070
✅ GCS Bucket: citrature-uploads
✅ GCS Project ID: citrature-prod
✅ Google OAuth Client ID configured: xxxxxxxx...
✅ Usage Limits - Topic Papers: 30
✅ Usage Limits - Graph Depth: 3
✅ Usage Limits - Collections Per User: 1
✅ Usage Limits - Monthly Chat Quota: 100
✅ All required environment variables loaded successfully
```

### Verification Tests

The verification script (`scripts/verify_startup.sh`) confirms:

1. ✅ All seven services are running
2. ✅ All health checks pass
3. ✅ Inter-service connectivity works (api → db, rabbitmq, redis, grobid)
4. ✅ Environment variables loaded successfully
5. ✅ Persistent volumes exist
6. ✅ Shared network configured correctly

## Troubleshooting

### Service Not Starting

```bash
# View service logs
docker-compose logs <service-name>

# Restart a specific service
docker-compose restart <service-name>
```

### Missing Environment Variable

If you see `ValidationError` on startup, check that all required variables are set in `.env`:

```bash
grep -E "^(API_ORIGIN|POSTGRES_DSN|GOOGLE_CLIENT_ID)" .env
```

### Database Connection Issues

```bash
# Verify database is accessible
docker exec citrature-api ping -c 1 db
docker exec citrature-db pg_isready -U citrature -d citrature
```

### GROBID Startup Time

GROBID can take 5-10 minutes on first startup to download models. This is normal.

```bash
# Monitor GROBID logs
docker-compose logs -f grobid
```

## Production Deployment

For production deployments:

1. **Use managed services**: Managed PostgreSQL, Redis, and RabbitMQ
2. **Secure secrets**: Use secret management (AWS Secrets Manager, GCP Secret Manager)
3. **Update URLs**: Set `API_ORIGIN` and `WEB_ORIGIN` to production domains
4. **Enable SSL**: Configure HTTPS for all services
5. **Scale workers**: Run multiple worker containers with `--concurrency` flag
6. **Monitor logs**: Centralize logs with ELK, Datadog, or similar

## Reference

This configuration implements **Step 1: Microservice and Environment Configuration** from the Citrature Implementation Plan, establishing a robust, centralized configuration system that prevents runtime errors and ensures consistency across the distributed system.

