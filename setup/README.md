# Setup Folder - AI Video Editor

**All setup scripts and development commands in one place**

---

## 🚀 Quick Start

```powershell
# From setup folder (c:\Office\editor\setup)
.\setup.ps1              # Install everything
.\dev.ps1                # Start all services
```

---

## 📁 What's in This Folder

```
setup/
├── setup.ps1                 # Initial setup (install dependencies)
├── dev.ps1                   # Start all services (Docker)
├── dev-backend.ps1           # Start backend only
├── dev-frontend.ps1          # Start frontend only
├── test.ps1                  # Run all tests
├── lint.ps1                  # Lint code
├── format.ps1                # Format code
├── stop.ps1                  # Stop Docker services
├── logs.ps1                  # View Docker logs
├── POWERSHELL_GUIDE.md       # Complete documentation
└── README.md                 # This file
```

---

## 🎯 First Time Setup

1. **Open PowerShell** in the setup folder
2. **Run setup:**
   ```powershell
   .\setup.ps1
   ```
3. **Wait for completion** (~10 minutes)
4. **Start development:**
   ```powershell
   .\dev.ps1
   ```

---

## 📋 Daily Development Commands

### Start Services
```powershell
.\dev.ps1                # Start everything (Docker)
.\dev-backend.ps1        # Start backend only
.\dev-frontend.ps1       # Start frontend only
```

### Quality Checks
```powershell
.\lint.ps1               # Check code quality
.\format.ps1             # Auto-format code
.\test.ps1               # Run tests
```

### Monitoring
```powershell
.\logs.ps1               # View Docker logs
.\stop.ps1               # Stop services
```

---

## 🔧 What Each Script Does

| Script | Purpose | Time |
|--------|---------|------|
| `setup.ps1` | Install all dependencies | ~10 min |
| `dev.ps1` | Start all services | Instant |
| `dev-backend.ps1` | Start FastAPI server | Instant |
| `dev-frontend.ps1` | Start React dev server | Instant |
| `test.ps1` | Run all tests | ~2 min |
| `lint.ps1` | Check code quality | ~30 sec |
| `format.ps1` | Auto-format code | ~30 sec |
| `stop.ps1` | Stop Docker services | ~10 sec |
| `logs.ps1` | View service logs | Continuous |

---

## 🌐 Access Points

Once services are running:

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 📖 Full Documentation

For detailed information about each script, see `POWERSHELL_GUIDE.md`

---

## 🆘 Troubleshooting

### Setup fails?
```powershell
.\setup.ps1              # Run again
```

### Services won't start?
```powershell
.\stop.ps1               # Stop everything
.\dev.ps1                # Start again
```

### Need to see logs?
```powershell
.\logs.ps1               # View Docker logs
```

---

## ✅ Checklist

- [ ] Run `.\setup.ps1` (first time only)
- [ ] Run `.\dev.ps1` to start services
- [ ] Open http://localhost:3000 in browser
- [ ] Start coding!

---

**Status:** Setup folder ready  
**Next:** Run `.\setup.ps1` to initialize the project
