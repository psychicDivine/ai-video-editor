# AI VIDEO EDITOR - DETAILED PROJECT TICKETS

**Total Tickets:** 28  
**Estimated Hours:** 56 hours (8 hours/day × 7 days)  
**Status:** Ready for Implementation

---

## **Daily Progress Summary — 2025-12-30**

- **Today (wrap-up):** Implemented transition plumbing (FFmpeg xfade wiring + audio acrossfade), added TransitionService and frei0r support, MLT exporter, frontend selectors, and a test harness. Ran the test harness; pipeline produced `output.mp4` but FFmpeg xfade step initially failed due to a malformed `filter_complex` (video/audio sections not properly separated).
- **Current blocker:** FFmpeg `xfade` run failed with "Trailing garbage after a filter" parsing error caused by missing separator between video and audio filter graphs. I patched `FFmpegHandler.concatenate_with_transitions` to insert the semicolon separator, clamp transition duration, and log the full `filter_complex`. Next step is to re-run the harness and confirm xfade succeeds across real segments.
- **What to resume next:** From code: re-run `python test_video_flow.py` (capture to `test_run2.log`), inspect the tail of `test_run2.log` for ffmpeg stderr. If xfade still fails, enforce per-input `-vf scale,fps,pix_fmt` when building filter graph or create a minimal reproducer in `backend/tmp_test` to isolate ffmpeg args.
- **Artifacts / quick references:** test outputs are in `backend/test_output/test_job_real_assets` (see `output.mp4`), working example clips in `backend/tmp_test` (contains `blue.mp4`, `red.mp4`, `test_transition.mp4`, `test_project.mlt`). The main handler is `backend/app/services/ffmpeg_handler.py` and pipeline orchestrator is `backend/app/services/video_processor.py`.
- **Status:** Partial success — end-to-end flow produces `output.mp4`; video-level xfade currently falls back to simple concat but MLT export and audio mixing complete. Manual inspection of `backend/tmp_test/test_transition.mp4` shows transitions work in the simpler reproducer.
- **Owner / notes:** Continue from logs and re-run; expected quick fix and verification (estimated 30–90 minutes). I'll keep `PROJECT_TICKETS.md` top section updated daily with the latest blocker/progress.


## ⏩ Next Steps (Pre-AI, Finalize MVP) — Status & Progress

| Task                                                      | Status        | Last Update      | Comments                                  |
|-----------------------------------------------------------|---------------|------------------|--------------------------------------------|
| Polish UI/UX (progress bar, error messages, mobile)       | In Progress   | 2025-12-29       | Theme toggle, modern minimalist started; progress bar & error UI improved |
| Add robust error handling (backend + frontend)            | In Progress   | 2025-12-29       | Backend standardized error handlers added; frontend upload parsing improved |
| Add integration/unit tests (upload → process → download)  | Not Started   |                  | To be added after UI polish                |
| Finalize documentation (README, SETUP, API)               | Not Started   |                  | Will update after code/test stabilization  |
| Docker build/test for full stack                          | Not Started   |                  | To be done before final QA                 |
| Final manual QA: upload, process, download, cleanup       | Pending       |                  | Will be performed by user                  |

**Progress:**  
`[■■■■■□□□□□] 50% Complete`  
(3/6 tasks started or in progress)

**Progress Graph (quick view):**
```
UI/UX       [■■■■■□□□□□] 50%
Error Hndlg  [■■■□□□□□□□] 30%
Tests       [■■■■■□□□□□] 50%
Docs        [■■■□□□□□□□] 30%
Docker      [■■■□□□□□□□] 30%
QA          [□□□□□□□□□□] 0%
```

---

## **Sprint 1 (2025-12-29 → 2026-01-05)**

Goal: Finish UI polish, complete backend hardening, broaden tests, and get Docker build/tests running so we can perform final QA.

| Ticket ID | Task | Owner | Est. Hours | Status | Notes |
|-----------|------|-------:|-----------:|--------| -------|
| S1-1 | Finish UI polish (progress bar, error UI, mobile) | frontend | 8h | In Progress | Accessibility checks + responsive tweaks applied |
| S1-2 | Backend error handling & structured logging | backend | 6h | In Progress | Centralized FastAPI handlers added; Sentry optional integration planned |
| S1-3 | Extend tests (failure cases, edge conditions) | backend | 8h | In Progress | Integration test for upload→process added; add file-size/style failure tests |
| S1-4 | Dockerize & CI smoke tests (postgres, redis, backend, frontend) | devops | 12h | In Progress | Add docker build/test; verify podman compatibility |
| S1-5 | Finalize docs (README, SETUP, API) | docs | 6h | In Progress | Add run/test steps, vscode tips, and troubleshooting guides |

**Acceptance Criteria (Sprint 1):**
- UI responsive on mobile and desktop; progress and error messaging clear and actionable.
- Backend returns structured error payloads and logs exceptions; tests cover happy/failure flows.
- Docker compose (or Podman) builds backend+frontend and services for smoke tests.
- README and SETUP updated with clear start/test steps.

---

**Timeline:**
```
2025-12-28 | Polish UI/UX started
2025-12-29 | Sprint 1 kickoff; UI & error handling work started
2025-12-30 | Integration tests expanded; backend logging added
2025-12-31 | Docker build/test verification (podman/docker)
2026-01-03 | Docs updated; pre-QA checklist prepared
2026-01-05 | Sprint 1 demo and handoff to QA
```

---

## PHASE 1: PROJECT SETUP (Day 1 - 4 hours)

### TICKET 1.1: Initialize Git Repo & Folder Structure
```
ID: TICKET-1.1
Title: Initialize Git Repo & Folder Structure
Priority: CRITICAL
Time Estimate: 30 minutes
Status: PENDING

Description:
Create project directory with all folders and initialize git repository.

Subtasks:
  [ ] Create ai-video-editor/ root folder
  [ ] Create frontend/, backend/, docs/ subdirectories
  [ ] Initialize git repo (git init)
  [ ] Create .gitignore file
  [ ] Create README.md with project overview
  [ ] Create SETUP.md with setup instructions
  [ ] Create initial commit

Acceptance Criteria:
  ✓ All folders created as per PROJECT_STRUCTURE
  ✓ Git initialized and first commit made
  ✓ .gitignore excludes: node_modules/, __pycache__/, .env, uploads/, dist/, build/
  ✓ README.md has project description and quick start
  ✓ Can run: git log and see initial commit

Dependencies: None
Blocks: All other tickets
```

### TICKET 1.2: Docker & Docker Compose Setup
```
ID: TICKET-1.2
Title: Docker & Docker Compose Setup
Priority: CRITICAL
Time Estimate: 1 hour
Status: PENDING

Description:
Create Docker and Docker Compose configuration for all services.

Files to Create:
  - docker-compose.yml
  - backend/Dockerfile
  - frontend/Dockerfile
  - backend/.dockerignore
  - frontend/.dockerignore

Docker Compose Services:
  1. postgres:15 (port 5432)
     - POSTGRES_DB: ai_video_editor
     - POSTGRES_USER: editor
     - POSTGRES_PASSWORD: editor_pass
     - Volume: postgres_data:/var/lib/postgresql/data

  2. redis:7 (port 6379)
     - No password (dev only)
     - Volume: redis_data:/data

  3. backend (port 8000)
     - Build from backend/Dockerfile
     - Depends on: postgres, redis
     - Environment: DATABASE_URL, REDIS_URL, etc.
     - Volume: ./backend:/app

  4. frontend (port 3000)
     - Build from frontend/Dockerfile
     - Depends on: backend
     - Volume: ./frontend:/app

Acceptance Criteria:
  ✓ docker-compose up builds without errors
  ✓ All 4 services start successfully
  ✓ Services can communicate (backend → postgres, redis)
  ✓ Ports accessible: 5432, 6379, 8000, 3000
  ✓ docker-compose down stops all services cleanly
  ✓ docker-compose logs shows no critical errors

Dependencies: TICKET-1.1
Blocks: TICKET-1.3, TICKET-1.4
```

### TICKET 1.3: Backend Environment Setup
```
ID: TICKET-1.3
Title: Backend Environment Setup
Priority: CRITICAL
Time Estimate: 1 hour
Status: PENDING

Description:
Configure FastAPI project structure and dependencies.

Files to Create:
  - backend/requirements.txt
  - backend/app/__init__.py
  - backend/app/main.py
  - backend/app/config.py
  - backend/.env.example
  - backend/Dockerfile

requirements.txt (Core):
  fastapi==0.104.1
  uvicorn==0.24.0
  sqlalchemy==2.0.23
  psycopg2-binary==2.9.9
  alembic==1.12.1
  celery==5.3.4
  redis==5.0.1
  ffmpeg-python==0.2.1
  librosa==0.10.0
  opencv-python==4.8.1.78
  numpy==1.24.3
  python-multipart==0.0.6
  aiofiles==23.2.1
  python-dotenv==1.0.0
  pydantic==2.4.2
  pydantic-settings==2.0.3

app/main.py:
  - FastAPI app initialization
  - CORS configuration (allow frontend)
  - Health check endpoint: GET /health
  - Database initialization
  - Celery integration

app/config.py:
  - Environment variables (DATABASE_URL, REDIS_URL, etc.)
  - Settings class with Pydantic
  - Load from .env file

.env.example:
  DATABASE_URL=postgresql://editor:editor_pass@postgres:5432/ai_video_editor
  REDIS_URL=redis://redis:6379/0
  SECRET_KEY=your-secret-key-here
  UPLOAD_DIR=/app/uploads
  MAX_FILE_SIZE=104857600
  ALLOWED_VIDEO_FORMATS=mp4,mov,avi
  ALLOWED_AUDIO_FORMATS=mp3,wav,m4a

Acceptance Criteria:
  ✓ requirements.txt complete with all dependencies
  ✓ FastAPI app runs on 8000 without errors
  ✓ GET /health returns {"status": "ok"}
  ✓ CORS configured for http://localhost:3000
  ✓ Database connection works
  ✓ .env.example has all required variables
  ✓ Dockerfile builds successfully

Dependencies: TICKET-1.2
Blocks: TICKET-3.1
```

### TICKET 1.4: Frontend Environment Setup
```
ID: TICKET-1.4
Title: Frontend Environment Setup
Priority: CRITICAL
Time Estimate: 1 hour
Status: PENDING

Description:
Initialize React + TypeScript + TailwindCSS project.

Setup Commands:
  npm create vite@latest frontend -- --template react-ts
  cd frontend
  npm install
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p
  npm install @tanstack/react-query axios lucide-react
  npm install -D @types/node

Files to Create/Modify:
  - frontend/src/App.tsx (basic structure)
  - frontend/src/main.tsx (React entry point)
  - frontend/tailwind.config.js (TailwindCSS config)
  - frontend/vite.config.ts (Vite config with API proxy)
  - frontend/.env.example
  - frontend/Dockerfile
  - frontend/package.json (scripts configured)

vite.config.ts:
  - Proxy API calls to http://localhost:8000
  - Port: 3000
  - HMR enabled for development

Acceptance Criteria:
  ✓ npm run dev works on port 3000
  ✓ React app loads without errors
  ✓ TailwindCSS classes work (test with bg-blue-500)
  ✓ Can make API calls to backend via proxy
  ✓ npm run build completes successfully
  ✓ Dockerfile builds successfully
  ✓ TypeScript compilation has no errors

Dependencies: TICKET-1.2
Blocks: TICKET-2.1
```

---

## PHASE 2: FRONTEND UI (Day 1-2 - 8 hours)

### TICKET 2.1: Upload Form Component
```
ID: TICKET-2.1
Title: Upload Form Component
Priority: HIGH
Time Estimate: 2 hours
Status: PENDING

Description:
Build drag-drop file upload UI for videos and images.

File: frontend/src/components/UploadForm.tsx

Features:
  - Drag-drop area for videos/images
  - File input fallback (click to browse)
  - Accept only: .mp4, .mov, .avi, .png, .jpg, .jpeg
  - Show selected files with thumbnails
  - Max 5 files, max 100MB each
  - Display file size and duration (for videos)
  - Remove individual files
  - Clear all files button
  - Loading state during upload

UI Elements:
  - Large drop zone with icon (Upload icon from Lucide)
  - File list with thumbnails
  - Progress bar for each file
  - Error messages for invalid files
  - Submit button (disabled until files selected)

Validation:
  - File type validation
  - File size validation (100MB max)
  - Max 5 files validation
  - Show clear error messages

Acceptance Criteria:
  ✓ Drag-drop works (files added to list)
  ✓ Click to browse works
  ✓ File validation works (rejects invalid types/sizes)
  ✓ Shows file list with thumbnails
  ✓ Shows file sizes correctly
  ✓ Beautiful UI with Lucide icons
  ✓ Responsive on mobile (tested on 375px width)
  ✓ Accessible (proper labels, ARIA attributes)

Dependencies: TICKET-1.4
Blocks: TICKET-2.3
```

### TICKET 2.2: Music Upload Component
```
ID: TICKET-2.2
Title: Music Upload Component
Priority: HIGH
Time Estimate: 1 hour
Status: PENDING

Description:
Build music file upload component.

File: frontend/src/components/MusicUpload.tsx

Features:
  - Single audio file upload (mp3, wav, m4a)
  - Show audio duration
  - Play preview button
  - File size display
  - Required field validation
  - Drag-drop support
  - Remove file button

UI Elements:
  - Drop zone for audio
  - File info (name, size, duration)
  - Play button with audio player
  - Remove button
  - Error messages

Validation:
  - File type validation (mp3, wav, m4a only)
  - File size validation (max 50MB)
  - Required field check

Acceptance Criteria:
  ✓ Audio file upload works
  ✓ Duration detection works (shows in seconds)
  ✓ Play preview works
  ✓ File size displays correctly
  ✓ Validation works (rejects invalid files)
  ✓ Beautiful UI matching UploadForm style
  ✓ Responsive on mobile

Dependencies: TICKET-1.4
Blocks: TICKET-2.3
```

### TICKET 2.3: Style Selector Component
```
ID: TICKET-2.3
Title: Style Selector Component
Priority: HIGH
Time Estimate: 1.5 hours
Status: PENDING

Description:
Build style preset selector with preview.

File: frontend/src/components/StyleSelector.tsx

Styles (4 presets):
  1. CINEMATIC_DRAMA
     - Description: "Dramatic, professional, moody"
     - Color: Cool tones (5600K)
     - Transitions: Slow dissolves (500ms)
     - Camera: Slow, deliberate
     - Icon: Film icon

  2. ENERGETIC_DANCE
     - Description: "Dynamic, energetic, fast-paced"
     - Color: Warm tones (2700K)
     - Transitions: Hard cuts (0ms)
     - Camera: Dynamic pans/zooms
     - Icon: Zap icon

  3. LUXE_TRAVEL
     - Description: "Golden hour, wanderlust, luxury"
     - Color: Warm golden (3200K)
     - Transitions: Slow dissolves (500ms+)
     - Camera: Slow tracking
     - Icon: Globe icon

  4. MODERN_MINIMAL
     - Description: "Clean, professional, minimal"
     - Color: Neutral (4500K)
     - Transitions: Subtle fades
     - Camera: Static or subtle
     - Icon: Minimize icon

UI Elements:
  - Grid of 4 style cards
  - Each card shows: name, description, icon, preview
  - Selected state (border highlight)
  - Radio button for selection
  - Smooth transitions between selections

Acceptance Criteria:
  ✓ All 4 styles display correctly
  ✓ Selection works (radio button updates)
  ✓ Selected style highlighted
  ✓ Icons display correctly
  ✓ Descriptions clear and helpful
  ✓ Responsive grid (2 columns on mobile, 4 on desktop)
  ✓ Accessible (proper labels, keyboard navigation)

Dependencies: TICKET-1.4
Blocks: TICKET-2.4
```

### TICKET 2.4: Main Editor Page
```
ID: TICKET-2.4
Title: Main Editor Page
Priority: HIGH
Time Estimate: 2 hours
Status: PENDING

Description:
Build main editor page that combines all components.

File: frontend/src/pages/Editor.tsx

Layout:
  - Header with logo and title
  - Left panel: Upload Form + Music Upload
  - Right panel: Style Selector + Options
  - Bottom: Generate button + Progress tracker

Components Used:
  - UploadForm (left)
  - MusicUpload (left)
  - StyleSelector (right)
  - ProgressTracker (bottom)
  - Header (top)

Features:
  - Form validation (all fields required)
  - Generate button (disabled until all fields filled)
  - Loading state during processing
  - Error handling and display
  - Success message with download link

Form State:
  - videos: File[]
  - music: File
  - style: StylePreset
  - options: {
      duration: 30,
      aspectRatio: "9:16"
    }

Acceptance Criteria:
  ✓ All components render correctly
  ✓ Form validation works
  ✓ Generate button disabled until ready
  ✓ Can submit form to backend
  ✓ Responsive layout (mobile-first)
  ✓ Beautiful, professional UI
  ✓ Accessible (proper semantic HTML)

Dependencies: TICKET-2.1, TICKET-2.2, TICKET-2.3
Blocks: TICKET-3.1
```

### TICKET 2.5: Progress Tracker Component
```
ID: TICKET-2.5
Title: Progress Tracker Component
Priority: MEDIUM
Time Estimate: 1 hour
Status: PENDING

Description:
Build progress tracking UI for video processing.

File: frontend/src/components/ProgressTracker.tsx

Features:
  - Show processing status (uploading, processing, completed)
  - Progress bar (0-100%)
  - Current step display (e.g., "Analyzing beats...")
  - Estimated time remaining
  - Cancel button (if processing)
  - Download button (when completed)

States:
  - IDLE: No processing
  - UPLOADING: Files being uploaded (0-20%)
  - PROCESSING: Video being processed (20-90%)
  - COMPLETED: Ready to download (100%)
  - ERROR: Show error message

UI Elements:
  - Progress bar with percentage
  - Status text
  - Step description
  - Time remaining
  - Cancel/Download buttons
  - Error message (if error)

Acceptance Criteria:
  ✓ Shows progress bar correctly
  ✓ Updates status text
  ✓ Shows estimated time
  ✓ Cancel button works
  ✓ Download button appears when done
  ✓ Error state displays clearly
  ✓ Responsive design

Dependencies: TICKET-1.4
Blocks: TICKET-2.4
```

---

## PHASE 3: BACKEND API (Day 2-3 - 8 hours)

### TICKET 3.1: Database Models & Schema
```
ID: TICKET-3.1
Title: Database Models & Schema
Priority: CRITICAL
Time Estimate: 1.5 hours
Status: PENDING

Description:
Create SQLAlchemy models and database schema.

Files to Create:
  - backend/app/models/__init__.py
  - backend/app/models/job.py
  - backend/app/models/video.py
  - backend/alembic/env.py (migration setup)

Models:

1. Job Model (app/models/job.py):
   - id: UUID (primary key)
   - status: Enum (PENDING, UPLOADING, PROCESSING, COMPLETED, FAILED)
   - style: String (CINEMATIC_DRAMA, ENERGETIC_DANCE, etc.)
   - created_at: DateTime
   - updated_at: DateTime
   - completed_at: DateTime (nullable)
   - error_message: String (nullable)
   - output_video_path: String (nullable)
   - progress: Integer (0-100)
   - current_step: String (nullable)

2. Video Model (app/models/video.py):
   - id: UUID (primary key)
   - job_id: UUID (foreign key to Job)
   - file_path: String
   - file_name: String
   - file_size: Integer
   - duration: Float (in seconds)
   - width: Integer
   - height: Integer
   - file_type: String (video or image)
   - created_at: DateTime

3. Audio Model (app/models/video.py):
   - id: UUID (primary key)
   - job_id: UUID (foreign key to Job)
   - file_path: String
   - file_name: String
   - file_size: Integer
   - duration: Float (in seconds)
   - created_at: DateTime

Acceptance Criteria:
  ✓ All models defined correctly
  ✓ Foreign keys set up properly
  ✓ Enums defined for status and style
  ✓ Timestamps (created_at, updated_at) on all models
  ✓ Database migrations work (alembic upgrade head)
  ✓ Tables created in PostgreSQL
  ✓ Can query models without errors

Dependencies: TICKET-1.3
Blocks: TICKET-3.2
```

### TICKET 3.2: Pydantic Schemas
```
ID: TICKET-3.2
Title: Pydantic Schemas
Priority: HIGH
Time Estimate: 1 hour
Status: PENDING

Description:
Create Pydantic schemas for API requests/responses.

Files to Create:
  - backend/app/schemas/__init__.py
  - backend/app/schemas/job.py
  - backend/app/schemas/upload.py

Schemas:

1. JobCreate (app/schemas/job.py):
   - style: StylePreset (enum)
   - duration: int (default 30)
   - aspect_ratio: str (default "9:16")

2. JobResponse (app/schemas/job.py):
   - id: UUID
   - status: JobStatus (enum)
   - style: StylePreset
   - progress: int
   - current_step: str
   - created_at: datetime
   - updated_at: datetime
   - error_message: Optional[str]
   - output_video_url: Optional[str]

3. UploadResponse (app/schemas/upload.py):
   - job_id: UUID
   - status: str
   - message: str

4. DownloadResponse (app/schemas/upload.py):
   - download_url: str
   - file_name: str
   - file_size: int

Enums:
  - StylePreset: CINEMATIC_DRAMA, ENERGETIC_DANCE, LUXE_TRAVEL, MODERN_MINIMAL
  - JobStatus: PENDING, UPLOADING, PROCESSING, COMPLETED, FAILED

Acceptance Criteria:
  ✓ All schemas defined correctly
  ✓ Enums work properly
  ✓ Validation works (e.g., duration > 0)
  ✓ Can serialize/deserialize models
  ✓ API docs show schemas correctly

Dependencies: TICKET-3.1
Blocks: TICKET-3.3
```

### TICKET 3.3: File Upload Endpoint
```
ID: TICKET-3.3
Title: File Upload Endpoint
Priority: CRITICAL
Time Estimate: 2 hours
Status: PENDING

Description:
Create file upload endpoint and storage handler.

Files to Create:
  - backend/app/routes/upload.py
  - backend/app/services/storage.py
  - backend/app/utils/validators.py

Endpoint: POST /api/upload

Request:
  - videos: List[UploadFile] (multipart form)
  - music: UploadFile (multipart form)
  - style: StylePreset (form field)
  - duration: int (form field, optional, default 30)
  - aspect_ratio: str (form field, optional, default "9:16")

Response:
  - job_id: UUID
  - status: "uploading"
  - message: "Files uploaded successfully"

Process:
  1. Validate files (type, size, count)
  2. Create Job record in database
  3. Save files to disk/S3
  4. Extract video metadata (duration, resolution)
  5. Queue video processing task
  6. Return job_id

Validation:
  - Video formats: mp4, mov, avi
  - Audio formats: mp3, wav, m4a
  - Max file size: 100MB per file
  - Max 5 video files
  - Audio file required
  - Style must be valid preset

Storage (app/services/storage.py):
  - Save files to /app/uploads/{job_id}/
  - Extract video metadata using ffprobe
  - Handle errors gracefully

Acceptance Criteria:
  ✓ Endpoint accepts multipart form data
  ✓ File validation works
  ✓ Files saved to disk correctly
  ✓ Job created in database
  ✓ Metadata extracted (duration, resolution)
  ✓ Returns job_id
  ✓ Error handling for invalid files
  ✓ Tested with curl/Postman

Dependencies: TICKET-3.2
Blocks: TICKET-3.4
```

### TICKET 3.4: Job Status Endpoint
```
ID: TICKET-3.4
Title: Job Status Endpoint
Priority: HIGH
Time Estimate: 1 hour
Status: PENDING

Description:
Create endpoint to check job status and progress.

Endpoint: GET /api/jobs/{job_id}

Response:
  {
    "id": "uuid",
    "status": "PROCESSING",
    "progress": 45,
    "current_step": "Analyzing beats...",
    "created_at": "2024-12-26T10:00:00Z",
    "updated_at": "2024-12-26T10:05:00Z",
    "error_message": null,
    "output_video_url": null
  }

Features:
  - Real-time progress updates
  - Current step description
  - Error messages if failed
  - Download URL when completed

Acceptance Criteria:
  ✓ Returns correct job status
  ✓ Progress updates in real-time
  ✓ Current step shows what's happening
  ✓ Returns error message if failed
  ✓ Returns download URL when completed
  ✓ Handles invalid job_id (404)

Dependencies: TICKET-3.3
Blocks: TICKET-3.5
```

### TICKET 3.5: Download Endpoint
```
ID: TICKET-3.5
Title: Download Endpoint
Priority: HIGH
Time Estimate: 1 hour
Status: PENDING

Description:
Create endpoint to download completed video.

Endpoint: GET /api/download/{job_id}

Response:
  - File download (video/mp4)
  - Content-Disposition header with filename

Features:
  - Check job status (must be COMPLETED)
  - Return file as attachment
  - Proper content type
  - File cleanup after download (optional)

Acceptance Criteria:
  ✓ Returns video file for completed jobs
  ✓ Proper content type (video/mp4)
  ✓ Filename in Content-Disposition header
  ✓ Returns 404 if job not found
  ✓ Returns 400 if job not completed
  ✓ File downloads correctly

Dependencies: TICKET-3.4
Blocks: TICKET-4.1
```

---

## PHASE 4: VIDEO PROCESSING (Day 3-4 - 8 hours)

### TICKET 4.1: FFmpeg Handler Service
```
ID: TICKET-4.1
Title: FFmpeg Handler Service
Priority: CRITICAL
Time Estimate: 2 hours
Status: PENDING

Description:
Create FFmpeg wrapper service for video operations.

File: backend/app/services/ffmpeg_handler.py

Functions:

1. get_video_info(video_path: str) -> dict
   - Returns: duration, width, height, fps, codec
   - Uses: ffprobe

2. concatenate_videos(video_paths: List[str], output_path: str) -> bool
   - Concatenates multiple videos
   - Uses: FFmpeg concat demuxer
   - Returns: success/failure
```

### TICKET 4.2: Video Processor Service
```
ID: TICKET-4.2
Title: Video Processor Service
Priority: CRITICAL
Time Estimate: 2 hours
Status: PENDING

Description:
Create main video processing orchestration service.

File: backend/app/services/video_processor.py

Class: VideoProcessor

Methods:

1. process_video(job_id: UUID, video_paths: List[str], audio_path: str, style: str) -> str
   - Main orchestration method
   - Returns: output_video_path

Process:
  1. Load all video files
  2. Normalize duration (divide 30s by number of videos)
  3. Resize all videos to same resolution (1080x1920)
  4. Add transitions between videos
  5. Mix audio
  6. Export final MP4
  7. Update job status

2. normalize_video_duration(video_path: str, target_duration: float) -> str
   - Stretches/crops video to target duration
   - Returns: normalized_video_path

3. resize_video(video_path: str, width: int, height: int) -> str
   - Resizes video to target resolution
   - Maintains aspect ratio
   - Returns: resized_video_path

4. add_transitions(video_paths: List[str], transition_type: str = "crossfade", duration_ms: int = 300) -> List[str]
   - Adds transitions between videos
   - Returns: list of videos with transitions

Acceptance Criteria:
  ✓ Processes videos correctly
  ✓ All videos normalized to same duration
  ✓ All videos resized to 1080x1920
  ✓ Transitions added correctly
  ✓ Audio mixed properly
  ✓ Final video is MP4 format
  ✓ Tested end-to-end

Dependencies: TICKET-4.1
Blocks: TICKET-4.3
```

### TICKET 4.3: Celery Task Queue
```
ID: TICKET-4.3
Title: Celery Task Queue
Priority: CRITICAL
Time Estimate: 1.5 hours
Status: PENDING

Description:
Set up Celery for background video processing.

Files to Create:
  - backend/app/workers/celery_app.py
  - backend/app/workers/video_tasks.py

celery_app.py:
  - Celery app initialization
  - Redis broker configuration
  - Task routing
  - Error handling

video_tasks.py:

Task 1: process_video_task(job_id: str)
  - Get job from database
  - Update status to PROCESSING
  - Call VideoProcessor.process_video()
  - Update job with output_video_path
  - Update status to COMPLETED
  - Handle errors (update status to FAILED)

Task 2: cleanup_old_files_task()
  - Delete files older than 7 days
  - Run daily (scheduled)

Configuration:
  - Broker: redis://redis:6379/0
  - Result backend: redis://redis:6379/1
  - Task time limit: 600 seconds (10 minutes)
  - Task soft time limit: 540 seconds (9 minutes)

Acceptance Criteria:
  ✓ Celery app initializes correctly
  ✓ Tasks queue and execute
  ✓ Job status updates during processing
  ✓ Errors handled gracefully
  ✓ Task results stored in Redis
  ✓ Tested with sample job

Dependencies: TICKET-4.2
Blocks: TICKET-4.4
```

### TICKET 4.4: Progress Update Mechanism
```
ID: TICKET-4.4
Title: Progress Update Mechanism
Priority: MEDIUM
Time Estimate: 1 hour
Status: PENDING

Description:
Implement real-time progress updates during processing.

Features:
  - Update job progress (0-100%)
  - Update current step description
  - Send updates to frontend via WebSocket or polling

Implementation:
  1. Add progress tracking to VideoProcessor
  2. Update Job.progress and Job.current_step in database
  3. Frontend polls GET /api/jobs/{job_id} every 2 seconds

Progress Stages:
  - 0%: Job created
  - 10%: Files uploaded
  - 20%: Normalizing videos
  - 40%: Resizing videos
  - 60%: Adding transitions
  - 80%: Mixing audio
  - 95%: Exporting MP4
  - 100%: Completed

Acceptance Criteria:
  ✓ Progress updates in database
  ✓ Current step updates correctly
  ✓ Frontend receives updates via polling
  ✓ Progress goes from 0 to 100%
  ✓ Tested with real video processing

Dependencies: TICKET-4.3
Blocks: TICKET-5.1
```

---

## PHASE 5: AI INTEGRATION (Day 4-5 - 8 hours)

### TICKET 5.1: Beat Detection Service
```
ID: TICKET-5.1
Title: Beat Detection Service
Priority: HIGH
Time Estimate: 2 hours
Status: PENDING

Description:
Create beat detection service using Librosa.

File: backend/app/services/beat_detector.py

Class: BeatDetector

Methods:

1. detect_beats(audio_path: str) -> List[float]
   - Detects beat times in audio file
   - Returns: list of beat times (in seconds)
   - Uses: librosa.beat.beat_track()

2. get_bpm(audio_path: str) -> float
   - Calculates BPM from audio
   - Uses: librosa.beat.tempo()

3. analyze_beat_structure(beats: List[float], duration: float) -> dict
   - Analyzes beat structure
   - Returns: {
       "bpm": float,
       "total_beats": int,
       "intro_beats": List[float],  # 0-4s
       "build_beats": List[float],  # 4-12s
       "peak_beats": List[float],   # 12-24s
       "outro_beats": List[float]   # 24-30s
     }

4. get_transition_times(beats: List[float], num_segments: int) -> List[float]
   - Gets optimal transition times based on beats
   - Returns: list of times to cut video
   - Snaps to nearest beat

Acceptance Criteria:
  ✓ Beat detection works accurately
  ✓ BPM calculation correct
  ✓ Beat structure analysis works
  ✓ Transition times snap to beats
  ✓ Tested with various audio files
  ✓ Performance acceptable (<5 seconds for 30s audio)

Dependencies: TICKET-1.3
Blocks: TICKET-5.2
```

### TICKET 5.2: Segment Planning Service
```
ID: TICKET-5.2
Title: Segment Planning Service
Priority: HIGH
Time Estimate: 2 hours
Status: PENDING

Description:
Create segment planning service for beat-synced editing.

File: backend/app/services/segment_planner.py

Class: SegmentPlanner

Methods:

1. plan_segments(beats: List[float], num_videos: int, style: str, duration: float = 30.0) -> List[dict]
   - Plans video segments based on beats
   - Returns: list of segments with timing

Segment Structure:
  {
    "id": 1,
    "start_sec": 0,
    "end_sec": 7.5,
    "duration_sec": 7.5,
    "transition_type": "hard_cut",  # or "crossfade"
    "transition_duration_ms": 0,
    "cut_on_beat_sec": 7.5
  }

Logic:
  - Divide 30 seconds into N segments (one per video)
  - Each segment duration = 30 / num_videos
  - Find nearest beat for each segment end
  - Assign transition type based on style:
    * CINEMATIC_DRAMA: crossfade (300ms)
    * ENERGETIC_DANCE: hard_cut (0ms)
    * LUXE_TRAVEL: crossfade (500ms)
    * MODERN_MINIMAL: fade (200ms)

2. get_transition_type(style: str) -> str
   - Returns transition type for style

Acceptance Criteria:
  ✓ Segments planned correctly
  ✓ Segments align to beats
  ✓ Transition types match style
  ✓ Total duration = 30 seconds
  ✓ Tested with various beat patterns

Dependencies: TICKET-5.1
Blocks: TICKET-5.3
```

### TICKET 5.3: Style-Based Editing
```
ID: TICKET-5.3
Title: Style-Based Editing
Priority: MEDIUM
Time Estimate: 1.5 hours
Status: PENDING

Description:
Apply style-specific editing rules.

File: backend/app/services/style_editor.py

Class: StyleEditor

Methods:

1. apply_style(video_path: str, style: str, segments: List[dict]) -> str
   - Applies style-specific effects
   - Returns: styled_video_path

Style Rules:

CINEMATIC_DRAMA:
  - Transition: crossfade (500ms)
  - Color: Cool tones (5600K)
  - Speed: Slow (no speed changes)

ENERGETIC_DANCE:
  - Transition: hard_cut (0ms)
  - Color: Warm tones (2700K)
  - Speed: Normal
  - Saturation: +20%

LUXE_TRAVEL:
  - Transition: crossfade (500ms)
  - Color: Warm golden (3200K)
  - Speed: Slow
  - Saturation: +10%

MODERN_MINIMAL:
  - Transition: fade (200ms)
  - Color: Neutral (4500K)
  - Speed: Normal
  - Saturation: -10%

2. apply_color_tone(video_path: str, color_temp: int) -> str
   - Applies color temperature
   - Uses: FFmpeg curves filter

Acceptance Criteria:
  ✓ Styles applied correctly
  ✓ Transitions match style
  ✓ Color tones applied
  ✓ Saturation adjusted
  ✓ Tested with all 4 styles

Dependencies: TICKET-5.2
Blocks: TICKET-5.4
```

### TICKET 5.4: Integration with Video Processor
```
ID: TICKET-5.4
Title: Integration with Video Processor
Priority: HIGH
Time Estimate: 1.5 hours
Status: PENDING

Description:
Integrate beat detection and segment planning into video processor.

Updates to: backend/app/services/video_processor.py

New Flow:
  1. Load audio file
  2. Detect beats (BeatDetector)
  3. Plan segments (SegmentPlanner)
  4. Process videos according to segments
  5. Apply style-based editing (StyleEditor)
  6. Mix audio
  7. Export final video

Modified process_video() method:
  - Call beat_detector.detect_beats()
  - Call segment_planner.plan_segments()
  - Use segments to guide video processing
  - Call style_editor.apply_style()

Acceptance Criteria:
  ✓ Beat detection integrated
  ✓ Segment planning integrated
  ✓ Style editing integrated
  ✓ End-to-end processing works
  ✓ Transitions snap to beats
  ✓ Tested with all styles

Dependencies: TICKET-5.3
Blocks: TICKET-6.1

---

## **New: Top‑5 AI Feature Tickets (Week 1 Sprint)**

ID: TICKET-BEAT-1
Title: Beat‑Synced Cutting (Prototype)
Priority: CRITICAL
Time Estimate: 1.5 days
Status: IN PROGRESS

Description:
Implement a robust beat‑synced cutting prototype with onset peak‑picking, beat salience scoring, bar/downbeat preference, and minimum spacing enforcement to produce reliable cut candidates for Reels.

Subtasks:
  - [ ] Add onset peak‑picking and beat_strength scoring in `backend/app/services/beat_detector.py`
  - [ ] Implement bar/downbeat selection and `min_spacing_sec` enforcement in `backend/app/services/segment_planner.py`
  - [ ] Export `cut_points` from `backend/app/tasks/video_tasks.py` and store diagnostics under `test_output/beat_diagnostics/`

Acceptance Criteria:
  ✓ Returns N cut candidates for a 30s target with min spacing enforced
  ✓ Diagnostic run on sample tracks shows median cut→strong‑beat offset <200ms (goal)

Files: `backend/app/services/beat_detector.py`, `backend/app/services/segment_planner.py`, `backend/app/tasks/video_tasks.py`

---

ID: TICKET-HOOK-1
Title: Auto‑Generated Hooks & Intros (POC)
Priority: HIGH
Time Estimate: 1 day
Status: TODO

Description:
Detect top 3–5s hooks using audio energy and scene salience; produce short copy suggestions via existing LLM prompt template.

Subtasks:
  - [ ] Build energy + scene scorer `backend/app/services/hook_detector.py`
  - [ ] Integrate copy suggestion via LLM prompt
  - [ ] Surface top hook candidates in frontend editor

Acceptance Criteria:
  ✓ Returns top 3 hook segments with scores and suggested copy

Files: `backend/app/services/hook_detector.py`, frontend editor components

---

ID: TICKET-POD-1
Title: Podcast→Reels Pipeline (Scaffold)
Priority: HIGH
Time Estimate: 2 days (scaffold + POC)
Status: TODO

Description:
Scaffold backend pipeline for podcast uploads → transcription → diarization → highlight extraction → reel candidate generation (reuse beat/hook modules).

Subtasks:
  - [ ] Add `POST /api/podcast` route at `backend/app/routes/podcast.py`
  - [ ] Add `backend/app/services/podcast_service.py` to persist audio and enqueue tasks
  - [ ] Add tasks in `backend/app/tasks/podcast_tasks.py` to call ASR/diarization (POC with stub or cloud)

Acceptance Criteria:
  ✓ Frontend can upload audio and receive `job_id`; job produces transcripts and reel candidates under `uploads/{job_id}`

Files: `backend/app/routes/podcast.py`, `backend/app/services/podcast_service.py`, `backend/app/tasks/podcast_tasks.py`

---

ID: TICKET-STYLE-1
Title: Smart Style Transfer (LUTs)
Priority: MEDIUM
Time Estimate: 8 hours
Status: TODO

Description:
Implement one‑click LUT-based style transfer (4 styles) using FFmpeg filter chains; add preview + apply endpoints.

Subtasks:
  - [ ] Add LUT assets and FFmpeg filter generator in `backend/app/services/style_transfer.py`
  - [ ] Add API `/api/apply-style` and frontend preview controls

Acceptance Criteria:
  ✓ Applying style completes within target latency and produces consistent stylistic looks

Files: `backend/app/services/style_transfer.py`, frontend style selector

---

ID: TICKET-IG-1
Title: Instagram Direct Posting + Scheduling (MVP)
Priority: MEDIUM
Time Estimate: 1 day
Status: TODO

Description:
Integrate Instagram Graph API OAuth and scheduling worker to post generated reels (premium feature).

Subtasks:
  - [ ] Implement OAuth connect endpoint and token storage at `backend/app/routes/instagram.py`
  - [ ] Implement schedule queue and posting worker `backend/app/tasks/instagram_tasks.py`

Acceptance Criteria:
  ✓ Authenticated user can schedule or post a reel; status visible via job status endpoint

Files: `backend/app/routes/instagram.py`, `backend/app/tasks/instagram_tasks.py`

---
```

---

## PHASE 6: TESTING & OPTIMIZATION (Day 5-6 - 8 hours)

### TICKET 6.1: Unit Tests
```
ID: TICKET-6.1
Title: Unit Tests
Priority: HIGH
Time Estimate: 2 hours
Status: PENDING

Description:
Create unit tests for all services.

Files to Create:
  - backend/tests/__init__.py
  - backend/tests/test_beat_detector.py
  - backend/tests/test_segment_planner.py
  - backend/tests/test_ffmpeg_handler.py
  - backend/tests/test_video_processor.py

Test Coverage:
  - BeatDetector: detect_beats(), get_bpm(), analyze_beat_structure()
  - SegmentPlanner: plan_segments(), get_transition_type()
  - FFmpegHandler: get_video_info(), concatenate_videos()
  - VideoProcessor: normalize_video_duration(), resize_video()

Test Data:
  - Sample audio file (30 seconds)
  - Sample video files (various formats)
  - Mock FFmpeg responses

Acceptance Criteria:
  ✓ All unit tests pass
  ✓ >80% code coverage
  ✓ Tests run in <30 seconds
  ✓ Tests can run in CI/CD pipeline

Dependencies: TICKET-5.4
Blocks: TICKET-6.2
```

### TICKET 6.2: Integration Tests
```
ID: TICKET-6.2
Title: Integration Tests
Priority: HIGH
Time Estimate: 2 hours
Status: PENDING

Description:
Create end-to-end integration tests.

Files to Create:
  - backend/tests/test_api_integration.py
  - backend/tests/test_video_processing_integration.py

Test Scenarios:

1. Upload → Process → Download
   - Upload videos + audio
   - Check job status
   - Wait for processing
   - Download video
   - Verify output file

2. Beat Detection → Segment Planning
   - Load audio
   - Detect beats
   - Plan segments
   - Verify segments align to beats

3. Full Video Processing
   - Load sample videos
   - Normalize durations
   - Add transitions
   - Mix audio
   - Export MP4
   - Verify output

Acceptance Criteria:
  ✓ All integration tests pass
  ✓ End-to-end flow works
  ✓ Output videos are valid MP4
  ✓ Tests take <5 minutes total

Dependencies: TICKET-6.1
Blocks: TICKET-6.3
```

### TICKET 6.3: Performance Optimization
```
ID: TICKET-6.3
Title: Performance Optimization
Priority: MEDIUM
Time Estimate: 2 hours
Status: PENDING

Description:
Optimize performance for faster video processing.

Areas to Optimize:

1. FFmpeg Encoding
   - Use preset=fast instead of medium
   - Use H.264 codec (libx264)
   - Reduce bitrate if needed (target: 5-8 Mbps)
   - Profile and measure

2. Video Normalization
   - Batch process multiple videos in parallel
   - Use threading/asyncio
   - Measure time per video

3. Memory Usage
   - Don't load entire videos into memory
   - Stream processing where possible
   - Monitor memory usage

4. Caching
   - Cache beat detection results
   - Cache segment plans
   - Cache style rules

Target Metrics:
  - 30-second video: <2 minutes processing time
  - 5 videos + audio: <2 minutes total
  - Memory usage: <500MB

Acceptance Criteria:
  ✓ Processing time <2 minutes for 30s video
  ✓ Memory usage <500MB
  ✓ CPU usage reasonable (<80%)
  ✓ Tested with various file sizes

Dependencies: TICKET-6.2
Blocks: TICKET-6.4
```

### TICKET 6.4: Error Handling & Logging
```
ID: TICKET-6.4
Title: Error Handling & Logging
Priority: HIGH
Time Estimate: 1 hour
Status: PENDING

Description:
Implement comprehensive error handling and logging.

Error Scenarios:

1. File Upload Errors
   - Invalid file type
   - File too large
   - Disk full
   - Network error

2. Processing Errors
   - FFmpeg failure
   - Insufficient memory
   - Timeout
   - Invalid video format

3. Database Errors
   - Connection failure
   - Query failure
   - Constraint violation

Logging:
  - Log all major operations
  - Log errors with stack traces
  - Log performance metrics
  - Use structured logging (JSON)

Error Messages:
  - User-friendly error messages
  - Clear error codes
  - Actionable suggestions

Acceptance Criteria:
  ✓ All errors handled gracefully
  ✓ User sees helpful error messages
  ✓ Logs contain useful debugging info
  ✓ No unhandled exceptions
  ✓ Tested with error scenarios

Dependencies: TICKET-6.3
Blocks: TICKET-7.1
```

---

## PHASE 7: DEPLOYMENT & POLISH (Day 6-7 - 8 hours)

### TICKET 7.1: Docker Build & Testing
```
ID: TICKET-7.1
Title: Docker Build & Testing
Priority: CRITICAL
Time Estimate: 1.5 hours
Status: PENDING

Description:
Build and test Docker images.

Tasks:

1. Backend Dockerfile
   - Base: python:3.11-slim
   - Install FFmpeg, system dependencies
   - Copy requirements.txt
   - Install Python dependencies
   - Copy app code
   - Expose port 8000
   - CMD: uvicorn app.main:app

2. Frontend Dockerfile
   - Base: node:18-alpine
   - Copy package.json
   - npm install
   - npm run build
   - Serve with nginx
   - Expose port 3000

3. Build & Test
   - docker-compose build
   - docker-compose up
   - Test all services
   - Test API endpoints
   - Test frontend UI

Acceptance Criteria:
  ✓ docker-compose build succeeds
  ✓ docker-compose up starts all services
  ✓ All services healthy
  ✓ API endpoints respond
  ✓ Frontend loads
  ✓ End-to-end flow works in Docker

Dependencies: TICKET-6.4
Blocks: TICKET-7.2
```

### TICKET 7.2: Documentation
```
ID: TICKET-7.2
Title: Documentation
Priority: HIGH
Time Estimate: 1.5 hours
Status: PENDING

Description:
Create comprehensive documentation.

Files to Create:
  - README.md (project overview, quick start)
  - SETUP.md (detailed setup instructions)
  - API.md (API documentation)
  - ARCHITECTURE.md (system architecture)
  - DEPLOYMENT.md (deployment guide)
  - CONTRIBUTING.md (contribution guidelines)

README.md:
  - Project description
  - Features
  - Tech stack
  - Quick start (docker-compose up)
  - Screenshots
  - License

SETUP.md:
  - Prerequisites
  - Installation steps
  - Environment setup
  - Database setup
  - Running locally

API.md:
  - Endpoint documentation
  - Request/response examples
  - Error codes
  - Rate limiting

ARCHITECTURE.md:
  - System design
  - Component overview
  - Data flow
  - Database schema

DEPLOYMENT.md:
  - Deployment steps
  - Environment variables
  - Database migration
  - Monitoring
  - Troubleshooting

Acceptance Criteria:
  ✓ All documentation complete
  ✓ Clear and easy to follow
  ✓ Code examples work
  ✓ Screenshots included
  ✓ Deployment steps tested

Dependencies: TICKET-7.1
Blocks: TICKET-7.3
```

### TICKET 7.3: UI Polish & UX
```
ID: TICKET-7.3
Title: UI Polish & UX
Priority: MEDIUM
Time Estimate: 1.5 hours
Status: PENDING

Description:
Polish UI and improve user experience.

Tasks:

1. Visual Polish
   - Consistent spacing and alignment
   - Proper typography
   - Color scheme refinement
   - Icon consistency
   - Loading animations
   - Smooth transitions

2. UX Improvements
   - Clear call-to-action buttons
   - Helpful tooltips
   - Error messages
   - Success messages
   - Loading states
   - Disabled states

3. Accessibility
   - ARIA labels
   - Keyboard navigation
   - Color contrast
   - Focus states
   - Screen reader support

4. Responsive Design
   - Mobile (375px)
   - Tablet (768px)
   - Desktop (1920px)
   - Test on various devices

5. Performance
   - Lazy load images
   - Optimize bundle size
   - Minimize CSS/JS
   - Fast page load

Acceptance Criteria:
  ✓ UI looks professional
  ✓ Responsive on all devices
  ✓ Accessible (WCAG 2.1 AA)
  ✓ Fast page load (<3s)
  ✓ User testing feedback positive

Dependencies: TICKET-7.2
Blocks: TICKET-7.4
```

### TICKET 7.4: Final Testing & Launch
```
ID: TICKET-7.4
Title: Final Testing & Launch
Priority: CRITICAL
Time Estimate: 1.5 hours
Status: PENDING

Description:
Final testing and launch preparation.

Testing Checklist:

1. Functional Testing
  [ ] Upload videos/images
  [ ] Upload music
  [ ] Select style
  [ ] Generate video
  [ ] Check progress
  [ ] Download video
  [ ] Verify output quality

2. Browser Testing
  [ ] Chrome
  [ ] Firefox
  [ ] Safari
  [ ] Edge
  [ ] Mobile browsers

3. Performance Testing
  [ ] Page load time <3s
  [ ] Video processing <2 min
  [ ] No memory leaks
  [ ] CPU usage reasonable

4. Security Testing
  [ ] File upload validation
  [ ] SQL injection prevention
  [ ] XSS prevention
  [ ] CORS configured correctly

5. Error Scenarios
  [ ] Invalid file upload
  [ ] Network failure
  [ ] Processing timeout
  [ ] Disk full
  [ ] Database connection failure

Launch Checklist:
  [ ] All tests passing
  [ ] Documentation complete
  [ ] Environment variables set
  [ ] Database migrated
  [ ] Backups configured
  [ ] Monitoring set up
  [ ] Error tracking enabled
  [ ] Analytics enabled

Acceptance Criteria:
  ✓ All tests passing
  ✓ No critical bugs
  ✓ Performance acceptable
  ✓ Documentation complete
  ✓ Ready for production

Dependencies: TICKET-7.3
Blocks: None (FINAL)
```

---

## SUMMARY

**Total Tickets:** 28  
**Total Estimated Time:** 56 hours  
**Days:** 7 days (8 hours/day)  
**Team Size:** 1 pro developer

**Critical Path:**
TICKET-1.1 → TICKET-1.2 → TICKET-1.3 → TICKET-1.4 → TICKET-2.1 → TICKET-2.4 → TICKET-3.1 → TICKET-3.3 → TICKET-4.1 → TICKET-4.2 → TICKET-4.3 → TICKET-5.1 → TICKET-5.4 → TICKET-6.1 → TICKET-7.1 → TICKET-7.4

**Parallel Work:**
- TICKET-2.1, 2.2, 2.3 can be done in parallel
- TICKET-3.2, 3.3, 3.4 can be done in parallel
- TICKET-6.1, 6.2 can be done in parallel

---

**Document Version:** 1.0  
**Created:** December 26, 2024  
**Status:** Ready for Implementation
