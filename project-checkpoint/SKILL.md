---
name: project-checkpoint
description: Save project progress by updating docs/current.md, docs/task.md, and docs/decision.md based on conversation context and git changes. Reads git diff/log and the conversation to infer what was accomplished, then updates task status markers, refreshes the current state snapshot, and appends new decisions. Does NOT rewrite docs/design.md or docs/plan.md without explicit user confirmation — those require the user to name specific sections to update. This skill must be explicitly invoked by the user. Trigger when the user says "save progress", "checkpoint", "record what I did", "update project state", "mark tasks done", "保存进度", "记录一下", or similar explicit save/checkpoint requests. Also suggest this skill to the user at the end of a productive session if they haven't already used it.
---

# Project Checkpoint

Save project progress to `docs/` by analyzing what changed — conversation context, git history, and file diffs — and syncing the results into the context-tracking files. This skill is the **write** counterpart to `project-bootstrap` (which reads and restores).

The skill updates only what changed. It never rewrites entire files when a targeted update will do.

## What Gets Updated

| File | Update policy | How |
|------|--------------|-----|
| `docs/task.md` | **Free** — update directly | Mark SubTasks ✅ / 🔄 / ⏸️ based on completed work |
| `docs/current.md` | **Free** — update directly | Refresh Phase/Task/SubTask/Blocker/NextStep/Decisions |
| `docs/decision.md` | **Free** — append only | Add new decisions made during the session |
| `docs/design.md` | **Restricted** — user must confirm each section | Append to specific sections only; never rewrite the whole file |
| `docs/plan.md` | **Restricted** — user must confirm each section | Append to milestones or dependencies; never rewrite the whole file |
| `CLAUDE.md` / `AGENTS.md` | **Restricted** — user must confirm each change | Targeted edits to sections invalidated by session changes (layout, commands, conventions); never rewrite the whole file |

## Prerequisites

- `docs/` directory must exist with at least `current.md` and `task.md`. If not, tell the user to run `project-bootstrap` first.
- The project should be a git repository (for `git diff` and `git log` context). If not, rely solely on conversation analysis.

## Workflow

### Step 1: Verify `docs/` directory

Check that `docs/` exists with `current.md` and `task.md`. If either is missing:

> `docs/` is not fully set up. Run project-bootstrap first to initialize the context files, then use this skill to save progress.

### Step 2: Gather context

Collect three sources of evidence about what happened during the session:

#### 2a. Read current state files

Read these files to understand where the project stood:
- `docs/current.md` — the last saved state
- `docs/task.md` — the full task breakdown with status markers
- `docs/decision.md` — existing decisions (if present)

#### 2b. Git analysis

Run these commands and capture output:

```bash
git diff --stat          # Which files changed, how much
git log --oneline -10    # Recent commits (check for new commits made in this session)
git diff --cached --stat # Staged but uncommitted changes
```

The diff stats tell you which modules/files were touched. Map these back to the tasks in `task.md`. For example, if `src/commands/squash.go` shows +80 lines and the task list has "Implement basic squash logic", that subtask should likely be marked complete.

**If git is not available or the project is not a git repo:** skip git analysis and rely on conversation context and file modification times.

#### 2c. Conversation analysis

Review the conversation for:
- Tasks the user said they completed
- Decisions explicitly made
- Blockers that came up
- New tasks or phases that emerged
- Files the user mentioned creating or modifying

### Step 3: Match work to tasks

Cross-reference the evidence against `task.md`:

1. For each SubTask in `task.md`, look for evidence it was worked on or completed:
   - Files mentioned in `git diff --stat` match the subtask description
   - User explicitly said "I did X" or "X is done"
   - New commits reference the subtask
   - Conversation shows the work was done

2. Determine the new status for each affected SubTask:
   - **✅ done** — clear evidence of completion (tests pass, user confirmed, commit exists)
   - **🔄 in_progress** — started but not finished (partial diff, user said "still working on")
   - **⏸️ blocked** — user mentioned a blocker (note the reason)
   - **⬜ pending** — no evidence of work (leave unchanged)

3. If a SubTask was started but not in the task list, suggest adding it. Don't add silently — ask the user.

**When in doubt about a status, ask.** A wrong ✅ is worse than an extra 🔄.

### Step 4: Update `task.md`

Update the matched SubTask status markers in `docs/task.md`. For each change:

- Change `⬜` → `🔄` for subtasks that were started
- Change `⬜` or `🔄` → `✅` for subtasks that were completed
- Change any marker → `⏸️` for blocked subtasks (append the reason after the marker, e.g.: `⏸️ blocked — waiting for API key from DevOps`)

After updating subtasks, re-derive Task and Phase status:
- If any SubTask is 🔄 → its parent Task is in_progress
- If any SubTask is ⏸️ and none are 🔄 → its parent Task is blocked
- If all SubTasks are ✅ → its parent Task is done
- Phases derive the same way from their Tasks

**Do not reorder, delete, or add entries without asking the user.** Only change status markers.

### Step 5: Update `current.md`

After `task.md` is updated, refresh `docs/current.md` to reflect the new state:

1. **Current Phase:** Scan `task.md` for the first Phase with unfinished subtasks. If all Phases are done, note "All phases complete."
2. **Current Task:** Within the current Phase, find the first Task with unfinished subtasks.
3. **Current SubTask:** Within that Task, find the first ⬜ SubTask. If the current subtask is 🔄, keep it as the current subtask.
4. **Current Blocker:** Check if the current subtask is ⏸️. If so, set the blocker to the reason noted in `task.md`. If a different blocker came up in conversation, record it.
5. **Next Step:** Derive from the current subtask — what's the concrete first action? Make it specific and actionable.
6. **Important Decisions:** If new decisions were made during the session, add a brief numbered summary. Keep the numbering sequential from the previous state. Only include genuinely important decisions — not every small choice.

**When updating current.md, preserve the format exactly.** Replace only the values, not the structure or labels.

### Step 6: Update `decision.md` (if applicable)

If the conversation includes a significant new decision that isn't already in `decision.md`:

1. Read the current `decision.md` to find the last decision number.
2. Append a new entry following the exact template format (Context → Decision → Rationale → Alternatives Considered).
3. Add the decision to the Table of Contents.

**Only add decisions that have lasting relevance.** Trivial choices don't need recording.

### Step 7: Check for design/plan changes

Review the conversation analysis from Step 2c for evidence that design or plan topics were discussed during the session:

- Architecture decisions, component design, data model changes, technology choices
- Timeline/milestone changes, scope adjustments, new dependencies, roadmap shifts

**If evidence exists** — the conversation touched on design or planning:

> We discussed design/plan topics this session (e.g., `<brief example>`). Do `docs/design.md` or `docs/plan.md` need updates? If so, which specific sections should I update, and what changed?

**If no evidence** — design and plan were not discussed:

Skip to Step 8. No prompt is needed.

---

When the user names specific sections to update:
- Read only that section of `design.md` or `plan.md`.
- Append the new information at the end of the specified section. **Never replace or rewrite the section.**
- If the user asks about something that would require restructuring the whole file, recommend they edit it manually instead.

### Step 8: Check CLAUDE.md / AGENTS.md

If the session changed anything these files describe (project layout, commands, conventions, tech choices), point out the stale parts and ask the user whether to update them. Never rewrite the whole file; skip silently if nothing is stale or neither file exists.

### Step 9: Output change summary

Present a clear summary of everything that was updated:

```
Checkpoint saved.

docs/task.md:
  ✅ Implement basic squash logic
  🔄 Add interactive mode for selecting commits

docs/current.md:
  Current SubTask → "Add interactive mode for selecting commits"
  Next Step → "Integrate bubbletea TUI library and build commit selection UI"

docs/decision.md:
  + Decision 4 — Use bubbletea over fyne for interactive TUI

Design/plan: no changes discussed. To update, tell me which sections to edit.
```

If nothing changed, say so honestly:

> No changes detected. The project state appears to already be up to date.

## Edge Cases

- **`docs/` doesn't exist or is incomplete**: tell the user to run `project-bootstrap` first. Exit.
- **No changes detected**: report honestly. Don't fabricate updates.
- **Git repo has no commits yet**: use `git diff --stat` (unstaged changes) and conversation analysis. Mention that the lack of commit history limits context.
- **SubTask in conversation doesn't exist in task.md**: don't add it silently. Ask: "I noticed work on X, but it's not in task.md. Should I add it? Under which Task/Phase?"
- **Multiple SubTasks map to the same changed files**: ask the user which subtask the work corresponds to, or mark the most specific match.
- **User asks to update design.md with a major restructure**: refuse politely. "That kind of change would rewrite most of the file. Please edit design.md manually — this skill only appends to specific sections."
- **Partial work on a subtask without clear completion**: mark as 🔄 (in_progress), not ✅. Err on the side of less-done.
- **The user asks the skill to infer too much**: if the evidence is thin and the user is asking for a full project analysis, push back. This skill checkpoints what happened — it doesn't re-derive the entire project plan from scratch.

## What This Skill Does NOT Do

- **Does not rewrite design.md or plan.md in full.** Only appends to user-approved sections.
- **Does not create new tasks or reorder existing ones without asking.**
- **Does not auto-trigger.** The user must invoke this skill explicitly.
- **Does not initialize docs/.** That's `project-bootstrap`'s job.
- **Does not execute code or modify project source files.** It only updates docs/ context files.
