# Docker Setup - Redis & PostgreSQL

**Complete database infrastructure for AI Video Editor**

---

## 📁 Folder Structure

```
docker/
├── docker-compose.yml          # Services definition
├── start-databases.ps1         # One-click startup script
├── stop-databases.ps1          # Stop all services
├── README.md                   # This file
└── .env.example                # Environment variables template
```

---

## 🚀 Quick Start

### Option 1: PowerShell Script (Recommended)
```powershell
cd c:\Office\editor\docker
.\start-databases.ps1
```

### Option 2: Manual Command
```powershell
cd c:\Office\editor\docker
podman-compose -f docker-compose.yml up -d
```

---

## ✅ What Gets Started

- **PostgreSQL 15** (Port 5432)
  - Database: `ai_video_editor`
  - User: `editor`
  - Password: `editor_pass`

- **Redis 7** (Port 6379)
  - Cache & Message Broker
  - Data persistence enabled

---

## 🔗 Connection Details

### PostgreSQL
```
Host:     localhost
Port:     5432
Database: ai_video_editor
User:     editor
Password: editor_pass
```

### Redis
```
Host:     localhost
Port:     6379
Database: 0
```

---

## 🔌 Connect DBeaver

1. **Open DBeaver**
2. **New Database Connection** → PostgreSQL
3. **Fill in:**
   - Server Host: `localhost`
   - Port: `5432`
   - Database: `ai_video_editor`
   - Username: `editor`
   - Password: `editor_pass`
4. **Test Connection** → Should show "Connected"
5. **Finish**

---

## 🔌 Connect Backend

Update `backend/.env`:
```
DATABASE_URL=postgresql://editor:editor_pass@localhost:5432/ai_video_editor
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
```

Or update `backend/app/config.py`:
```python
database_url: str = "postgresql://editor:editor_pass@localhost:5432/ai_video_editor"
redis_url: str = "redis://localhost:6379/0"
```

---

## 📊 Check Status

```powershell
cd c:\Office\editor\docker
podman-compose -f docker-compose.yml ps
```

**Expected output:**
```
CONTAINER ID  IMAGE              COMMAND           CREATED        STATUS
xxxxx         postgres:15-alpine postgres          2 minutes ago  Up 2 minutes
xxxxx         redis:7-alpine     redis-server      2 minutes ago  Up 2 minutes
```

---

## 🧪 Test Connections

### Test PostgreSQL
```powershell
# Using psql
psql -h localhost -U editor -d ai_video_editor -c "SELECT version();"

# Or using Python
python -c "import psycopg2; conn = psycopg2.connect('dbname=ai_video_editor user=editor password=editor_pass host=localhost'); print('Connected!')"
```

### Test Redis
```powershell
# Using redis-cli
redis-cli -h localhost ping
# Should return: PONG

# Or using Python
python -c "import redis; r = redis.Redis(host='localhost', port=6379); print(r.ping())"
```

---

## 🛑 Stop Services

```powershell
cd c:\Office\editor\docker
podman-compose -f docker-compose.yml down
```

---

## 🗑️ Clean Everything

```powershell
cd c:\Office\editor\docker
# Stop and remove containers + volumes
podman-compose -f docker-compose.yml down -v
```

---

## 📋 Troubleshooting

### Podman not installed
```powershell
# Install via Chocolatey
choco install podman-desktop

# Or download from
https://podman.io/
```

### Podman machine won't start
```powershell
podman machine list
podman machine stop
podman machine start
```

### Services won't start
```powershell
# Check logs
podman-compose -f docker-compose.yml logs postgres
podman-compose -f docker-compose.yml logs redis

# Rebuild
podman-compose -f docker-compose.yml up -d --build
```

### Port already in use
```powershell
# Check what's using port 5432
netstat -ano | findstr :5432

# Kill process (if needed)
taskkill /PID <PID> /F
```

### Can't connect to database
```powershell
# Verify containers are running
podman ps

# Check container logs
podman logs ai_video_editor_postgres
podman logs ai_video_editor_redis

# Verify ports are exposed
podman port ai_video_editor_postgres
podman port ai_video_editor_redis
```

---

## 💾 Data Persistence

- PostgreSQL data: `postgres_data` volume
- Redis data: `redis_data` volume
- Data persists after stopping containers
- Data only removed with `down -v` command

---

## 🔐 Security Notes

**⚠️ Development Only:**
- Default credentials are for development
- Change passwords for production
- Don't expose ports publicly
- Use strong secrets in production

---

## 📚 Related Files

- `backend/.env` - Backend configuration
- `backend/app/config.py` - Backend settings
- `docker-compose.yml` - Service definitions
- `start-databases.ps1` - Startup script

---

## 🎯 Complete Setup Checklist

- [ ] Podman installed
- [ ] Podman machine started
- [ ] Services running (postgres + redis)
- [ ] PostgreSQL accessible on localhost:5432
- [ ] Redis accessible on localhost:6379
- [ ] DBeaver connected (optional)
- [ ] Backend .env updated
- [ ] Backend can connect to databases

---

## 🚀 Next Steps

1. Run: `.\start-databases.ps1`
2. Update `backend/.env`
3. Restart backend
4. Start Celery worker
5. Test complete system

---

**Status:** Ready to deploy!
