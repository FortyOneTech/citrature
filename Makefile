# ================================================================================
# Citrature Platform Makefile
# ================================================================================
# This Makefile provides convenient commands for managing the Citrature platform
# development environment and verifying proper configuration.
# ================================================================================

.PHONY: help env dev dev-down dev-destroy verify clean logs status frontend

# Default target
help:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "📚 Citrature Platform - Available Commands"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "🔧 Setup & Configuration:"
	@echo "  make env          - Copy .env.example to .env (first-time setup)"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make dev          - Start all services with docker-compose up --build"
	@echo "  make dev-down     - Stop all services gracefully"
	@echo "  make dev-destroy  - Destroy environment (remove volumes and containers)"
	@echo ""
	@echo "✅ Verification:"
	@echo "  make verify       - Run comprehensive startup verification tests"
	@echo ""
	@echo "📊 Monitoring:"
	@echo "  make logs         - Show live logs from all services"
	@echo "  make status       - Show status of all running services"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean        - Clean up containers and volumes"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""

# Copy .env.example to .env
env:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🔧 Setting up environment configuration..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@if [ -f .env ]; then \
		echo "⚠️  .env file already exists. Backing up to .env.backup"; \
		cp .env .env.backup; \
	fi
	@cp .env.example .env
	@if [ -f frontend/.env ]; then \
		echo "⚠️  frontend/.env file already exists. Backing up to frontend/.env.backup"; \
		cp frontend/.env frontend/.env.backup; \
	fi
	@cp frontend/.env.example frontend/.env
	@echo "✅ Environment files created"
	@echo ""
	@echo "📝 Next steps:"
	@echo "  1. Edit .env with your actual configuration values"
	@echo "  2. Edit frontend/.env with your frontend configuration"
	@echo "  3. Run 'make dev' to start the platform"
	@echo "  4. Run 'make verify' to verify everything is working"
	@echo ""

# Start development environment
dev:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🚀 Starting Citrature development environment..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@if [ ! -f .env ]; then \
		echo "❌ Error: .env file not found. Run 'make env' first."; \
		exit 1; \
	fi
	docker-compose up --build

# Stop development environment
dev-down:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "⏹️  Stopping Citrature development environment..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	docker-compose down
	@echo "✅ All services stopped"

# Destroy development environment (WARNING: removes all data)
dev-destroy:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "⚠️  WARNING: This will destroy all containers, volumes, and data!"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "Press Ctrl+C within 5 seconds to cancel..."
	@sleep 5
	@echo "🗑️  Destroying development environment..."
	docker-compose down -v --remove-orphans
	docker system prune -af --volumes
	docker volume prune --all -f
	@echo "✅ Development environment destroyed"

# Run comprehensive startup verification
verify:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "✅ Running startup verification tests..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@chmod +x scripts/verify_startup.sh
	@./scripts/verify_startup.sh

# Start only frontend service
frontend:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🎨 Starting frontend service..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	docker-compose up --build frontend

# Show live logs
logs:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "📜 Showing live logs from all services (Ctrl+C to exit)..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	docker-compose logs -f

# Show service status
status:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "📊 Service Status"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@docker-compose ps
	@echo ""
	@echo "Service Endpoints:"
	@echo "  🌐 Frontend:     http://localhost:3000"
	@echo "  🔌 API:          http://localhost:8000"
	@echo "  📖 API Docs:     http://localhost:8000/docs"
	@echo "  🐰 RabbitMQ UI:  http://localhost:15672"
	@echo ""

# Clean up everything
clean:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🧹 Cleaning up containers and volumes..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup complete"
