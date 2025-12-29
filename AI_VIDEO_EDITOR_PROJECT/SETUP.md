# AI VIDEO EDITOR - SETUP GUIDE

**Last Updated:** December 26, 2024  
**Status:** Ready for Implementation

---

## PREREQUISITES

### System Requirements
- **OS:** Windows, macOS, or Linux
- **RAM:** 8GB minimum (16GB recommended)
- **Disk Space:** 20GB free (for videos and processing)
- **CPU:** 4 cores minimum (8+ recommended)

### Software Requirements
- **Docker:** 20.10+ ([Download](https://www.docker.com/products/docker-desktop))
- **Docker Compose:** 2.0+ (included with Docker Desktop)
- **Git:** 2.30+ ([Download](https://git-scm.com/))
- **Node.js:** 18+ ([Download](https://nodejs.org/))
- **Python:** 3.11+ ([Download](https://www.python.org/))

### Verify Installation
```bash
# Check Docker
docker --version
docker-compose --version

# Check Node.js
node --version
npm --version

# Check Python
python --version
```

---

## QUICK START (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ai-video-editor.git
cd ai-video-editor
```

### 2. Start Services
```bash
docker-compose up -d
```

### 3. Wait for Services to Start
```bash
# Check status
docker-compose ps

# Expected output:
# NAME                COMMAND                  STATUS
# postgres            "docker-entrypoint.s…"   Up 2 minutes
# redis               "redis-server"           Up 2 minutes
# backend             "uvicorn app.main:app"   Up 1 minute
# frontend            "npm run dev"            Up 1 minute
```

### 4. Access Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### 5. Test Upload
1. Go to http://localhost:3000
2. Upload 2-3 videos/images
3. Upload music file
4. Select style
5. Click "Generate Video"
6. Wait for processing
7. Download result

---

## DETAILED SETUP

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/ai-video-editor.git
cd ai-video-editor
```

### Step 2: Configure Environment

#### Backend Configuration
```bash
# Copy example env file
cp backend/.env.example backend/.env

# Edit backend/.env
# Set these variables:
DATABASE_URL=postgresql://editor:editor_pass@postgres:5432/ai_video_editor
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-here-change-in-production
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=104857600
ALLOWED_VIDEO_FORMATS=mp4,mov,avi
ALLOWED_AUDIO_FORMATS=mp3,wav,m4a
```

#### Frontend Configuration
```bash
# Copy example env file
cp frontend/.env.example frontend/.env

# Edit frontend/.env
VITE_API_URL=http://localhost:8000
```

### Step 3: Build Docker Images
```bash
# Build all images
docker-compose build

# Expected output:
# Building postgres
# Building redis
# Building backend
# Building frontend
# Successfully built ...
```

### Step 4: Start Services
```bash
# Start in background
docker-compose up -d

# Or start in foreground (for debugging)
docker-compose up

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Step 5: Initialize Database
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create tables
docker-compose exec backend python -c "from app.models import *; from app.config import engine; Base.metadata.create_all(bind=engine)"
```

### Step 6: Verify Setup
```bash
# Test backend health
curl http://localhost:8000/health

# Expected response:
# {"status":"ok"}

# Test frontend
curl http://localhost:3000

# Expected: HTML response
```

---

## LOCAL DEVELOPMENT (Without Docker)

### Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://editor:editor_pass@localhost:5432/ai_video_editor
export REDIS_URL=redis://localhost:6379/0

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Expected output:
# VITE v4.4.9  ready in 123 ms
# ➜  Local:   http://localhost:3000/
```

### Database Setup (PostgreSQL)
```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql
# Windows: Download from https://www.postgresql.org/download/windows/

# Start PostgreSQL service
# macOS: brew services start postgresql
# Ubuntu: sudo systemctl start postgresql
# Windows: Start PostgreSQL service

# Create database
createdb ai_video_editor

# Create user
createuser editor -P
# Password: editor_pass

# Grant privileges
psql -U postgres -d ai_video_editor -c "GRANT ALL PRIVILEGES ON DATABASE ai_video_editor TO editor;"
```

### Redis Setup
```bash
# Install Redis
# macOS: brew install redis
# Ubuntu: sudo apt-get install redis-server
# Windows: Download from https://github.com/microsoftarchive/redis/releases

# Start Redis
# macOS: brew services start redis
# Ubuntu: sudo systemctl start redis-server
# Windows: redis-server.exe
```

### Celery Worker Setup
```bash
# In backend directory with venv activated
celery -A app.workers.celery_app worker --loglevel=info
```

---

## TROUBLESHOOTING

### Docker Issues

#### "docker-compose: command not found"
```bash
# Install Docker Compose
# macOS/Windows: Included with Docker Desktop
# Linux: sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
# sudo chmod +x /usr/local/bin/docker-compose
```

#### "Cannot connect to Docker daemon"
```bash
# Start Docker Desktop (macOS/Windows)
# Or start Docker service (Linux)
sudo systemctl start docker
```

#### "Port 5432 already in use"
```bash
# Change port in docker-compose.yml
# Change: "5432:5432"
# To: "5433:5432"
# Then update DATABASE_URL
```

### Backend Issues

#### "ModuleNotFoundError: No module named 'app'"
```bash
# Make sure you're in backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt
```

#### "psycopg2 error"
```bash
# Install system dependencies
# Ubuntu: sudo apt-get install libpq-dev
# macOS: brew install libpq

# Reinstall psycopg2
pip install --force-reinstall psycopg2-binary
```

#### "FFmpeg not found"
```bash
# Install FFmpeg
# macOS: brew install ffmpeg
# Ubuntu: sudo apt-get install ffmpeg
# Windows: Download from https://ffmpeg.org/download.html
```

### Frontend Issues

#### "npm: command not found"
```bash
# Install Node.js from https://nodejs.org/
# Verify installation
node --version
npm --version
```

#### "Port 3000 already in use"
```bash
# Change port in vite.config.ts
# Or kill process using port 3000
# macOS/Linux: lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9
# Windows: netstat -ano | findstr :3000
```

#### "CORS error"
```bash
# Make sure backend CORS is configured
# In backend/app/main.py:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Database Issues

#### "Connection refused"
```bash
# Check PostgreSQL is running
# macOS: brew services list | grep postgresql
# Ubuntu: sudo systemctl status postgresql
# Windows: Check Services in Control Panel

# Check connection string
# Should be: postgresql://editor:editor_pass@localhost:5432/ai_video_editor
```

#### "Database does not exist"
```bash
# Create database
createdb ai_video_editor

# Or via psql
psql -U postgres
CREATE DATABASE ai_video_editor;
```

---

## ENVIRONMENT VARIABLES

### Backend (.env)

```
# Database
DATABASE_URL=postgresql://editor:editor_pass@postgres:5432/ai_video_editor

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-here

# File Upload
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=104857600  # 100MB

# Allowed Formats
ALLOWED_VIDEO_FORMATS=mp4,mov,avi
ALLOWED_AUDIO_FORMATS=mp3,wav,m4a

# Processing
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Logging
LOG_LEVEL=INFO

# Optional: Gemini API (for advanced features)
GEMINI_API_KEY=your-api-key-here
```

### Frontend (.env)

```
# API Configuration
VITE_API_URL=http://localhost:8000

# Optional: Analytics
VITE_ANALYTICS_ID=your-analytics-id
```

---

## VERIFICATION CHECKLIST

After setup, verify everything works:

```bash
# 1. Check all services running
docker-compose ps

# 2. Test backend health
curl http://localhost:8000/health

# 3. Test database connection
docker-compose exec backend python -c "from app.config import engine; engine.connect(); print('DB OK')"

# 4. Test Redis connection
docker-compose exec redis redis-cli ping

# 5. Test frontend loads
curl http://localhost:3000

# 6. Check logs for errors
docker-compose logs --tail=50

# 7. Test file upload endpoint
curl -X POST http://localhost:8000/api/upload \
  -F "videos=@test.mp4" \
  -F "music=@test.mp3" \
  -F "style=CINEMATIC_DRAMA"
```

---

## NEXT STEPS

1. ✅ Setup complete
2. 📖 Read [ARCHITECTURE.md](./ARCHITECTURE.md) to understand system design
3. 🚀 Read [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment
4. 📚 Read [API.md](./API.md) for API documentation
5. 🧪 Run tests: `docker-compose exec backend pytest`

---

**Need Help?**
- Check logs: `docker-compose logs -f`
- Restart services: `docker-compose restart`
- Reset everything: `docker-compose down -v && docker-compose up -d`
