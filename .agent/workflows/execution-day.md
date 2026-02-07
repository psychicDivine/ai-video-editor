---
description: Days 2-3 Execution Workflow - Task pickup, implementation, and documentation
---

# ⚡ Days 2-3: Execution Workflow

This workflow is executed by the **Executor Agent** during the implementation phase.

## Prerequisites
- Sprint document exists: `docs/sprints/SPRINT_XXX.md`
- Tickets are defined: `docs/tickets/TICKET_XXX.md`
- Tasks are ready: `docs/tasks/TASK_XXX_YYY.md`

---

## Step 1: Morning Task Pickup

// turbo
1. List available tasks:
```powershell
Get-ChildItem docs/tasks/*.md | ForEach-Object { 
    $content = Get-Content $_ -Raw
    if ($content -match "🔴 Not Started") { 
        Write-Output $_.Name 
    }
}
```

2. Read the task file you're picking up
3. Update task status to 🟡 In Progress
4. Note start time in Time Log

---

## Step 2: Understand Context

Before coding:

1. **Read the parent ticket** for full context
2. **Check dependencies** - are prerequisite tasks done?
3. **Review "Files to Modify"** section
4. **Understand acceptance criteria** from ticket

---

## Step 3: Implementation

### Backend (Python)

// turbo
1. Activate virtual environment:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
```

// turbo
2. Run existing tests to ensure baseline:
```powershell
pytest -x --tb=short
```

3. Implement changes following coding standards:
   - Type hints on all functions
   - Docstrings for public functions
   - Pydantic models for request/response

// turbo
4. Format code:
```powershell
black .
ruff check . --fix
```

### Frontend (TypeScript)

// turbo
1. Ensure dev server is running:
```powershell
cd frontend
npm run dev
```

2. Implement changes:
   - TypeScript interfaces for props
   - Functional components with React Query
   - Tailwind for styling

// turbo
3. Type check:
```powershell
npm run type-check
```

---

## Step 4: Write Tests

### Backend Tests

Location: `backend/tests/`

```python
# test_feature.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_new_feature():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/endpoint", json={...})
    assert response.status_code == 200
```

### Frontend Tests

Location: Adjacent to component

```typescript
// Component.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

describe('ComponentName', () => {
  it('should render correctly', () => {
    render(<Component />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

---

## Step 5: Update Task Documentation

After completing implementation:

1. Update task status to 🟢 Completed
2. Fill in "Executor Notes":
   - Any deviations from plan
   - Technical decisions made
   - Blockers encountered
   - Suggestions for improvements
3. Update Time Log with actual hours

---

## Step 6: Update Ticket Observations

In the parent TICKET_XXX.md:

1. Add to "Implementation Notes"
2. Document any blockers
3. Suggest improvements for future sprints

---

## Step 7: Commit Changes

```powershell
git add .
git commit -m "feat(TASK_XXX_YYY): Brief description

Detailed explanation of changes.

Refs: TASK_XXX_YYY"
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

## Mid-Sprint Check (End of Day 2)

- [ ] At least 50% of tasks 🟢 Completed
- [ ] No critical blockers
- [ ] Tests passing for completed tasks
- [ ] Documentation updated

If blocked:
1. Document blocker in task
2. Mark task as ⚫ Blocked
3. Pick up next available task
4. Escalate to Planner if architectural issue

---

## End of Day 3

- [ ] All assigned tasks completed or documented
- [ ] All tests passing
- [ ] Code formatted and linted
- [ ] Task statuses updated
- [ ] Ticket observations filled in
- [ ] Ready for Day 4 testing

---

## Quick Reference Commands

// turbo-all
```powershell
# Backend tests
cd backend && pytest -x --tb=short

# Frontend tests
cd frontend && npm test

# Format all
cd backend && black . && ruff check . --fix
cd frontend && npm run format

# Type check
cd frontend && npm run type-check

# test coverage and genrate html
 uv run pytest --cov=src --cov-config=.coveragerc --cov-report=html src/tests

# Start services
uvicorn app.main:app --reload --port 8000
celery -A app.celery_app.celery_app worker --loglevel=info -P solo
```