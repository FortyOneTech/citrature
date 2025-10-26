# Citrature Platform Makefile

.PHONY: help env dev dev-down clean logs status

# Default target
help:
	@echo "Available commands:"
	@echo "  env       - Copy .env.example to .env"
	@echo "  dev       - Start development environment with docker-compose up --build"
	@echo "  dev-down  - Stop development environment with docker-compose down"
	@echo "  frontend  - Start only frontend service"
	@echo "  logs      - Show live logs from all services"
	@echo "  status    - Show status of all services"
	@echo "  clean     - Clean up containers and volumes"

# Copy .env.example to .env
env:
	@echo "Copying .env.example to .env..."
	@cp .env.example .env
	@cp frontend/.env.example frontend/.env
	@echo "✅ Environment file created. Please edit .env with your actual values."

# Start development environment
dev:
	@echo "Starting development environment..."
	docker-compose up --build

# Stop development environment
dev-down:
	@echo "Stopping development environment..."
	docker-compose down

dev-destroy:
	@echo "Destroying development environment..."
	docker-compose down -v --remove-orphans
	docker system prune -af --volumes
	docker volume prune --all -f
	@echo "✅ Development environment destroyed."

# Start only frontend service
frontend:
	@echo "Starting frontend service..."
	docker-compose up --build frontend

# Show live logs
logs:
	@echo "Showing live logs from all services..."
	docker-compose logs -f

# Show service status
status:
	@echo "Service status:"
	docker-compose ps

# Clean up everything
clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup complete."
