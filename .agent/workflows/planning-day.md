---
description: Day 1 Planning Workflow - Roadmap review, sprint creation, and ticket specification
---

# 📋 Day 1: Planning Workflow

This workflow is executed by the **Planner Agent** at the start of each 4-day sprint.

## Prerequisites
- Access to `docs/ROADMAP.md`
- Review of previous sprint retrospective
- User feedback or feature requests (if any)

---

## Step 1: Review Previous Sprint

// turbo
1. Read the current sprint document:
```powershell
Get-Content docs/sprints/SPRINT_*.md | Select-Object -Last 200
```

2. List all completed tasks:
```powershell
Get-ChildItem docs/tasks/*.md | ForEach-Object { Select-String -Path $_ -Pattern "🟢 Completed" }
```

3. Summarize:
   - What was completed?
   - What was blocked?
   - What needs to carry over?

---

## Step 2: Update Roadmap

1. Open `docs/ROADMAP.md`
2. Move completed features to "Completed" section
3. Update milestone statuses:
   - 🟢 Complete
   - 🟡 In Progress
   - 🔴 Blocked
4. Adjust priorities based on user feedback

---

## Step 3: Create New Sprint Document

1. Determine sprint number (increment from last)
2. Create `docs/sprints/SPRINT_XXX.md` using template:

```markdown
# Sprint XXX: [Theme/Focus]

## Duration
Start: YYYY-MM-DD
End: YYYY-MM-DD (4 days later)

## Goals
1. [Primary goal from ROADMAP]
2. [Secondary goal]
3. [Stretch goal]

## Tickets
| ID | Title | Status | Priority | Skills |
|----|-------|--------|----------|--------|
| TICKET_XXX | Feature Name | 🔴 Not Started | P1 | Python, FFmpeg |

## Daily Log
### Day 1 (Planning)
- Created sprint document
- Defined X tickets

### Day 2-3 (Execution)
- [To be filled by Executor]

### Day 4 (Testing)
- [To be filled by Tester]

## Retrospective
[To be filled at sprint end]
```

---

## Step 4: Create Ticket Specifications

For each goal, create detailed TICKET_XXX.md:

1. **Identify the feature/bug** from ROADMAP
2. **Create ticket file**: `docs/tickets/TICKET_XXX.md`
3. **Fill in template**:
   - Type (Feature/Bug/Refactor/Docs)
   - Priority (P0-P3)
   - Detailed description
   - Acceptance criteria (specific, testable)
   - Technical approach
   - Testing requirements
   - Dependencies

### Skills Assignment
Based on ticket requirements, assign skills:
- **Python**: Backend API, services, AI integration
- **TypeScript**: Frontend components, state management
- **FFmpeg**: Video processing, encoding
- **AI/ML**: Gemini, Whisper, YOLOv8 integration
- **DevOps**: Docker, deployment, infrastructure

---

## Step 5: Break Down into Tasks

For each ticket, create atomic TASK_XXX_YYY.md files:

1. Tasks should be 1-4 hours of work
2. Each task targets specific files
3. Tasks should be independently testable
4. Include clear verification steps

Example breakdown:
```
TICKET_005: Add TikTok Caption Style
├── TASK_005_001: Create TikTok caption template
├── TASK_005_002: Add bounce animation CSS
├── TASK_005_003: Integrate with caption service
└── TASK_005_004: Write unit tests
```

---

## Step 6: Handoff to Executors

1. Update sprint document with all tickets
2. Ensure all tasks have clear "Files to Modify"
3. Set initial statuses to 🔴 Not Started
4. Notify that sprint is ready for execution

---

## Verification Checklist

Before ending Day 1:
- [ ] ROADMAP.md is updated
- [ ] New SPRINT_XXX.md is created
- [ ] All tickets have acceptance criteria
- [ ] All tasks are linked to tickets
- [ ] Skills are assigned to each ticket
- [ ] No blockers on Day 2 execution
