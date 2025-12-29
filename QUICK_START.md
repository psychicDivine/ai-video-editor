# QUICK START - AI VIDEO EDITOR

**Get started in 5 minutes**

---

## 1️⃣ INSTALL DEPENDENCIES

### Backend (UV - Modern Python Package Manager)
```bash
cd backend

# Install UV if you don't have it
pip install uv

# Install all dependencies (including dev tools)
uv pip install -e ".[dev]"

# Or just production dependencies
uv pip install -e .
```

### Frontend (Node.js)
```bash
cd frontend

# Install dependencies
npm install

# Alternative package managers (faster):
pnpm install    # if you have pnpm
bun install     # if you have bun
```

---

## 2️⃣ START DEVELOPMENT

### Option A: Docker Compose (Recommended)
```bash
# From project root
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Option B: Local Development
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Celery Worker (optional)
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

---

## 3️⃣ VERIFY SETUP

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend
open http://localhost:3000

# API Documentation
open http://localhost:8000/docs
```

---

## 4️⃣ NEXT STEPS

1. Read `SETUP_COMPLETE.md` for detailed information
2. Follow `IMPLEMENTATION_GUIDE.md` to start building
3. Reference `PROJECT_TICKETS.md` for detailed requirements
4. Check `ARCHITECTURE.md` for system design

---

## 🛠️ WHAT'S INSTALLED

### Backend
- FastAPI (web framework)
- SQLAlchemy (database ORM)
- Celery (task queue)
- Redis (cache/broker)
- PostgreSQL (database)
- FFmpeg (video processing)
- Librosa (beat detection)
- OpenCV (image processing)
- Pytest (testing)
- Black, Ruff, MyPy (code quality)

### Frontend
- React 18 (UI framework)
- TypeScript (type safety)
- Vite (build tool)
- TailwindCSS (styling)
- React Query (state management)
- Vitest (testing)
- ESLint, Prettier (code quality)

### DevOps
- Docker (containerization)
- Docker Compose (orchestration)
- PostgreSQL 15 (database)
- Redis 7 (cache)

---

## 📊 PROJECT STATUS

✅ Project structure created  
✅ VS Code configuration ready  
✅ Docker setup complete  
✅ Dependencies configured  
✅ Modern tooling (UV + Vite)  
⏳ Ready for implementation

---

**Next:** Run `docker-compose up -d` and start building!
