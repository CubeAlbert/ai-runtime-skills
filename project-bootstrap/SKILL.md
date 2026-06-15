---
name: project-bootstrap
description: Restore project context at the start of a new session by reading docs/current.md — a lightweight snapshot of the current goal, task, blocker, next step, and recent decisions. Loads docs/design.md, docs/plan.md, docs/task.md, and docs/decision.md on demand when deeper context is needed. Initializes the docs/ directory with templates if it doesn't exist. This skill must be explicitly invoked by the user — it does not auto-trigger. Trigger when the user says "bootstrap the project", "restore project state", "load project context", "continue where we left off", "what are we working on", "启动项目", "恢复上下文", or similar explicit requests to pick up work.
---

# Project Bootstrap

Restore project context from `docs/` at the start of a session. The skill is **read-only** — it loads state and presents it to the user, but another skill handles updating `current.md`.

A second skill (to be created separately) handles *updating* `docs/current.md` as work progresses. This separation keeps each skill focused: bootstrap reads and restores; the companion writes and updates.

## Files

| File | Role | When loaded |
|------|------|-------------|
| `docs/current.md` | Lightweight entry point — current goal, task, blocker, next step, key decisions | Every invocation |
| `docs/design.md` | Architecture and design decisions | On demand — when the LLM judges it needs deeper design context |
| `docs/plan.md` | Implementation plan, milestones, sequencing | On demand — when the LLM needs scheduling or roadmap context |
| `docs/task.md` | Task list with status tracking | On demand — when the LLM needs the full task breakdown |
| `docs/decision.md` | Decision log (optional) | On demand — when the LLM needs historical decision rationale |

**`current.md` is the entry point.** It should be short — just enough for the LLM to understand where the project stands. From there, the LLM decides whether it needs `design.md`, `plan.md`, `task.md`, or `decision.md` to answer the user's request.

Example: if `current.md` says the next step is "implement the /api/users endpoint", the LLM should read `design.md` for the API design. If it says the next step is "fill in the remaining route handlers" and the framework is already clear, the LLM may skip `design.md`.

## Bundled Resources

- `assets/current.md` — Template for the entry-point file
- `assets/design.md` — Template for design documentation
- `assets/plan.md` — Template for the implementation plan
- `assets/task.md` — Template for task tracking
- `assets/decision.md` — Template for the optional decision log

Always read templates from `assets/` at invocation time — never hardcode template content into this skill.

## Workflow

### Step 1: Check for `docs/` directory

Check if a `docs/` directory exists in the project root.

**If `docs/` does not exist:**
Ask the user:

> The `docs/` directory doesn't exist yet. This skill requires it to store project context files (`current.md`, `design.md`, `plan.md`, `task.md`, and optionally `decision.md`). Create it now?

- **User says no** → exit with: "Skipping bootstrap. The `docs/` directory is required for this skill. Create it manually or run this skill again when you're ready."
- **User says yes** → continue to Step 2 (initialize).

**If `docs/` exists:**

Continue to Step 3 (restore).

### Step 2: Initialize `docs/` directory

Create the directory and ask which files to set up:

1. Create `docs/` directory.
2. Ask the user:

> Which files should I initialize?
>
> Required (recommended):
> 1. `current.md` — current state snapshot (phase, task, subTask, blocker, next step)
> 2. `design.md` — architecture and design decisions
> 3. `plan.md` — implementation plan and milestones
> 4. `task.md` — task list with status tracking
>
> Optional:
> 5. `decision.md` — chronological log of important decisions
>
> I can create all five, or a subset. Which would you like?

If the user selects specific files, create only those from the templates in `assets/`. If the user says "all" or doesn't specify, create all five.

3. For each selected file, read the corresponding template from `assets/` and write it to `docs/`.
4. After initialization, output:

> `docs/` initialized with: [list of files created].
>
> Next: use the companion skill to fill in `current.md` with your project's actual state, or edit the files directly. Then run this skill again to restore context.

### Step 3: Restore project state

`docs/` exists. Check for the entry point:

1. **Try to read `docs/current.md`.**
   - If it doesn't exist → create it from `assets/current.md`, then inform the user:
     > `docs/current.md` was missing — I created it from the template. It has placeholder content. Use the companion skill to fill it in with your actual project state, then run this skill again.
   - If it exists but contains only placeholders (e.g., `[To be defined]` throughout) → inform the user:
     > `docs/current.md` exists but hasn't been filled in yet. Use the companion skill to populate it with your actual project state.
   - If it has real content → continue.

2. **Check for the three core files: `design.md`, `plan.md`, `task.md`.**
   - If **all three are missing** → ask:
     > `design.md`, `plan.md`, and `task.md` are all missing. Would you like me to create them from templates?
     - Yes → create from templates.
     - No → proceed with what's available.
   - If **some exist and some don't** → note the gaps in the output but proceed. Don't block — the user may not need all files.

3. **Check for `docs/decision.md`.**
   - If it exists → note it as available.
   - If it doesn't → don't prompt. This file is optional.

### Step 4: Determine output mode

Before outputting, decide whether this is a **restore** (real project state exists) or an **init** (files were just created from templates and contain no real content).

- **Restore mode** — when `current.md` has real content (not just created from template, not all placeholders). This means the project has been worked on before and state can be restored.
- **Init mode** — when `current.md` was just created from template in this invocation, or `current.md` exists but contains only placeholder values (`[To be defined]`, `[Phase name]`, `[SubTask description]`, etc.). This means the project is freshly initialized and has no real state to restore.

#### If Restore mode:

Present the project state in this exact format:

```
Project State Restored.

Current Phase:      <from current.md>
Current Task:       <from current.md>
Current SubTask:    <from current.md>
Current Blocker:    <from current.md, or "None">
Next Step:          <from current.md>
Important Decisions: <from current.md, or "None">

Available context files:
  docs/design.md     <present / not present>
  docs/plan.md       <present / not present>
  docs/task.md       <present / not present>
  docs/decision.md   <present / not present>

Waiting for instruction.
```

#### If Init mode:

Output:

```
Project Initialized.

Created files: <list the files that were created or already existed as templates>

Available context files:
  docs/current.md    <present / not present>
  docs/design.md     <present / not present>
  docs/plan.md       <present / not present>
  docs/task.md       <present / not present>
  docs/decision.md   <present / not present>

Next: use the companion skill to fill in current.md with your project's actual state, or edit the files directly. Then run this skill again to restore context.
```

### Step 5: Load additional context on demand

After presenting the state, the LLM decides whether it needs more context to handle the user's next request. This is a judgment call, not a fixed rule. The guiding principle: **load only what's relevant to the task at hand.**

- If the user's request involves architecture, structure, or API design → read `docs/design.md`.
- If the user asks about sequencing, milestones, or priorities → read `docs/plan.md`.
- If the user needs the full task breakdown or status → read `docs/task.md`.
- If the user asks about past tradeoffs or rationale → read `docs/decision.md`.

Don't load files preemptively. Wait for a concrete request, then decide what context is needed.

## Edge Cases

- **`docs/` has unrelated files**: ignore them. This skill only touches the five named files.
- **`current.md` was updated manually by the user**: reads it as-is. No validation beyond checking for placeholder content.
- **One of the core files is empty or corrupted**: note it in the output as "present but empty" and proceed.
- **User runs the skill when context is already loaded**: still go through the flow. The output serves as a checkpoint that both the user and LLM are aligned on the current state.
- **Non-interactive environments**: if Step 2 or Step 3 needs a user decision and stdin is unavailable, default to initializing all files and proceed.

## What This Skill Does NOT Do

- **Does not update `current.md`.** That's the companion skill's job. If the user asks to update the current state during the session, tell them to use the companion skill.
- **Does not create project files outside `docs/`.** This is not a project scaffolder — it only sets up the context-tracking files.
- **Does not auto-trigger.** The user must invoke this skill explicitly.
- **Does not execute tasks or modify code.** It restores context so the LLM can work effectively; it doesn't do the work itself.
