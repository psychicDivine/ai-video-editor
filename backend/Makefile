.PHONY: help install dev test lint format clean migrate

help:
	@echo "Backend - Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install            - Install dependencies (venv + packages)"
	@echo "  make install-dev        - Install with dev dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev                - Start development server"
	@echo "  make celery             - Start Celery worker"
	@echo ""
	@echo "Quality Commands:"
	@echo "  make test               - Run tests"
	@echo "  make lint               - Lint code"
	@echo "  make format             - Format code"
	@echo "  make type-check         - Type checking with mypy"
	@echo ""
	@echo "Database Commands:"
	@echo "  make migrate            - Run database migrations"
	@echo "  make migrate-create     - Create new migration"
	@echo ""
	@echo "Cleanup Commands:"
	@echo "  make clean              - Remove cache and build files"
	@echo "  make clean-venv         - Remove virtual environment"

# Setup
install:
	@echo "📦 Creating virtual environment..."
	python -m venv venv
	@echo "📦 Upgrading pip..."
	.\venv\Scripts\pip install --upgrade pip
	@echo "📦 Installing UV..."
	.\venv\Scripts\pip install uv
	@echo "📦 Installing dependencies..."
	.\venv\Scripts\uv pip install -e "."
	@echo "✅ Installation complete"

install-dev:
	@echo "📦 Creating virtual environment..."
	python -m venv venv
	@echo "📦 Upgrading pip..."
	.\venv\Scripts\pip install --upgrade pip
	@echo "📦 Installing UV..."
	.\venv\Scripts\pip install uv
	@echo "📦 Installing dependencies with dev tools..."
	.\venv\Scripts\uv pip install -e ".[dev]"
	@echo "✅ Installation complete"

# Development
dev:
	@echo "🚀 Starting FastAPI development server..."
	.\venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

celery:
	@echo "🚀 Starting Celery worker..."
	.\venv\Scripts\celery -A app.workers.celery_app worker --loglevel=info

# Testing
test:
	@echo "🧪 Running tests..."
	.\venv\Scripts\pytest tests/ -v --cov=app --cov-report=html

test-watch:
	@echo "🧪 Running tests in watch mode..."
	.\venv\Scripts\pytest tests/ -v --cov=app -x

test-coverage:
	@echo "📊 Generating coverage report..."
	.\venv\Scripts\pytest tests/ --cov=app --cov-report=html
	@echo "✅ Coverage report generated in htmlcov/index.html"

# Code Quality
lint:
	@echo "🔍 Linting with Ruff..."
	.\venv\Scripts\ruff check app/
	@echo "✅ Linting complete"

format:
	@echo "✨ Formatting with Black..."
	.\venv\Scripts\black app/
	@echo "✅ Formatting complete"

type-check:
	@echo "🔍 Type checking with MyPy..."
	.\venv\Scripts\mypy app/
	@echo "✅ Type checking complete"

quality: lint format type-check
	@echo "✅ All quality checks passed"

# Database
migrate:
	@echo "🗄️ Running database migrations..."
	.\venv\Scripts\alembic upgrade head
	@echo "✅ Migrations complete"

migrate-create:
	@echo "📝 Creating new migration..."
	@read -p "Enter migration name: " name; \
	.\venv\Scripts\alembic revision --autogenerate -m "$$name"

migrate-downgrade:
	@echo "⬇️ Downgrading database..."
	.\venv\Scripts\alembic downgrade -1

# Cleanup
clean:
	@echo "🧹 Removing cache and build files..."
	rmdir /s /q __pycache__ 2>nul || true
	rmdir /s /q .pytest_cache 2>nul || true
	rmdir /s /q .mypy_cache 2>nul || true
	rmdir /s /q build 2>nul || true
	rmdir /s /q dist 2>nul || true
	rmdir /s /q *.egg-info 2>nul || true
	del /q .coverage 2>nul || true
	@echo "✅ Cleanup complete"

clean-venv:
	@echo "🗑️ Removing virtual environment..."
	rmdir /s /q venv 2>nul || true
	@echo "✅ Virtual environment removed"

# Status
status:
	@echo "📊 Backend Status"
	@echo "================="
	@if exist "venv" (echo "✅ Virtual environment exists") else (echo "❌ Virtual environment missing")
	@if exist "venv\Scripts\uvicorn.exe" (echo "✅ Dependencies installed") else (echo "❌ Dependencies not installed")
	@echo ""
	@echo "Run 'make install-dev' to set up the environment"
