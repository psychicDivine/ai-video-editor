# 🧪 R&D Insights & Future Roadmap (v3+)

This document consolidates research and future directions for the AI Video Editor, focusing on semantic editing and advanced AI integration.

## 🚀 Semantic Video Commands (Vision)
The goal for v3 is to enable natural language editing powered by Vision-Language Models (VLMs).

### Planned Features
- **Object-Specific Tracking**: Using SAM 2 (Segment Anything) to follow specific objects or people throughout a clip.
- **Semantic Search**: "Clip from when they say [quote]" using Whisper + semantic vector search.
- **Engagement Scoring**: Auto-detecting funny, surprising, or high-energy moments using VLM analysis.
- **Auto-Trimming**: Automatically removing "boring" or low-information segments to keep viewer attention.

### v3 Tech Stack Candidates
| Component | Model / Technology |
|-----------|---------------------|
| **Scene Understanding** | SmolVLM / Qwen-VL (Scene analysis) |
| **Object Tracking** | SAM 2 (Precise segmentation/tracking) |
| **Audio Reasoning** | Whisper + LLM (Contextual clipping) |
| **Video Enhancement** | Real-ESRGAN (Production-ready upscaling) |

## 📈 Learning from v2
- **Gemini 1.5 Flash** is highly effective for finding viral clips at low resolution (240p).
- **YOLOv8** is reliable for person-tracking but can be improved with **MediaPipe** for face-centric crops.
- **FFmpeg xfade** requires precise filter graph management to avoid "trailing garbage" errors.

## 🛠️ Infrastructure Evolution
- Transition from local `.venv` management to **UV** for faster, more reliable dependency handling.
- Move towards **Podman/Docker** for standardized database environments (PostgreSQL + Redis).
