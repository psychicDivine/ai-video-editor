# Docker Quick Start

**Get databases running in 30 seconds**

---

## 🚀 One Command

```powershell
cd c:\Office\editor\docker
.\start-databases.ps1
```

Done! PostgreSQL and Redis are running.

---

## 📋 Connection Details

**PostgreSQL:**
- Host: `localhost`
- Port: `5432`
- Database: `ai_video_editor`
- User: `editor`
- Password: `editor_pass`

**Redis:**
- Host: `localhost`
- Port: `6379`

---

## 🔌 Update Backend

Edit `backend/.env`:
```
DATABASE_URL=postgresql://editor:editor_pass@localhost:5432/ai_video_editor
REDIS_URL=redis://localhost:6379/0
```

---

## 🛑 Stop Databases

```powershell
cd c:\Office\editor\docker
.\stop-databases.ps1
```

---

## 📖 Full Documentation

See `README.md` for complete setup guide.
