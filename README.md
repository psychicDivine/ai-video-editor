# 🎬 AI Video Editor

**Magic Box SaaS**: One-click YouTube → Viral Reels pipeline with AI captions and smart reframing. A powerful, automated pipeline that turns raw podcasts or footage into professional-grade short-form content (Reels/TikToks/Shorts).

## ✨ Features

- **🎯 Viral Highlight Detection:** Powered by **Gemini 1.5 Flash** to analyze and find the most engaging moments in long-form podcasts or videos.
- **🗣️ Smart AI Captions:** Uses **OpenAI Whisper** for highly accurate, word-level dynamic captions.
- **🧍 Smart Reframing & Tracking:** Automatically converts landscape video to 9:16 vertical format using **YOLOv8 Nano** to track and center the active speaker (Smart Cameraman).
- **📈 AI Upscaling:** Enhances low-resolution clips to crisp quality using **Real-ESRGAN**.
- **🎵 Beat Sync & Audio Mixing:** Leverages **Librosa** to detect tempo and beat-sync background music with proper audio ducking.
- **⚡ Fully Automated Pipeline:** Handles downloading (via `yt-dlp`), clipping, reframing, captioning, and rendering entirely asynchronously.
- **🚀 Scalable Architecture:** Built with FastAPI, Celery, and Redis to handle heavy video processing tasks concurrently.

## 🛠️ Tech Stack

### Backend
- **Core:** Python 3.11+, UV, FastAPI, Celery, Redis, Uvicorn
- **Database:** PostgreSQL (Metadata), SQLAlchemy (ORM)

### AI/ML
- **Viral Detection:** Gemini 1.5 Flash
- **Transcription:** OpenAI Whisper
- **Object Detection:** YOLOv8 Nano
- **Upscaling:** Real-ESRGAN
- **Audio Analysis:** Librosa
- **Computer Vision:** OpenCV
- **Media Processing:** FFmpeg (via Python subprocess)

### Frontend
- **Core:** Node.js, Vite, React, TypeScript
- **Styling:** TailwindCSS, Lucide React
- **State/Data:** TanStack Query, Axios
- **Infrastructure:** Podman/Docker Compose, yt-dlp

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
2. Enter a **YouTube URL** (Podcast/Video) or upload your raw video files.
3. Configure your processing options (e.g., Enable Smart Reframing, AI Captions).
4. Click **Generate Highlights**.
5. The **AI Director** will download, analyze, and segment the video into viral clips.
6. Review and download your ready-to-publish vertical videos with baked-in captions!

> **⚠️ Note:** This app does **not** keep upload history or user accounts. All uploaded files are deleted after processing, and your output video is deleted from the server after 1 hour. Please download your video as soon as it is ready.

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
