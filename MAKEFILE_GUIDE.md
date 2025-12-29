# Makefile Guide - AI Video Editor

**Quick command reference for development**

---

## 🚀 Quick Start

```bash
# From project root
make setup          # Install everything
make dev            # Start all services
```

That's it! Your development environment is ready.

---

## 📋 Root Makefile Commands

Run these from the project root (`c:\Office\editor\`)

### Setup Commands
```bash
make setup              # Complete setup (backend + frontend)
make install            # Install all dependencies
make install-backend    # Install backend only
make install-frontend   # Install frontend only
```

### Development Commands
```bash
make dev                # Start all services (Docker)
make dev-backend        # Start backend locally
make dev-frontend       # Start frontend locally
```

### Quality Commands
```bash
make test               # Run all tests
make lint               # Lint all code
make format             # Format all code
```

### Docker Commands
```bash
make docker-up          # Start Docker containers
make docker-down        # Stop Docker containers
make docker-logs        # View Docker logs
make docker-build       # Build Docker images
make docker-ps          # Show container status
```

### Database Commands
```bash
make db-migrate         # Run migrations
make db-reset           # Reset database
```

### Cleanup Commands
```bash
make clean              # Remove cache/build files
make clean-venv         # Remove virtual environments
make clean-cache        # Remove Python cache
```

### Status
```bash
make status             # Show project status
make help               # Show all commands
```

---

## 🔧 Backend Makefile Commands

Run these from `backend/` directory

### Setup
```bash
make install            # Install dependencies
make install-dev        # Install with dev tools
```

### Development
```bash
make dev                # Start FastAPI server (port 8000)
make celery             # Start Celery worker
```

### Testing
```bash
make test               # Run tests with coverage
make test-watch        # Run tests in watch mode
make test-coverage     # Generate coverage report
```

### Code Quality
```bash
make lint               # Lint with Ruff
make format             # Format with Black
make type-check         # Type check with MyPy
make quality            # Run all checks
```

### Database
```bash
make migrate            # Run migrations
make migrate-create     # Create new migration
make migrate-downgrade  # Downgrade one migration
```

### Cleanup
```bash
make clean              # Remove cache files
make clean-venv         # Remove virtual environment
make status             # Show backend status
```

---

## 🎨 Frontend Makefile Commands

Run these from `frontend/` directory

### Setup
```bash
make install            # Install npm dependencies
```

### Development
```bash
make dev                # Start dev server (port 3000)
make build              # Build for production
make preview            # Preview production build
```

### Testing
```bash
make test               # Run tests
make test-ui            # Run tests with UI
make test-coverage      # Run tests with coverage
```

### Code Quality
```bash
make lint               # Lint with ESLint
make format             # Format with Prettier
make type-check         # Type check with TypeScript
make quality            # Run all checks
```

### Cleanup
```bash
make clean              # Remove build files
make clean-deps         # Remove node_modules
make status             # Show frontend status
```

---

## 📊 Typical Development Workflow

### Day 1: Initial Setup
```bash
# From project root
make setup              # ~5 minutes
make status             # Verify everything
```

### Daily Development
```bash
# Option 1: Using Docker (recommended)
make dev                # Starts everything
make docker-logs        # View logs

# Option 2: Local development
make dev-backend        # Terminal 1
make dev-frontend       # Terminal 2
```

### Before Committing
```bash
# From project root
make lint               # Check code quality
make format             # Auto-format code
make test               # Run tests
```

### Cleanup
```bash
make clean              # Remove cache files
```

---

## 🐳 Docker Workflow

```bash
# Start all services
make docker-up

# View status
make docker-ps

# View logs
make docker-logs

# Stop all services
make docker-down
```

---

## 🧪 Testing Workflow

### Backend
```bash
cd backend
make test               # Run with coverage
make test-watch        # Run in watch mode
make test-coverage     # Generate HTML report
```

### Frontend
```bash
cd frontend
make test               # Run tests
make test-ui            # Run with UI
make test-coverage     # Generate coverage
```

### All Tests
```bash
make test               # From project root
```

---

## 🔍 Code Quality Workflow

### Check Quality
```bash
make lint               # Check for issues
```

### Auto-fix
```bash
make format             # Auto-format code
```

### Type Checking
```bash
cd backend
make type-check         # Python types

cd frontend
make type-check         # TypeScript types
```

### Complete Check
```bash
make quality            # Run all checks
```

---

## 💾 Database Workflow

```bash
cd backend

# Run pending migrations
make migrate

# Create new migration
make migrate-create

# Downgrade one migration
make migrate-downgrade
```

---

## 🗑️ Cleanup Commands

### Remove Cache Only
```bash
make clean              # Safe to run anytime
```

### Remove Virtual Environments
```bash
make clean-venv         # Removes venv, requires reinstall
```

### Remove Everything
```bash
make clean-venv         # Remove venvs
make clean-deps         # Remove node_modules
make clean              # Remove cache
```

---

## ⚙️ Environment Variables

### Backend
Create `backend/.env`:
```
DATABASE_URL=postgresql://editor:editor_pass@localhost:5432/ai_video_editor
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key
```

### Frontend
Create `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

---

## 🆘 Troubleshooting

### Backend won't start
```bash
cd backend
make clean-venv
make install-dev
make dev
```

### Frontend won't start
```bash
cd frontend
make clean-deps
make install
make dev
```

### Docker issues
```bash
make docker-down
make docker-build
make docker-up
```

### Tests failing
```bash
make clean              # Clear cache
make test               # Run again
```

---

## 📝 Command Cheatsheet

| Task | Command |
|------|---------|
| **Setup** | `make setup` |
| **Start Dev** | `make dev` |
| **Run Tests** | `make test` |
| **Check Quality** | `make lint` |
| **Auto-format** | `make format` |
| **View Status** | `make status` |
| **Stop Services** | `make docker-down` |
| **Clean Cache** | `make clean` |
| **Help** | `make help` |

---

## 🎯 Pro Tips

1. **Always run `make setup` first** - Sets up everything correctly
2. **Use `make dev` for development** - Starts all services at once
3. **Run `make lint` before committing** - Catch issues early
4. **Use `make test-watch` for TDD** - Auto-run tests on file changes
5. **Check `make status` anytime** - See what's installed
6. **Use `make clean` regularly** - Keep workspace clean

---

## 🔗 Related Files

- `Makefile` - Root makefile (project-wide commands)
- `backend/Makefile` - Backend-specific commands
- `frontend/Makefile` - Frontend-specific commands
- `QUICK_START.md` - Quick start guide
- `SETUP_COMPLETE.md` - Detailed setup guide

---

**Status:** Makefiles ready for use  
**Next:** Run `make setup` to initialize the project
