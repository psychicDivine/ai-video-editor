.PHONY: help install install-backend install-frontend setup dev dev-backend dev-frontend test lint format clean docker-up docker-down docker-logs podman-up podman-down devcontainer

# Use podman instead of docker if available
DOCKER := $(shell command -v podman 2>/dev/null || echo docker)

help:
	@echo "AI Video Editor - Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup              - Complete project setup (venv + dependencies)"
	@echo "  make install            - Install all dependencies (backend + frontend)"
	@echo "  make install-backend    - Install backend dependencies"
	@echo "  make install-frontend   - Install frontend dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev                - Start all services (Docker)"
	@echo "  make dev-backend        - Start backend only (local)"
	@echo "  make dev-frontend       - Start frontend only (local)"
	@echo ""
	@echo "Quality Commands:"
	@echo "  make test               - Run all tests"
	@echo "  make lint               - Lint code (backend + frontend)"
	@echo "  make format             - Format code (backend + frontend)"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-up          - Start Docker containers"
	@echo "  make docker-down        - Stop Docker containers"
	@echo "  make docker-logs        - View Docker logs"
	@echo "  make docker-build       - Build Docker images"
	@echo ""
	@echo "Cleanup Commands:"
	@echo "  make clean              - Remove all generated files"
	@echo "  make clean-venv         - Remove virtual environments"
	@echo "  make clean-cache        - Remove Python cache files"

# Setup
setup: install-backend install-frontend
	@echo "✅ Setup complete!"
	@echo "Next: make dev"

install: install-backend install-frontend

install-backend:
	@echo "📦 Installing backend dependencies..."
	cd backend && python -m venv venv
	cd backend && .\venv\Scripts\pip install --upgrade pip
	cd backend && .\venv\Scripts\pip install uv
	cd backend && .\venv\Scripts\uv pip install -e ".[dev]"
	@echo "✅ Backend dependencies installed"

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Frontend dependencies installed"

# Development
dev: docker-up
	@echo "🚀 All services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

dev-backend:
	@echo "🚀 Starting backend..."
	cd backend && .\venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "🚀 Starting frontend..."
	cd frontend && npm run dev

# Testing
test:
	@echo "🧪 Running tests..."
	cd backend && .\venv\Scripts\pytest tests/ -v --cov=app

test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && .\venv\Scripts\pytest tests/ -v --cov=app

test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontend && npm run test

# Code Quality
lint:
	@echo "🔍 Linting code..."
	cd backend && .\venv\Scripts\ruff check app/
	cd frontend && npm run lint

lint-backend:
	@echo "🔍 Linting backend..."
	cd backend && .\venv\Scripts\ruff check app/

lint-frontend:
	@echo "🔍 Linting frontend..."
	cd frontend && npm run lint

format:
	@echo "✨ Formatting code..."
	cd backend && .\venv\Scripts\black app/
	cd frontend && npm run format

format-backend:
	@echo "✨ Formatting backend..."
	cd backend && .\venv\Scripts\black app/

format-frontend:
	@echo "✨ Formatting frontend..."
	cd frontend && npm run format

# Docker
docker-up:
	@echo "🐳 Starting Docker containers..."
	docker-compose up -d
	@echo "✅ Containers started"

docker-down:
	@echo "🛑 Stopping Docker containers..."
	docker-compose down
	@echo "✅ Containers stopped"

docker-logs:
	@echo "📋 Docker logs..."
	docker-compose logs -f

docker-build:
	@echo "🔨 Building Docker images..."
	docker-compose build --no-cache

docker-ps:
	@echo "📊 Docker containers status..."
	docker-compose ps

# Database
db-migrate:
	@echo "🗄️ Running database migrations..."
	cd backend && .\venv\Scripts\alembic upgrade head

db-reset:
	@echo "⚠️ Resetting database..."
	docker-compose down -v
	docker-compose up -d postgres
	@echo "✅ Database reset"

# Cleanup
clean: clean-cache clean-build
	@echo "🧹 Cleanup complete"

clean-venv:
	@echo "🗑️ Removing virtual environments..."
	rmdir /s /q backend\venv 2>nul || true
	rmdir /s /q frontend\node_modules 2>nul || true
	@echo "✅ Virtual environments removed"

clean-cache:
	@echo "🗑️ Removing cache files..."
	cd backend && rmdir /s /q __pycache__ 2>nul || true
	cd backend && rmdir /s /q .pytest_cache 2>nul || true
	cd backend && rmdir /s /q .mypy_cache 2>nul || true
	cd frontend && rmdir /s /q node_modules\.cache 2>nul || true
	@echo "✅ Cache files removed"

clean-build:
	@echo "🗑️ Removing build files..."
	cd backend && rmdir /s /q build 2>nul || true
	cd backend && rmdir /s /q dist 2>nul || true
	cd frontend && rmdir /s /q dist 2>nul || true
	@echo "✅ Build files removed"

# Status
status:
	@echo "📊 Project Status"
	@echo "================="
	@echo ""
	@echo "Backend:"
	@if exist "backend\venv" (echo "  ✅ Virtual environment exists") else (echo "  ❌ Virtual environment missing")
	@if exist "backend\venv\Scripts\uvicorn.exe" (echo "  ✅ Dependencies installed") else (echo "  ❌ Dependencies not installed")
	@echo ""
	@echo "Frontend:"
	@if exist "frontend\node_modules" (echo "  ✅ Dependencies installed") else (echo "  ❌ Dependencies not installed")
	@echo ""
	@echo "Docker:"
	docker-compose ps
