# Tasks

Work is organized in three levels: **Phase → Task → SubTask**. Phases are sequential — complete a phase before starting the next. The LLM plans the ordering at creation time and must preserve it on updates.

| Symbol | Status | Meaning |
|--------|--------|---------|
| ⬜ | pending | Not yet started |
| 🔄 | in_progress | Currently working on |
| ✅ | done | Completed |
| ⏸️ | blocked | Blocked — note the reason after the marker |

Status markers are set on SubTasks. Task and Phase status is derived: if any SubTask is 🔄, its parent Task is in_progress; if all are ✅, the Task is done.

## Phase 1 — [Phase name]

### 1. [Task name]

- ⬜ [SubTask description]
- ⬜ [SubTask description]

### 2. [Task name]

- ⬜ [SubTask description]
- ⬜ [SubTask description]

## Phase 2 — [Phase name]

### 1. [Task name]

- ⬜ [SubTask description]
- ⬜ [SubTask description]
