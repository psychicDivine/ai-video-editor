# AI VIDEO EDITOR - ARCHITECTURE GUIDE

**Last Updated:** December 26, 2024  
**Status:** Ready for Implementation

---

## SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│                    (React Frontend)                             │
│                   http://localhost:3000                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    HTTP/REST API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     FASTAPI BACKEND                             │
│                   http://localhost:8000                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Routes:                                                  │  │
│  │ - POST /api/upload (file upload)                        │  │
│  │ - GET /api/jobs/{job_id} (job status)                   │  │
│  │ - GET /api/download/{job_id} (download video)           │  │
│  │ - GET /health (health check)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐          ┌─────────┐         ┌─────────┐
   │PostgreSQL│          │  Redis  │         │ Celery  │
   │Database  │          │ Cache   │         │ Worker  │
   │ (Jobs)   │          │ (Queue) │         │(Process)│
   └─────────┘          └─────────┘         └─────────┘
```

---

## COMPONENT ARCHITECTURE

### Frontend (React)
```
frontend/
├── src/
│   ├── components/
│   │   ├── UploadForm.tsx          # Drag-drop video/image upload
│   │   ├── MusicUpload.tsx         # Audio file upload
│   │   ├── StyleSelector.tsx       # Style preset selector
│   │   ├── ProgressTracker.tsx     # Processing progress display
│   │   └── Header.tsx              # App header/navigation
│   ├── pages/
│   │   ├── Home.tsx                # Landing page
│   │   └── Editor.tsx              # Main editor page
│   ├── services/
│   │   ├── api.ts                  # API client (axios)
│   │   └── uploadService.ts        # File upload logic
│   ├── hooks/
│   │   ├── useUpload.ts            # Upload state management
│   │   └── useJobStatus.ts         # Job polling
│   ├── App.tsx                     # Root component
│   └── main.tsx                    # Entry point
├── Dockerfile                      # Docker image
└── vite.config.ts                  # Build config
```

**Key Libraries:**
- React 18: UI framework
- TypeScript: Type safety
- TailwindCSS: Styling
- React Query: State management
- Axios: HTTP client
- Lucide: Icons

---

### Backend (FastAPI)
```
backend/
├── app/
│   ├── main.py                     # FastAPI app initialization
│   ├── config.py                   # Configuration & environment
│   ├── models/
│   │   ├── job.py                  # Job SQLAlchemy model
│   │   └── video.py                # Video/Audio models
│   ├── schemas/
│   │   ├── job.py                  # Job Pydantic schemas
│   │   └── upload.py               # Upload schemas
│   ├── routes/
│   │   ├── upload.py               # POST /api/upload
│   │   ├── jobs.py                 # GET /api/jobs/{id}
│   │   └── download.py             # GET /api/download/{id}
│   ├── services/
│   │   ├── video_processor.py      # Main video processing
│   │   ├── beat_detector.py        # Beat detection (Librosa)
│   │   ├── ffmpeg_handler.py       # FFmpeg wrapper
│   │   ├── segment_planner.py      # Segment planning
│   │   ├── style_editor.py         # Style-based editing
│   │   └── storage.py              # File storage
│   ├── workers/
│   │   ├── celery_app.py           # Celery configuration
│   │   └── video_tasks.py          # Background tasks
│   └── utils/
│       ├── logger.py               # Logging setup
│       └── validators.py           # Input validation
├── migrations/                     # Alembic migrations
├── tests/                          # Unit & integration tests
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker image
└── .env.example                    # Environment template
```

**Key Libraries:**
- FastAPI: Web framework
- SQLAlchemy: ORM
- Pydantic: Data validation
- Celery: Task queue
- Redis: Message broker
- FFmpeg-Python: Video processing
- Librosa: Beat detection
- OpenCV: Image processing

---

## DATA FLOW

### 1. File Upload Flow
```
User Upload
    │
    ▼
Frontend: UploadForm.tsx
    │ (Multipart form data)
    ▼
Backend: POST /api/upload
    │
    ├─ Validate files
    ├─ Create Job record (status: UPLOADING)
    ├─ Save files to /uploads/{job_id}/
    ├─ Extract metadata (duration, resolution)
    └─ Queue Celery task: process_video_task(job_id)
    │
    ▼
Response: {job_id, status: "uploading"}
    │
    ▼
Frontend: Poll GET /api/jobs/{job_id}
    │ (every 2 seconds)
    ▼
Display progress to user
```

### 2. Video Processing Flow
```
Celery Worker: process_video_task(job_id)
    │
    ├─ Load videos from disk
    ├─ Load audio file
    │
    ├─ Beat Detection
    │  └─ BeatDetector.detect_beats(audio)
    │     └─ Returns: [0.5, 1.0, 1.5, 2.0, ...]
    │
    ├─ Segment Planning
    │  └─ SegmentPlanner.plan_segments(beats, num_videos, style)
    │     └─ Returns: [{start: 0, end: 7.5, transition: "crossfade"}, ...]
    │
    ├─ Video Processing
    │  ├─ Normalize video durations
    │  ├─ Resize to 1080x1920
    │  └─ Add transitions between clips
    │
    ├─ Style Application
    │  └─ StyleEditor.apply_style(video, style)
    │     └─ Apply color tone, saturation, etc.
    │
    ├─ Audio Mixing
    │  └─ Mix audio with video
    │
    ├─ Export MP4
    │  └─ H.264 codec, AAC audio
    │
    └─ Update Job (status: COMPLETED, output_video_path: "/uploads/{job_id}/output.mp4")
```

### 3. Download Flow
```
User clicks Download
    │
    ▼
Frontend: GET /api/download/{job_id}
    │
    ▼
Backend: Check job status (must be COMPLETED)
    │
    ├─ If COMPLETED:
    │  └─ Return file as attachment
    │
    └─ If NOT COMPLETED:
       └─ Return 400 error
```

---

## DATABASE SCHEMA

### Job Table
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    status VARCHAR(20),  -- PENDING, UPLOADING, PROCESSING, COMPLETED, FAILED
    style VARCHAR(50),   -- CINEMATIC_DRAMA, ENERGETIC_DANCE, etc.
    progress INTEGER,    -- 0-100
    current_step VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    output_video_path VARCHAR(255)
);
```

### Video Table
```sql
CREATE TABLE videos (
    id UUID PRIMARY KEY,
    job_id UUID FOREIGN KEY,
    file_path VARCHAR(255),
    file_name VARCHAR(255),
    file_size INTEGER,
    duration FLOAT,
    width INTEGER,
    height INTEGER,
    file_type VARCHAR(10),  -- 'video' or 'image'
    created_at TIMESTAMP
);
```

### Audio Table
```sql
CREATE TABLE audios (
    id UUID PRIMARY KEY,
    job_id UUID FOREIGN KEY,
    file_path VARCHAR(255),
    file_name VARCHAR(255),
    file_size INTEGER,
    duration FLOAT,
    created_at TIMESTAMP
);
```

---

## API ENDPOINTS

### Upload Endpoint
```
POST /api/upload

Request:
  Content-Type: multipart/form-data
  
  videos: [File, File, ...]  (max 5 files, 100MB each)
  music: File                (mp3, wav, m4a)
  style: "CINEMATIC_DRAMA"   (enum)
  duration: 30               (optional, default 30)
  aspect_ratio: "9:16"       (optional, default 9:16)

Response (200):
  {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "uploading",
    "message": "Files uploaded successfully"
  }

Error (400):
  {
    "detail": "Invalid file type. Allowed: mp4, mov, avi"
  }
```

### Job Status Endpoint
```
GET /api/jobs/{job_id}

Response (200):
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "PROCESSING",
    "progress": 45,
    "current_step": "Adding transitions...",
    "created_at": "2024-12-26T10:00:00Z",
    "updated_at": "2024-12-26T10:05:00Z",
    "error_message": null,
    "output_video_url": null
  }

Error (404):
  {
    "detail": "Job not found"
  }
```

### Download Endpoint
```
GET /api/download/{job_id}

Response (200):
  [Binary video file]
  Content-Type: video/mp4
  Content-Disposition: attachment; filename="output.mp4"

Error (400):
  {
    "detail": "Job not completed yet"
  }

Error (404):
  {
    "detail": "Job not found"
  }
```

### Health Check
```
GET /health

Response (200):
  {
    "status": "ok"
  }
```

---

## PROCESSING PIPELINE

### Video Processing Steps

```
Step 1: Load Files
  ├─ Read video files from disk
  ├─ Read audio file
  └─ Extract metadata (duration, resolution, fps)

Step 2: Normalize Durations
  ├─ Calculate target duration per video: 30 / num_videos
  ├─ For each video:
  │  ├─ If duration < target: stretch (slow motion)
  │  └─ If duration > target: crop (speed up)
  └─ Result: All videos same duration

Step 3: Resize Videos
  ├─ Target resolution: 1080x1920 (9:16 aspect ratio)
  ├─ For each video:
  │  ├─ Calculate scaling factor
  │  ├─ Resize maintaining aspect ratio
  │  └─ Add letterbox/pillarbox if needed
  └─ Result: All videos 1080x1920

Step 4: Detect Beats
  ├─ Load audio file
  ├─ Use Librosa to detect beat times
  └─ Result: [0.5, 1.0, 1.5, 2.0, ...]

Step 5: Plan Segments
  ├─ Divide 30 seconds into N segments
  ├─ Snap segment boundaries to beat times
  ├─ Assign transition types based on style
  └─ Result: [{start: 0, end: 7.5, transition: "crossfade"}, ...]

Step 6: Add Transitions
  ├─ For each pair of adjacent videos:
  │  ├─ If transition_type == "hard_cut": concatenate directly
  │  └─ If transition_type == "crossfade": use xfade filter
  └─ Result: Videos with smooth transitions

Step 7: Apply Style
  ├─ Apply color tone (warm/cool/neutral)
  ├─ Adjust saturation
  ├─ Apply contrast
  └─ Result: Style-matched video

Step 8: Mix Audio
  ├─ Sync audio to video duration
  ├─ Adjust audio levels
  └─ Result: Video with audio

Step 9: Export MP4
  ├─ Encode with H.264 codec
  ├─ Use AAC audio codec
  ├─ Set bitrate: 5-8 Mbps
  └─ Result: Final output.mp4

Step 10: Update Job
  ├─ Set status: COMPLETED
  ├─ Set output_video_path
  └─ Set completed_at timestamp
```

---

## PERFORMANCE CONSIDERATIONS

### Video Processing Time
```
Target: <2 minutes for 30-second video

Breakdown:
├─ Load files: 5 seconds
├─ Normalize durations: 15 seconds
├─ Resize videos: 20 seconds
├─ Beat detection: 10 seconds
├─ Segment planning: 5 seconds
├─ Add transitions: 20 seconds
├─ Apply style: 10 seconds
├─ Mix audio: 10 seconds
├─ Export MP4: 30 seconds
└─ Total: ~125 seconds (2 minutes)
```

### Memory Usage
```
Target: <500MB

Breakdown:
├─ Python process: 100MB
├─ Video in memory: 200MB (1080x1920 @ 30fps)
├─ Audio in memory: 50MB
├─ FFmpeg process: 100MB
└─ Total: ~450MB
```

### Optimization Strategies
1. **Stream Processing:** Don't load entire videos into memory
2. **Parallel Processing:** Process multiple videos in parallel
3. **Caching:** Cache beat detection results
4. **Compression:** Use fast FFmpeg preset
5. **Async I/O:** Use async file operations

---

## SECURITY CONSIDERATIONS

### File Upload Security
- ✅ Validate file types (whitelist only allowed formats)
- ✅ Validate file sizes (max 100MB per file)
- ✅ Scan for malware (optional: use ClamAV)
- ✅ Store files outside web root
- ✅ Use unique filenames (UUID-based)

### API Security
- ✅ CORS configured (allow only frontend origin)
- ✅ Rate limiting on upload endpoint
- ✅ Input validation (Pydantic schemas)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS prevention (React escaping)

### Data Security
- ✅ Encrypt sensitive data in database
- ✅ Use HTTPS in production
- ✅ Secure environment variables (.env)
- ✅ Database backups
- ✅ File cleanup after download (optional)

---

## SCALABILITY

### Horizontal Scaling
```
Current (Single Server):
├─ 1 Frontend
├─ 1 Backend
├─ 1 Celery Worker
├─ 1 PostgreSQL
└─ 1 Redis

Scaled (Multiple Servers):
├─ Load Balancer (Nginx)
├─ Multiple Frontends (CDN)
├─ Multiple Backends (Kubernetes)
├─ Multiple Celery Workers
├─ PostgreSQL Cluster
└─ Redis Cluster
```

### Database Optimization
- Add indexes on frequently queried columns
- Implement connection pooling
- Archive old jobs
- Partition large tables

### Caching Strategy
- Cache beat detection results
- Cache segment plans
- Cache style rules
- Use Redis for session storage

---

## MONITORING & LOGGING

### Metrics to Track
```
Application Metrics:
├─ Request latency (p50, p95, p99)
├─ Error rate
├─ Video processing time
├─ File upload size
├─ Job success rate

System Metrics:
├─ CPU usage
├─ Memory usage
├─ Disk usage
├─ Network I/O
└─ Database connections
```

### Logging Strategy
```
Log Levels:
├─ DEBUG: Detailed information for debugging
├─ INFO: General informational messages
├─ WARNING: Warning messages
├─ ERROR: Error messages
└─ CRITICAL: Critical errors

Log Locations:
├─ Application logs: /var/log/app/
├─ FFmpeg logs: /var/log/ffmpeg/
├─ Database logs: /var/log/postgres/
└─ Celery logs: /var/log/celery/
```

---

## DEPLOYMENT ARCHITECTURE

### Development
```
Local Machine
├─ Docker Desktop
├─ docker-compose.yml
└─ All services in containers
```

### Staging
```
AWS EC2 Instance
├─ Docker containers
├─ RDS PostgreSQL
├─ ElastiCache Redis
└─ S3 for file storage
```

### Production
```
AWS ECS Cluster
├─ Multiple container instances
├─ Load balancer (ALB)
├─ RDS PostgreSQL (Multi-AZ)
├─ ElastiCache Redis (Cluster mode)
├─ S3 for file storage
├─ CloudFront CDN
└─ CloudWatch monitoring
```

---

**Document Version:** 1.0  
**Created:** December 26, 2024  
**Status:** Ready for Implementation
