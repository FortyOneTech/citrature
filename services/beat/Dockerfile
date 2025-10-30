FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY services/beat/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY shared/ /app/shared/

# Copy beat service code
COPY services/beat/ /app/services/beat/

# Set Python path
ENV PYTHONPATH=/app

WORKDIR /app/services/beat

CMD ["celery", "-A", "beat:celery_app", "beat", "--loglevel=info"]

