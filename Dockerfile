FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 citrature && chown -R citrature:citrature /app
USER citrature

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "citrature.main:app", "--host", "0.0.0.0", "--port", "8000"]
