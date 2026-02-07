---
description: Day 4 Testing Workflow - Feature validation, user acceptance, and sprint retrospective
---

# 🧪 Day 4: Testing & Release Workflow

This workflow is executed by the **Tester Agent** and involves user handoff for acceptance testing.

## Prerequisites
- All tasks marked 🟢 Completed or ⚫ Blocked
- Code is merged and deployable
- Test environment is available

---

## Step 1: Run Full Test Suite

### Backend Tests

// turbo
```powershell
cd backend
uv run pytest --cov=app --cov-report=html --cov-report=term-missing
```

Expected outcome:
- All tests pass
- Coverage > 70% for new code
- No regressions

### Frontend Tests

// turbo
```powershell
cd frontend
npm run test:coverage
```

Expected outcome:
- All tests pass
- No TypeScript errors
- Component tests for new features

---

## Step 2: Integration Testing

Test the full pipeline end-to-end:

### Start All Services

// turbo
```powershell
# Terminal 1: Backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Celery
cd backend
uv run celery -A app.celery_app.celery_app worker --loglevel=info -P solo

# Terminal 3: Frontend
cd frontend
npm run dev
```

### Test Scenarios

For each new feature, test:

1. **Happy path**: Normal usage flow
2. **Edge cases**: Empty inputs, max values
3. **Error handling**: Invalid data, network errors
4. **Performance**: Response times, memory usage

---

## Step 3: Feature-Specific Validation

For each TICKET in the sprint:

1. Read acceptance criteria
2. Create a checklist:

```markdown
## TICKET_XXX Validation

### Acceptance Criteria Check
- [ ] Criterion 1: [PASS/FAIL] Notes...
- [ ] Criterion 2: [PASS/FAIL] Notes...

### Manual Testing
- [ ] UI renders correctly
- [ ] API returns expected data
- [ ] Error messages are user-friendly
- [ ] Performance is acceptable

### Regression Check
- [ ] Existing features still work
- [ ] No console errors
- [ ] No broken layouts
```

---

## Step 4: User Acceptance Testing (UAT)

### Handoff to User

1. **Prepare demo environment**:
   - Ensure all services running
   - Clear test data if needed
   - Prepare sample inputs

2. **Create UAT document**:

```markdown
# UAT: Sprint XXX Features

## Features to Test
1. [Feature A] - How to test, expected result
2. [Feature B] - How to test, expected result

## Test URLs
- Frontend: http://localhost:5173
- API: http://localhost:8000/docs

## Sample Test Data
- YouTube URL: [example]
- Expected output: [description]

## Feedback Form
### Feature A
- [ ] Works as expected
- [ ] Needs improvements: ___
- [ ] Bugs found: ___

### Feature B
- [ ] Works as expected
- [ ] Needs improvements: ___
- [ ] Bugs found: ___
```

3. **Collect feedback**:
   - Issues go to new BUG tickets
   - Improvements go to ROADMAP backlog

---

## Step 5: Bug Documentation

For any failures:

1. Create `docs/tickets/TICKET_XXX.md` with Type: Bug
2. Include:
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots/logs
   - Severity (P0-P3)

---

## Step 6: Update Sprint Retrospective

In `docs/sprints/SPRINT_XXX.md`:

```markdown
## Retrospective

### What Worked Well
- [Positive outcome 1]
- [Positive outcome 2]

### What Didn't Work
- [Issue 1] → Action: [fix]
- [Issue 2] → Action: [fix]

### Metrics
- Tickets completed: X/Y
- Tasks completed: X/Y
- Test coverage: X%
- Bugs found: X
- UAT feedback: [summary]

### Action Items for Next Sprint
- [ ] Action 1
- [ ] Action 2
```

---

## Step 7: Update ROADMAP

1. Mark completed milestones as 🟢 Complete
2. Move delivered features to "Completed" section
3. Add new items from UAT feedback
4. Adjust priorities for next sprint

---

## Step 8: Prepare for Next Sprint

1. Close out current sprint document
2. Identify carryover tasks (if any)
3. Note technical debt for future
4. Celebrate wins! 🎉

---

## Testing Checklist

### Before UAT
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] No linting errors
- [ ] Documentation updated
- [ ] Services running stable

### After UAT
- [ ] User feedback collected
- [ ] Bugs documented
- [ ] Sprint retrospective complete
- [ ] ROADMAP updated
- [ ] Next sprint can begin

---

## Quick Commands

// turbo-all
```powershell
# Full test suite
cd backend && pytest --cov=app
cd frontend && npm run test:coverage

# Linting
cd backend && ruff check .
cd frontend && npm run lint

# Build check (for release)
cd frontend && npm run build
```
