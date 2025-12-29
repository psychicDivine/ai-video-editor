# 🎬 AI Video Editor

A powerful, automated video editing pipeline that turns raw footage and music into professional-grade short-form content (Reels/TikToks). Powered by **Gemini 1.5 Pro** for intelligent scene selection and **Librosa** for beat-synced cutting.

## ✨ Features

- **🤖 AI Director (Gemini 1.5 Pro):** "Watches" your raw video, understands the content, and selects the best highlights based on your style prompt (e.g., "Cinematic", "Fast-paced").
- **🎵 Beat Sync Technology:** Automatically detects musical beats and tempo to cut videos exactly on rhythm.
- **⚡ Automated Pipeline:**
  - **Smart Trimming:** Cuts video segments to match music energy.
  - **Auto-Resize:** Converts landscape/4K footage into 9:16 vertical format for mobile.
  - **Transitions:** Applies professional cross-fades between clips.
  - **Audio Mixing:** Mixes background music with proper fading and synchronization.
- **🚀 Scalable Architecture:** Built with FastAPI, Celery, and Redis to handle heavy video processing tasks asynchronously.

## 🛠️ Tech Stack

- **Backend:** Python 3.11, FastAPI, Celery, Redis
- **AI/ML:** Google Gemini 1.5 Pro (Video Understanding), Librosa (Audio Analysis)
- **Video Processing:** FFmpeg (via Python subprocess)
- **Frontend:** React, TypeScript, TailwindCSS, Vite
- **Database:** PostgreSQL (Metadata), Redis (Task Queue)
- **Infrastructure:** Podman/Docker Compose

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (Managed via `uv`)
- **Node.js 18+**
- **FFmpeg** (Installed and added to PATH)
- **Podman** or **Docker Desktop** (for Redis/Postgres)
- **Google Gemini API Key** (Free from [Google AI Studio](https://aistudio.google.com/app/apikey))

### 1. Infrastructure Setup
Start the required databases (PostgreSQL & Redis):
```powershell
# Windows (PowerShell)
.\start-databases.ps1
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies using uv
uv sync

# Configure Environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start the API Server
uv run uvicorn app.main:app --reload

# Start the Worker (in a separate terminal)
uv run celery -A app.celery_app worker --loglevel=info
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Development Server
npm run dev
```

## 📝 Usage

1. Open `http://localhost:5173` in your browser.
2. Upload your raw **Video Files** (mp4, mov).
3. Upload a **Music Track** (mp3, wav).
4. Select a **Style** (e.g., Cinematic, VLOG, Intense).
5. Click **Generate**.
6. The **AI Director** will analyze your footage, finding the best moments that fit the music.
7. Download your fully edited video!

## 📂 Project Structure

```
ai-video-editor/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── ai_director.py    # Gemini 1.5 Pro Integration
│   │   │   ├── beat_detector.py  # Audio Analysis
│   │   │   ├── video_processor.py# Core Editing Logic
│   │   │   └── ffmpeg_handler.py # FFmpeg Wrapper
│   │   ├── tasks/                # Celery Tasks
│   │   └── routes/               # API Endpoints
│   └── uploads/                  # Temp storage for processing
├── frontend/                     # React Application
└── docker-compose.yml           # Database Services
```

## 🔧 Configuration

**Backend (`backend/.env`)**
```ini
DATABASE_URL=postgresql://editor:editor_pass@localhost:5432/ai_video_editor
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=your_gemini_key_here  <-- Required for AI Director
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
