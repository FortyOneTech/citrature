# Citrature Platform - Quick Start Guide

## ⚡ 5-Minute Setup

### Prerequisites Check

Before starting, ensure you have:

- [ ] Docker Desktop installed and running
- [ ] Google OAuth credentials (Client ID & Secret)
- [ ] OpenRouter API key
- [ ] Google Cloud Storage bucket configured
- [ ] Email address for Crossref API

### Setup Steps

#### 1. Initialize Environment

```bash
make env
```

This creates `.env` and `frontend/.env` from the example files.

#### 2. Configure Credentials

Edit `.env` and update these required fields:

```bash
# External API Keys
OPENROUTER_API_KEY=sk-or-v1-your-actual-key
CROSSREF_MAILTO=your-email@example.com

# Google OAuth (from Google Cloud Console)
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret

# Google Cloud Storage
GCS_BUCKET_NAME=your-bucket-name
GCS_PROJECT_ID=your-project-id
GCS_CREDENTIALS_JSON='{"type":"service_account",...}'

# Security (generate a random 32+ character string)
SECRET_KEY=your-secure-random-secret-key-min-32-chars
```

#### 3. Start Platform

```bash
make dev
```

Wait for all services to start (takes 2-5 minutes on first run).

#### 4. Verify

In another terminal:

```bash
make verify
```

You should see all checks passing ✅

#### 5. Access Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **RabbitMQ UI**: http://localhost:15672 (guest/guest)

## 🎯 What Just Happened?

The platform started **7 microservices**:

1. **PostgreSQL** - Database with pgvector
2. **Redis** - Task result backend
3. **RabbitMQ** - Message broker
4. **GROBID** - PDF processing service
5. **API** - FastAPI backend
6. **Worker** - Celery worker for background tasks
7. **Frontend** - React application

All running in Docker containers with proper networking and persistent storage.

## 📊 Verification Checklist

After running `make verify`, you should see:

- ✅ All 7 services running
- ✅ Health checks passing for db, redis, rabbitmq, grobid, api
- ✅ Inter-service connectivity confirmed (api ↔ db, rabbitmq, redis, grobid)
- ✅ Environment variables loaded successfully
- ✅ Persistent volumes created (pgdata, bm25_indices, redis_data, rabbitmq_data, grobid_data)
- ✅ Shared network `citrature-network` configured

## 🔧 Common Commands

```bash
# View all available commands
make help

# Show service status
make status

# View live logs
make logs

# Stop services (preserves data)
make dev-down

# Clean up everything (removes data!)
make clean
```

## 🐛 Troubleshooting

### Services won't start

```bash
# Check Docker is running
docker ps

# View service logs
make logs

# Restart specific service
docker-compose restart api
```

### Missing environment variable error

```bash
# Verify all required variables are set
grep -E "^(API_ORIGIN|POSTGRES_DSN|GOOGLE_CLIENT_ID|OPENROUTER_API_KEY)" .env

# Re-initialize if needed
make env
```

### Database connection failed

```bash
# Check database health
docker exec citrature-db pg_isready -U citrature -d citrature

# Restart database
docker-compose restart db
```

### GROBID slow to start

GROBID downloads models on first run (5-10 minutes). This is normal.

```bash
# Monitor GROBID startup
docker-compose logs -f grobid
```

## 📚 Next Steps

Once everything is verified:

1. **Create Google OAuth consent screen** (see README.md)
2. **Test authentication** - Navigate to http://localhost:3000 and sign in
3. **Upload a PDF** - Test the ingestion pipeline
4. **Explore API docs** - http://localhost:8000/docs

## 📖 Learn More

- **Configuration Guide**: See `CONFIGURATION.md` for detailed configuration reference
- **Implementation Details**: See `IMPLEMENTATION_STEP_1.md` for architecture overview
- **Full Documentation**: See `README.md` for complete platform documentation

## 🚀 You're Ready!

The Citrature platform is now running locally with:

- ✅ Centralized configuration management
- ✅ Health check-based startup ordering
- ✅ Persistent data storage
- ✅ Service-to-service networking
- ✅ Comprehensive verification

Happy researching! 🎓

