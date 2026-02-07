---
trigger: always_on
glob:
description: Master rules for AI Video Editor project - defines tech stack, architecture patterns, and agent collaboration protocols
---

# 🎬 AI Video Editor - Antigravity Agent Rules

> **Magic Box SaaS**: One-click YouTube → Viral Reels pipeline with AI captions and smart reframing.

---

## 📚 Project Architecture Documentation

All agents MUST follow the **hierarchical documentation structure**:

```
docs/
├── ROADMAP.md              # High-level vision, quarterly goals, milestones
├── sprints/
│   ├── SPRINT_001.md       # Sprint planning & retrospective
│   ├── SPRINT_002.md
│   └── ...
├── tickets/
│   ├── TICKET_001.md       # Detailed feature/bug specifications
│   ├── TICKET_002.md
│   └── ...
└── tasks/
    ├── TASK_001_001.md     # Atomic work units (linked to tickets)
    ├── TASK_001_002.md
    └── ...
```

### Document Relationships
```
ROADMAP.md
    └──> SPRINT_XXX.md (contains ticket references)
             └──> TICKET_XXX.md (detailed specs)
                      └──> TASK_XXX_YYY.md (executable work units)
```

---

## 🛠️ Technology Stack

### Backend (Python 3.11+)
| Component | Technology | Version |
|-----------|------------|---------|
| Package Manager | **UV** | Latest |
| Framework | FastAPI | 0.104.1 |
| Server | Uvicorn | 0.24.0 |
| Task Queue | Celery | 5.3.4 |
| Cache/Broker | Redis | 5.0.1 |
| ORM | SQLAlchemy | 2.0.23 |
| Database | PostgreSQL | Latest |
| Environment | `.venv` (UV managed) | - |

### AI/ML Stack
| Component | Model/Library | Purpose |
|-----------|---------------|---------|
| Viral Detection | Gemini 1.5 Flash | Find engaging moments |
| Object Detection | YOLOv8 Nano | Subject tracking for reframing |
| Transcription | OpenAI Whisper | Word-level captions |
| Upscaling | Real-ESRGAN | Low-res enhancement |
| Video Processing | FFmpeg | All video operations |
| Audio Analysis | Librosa | Beat detection |
| Computer Vision | OpenCV | Frame manipulation |

### Frontend (Node.js)
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Vite + React | 5.0.8 / 18.2.0 |
| Language | TypeScript | 5.3.3 |
| Styling | TailwindCSS | 3.3.6 |
| State | TanStack Query | 5.28.0 |
| Icons | Lucide React | 0.292.0 |
| HTTP Client | Axios | 1.6.2 |
| Testing | Vitest | 1.0.4 |

### Infrastructure
| Component | Technology | Purpose |
|-----------|------------|---------|
| Downloads | yt-dlp | YouTube video fetching |
| Containers | Docker/Podman | Deployment |
| OS | Windows (dev) | Primary development |

---

## 🤖 Agent Collaboration Protocol

### Agent Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                    PLANNER AGENT (Day 1)                     │
│  Role: Strategic reasoning, roadmap updates, ticket creation │
│  Skills: High-level architecture, prioritization, estimation │
│  Model: Higher reasoning (Claude/GPT-4 tier)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │ Creates/Updates
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              TICKET SPECIFICATION AGENT                      │
│  Role: Detailed technical specifications, acceptance criteria│
│  Skills: System design, API design, test case definition     │
│  Model: Higher reasoning with domain expertise               │
└──────────────────────────┬──────────────────────────────────┘
                           │ Produces
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               EXECUTOR AGENTS (Days 2-4)                     │
│  Role: Implement tasks, write code, run tests                │
│  Skills: Based on task requirements (Python/TS/DevOps/etc)   │
│  Model: Fast LLM optimized for execution speed               │
└──────────────────────────┬──────────────────────────────────┘
                           │ Produces
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    TESTER AGENT                              │
│  Role: Validate features, run test suites, user acceptance   │
│  Skills: QA, browser testing, API testing, regression        │
│  Model: Fast LLM with testing focus                          │
└─────────────────────────────────────────────────────────────┘
```

### 4-Day Sprint Cycle

| Day | Activity | Lead Agent | Deliverables |
|-----|----------|------------|--------------|
| **Day 1** | Planning & Review | Planner | Updated ROADMAP, new SPRINT doc, TICKET specs |
| **Day 2** | Implementation | Executor | Code, TASKs in progress |
| **Day 3** | Implementation | Executor | Code, TASKs completed |
| **Day 4** | Testing & Polish | Executor + Tester | Tests passing, TICKET updates |

---

## 📋 Document Templates

### ROADMAP.md Structure
```markdown
# 🗺️ AI Video Editor Roadmap

## Vision
[One paragraph describing the end goal]

## Current Version: X.Y
## Target Version: X.Z

## Quarterly Goals (Q1 2026)
- [ ] Goal 1 (links to TICKET_XXX)
- [ ] Goal 2 (links to TICKET_YYY)

## Milestones
### M1: Feature Name (Date)
- Status: 🟢 Complete | 🟡 In Progress | 🔴 Blocked
- Tickets: TICKET_001, TICKET_002
- Notes: ...

## Completed
- [x] Feature (TICKET_XXX) - Date
```

### SPRINT_XXX.md Structure
```markdown
# Sprint XXX: Title

## Duration
Start: YYYY-MM-DD
End: YYYY-MM-DD

## Goals
1. Primary Goal
2. Secondary Goal

## Tickets
| ID | Title | Status | Assignee | Priority |
|----|-------|--------|----------|----------|
| TICKET_001 | Feature X | 🟡 In Progress | Executor | P1 |

## Daily Log
### Day 1 (Planning)
- Decisions made...

### Day 2-3 (Execution)
- Tasks completed...

### Day 4 (Testing)
- Test results...

## Retrospective
### What Worked
### What Didn't
### Action Items
```

### TICKET_XXX.md Structure
```markdown
# TICKET_XXX: Title

## Metadata
- **Type**: Feature | Bug | Refactor | Docs
- **Priority**: P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low)
- **Sprint**: SPRINT_XXX
- **Estimated Hours**: X
- **Skills Required**: Python, TypeScript, FFmpeg, AI/ML

## Description
[Detailed description of the work]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Technical Approach
[Implementation details, architecture decisions]

## Tasks
- [ ] TASK_XXX_001: Subtask 1
- [ ] TASK_XXX_002: Subtask 2

## Testing Requirements
- Unit tests
- Integration tests
- Manual verification steps

## Dependencies
- Depends on: TICKET_YYY
- Blocks: TICKET_ZZZ

## Observations (Updated by Executor)
### Implementation Notes
### Blockers Encountered
### Suggested Improvements
```

### TASK_XXX_YYY.md Structure
```markdown
# TASK_XXX_YYY: Title

## Parent
- **Ticket**: TICKET_XXX
- **Sprint**: SPRINT_XXX

## Status
🔴 Not Started | 🟡 In Progress | 🟢 Completed | ⚫ Blocked

## Description
[Atomic, executable work unit description]

## Files to Modify
- `backend/app/services/example.py`
- `frontend/src/components/Example.tsx`

## Implementation Steps
1. Step 1
2. Step 2

## Verification
- [ ] Code compiles/lints
- [ ] Tests pass
- [ ] Manual verification done

## Time Log
| Date | Hours | Notes |
|------|-------|-------|
| 2026-01-23 | 2h | Initial implementation |

## Executor Notes
[Observations, blockers, suggestions during execution]
```

---

## 🎯 Agent Behavioral Rules

### For ALL Agents

1. **Always check docs first**: Before any work, read ROADMAP.md and active SPRINT
2. **Update documents**: After completing work, update relevant docs
3. **Link everything**: Every code change must reference a TASK_XXX_YYY
4. **Use conventional commits**: `feat(TASK_001_001): Add caption endpoint`
5. **Respect file structure**: Backend code in `/backend`, frontend in `/frontend`

### For Planner Agent (Day 1)

1. Review completed TASKs from previous sprint
2. Update ROADMAP with progress
3. Create new SPRINT_XXX.md
4. Break down goals into TICKET_XXX.md documents
5. Prioritize based on user feedback and blockers
6. Assign skills required for each ticket

### For Executor Agents (Days 2-4)

1. Pick up TASK from assigned TICKET
2. Update TASK status to 🟡 In Progress
3. Implement following the coding standards below
4. Write/update tests
5. Update TASK with observations and time log
6. Update TASK status to 🟢 Completed
7. Update TICKET with implementation notes

### For Tester Agent (Day 4)

1. Run full test suite: `pytest` (backend), `npm test` (frontend)
2. Perform manual testing based on TICKET acceptance criteria
3. Document any failures in TICKET observations
4. Create new BUG tickets if needed
5. Update SPRINT retrospective

---

## 💻 Coding Standards

### Python (Backend)
```python
# Use type hints
def process_video(video_id: str, options: ProcessOptions) -> VideoResult:
    """Process video with given options.
    
    Args:
        video_id: Unique video identifier
        options: Processing configuration
        
    Returns:
        VideoResult containing processed video paths
    """
    ...

# Async by default for I/O operations
async def fetch_youtube_info(url: str) -> YouTubeMetadata:
    ...

# Use Pydantic for data validation
class VideoRequest(BaseModel):
    url: HttpUrl
    options: Optional[ProcessOptions] = None
```

### TypeScript (Frontend)
```typescript
// Use interfaces for props
interface VideoCardProps {
  title: string;
  thumbnail: string;
  duration: number;
  onSelect: (id: string) => void;
}

// Functional components with explicit return types
export const VideoCard: React.FC<VideoCardProps> = ({ 
  title, 
  thumbnail, 
  duration, 
  onSelect 
}): JSX.Element => {
  // ...
};

// Use React Query for server state
const { data, isLoading, error } = useQuery({
  queryKey: ['video', videoId],
  queryFn: () => fetchVideo(videoId),
});
```

### File Naming
- Python: `snake_case.py`
- TypeScript: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- Tests: `test_module.py` or `Module.test.tsx`

---

## 🧪 Testing Requirements

### Backend
```bash
# Run tests
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html
```

### Frontend
```bash
# Run tests
cd frontend
npm test

# With UI
npm run test:ui
```

### Integration Testing
- API endpoints must have integration tests
- Use `httpx` for async API testing
- Mock external services (Gemini, YouTube)

---

## 🚀 Development Commands (Windows + UV)

### Backend
```powershell
# Sync dependencies
uv sync

# Start backend (UV managed)
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Start Celery worker (Windows + UV)
cd backend
uv run celery -A app.celery_app.celery_app worker --loglevel=info -P solo

# Add dependency
uv add <package_name>
```

### Frontend
```powershell
# Start frontend
cd frontend
npm run dev

# Build
npm run build

# Format
npm run format
```

### Docker
```powershell
# Full stack
docker-compose up -d

# Rebuild
docker-compose up -d --build
```

---

## 🔗 Key File Locations

| Purpose | Path |
|---------|------|
| FastAPI Entry | `backend/app/main.py` |
| Celery Config | `backend/app/celery_app.py` |
| Video Processor | `backend/app/services/video_processor.py` |
| AI Director | `backend/app/services/ai_director.py` |
| Reframing | `backend/app/services/ai_reframing.py` |
| Captions | `backend/app/services/caption_service.py` |
| YouTube Service | `backend/app/services/youtube_downloader.py` |
| Frontend Entry | `frontend/src/main.tsx` |
| Components | `frontend/src/components/` |
| API Routes | `backend/app/routes/` |
| Environment | `backend/.env` |

---

## ⚠️ Important Notes

1. **Windows Celery**: Always use `-P solo` pool
2. **Port 8000**: Reserved for backend
3. **Port 5173**: Reserved for frontend (Vite)
4. **Gemini API**: Required for AI features, set in `.env`
5. **FFmpeg**: Must be in PATH for video processing
6. **yt-dlp**: Must be in PATH for YouTube downloads

---

## 📝 Commit Message Format

```
<type>(<scope>): <subject>

<body>

Refs: TASK_XXX_YYY
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(captions): Add TikTok caption style preset

Implements glamorous TikTok-style captions with bounce animation
and gradient backgrounds.

Refs: TASK_003_002
```
