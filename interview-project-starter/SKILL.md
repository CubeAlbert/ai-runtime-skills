---
name: interview-project-starter
description: Analyze a project requirements document and generate a complete implementation plan for software engineering interviews. Reads one requirements file from docs/ (requirements.txt/md/docx/pdf), infers tech stack, breaks down work into prioritized tasks (core / bonus / extension), and produces docs/design.md, docs/plan.md, docs/task.md, docs/current.md, docs/decision.md, and CLAUDE.md — all compatible with project-bootstrap and project-checkpoint. This skill must be explicitly invoked by the user. Trigger when the user says "analyze the requirements", "start the interview project", "set up the project plan", "help me understand what to build", "开始面试项目", "分析需求", or similar explicit requests to turn a requirements document into a structured implementation plan. Also trigger when the user mentions they have a coding interview project and need to break it down.
---

# Interview Project Starter

Turn a single requirements document into a complete, prioritized implementation plan — optimized for software engineering interviews where the candidate uses an AI coding tool.

The skill produces all five `docs/` context files (compatible with `project-bootstrap` for restoring state and `project-checkpoint` for saving progress) plus a `CLAUDE.md` that drives implementation in the next session.

## Design Philosophy

This skill is built for **interview time pressure**. It makes opinionated, reasonable choices rather than asking the user to decide every detail. It prioritizes ruthlessly: core functionality comes first, polish comes later, and speculative features are noted but not scheduled.

**Key principles:**
- **No over-speculation.** If the requirement says "user login", don't build a frontend login form unless the requirements mention UI, testing, demo, or user-facing interaction.
- **Direct output.** Write everything without waiting for user confirmation. The candidate needs to see the plan and move on.
- **Infer and document.** Make reasonable tech-stack inferences from the requirements. When you make a judgment call, record it in `decision.md` so the reasoning is visible to the interviewer.

## Prerequisites

- A single requirements file at `docs/requirements.{txt,docx,pdf,md}`.
- The file must be the **only** requirements file in `docs/`. If there are multiple, the skill cannot determine which one to use.

## Workflow

### Step 1: Locate the requirements file

List all files in `docs/` and look for exactly one file matching `requirements.*` (any extension).

| Situation | Action |
|-----------|--------|
| No `docs/` directory | Create `docs/` and tell the user: "No `docs/` directory found. I created it. Please place your requirements file as `docs/requirements.txt` (or `.md`) and run this skill again." |
| No requirements file | Tell the user: "No `requirements.*` file found in `docs/`. Please add your requirements document as `docs/requirements.txt` (or `.md`, `.docx`, `.pdf`) and run this skill again." |
| Multiple requirements files | Tell the user: "Found multiple requirements files in `docs/`: [list them]. Please keep only one and run this skill again." |
| One requirements file | Continue to Step 2. |

### Step 2: Read the requirements

Read the requirements file.

- **`.txt` or `.md`**: read directly.
- **`.docx`**: attempt to extract text. If tools are unavailable → tell the user: "I can't parse `.docx` files in this environment. Please convert your requirements to `.txt` or `.md` and run this skill again."
- **`.pdf`**: attempt to extract text. Same fallback as `.docx` — if parsing fails, ask the user to convert.

### Step 3: Analyze the requirements

Extract the following from the requirements document:

1. **Project summary** — one paragraph: what this project is, who it's for, the core problem it solves.
2. **Core features** — what the system must do. These are non-negotiable; the project fails without them.
3. **Bonus features** — things that improve quality: error handling, input validation, logging, tests, edge-case handling. Also include: if the requirements mention testing, UAT, demo, or user interaction, add a minimal UI (CLI or web) for verification.
4. **Extension ideas** — what could come next. These are NOT scheduled for implementation, but noting them shows the interviewer you see the bigger picture.
5. **Tech stack** — infer from the requirements. Look for clues: file formats mentioned, API styles described, database references, language hints. If the requirements are silent, default to a reasonable modern stack (e.g., Python + FastAPI for backend, React for frontend if UI is needed). Record the rationale in `decision.md`.
6. **Constraints** — any hard limits: time, technology, performance, platform.

**Classification rules:**

```
🔴 Core    — Requirement explicitly asks for it. Project doesn't work without it.
🟡 Bonus   — Quality, robustness, testability. Do if time allows.
🟢 Extension — Not implemented. Shows architectural thinking.
```

**The "no over-speculation" rule:** If the requirements say "implement user authentication", the core tasks are: User entity/model, registration endpoint, login endpoint, session/token management. Do NOT add "login frontend page" unless the requirements mention UI, frontend, testing, demo, UAT, or any user-facing interaction. When in doubt, stay minimal — it's easier for the candidate to add scope than to explain why they built something not asked for.

### Step 4: Design the task breakdown

Organize work into **Phases → Tasks → SubTasks** following a logical build order:

- **Phases** are sequential. Complete Phase 1 before starting Phase 2.
- **Tasks** within a phase can be parallel if they don't depend on each other.
- **SubTasks** are the smallest concrete unit of work — one clear action.

Ordering rules:
1. Foundation first (project setup, database schema, core data models).
2. Core features in dependency order (what needs to exist before what).
3. Bonus features after all core features are done.
4. Extension ideas are listed but not scheduled as tasks.

### Step 5: Generate the output files

All generated files follow the exact formats expected by `project-bootstrap` and `project-checkpoint`. Read the bundled templates in `assets/` for the exact format of each file before writing.

#### 5a. `docs/design.md`

Read the template from `assets/design.md`. Fill in:

- **Project Description** — from Step 3 analysis.
- **Architecture Design** — tech stack, system boundaries, data flow. Include rationale for each major choice.
- **Project Structure** — annotated directory tree showing where everything goes.
- **Module Design** — one subsection per module. Include purpose, responsibilities, key interfaces, and design decisions.

#### 5b. `docs/plan.md`

Read the template from `assets/plan.md`. Fill in:

- **Milestones** — each maps to a Phase in `task.md`. Include expected output, acceptance criteria (concrete and verifiable), and dependencies.
- **Key Dependencies** — external services, cross-cutting technical prerequisites.

#### 5c. `docs/task.md`

Read the template from `assets/task.md`. Fill in:

- One Phase per milestone.
- Tasks and SubTasks from Step 4.
- Tag each SubTask with its priority: **🔴**, **🟡**, or **🟢**.
- All SubTasks initially marked **⬜** (pending).
- Extension ideas go in a separate final section: `## Extensions (not scheduled)` — these are bullet points, not tasks.

Example structure:

```
## Phase 1 — Project Setup & Data Layer

### 1. Project Scaffolding

- ⬜ 🔴 Initialize project with build tool and directory structure
- ⬜ 🔴 Configure linting and formatting

### 2. Database & Core Models

- ⬜ 🔴 Design and create the database schema
- ⬜ 🔴 Implement the User entity/model
- ⬜ 🟡 Add database migration tooling

## Phase 2 — Core Features

### 1. Authentication

- ⬜ 🔴 Implement user registration endpoint
- ⬜ 🔴 Implement login endpoint with token/session management
- ⬜ 🟡 Add input validation and error handling
- ⬜ 🟡 Write unit tests for auth endpoints

## Extensions (not scheduled)

- 🟢 Role-based access control — once auth is stable, add user roles and permissions
- 🟢 Rate limiting — protect endpoints from abuse in production
```

#### 5d. `docs/current.md`

Read the template from `assets/current.md`. Fill in:

- **Current Phase** — Phase 1 from task.md.
- **Current Task** — first Task in Phase 1.
- **Current SubTask** — first SubTask in that Task.
- **Current Blocker** — None (the project is starting fresh).
- **Next Step** — the concrete first action. Make it specific (e.g., "Run `npm init` and install dependencies" or "Create the project directory structure").
- **Important Decisions** — numbered summary from `decision.md`, keeping only the most impactful ones.

#### 5e. `docs/decision.md`

Read the template from `assets/decision.md`. Record:

- Tech stack choices and rationale.
- Architecture tradeoffs that affect the project.
- Any assumptions made during analysis (e.g., "Assumed REST API — requirements didn't specify GraphQL vs REST").

Each decision gets: Context → Decision → Rationale → Alternatives Considered.

#### 5f. `CLAUDE.md`

Overwrite `CLAUDE.md` completely. This is the entry point for the next session — `project-bootstrap` reads `docs/` to restore context, and `CLAUDE.md` drives the AI's behavior during implementation.

**If `CLAUDE.md` already exists:** tell the user: "`CLAUDE.md` already exists in this project. This skill generates a fresh CLAUDE.md for the interview project. Please remove or rename the existing CLAUDE.md and run this skill again."

Content structure:

```markdown
# [Project Name]

[One-paragraph description from Step 3]

## Tech Stack

- **Backend:** [language + framework]
- **Database:** [database]
- **Additional:** [other key tools]

## Getting Started

[How to start working — the first concrete action. Link to docs/current.md for full context.]

## Project Structure

[Annotated directory tree from design.md, kept brief]

## Task Overview

[Table: Phase | Task | Priority | Status — from task.md. Just Phase and top-level Tasks, not every SubTask.]

## Key Decisions

[2-3 most important decisions from decision.md, one line each]

## Documentation

- Current state: `docs/current.md`
- Full design: `docs/design.md`
- Implementation plan: `docs/plan.md`
- Task breakdown: `docs/task.md`
- Decision log: `docs/decision.md`
```

Keep CLAUDE.md under 100 lines. It's a map, not the territory — pointers to `docs/` for details.

### Step 6: Output the summary

After writing all files, present a structured summary:

```
Interview project plan generated.

📁 Files created:
  docs/design.md       — Architecture, tech stack, module design
  docs/plan.md         — Milestones, acceptance criteria, dependencies
  docs/task.md         — Prioritized task breakdown (🔴 core / 🟡 bonus / 🟢 extension)
  docs/current.md      — Current state snapshot (ready for project-bootstrap)
  docs/decision.md     — Key decisions and rationale
  CLAUDE.md            — Entry point for implementation

📋 Task breakdown:
  Phase 1 — [name]: N tasks, M subtasks
  Phase 2 — [name]: N tasks, M subtasks
  ...

🔴 Core:     X subtasks
🟡 Bonus:    Y subtasks
🟢 Extension: Z ideas

Next: Review the plan, then run project-bootstrap to restore context
or start a new session to begin implementation. The CLAUDE.md and
docs/ files will guide the AI through each task in priority order.
```

## Edge Cases

- **`docs/` doesn't exist**: Create it, then tell the user to place their requirements file and re-run.
- **Requirements file is unreadable (corrupted, wrong format, binary)**: Tell the user to replace it with a valid `.txt` or `.md` file.
- **Requirements are ambiguous or underspecified**: Make reasonable assumptions, document them in `decision.md`, and proceed. In an interview context, showing you can make decisions with incomplete information is a positive signal.
- **Requirements are overly complex for a single session**: Call this out in the summary. Suggest which phases are achievable and which might need scoping down. The task breakdown still covers everything, but the summary should be honest about effort.
- **`CLAUDE.md` already exists**: Block and tell the user to remove/rename it before re-running. This skill generates a fresh CLAUDE.md for the interview project — merging is out of scope.
- **`docs/` files already exist from a previous run**: Overwrite them. This skill initializes — project-checkpoint is for incremental updates.
- **Requirements mention a specific tech stack**: Use exactly what's specified. Don't second-guess the interviewer's choices.
- **Requirements don't mention a tech stack**: Infer from context clues. If there are none, default to a pragmatic modern stack and document the reasoning.

## What This Skill Does NOT Do

- **Does not write implementation code.** It produces plans and documentation only. The actual coding happens in the next session, driven by CLAUDE.md and `docs/`.
- **Does not update existing docs/ files incrementally.** That's `project-checkpoint`'s job. This skill initializes from scratch.
- **Does not handle multiple requirements files.** One file, one project, one plan.
- **Does not auto-trigger.** The user must invoke this skill explicitly.
- **Does not run project-bootstrap after generating files.** The user should do that manually in a fresh session.
