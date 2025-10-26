# Citrature

AI-powered research paper analysis and citation graph platform.

## Features

- **PDF Ingestion**: Upload and process research papers using GROBID
- **Topic Discovery**: Find relevant papers via Crossref API
- **Citation Graphs**: Build and visualize citation networks
- **AI Chat**: Query your research collection with natural language
- **Gap Analysis**: Identify research opportunities and gaps
- **Vector Search**: Hybrid BM25 + semantic search

## Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL with pgvector extension
- **Message Queue**: RabbitMQ with Celery workers
- **Cache**: Redis for task results
- **Storage**: Google Cloud Storage for files
- **AI**: OpenRouter API for embeddings and chat
- **PDF Processing**: GROBID service

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Cloud Storage bucket
- OpenRouter API key
- Crossref API access (free)
- Google OAuth credentials

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd citrature
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Set up Google OAuth**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Navigate to **APIs & Services > OAuth consent screen**
   - Choose **External** user type for public applications
   - Fill in required information:
     - App name: `Citrature`
     - User support email: Your email
     - Developer contact information: Your email
   - Save the consent screen configuration
   - Navigate to **APIs & Services > Credentials**
   - Click **+ CREATE CREDENTIALS** → **OAuth client ID**
   - Choose **Web application** as application type
   - Provide name: `Citrature Web Client`
   - Add **Authorized JavaScript origins**:
     - `http://localhost:3000` (for development)
     - `https://yourdomain.com` (for production)
   - Add **Authorized redirect URIs**:
     - `http://localhost:8000/auth/google/callback` (for development)
     - `https://yourdomain.com/auth/google/callback` (for production)
   - Click **Create**
   - Copy the **Client ID** and **Client Secret** to your `.env` file

4. **Create GCS credentials file**
   ```bash
   # Place your GCS service account JSON file as credentials.json
   ```

5. **Start services**
   ```bash
   docker-compose up -d
   ```

6. **Run database migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

7. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - RabbitMQ Management: http://localhost:15672 (guest/guest)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `RABBITMQ_URL` | RabbitMQ connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `OPENROUTER_API_KEY` | OpenRouter API key | Required |
| `CROSSREF_MAILTO` | Email for Crossref API | Required |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID (from Google Cloud Console) | Required |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret (from Google Cloud Console) | Required |
| `GOOGLE_REDIRECT_URI` | Google OAuth redirect URI (usually `http://localhost:8000/auth/google/callback`) | Required |
| `GCS_BUCKET_NAME` | Google Cloud Storage bucket | Required |
| `GCS_PROJECT_ID` | Google Cloud project ID | Required |
| `GCS_CREDENTIAL_PATH` | Path to GCS credentials JSON | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `REACT_APP_GOOGLE_CLIENT_ID` | Google OAuth client ID for frontend | Required |

### Usage Limits

- **Free Plan**: 1 collection, 30 topic papers, depth 3 graph, 100 monthly chats
- **Upload Limit**: 50MB per PDF
- **Supported Formats**: PDF only

## API Endpoints

### Authentication
- `POST /auth/google` - Google OAuth login
- `GET /auth/me` - Get current user
- `POST /auth/logout` - Logout

### Collections
- `POST /collections/` - Create collection
- `GET /collections/` - List collections
- `GET /collections/{id}` - Get collection
- `DELETE /collections/{id}` - Delete collection

### Ingestion
- `POST /ingest/pdf/{collection_id}` - Upload PDF
- `POST /ingest/topic/{collection_id}` - Search topic

### Graph
- `POST /graph/build/{collection_id}` - Build citation graph
- `GET /graph/{collection_id}` - Get graph data

### Chat
- `POST /chat/{collection_id}` - Chat with collection

### Search
- `GET /search/{collection_id}` - Search collection

## Development

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start database**
   ```bash
   docker-compose up -d db redis rabbitmq grobid
   ```

3. **Run migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start API server**
   ```bash
   uvicorn citrature.main:app --reload
   ```

5. **Start Celery worker**
   ```bash
   celery -A citrature.celery_app worker --loglevel=info
   ```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Deployment

### Production Considerations

1. **Environment Variables**: Use secure secret management
2. **Database**: Use managed PostgreSQL with pgvector
3. **Storage**: Configure GCS bucket with proper IAM
4. **Monitoring**: Add logging and metrics
5. **Scaling**: Use multiple Celery workers
6. **Security**: Enable HTTPS and proper CORS

### Docker Production

```bash
# Build production image
docker build -t citrature:latest .

# Run with production settings
docker run -d \
  --name citrature-api \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  citrature:latest
```

## Troubleshooting

### Google OAuth Issues

**Common Issues:**

1. **"Invalid client" error**
   - Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correctly set in `.env`
   - Verify the Client ID matches exactly (no extra spaces or characters)

2. **"Redirect URI mismatch" error**
   - Check that `GOOGLE_REDIRECT_URI` in `.env` matches exactly what's configured in Google Cloud Console
   - For development: `http://localhost:8000/auth/google/callback`
   - For production: `https://yourdomain.com/auth/google/callback`

3. **"Access blocked" error**
   - Ensure OAuth consent screen is properly configured
   - For production, you may need to verify your domain with Google

4. **Frontend Google Sign-In not working**
   - Verify `REACT_APP_GOOGLE_CLIENT_ID` is set in frontend environment
   - Check browser console for JavaScript errors
   - Ensure Google Identity Services script loads properly

**Environment Variables Checklist:**
```bash
# Backend (.env)
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Frontend (.env)
REACT_APP_GOOGLE_CLIENT_ID=your_client_id_here
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
