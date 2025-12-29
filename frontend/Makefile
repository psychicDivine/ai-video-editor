.PHONY: help install dev build test lint format clean

help:
	@echo "Frontend - Development Commands"
	@echo "==============================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install            - Install dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev                - Start development server"
	@echo "  make build              - Build for production"
	@echo "  make preview            - Preview production build"
	@echo ""
	@echo "Quality Commands:"
	@echo "  make test               - Run tests"
	@echo "  make test-ui            - Run tests with UI"
	@echo "  make test-coverage      - Run tests with coverage"
	@echo "  make lint               - Lint code"
	@echo "  make format             - Format code"
	@echo "  make type-check         - Type checking"
	@echo ""
	@echo "Cleanup Commands:"
	@echo "  make clean              - Remove build and cache files"
	@echo "  make clean-deps         - Remove node_modules"

# Setup
install:
	@echo "📦 Installing dependencies..."
	npm install
	@echo "✅ Dependencies installed"

# Development
dev:
	@echo "🚀 Starting development server..."
	npm run dev

build:
	@echo "🔨 Building for production..."
	npm run build
	@echo "✅ Build complete"

preview:
	@echo "👀 Previewing production build..."
	npm run preview

# Testing
test:
	@echo "🧪 Running tests..."
	npm run test

test-ui:
	@echo "🧪 Running tests with UI..."
	npm run test:ui

test-coverage:
	@echo "📊 Running tests with coverage..."
	npm run test:coverage
	@echo "✅ Coverage report generated"

# Code Quality
lint:
	@echo "🔍 Linting code..."
	npm run lint
	@echo "✅ Linting complete"

format:
	@echo "✨ Formatting code..."
	npm run format
	@echo "✅ Formatting complete"

type-check:
	@echo "🔍 Type checking..."
	npm run type-check
	@echo "✅ Type checking complete"

quality: lint format type-check
	@echo "✅ All quality checks passed"

# Cleanup
clean:
	@echo "🧹 Removing build and cache files..."
	rmdir /s /q dist 2>nul || true
	rmdir /s /q .vite 2>nul || true
	rmdir /s /q coverage 2>nul || true
	del /q .DS_Store 2>nul || true
	@echo "✅ Cleanup complete"

clean-deps:
	@echo "🗑️ Removing node_modules..."
	rmdir /s /q node_modules 2>nul || true
	del /q package-lock.json 2>nul || true
	@echo "✅ Dependencies removed"

# Status
status:
	@echo "📊 Frontend Status"
	@echo "=================="
	@if exist "node_modules" (echo "✅ Dependencies installed") else (echo "❌ Dependencies not installed")
	@if exist "dist" (echo "✅ Build exists") else (echo "❌ Build missing")
	@echo ""
	@echo "Run 'make install' to set up the environment"
