FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY services/worker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY shared/ /app/shared/

# Copy worker service code
COPY services/worker/ /app/services/worker/

# Set Python path
ENV PYTHONPATH=/app

WORKDIR /app/services/worker

CMD ["celery", "-A", "worker:celery_app", "worker", "--loglevel=info", "--concurrency=2"]

