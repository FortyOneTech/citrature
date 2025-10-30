#!/bin/bash

# ================================================================================
# Citrature Platform - Startup Verification Script
# ================================================================================
# This script verifies that all services have started correctly and can
# communicate with each other as specified in the Implementation Plan.
# ================================================================================

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Citrature Platform - Startup Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print success
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print info
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to print warning
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Step 1: Verify all services are running"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SERVICES=("citrature-db" "citrature-redis" "citrature-rabbitmq" "citrature-grobid" "citrature-api" "citrature-worker" "citrature-beat")

for service in "${SERVICES[@]}"; do
    if docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
        success "$service is running"
    else
        error "$service is NOT running"
        exit 1
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 Step 2: Verify service health checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check database health
info "Checking database health..."
if docker exec citrature-db pg_isready -U citrature -d citrature > /dev/null 2>&1; then
    success "Database is healthy"
else
    error "Database health check failed"
    exit 1
fi

# Check Redis health
info "Checking Redis health..."
if docker exec citrature-redis redis-cli ping | grep -q "PONG"; then
    success "Redis is healthy"
else
    error "Redis health check failed"
    exit 1
fi

# Check RabbitMQ health
info "Checking RabbitMQ health..."
if docker exec citrature-rabbitmq rabbitmq-diagnostics ping > /dev/null 2>&1; then
    success "RabbitMQ is healthy"
else
    error "RabbitMQ health check failed"
    exit 1
fi

# Check GROBID health (may take time to start)
info "Checking GROBID health (this may take up to 60 seconds)..."
MAX_ATTEMPTS=20
ATTEMPT=1
until docker exec citrature-grobid curl -f http://localhost:8070/api/isalive > /dev/null 2>&1; do
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        error "GROBID health check failed after waiting for startup"
        exit 1
    fi
    warning "GROBID is still starting up (attempt $ATTEMPT/$MAX_ATTEMPTS)..."
    ATTEMPT=$((ATTEMPT+1))
    sleep 3
done
success "GROBID is healthy"
# Check API health
info "Checking API health..."
if docker exec citrature-api curl -f http://localhost:8000/health > /dev/null 2>&1; then
    success "API is healthy"
else
    error "API health check failed"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Step 3: Verify service-to-service connectivity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# API can reach database
info "Testing API → Database connectivity..."
if docker exec citrature-api ping -c 1 db > /dev/null 2>&1; then
    success "API can reach database"
else
    error "API cannot reach database"
    exit 1
fi

# API can reach RabbitMQ
info "Testing API → RabbitMQ connectivity..."
if docker exec citrature-api ping -c 1 rabbitmq > /dev/null 2>&1; then
    success "API can reach RabbitMQ"
else
    error "API cannot reach RabbitMQ"
    exit 1
fi

# API can reach Redis
info "Testing API → Redis connectivity..."
if docker exec citrature-api ping -c 1 redis > /dev/null 2>&1; then
    success "API can reach Redis"
else
    error "API cannot reach Redis"
    exit 1
fi

# API can reach GROBID
info "Testing API → GROBID connectivity..."
if docker exec citrature-api ping -c 1 grobid > /dev/null 2>&1; then
    success "API can reach GROBID"
else
    error "API cannot reach GROBID"
    exit 1
fi

# Worker can reach database
info "Testing Worker → Database connectivity..."
if docker exec citrature-worker ping -c 1 db > /dev/null 2>&1; then
    success "Worker can reach database"
else
    error "Worker cannot reach database"
    exit 1
fi

# Worker can reach RabbitMQ
info "Testing Worker → RabbitMQ connectivity..."
if docker exec citrature-worker ping -c 1 rabbitmq > /dev/null 2>&1; then
    success "Worker can reach RabbitMQ"
else
    error "Worker cannot reach RabbitMQ"
    exit 1
fi

# Worker can reach Redis
info "Testing Worker → Redis connectivity..."
if docker exec citrature-worker ping -c 1 redis > /dev/null 2>&1; then
    success "Worker can reach Redis"
else
    error "Worker cannot reach Redis"
    exit 1
fi

# Worker can reach GROBID
info "Testing Worker → GROBID connectivity..."
if docker exec citrature-worker ping -c 1 grobid > /dev/null 2>&1; then
    success "Worker can reach GROBID"
else
    error "Worker cannot reach GROBID"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  Step 4: Verify environment variable loading"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

info "Checking API service logs for configuration confirmation..."
if docker logs citrature-api 2>&1 | grep -q "All required environment variables loaded successfully"; then
    success "API service confirmed all environment variables loaded"
else
    warning "API may not have logged configuration confirmation yet"
fi

info "Checking Worker service logs for configuration confirmation..."
if docker logs citrature-worker 2>&1 | grep -q "All required environment variables loaded successfully"; then
    success "Worker service confirmed all environment variables loaded"
else
    warning "Worker may not have logged configuration confirmation yet"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Step 5: Verify persistent volumes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

VOLUMES=("citrature-pgdata" "citrature-bm25-indices" "citrature-redis-data" "citrature-rabbitmq-data" "citrature-grobid-data")

for volume in "${VOLUMES[@]}"; do
    if docker volume inspect "$volume" > /dev/null 2>&1; then
        success "Volume $volume exists"
    else
        error "Volume $volume does NOT exist"
        exit 1
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Step 6: Verify network configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if docker network inspect citrature-network > /dev/null 2>&1; then
    success "Shared network 'citrature-network' exists"
else
    error "Shared network 'citrature-network' does NOT exist"
    exit 1
fi

# Verify all services are connected to the network
for service in "${SERVICES[@]}"; do
    if docker inspect "$service" | grep -q "citrature-network"; then
        success "$service is connected to citrature-network"
    else
        error "$service is NOT connected to citrature-network"
        exit 1
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Step 7: Display service status summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker-compose ps

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ All verification checks passed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Service endpoints:"
echo "  🌐 Frontend:         http://localhost:3000"
echo "  🔌 API:              http://localhost:8000"
echo "  📖 API Docs:         http://localhost:8000/docs"
echo "  🐰 RabbitMQ UI:      http://localhost:15672 (guest/guest)"
echo "  🔬 GROBID:           http://localhost:8070"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f          # All services"
echo "  docker-compose logs -f api      # API service only"
echo "  docker-compose logs -f worker   # Worker service only"
echo ""
success "Citrature platform is ready! 🚀"
echo ""

