# Starting Celery & Redis - Complete Guide

**Get the async processing system running**

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start Redis
```powershell
redis-server
```
**Expected output:** `Ready to accept connections`

### Step 2: Start Celery Worker (New Terminal)
```powershell
cd c:\Office\editor\backend
.\venv\Scripts\activate
celery -A app.celery_app worker --loglevel=info
```
**Expected output:** `celery@HOSTNAME ready to accept tasks`

### Step 3: Services Already Running
- ✅ Backend: http://localhost:8000 (Uvicorn)
- ✅ Frontend: http://localhost:3000 (Vite)
- ✅ Redis: localhost:6379
- ✅ Celery: Connected to Redis

---

## 📋 Complete Setup Checklist

- [ ] Redis running (Step 1)
- [ ] Celery worker running (Step 2)
- [ ] Backend running (http://localhost:8000)
- [ ] Frontend running (http://localhost:3000)

---

## 🧪 Test the System

1. Open http://localhost:3000 in browser
2. Upload 2-3 video clips
3. Upload a music track (3+ minutes)
4. Select a 30-second segment using the timeline
5. Choose a style
6. Click "Create Video"
7. Watch progress tracker update in real-time
8. Download finished video

---

## 🔍 Monitoring

### View Celery Tasks
```powershell
# In Celery worker terminal, you'll see:
# [tasks]
#   . app.tasks.video_tasks.process_video_task
#   . app.tasks.video_tasks.cleanup_old_jobs
```

### View Redis
```powershell
redis-cli
> KEYS *
> GET job_id_here
```

### View Backend Logs
```powershell
# In backend terminal, you'll see:
# INFO:app.main:Starting AI Video Editor API
# INFO:app.services.beat_detector:Detected X beats at Y BPM
```

---

## ⚠️ Troubleshooting

### Redis won't start
```powershell
# Check if Redis is installed
redis-cli --version

# If not installed, use Chocolatey:
choco install redis
```

### Celery won't connect
```powershell
# Make sure Redis is running first
redis-cli ping
# Should return: PONG

# Then start Celery
celery -A app.celery_app worker --loglevel=info
```

### Tasks not processing
```powershell
# Check Redis connection
redis-cli
> PING
# Should return: PONG

# Check Celery worker is running
# Should see: "celery@HOSTNAME ready to accept tasks"
```

### Video processing fails
```powershell
# Check FFmpeg is installed
ffmpeg -version

# Check Librosa is installed
cd backend
.\venv\Scripts\python -c "import librosa; print(librosa.__version__)"
```

---

## 📊 System Architecture

```
Frontend (React)
    ↓ (upload + music times)
FastAPI Upload Endpoint
    ↓ (save files, trigger task)
Redis Queue
    ↓ (async task)
Celery Worker
    ↓ (process_video_task)
Beat Detector (Librosa)
    ↓ (detect beats, find cuts)
FFmpeg Handler
    ↓ (concatenate, transition, mix, render)
Output Video
    ↓ (download link)
Frontend
```

---

## 🎯 Expected Workflow

1. **User uploads** → Files saved to disk
2. **Celery task triggered** → Job queued in Redis
3. **Worker picks up task** → Processing starts
4. **Progress updates** → Frontend polls job status
5. **Video rendered** → Download link appears
6. **User downloads** → Complete!

---

## 💡 Pro Tips

1. **Monitor progress** - Frontend shows real-time updates
2. **Check logs** - Celery worker shows detailed progress
3. **Use Redis CLI** - Debug job status if needed
4. **Keep terminals open** - Redis, Celery, Backend, Frontend

---

## 🚨 Important Notes

- **Redis must run first** - Celery depends on it
- **Celery worker must be running** - Tasks won't process without it
- **Backend must be running** - API endpoints needed
- **Frontend must be running** - UI for uploads

---

**Status:** Ready to test end-to-end!  
**Next:** Follow the 3 steps above and test the system
