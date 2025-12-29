# PowerShell Scripts Guide - AI Video Editor

**Windows-friendly command scripts for development**

---

## 🚀 Quick Start

```powershell
# From setup folder
.\setup.ps1              # Install everything
.\dev.ps1                # Start all services
```

---

## 📋 Available Scripts

### Setup
```powershell
.\setup.ps1              # Complete setup (backend + frontend)
```

### Development
```powershell
.\dev.ps1                # Start all services (Docker)
.\dev-backend.ps1        # Start backend only (FastAPI)
.\dev-frontend.ps1       # Start frontend only (React)
```

### Quality
```powershell
.\test.ps1               # Run all tests
.\lint.ps1               # Lint all code
.\format.ps1             # Format all code
```

### Docker
```powershell
.\stop.ps1               # Stop Docker services
.\logs.ps1               # View Docker logs
```

---

## 🔧 Detailed Commands

### .\setup.ps1
**What it does:**
- Creates Python virtual environment
- Installs UV package manager
- Installs backend dependencies (with dev tools)
- Installs frontend dependencies

**When to use:**
- First time setup
- After deleting venv or node_modules

**Time:** ~5-10 minutes

```powershell
.\setup.ps1
```

---

### .\dev.ps1
**What it does:**
- Starts all Docker containers
- Starts PostgreSQL, Redis, Backend, Frontend, Celery

**When to use:**
- Daily development
- Want everything running at once

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

```powershell
.\dev.ps1
```

---

### .\dev-backend.ps1
**What it does:**
- Activates Python virtual environment
- Starts FastAPI development server
- Enables hot reload

**When to use:**
- Working on backend only
- Want to see backend logs clearly

**Access:**
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

```powershell
.\dev-backend.ps1
```

---

### .\dev-frontend.ps1
**What it does:**
- Starts Vite development server
- Enables hot module replacement (HMR)

**When to use:**
- Working on frontend only
- Want to see frontend logs clearly

**Access:**
- Frontend: http://localhost:3000

```powershell
.\dev-frontend.ps1
```

---

### .\test.ps1
**What it does:**
- Runs backend tests with coverage
- Runs frontend tests

**When to use:**
- Before committing code
- Checking if changes broke anything

```powershell
.\test.ps1
```

---

### .\lint.ps1
**What it does:**
- Lints backend code with Ruff
- Lints frontend code with ESLint

**When to use:**
- Check code quality
- Find potential issues

```powershell
.\lint.ps1
```

---

### .\format.ps1
**What it does:**
- Formats backend code with Black
- Formats frontend code with Prettier

**When to use:**
- Auto-fix formatting issues
- Before committing code

```powershell
.\format.ps1
```

---

### .\stop.ps1
**What it does:**
- Stops all Docker containers

**When to use:**
- End of work day
- Need to free up resources

```powershell
.\stop.ps1
```

---

### .\logs.ps1
**What it does:**
- Shows real-time Docker logs

**When to use:**
- Debugging issues
- Monitoring services

```powershell
.\logs.ps1
```

---

## 📊 Typical Development Workflow

### Day 1: Initial Setup
```powershell
# From setup folder
.\setup.ps1              # ~10 minutes
```

### Daily Development
```powershell
# Option 1: Everything in Docker
.\dev.ps1                # Start all services
# Work on code...
.\stop.ps1               # Stop services

# Option 2: Local development
# Terminal 1
.\dev-backend.ps1

# Terminal 2
.\dev-frontend.ps1
```

### Before Committing
```powershell
.\lint.ps1               # Check quality
.\format.ps1             # Auto-fix formatting
.\test.ps1               # Run tests
```

---

## 🆘 Troubleshooting

### Setup fails
```powershell
# Try again
.\setup.ps1

# Or manual setup
cd ..\backend
python -m venv venv
.\venv\Scripts\activate.ps1
pip install uv
uv pip install -e ".[dev]"
cd ..\setup

cd ..\frontend
npm install
cd ..\setup
```

### Backend won't start
```powershell
# Check if venv exists
if (Test-Path "..\backend\venv") { 
    Write-Host "venv exists" 
} else { 
    Write-Host "venv missing - run .\setup.ps1"
}

# Try restarting
.\dev-backend.ps1
```

### Frontend won't start
```powershell
# Check if node_modules exists
if (Test-Path "..\frontend\node_modules") { 
    Write-Host "node_modules exists" 
} else { 
    Write-Host "node_modules missing - run .\setup.ps1"
}

# Try restarting
.\dev-frontend.ps1
```

### Docker issues
```powershell
# Stop everything
.\stop.ps1

# Check status
cd ..
docker-compose ps

# Rebuild
docker-compose build --no-cache

# Start again
cd setup
.\dev.ps1
```

---

## 📝 Script Locations

All scripts are in the setup folder: `c:\Office\editor\setup\`

```
c:\Office\editor\setup\
├── setup.ps1             # Initial setup
├── dev.ps1               # Start all services
├── dev-backend.ps1       # Start backend only
├── dev-frontend.ps1      # Start frontend only
├── test.ps1              # Run tests
├── lint.ps1              # Lint code
├── format.ps1            # Format code
├── stop.ps1              # Stop services
├── logs.ps1              # View logs
└── POWERSHELL_GUIDE.md   # This file
```

---

## 🎯 Command Cheatsheet

| Task | Command |
|------|---------|
| **Setup** | `.\setup.ps1` |
| **Start All** | `.\dev.ps1` |
| **Start Backend** | `.\dev-backend.ps1` |
| **Start Frontend** | `.\dev-frontend.ps1` |
| **Run Tests** | `.\test.ps1` |
| **Check Quality** | `.\lint.ps1` |
| **Auto-format** | `.\format.ps1` |
| **Stop Services** | `.\stop.ps1` |
| **View Logs** | `.\logs.ps1` |

---

## ⚙️ Requirements

- Windows 10/11
- PowerShell 5.0+ (built-in)
- Python 3.11+
- Node.js 18+
- Docker Desktop (for Docker commands)

---

## 🔐 Execution Policy

If you get "cannot be loaded because running scripts is disabled" error:

```powershell
# Allow scripts for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run scripts
.\setup.ps1
```

---

**Status:** PowerShell scripts ready in setup folder  
**Next:** Run `.\setup.ps1` to initialize the project
