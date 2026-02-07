# 🔄 Global Sync & Documentation Protocol

To ensure all AI agents (Antigravity and others) remain in sync with the project's architecture, roadmap, and tasks, the following protocol MUST be followed:

## 1. Single Source of Truth
The `docs/` directory is the **only** source of truth for:
- **Architecture**: `docs/ARCHITECTURE.md`
- **Roadmap**: `docs/ROADMAP.md`
- **Sprints**: `docs/sprints/`
- **Tickets/Tasks**: `docs/tickets/` and `docs/tasks/`

## 2. Update Process for Agents
Whenever an agent makes a change that affects the system architecture or task status:
1. **Read-First**: Always read relevant docs in `docs/` before starting a task.
2. **Atomic Updates**: Update the relevant `.md` file immediately after a change is finalized or a design decision is made.
3. **Commit Messages**: Reference the relevant TICKET or TASK in commit messages (e.g., `feat(TASK_001_001): Update caption logic`).
4. **Cross-Reference**: If a backend change affects a frontend component, update BOTH the task and the architecture notes in `docs/ARCHITECTURE.md`.

## 3. Maintenance
- **Day 1 (Planner)**: Updates `ROADMAP.md` and creates new `SPRINT_XXX.md`.
- **Daily (Executor)**: Updates `TASK_XXX_YYY.md` statuses and adds implementation notes.
- **Day 4 (Tester)**: Updates validation results in the sprint/ticket docs.

## 4. Conflict Resolution
If multiple agents are working in parallel:
- Use the latest file contents as the base.
- If a document is updated by another agent mid-task, re-read it to align the implementation plan.
