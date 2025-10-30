# Citrature Platform

AI-powered research paper analysis and citation graph platform.

## Architecture

### Microservices

- **frontend/** - React web application
- **services/api/** - FastAPI REST API service
- **services/worker/** - Celery worker for background tasks
- **services/beat/** - Celery Beat scheduler for periodic tasks
- **shared/** - Shared code (models, schemas, clients, config, database)

### Infrastructure Services

- **PostgreSQL** - Database with pgvector extension
- **Redis** - Result backend and caching
- **RabbitMQ** - Message broker for task queuing
- **GROBID** - PDF processing service

## Quick Start

### 1. Initialize Environment

```bash
make env
```

Edit `.env` with your actual credentials:
- `OPENROUTER_API_KEY`
- `CROSSREF_MAILTO`
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- `GCS_BUCKET_NAME` and `GCS_PROJECT_ID`
- `GCS_CREDENTIALS_JSON`
- `SECRET_KEY`

### 2. Start Platform

```bash
make dev
```

### 3. Verify

```bash
make verify
```

### 4. Access

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- RabbitMQ UI: http://localhost:15672 (guest/guest)

## Commands

```bash
make help         # Show all commands
make env          # Initialize environment
make dev          # Start all services
make dev-down     # Stop services
make verify       # Run verification tests
make status       # Show service status
make logs         # View logs
make clean        # Clean up
```

## Project Structure

```
citrature/
├── frontend/                # React application
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── services/
│   ├── api/                # FastAPI service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   └── routes/
│   ├── worker/             # Celery worker
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── worker.py
│   │   └── tasks/
│   └── beat/               # Celery Beat
│       ├── Dockerfile
│       ├── requirements.txt
│       └── beat.py
├── shared/                 # Shared utilities
│   ├── config.py          # Configuration management
│   ├── database.py        # Database connection
│   ├── models.py          # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── clients/           # External service clients
│   └── alembic/           # Database migrations
├── .env.example
├── docker-compose.yml
└── Makefile
```

## License

MIT
