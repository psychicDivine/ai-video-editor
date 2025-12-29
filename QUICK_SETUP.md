# Quick Setup - AI Video Editor

**Get running in 5 minutes**

---

## 🚀 Fastest Path: PowerShell Scripts

```powershell
cd c:\Office\editor\setup
.\setup.ps1
```

Wait ~10 minutes for dependencies to install, then:

```powershell
.\dev.ps1
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🐳 Alternative: Podman Desktop + Windsurf

**Prerequisites:**
- Podman Desktop installed
- Windsurf open with project

**Steps:**
1. Start Podman Desktop
2. In Windsurf, open integrated terminal
3. Run:
   ```powershell
   podman-compose -f docker-compose.yml up -d
   ```
4. Access services at localhost:3000 and localhost:8000

---

## 📝 What Each Approach Does

| Approach | Setup Time | Complexity | Best For |
|----------|-----------|-----------|----------|
| PowerShell Scripts | ~10 min | Simple | Quick local dev |
| Podman Desktop | ~5 min | Medium | Container isolation |
| Dev Container | ~15 min | Complex | Team consistency |

---

## ✅ Choose One and Start

**Recommended: PowerShell Scripts**
```powershell
cd c:\Office\editor\setup
.\setup.ps1
.\dev.ps1
```

Then proceed to PHASE 2 (Frontend UI development).

---

**Status:** Ready to build  
**Next:** Run setup and start coding!
