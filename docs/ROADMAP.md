# 🗺️ AI Video Editor Roadmap

> **Vision**: Create a one-click "Magic Box" that transforms any YouTube video into viral-ready short-form content with AI-powered captions and smart reframing.

---

## Current Version: 1.0.0
## Target Version: 2.0.0

---

## 🎯 Quarterly Goals (Q1 2026)

### 🔥 SPRINT PRIORITY: EditPlan Architecture (Jan 24-31)
- [x] Sync StyleSelector with backend styles (5 styles)
- [x] Add AI prompts to style_editor.py
- [x] Merge transitions into ffmpeg_handler.py
- [ ] Create effects.py service (slowmo, speedup, zoomPunch, etc.)
- [ ] Create EditPlan schema (Pydantic models)
- [ ] Create plan routes (/api/plan/generate, /api/plan/render)
- [ ] Create PlanRenderer service
- [ ] Update AI Director for EditPlan output
- [ ] Frontend EditPlan types + context

### High Priority
- [ ] Caption Style Presets (TikTok, Hormozi, Neon) → TICKET_001
- [ ] Post-Preview Caption Editor → TICKET_002
- [ ] AI Color Suggestion for Caption Contrast → TICKET_003

### Medium Priority
- [ ] Face-Centric Tracking with MediaPipe → TICKET_004
- [ ] Batch Processing for Multiple URLs → TICKET_005
- [ ] Progress Notification System → TICKET_006

### Low Priority
- [ ] Export to Social Platforms → TICKET_007
- [ ] User Authentication → TICKET_008
- [ ] Cloud Deployment → TICKET_009

---

## 📊 Milestones

### M1: Enhanced Captions (Target: Jan 30, 2026)
- **Status**: 🔴 Not Started
- **Tickets**: TICKET_001, TICKET_002, TICKET_003
- **Notes**: Focus on caption customization and style presets

### M2: Advanced Tracking (Target: Feb 15, 2026)
- **Status**: 🔴 Not Started
- **Tickets**: TICKET_004
- **Notes**: MediaPipe integration for tighter face framing

### M3: Production Ready (Target: Mar 1, 2026)
- **Status**: 🔴 Not Started
- **Tickets**: TICKET_007, TICKET_008, TICKET_009
- **Notes**: Authentication, cloud deployment, social export

---

## ✅ Completed Features

| Feature | Ticket | Completion Date |
|---------|--------|-----------------|
| YouTube Import + Caching | - | 2026-01-15 |
| AI Viral Clip Detection (Gemini) | - | 2026-01-15 |
| 9:16 Smart Reframing (YOLOv8) | - | 2026-01-18 |
| AI Captions (Whisper) | - | 2026-01-20 |
| Split-Screen Layout | - | 2026-01-20 |
| ZIP Download | - | 2026-01-22 |

---

## 🐛 Known Issues / Technical Debt

| Issue | Severity | Notes |
|-------|----------|-------|
| Gemini deprecation warning | Low | Switch to google.genai package |
| Windows Celery requires -P solo | Low | Document workaround |
| Real-ESRGAN Windows patching | Medium | Needs proper fix |

---

## 💡 Feature Backlog (Unscheduled)

From user feedback and future planning:

1. **Semantic Video Commands** (v3)
   - "Make a reel where X happens"
   - Natural language editing with VLM
   
2. **Object-Specific Tracking**
   - SAM 2 for following specific objects
   
3. **Audio Commands**
   - "Clip when they say X"
   - Whisper + semantic search

4. **Engagement Scoring**
   - Auto-detect funny/engaging moments

---

## 📝 Last Updated

- **Date**: 2026-01-23
- **By**: Planner Agent
- **Sprint**: SPRINT_001 (pending)
