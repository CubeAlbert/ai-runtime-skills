---
name: writing-task-manager
description: Persist and manage writing-task TODOs (papers, articles, essays, resumes) in a `.writing-tasks/` folder that mirrors the project layout, with a `writing-task-manager.md` index listing only files with unfinished work. The skill has two modes — **(1) Check**: show unfinished and in-progress tasks for a writing project; **(2) Record**: store a TODO list that the agent has already produced from upstream analysis into the persistent task files. The skill does not decompose goals or re-analyze — it stores and manages what is already in context. Use this skill whenever the user is working on a written document and wants to track TODOs across sessions, or whenever they want to add, mark in-progress, mark finished, or review writing tasks. Trigger on phrases like "save these tasks", "track these TODOs", "add a task to ...", "mark X as done", "mark X as in progress", "what's still open", "show my todo list", or any time the user has multiple writing TODOs to manage. Do not use for code/software tasks.
---

# Writing Task Manager

A persistence layer for TODOs that come out of long-form writing work (papers, articles, essays, resumes). The agent's *analysis* produces the todo list; **this skill** stores, indexes, and updates those todos on disk so they survive across sessions and stay usable despite short context windows.

The skill is strictly mechanical — it does **not** re-decompose, re-evaluate, or interpret the content of tasks. It moves task text in and out of files and keeps the index in sync.

## Storage Layout

The skill creates and maintains the following structure under the **project root** (the directory the agent was invoked from):

```
<project-root>/
└── .writing-tasks/
    ├── writing-task-manager.md   # Index: one line per file with unfinished work
    └── <mirrored-path>/...       # Per-file task lists, mirroring the project tree
        └── <source-file-name>    # (e.g., a.txt mirrors ./<path>/a.txt)
```

**Mirroring rule:** if the source file is `<project-root>/aa/bb/c.txt`, its task file is `<project-root>/.writing-tasks/aa/bb/c.txt`. Path components are preserved verbatim (just relocated under `.writing-tasks/`); the leaf filename is unchanged.

Example project:

```
my-paper/
├── intro.md
├── chapters/
│   └── methods.md
└── .writing-tasks/
    ├── writing-task-manager.md
    ├── intro.md
    └── chapters/
        └── methods.md
```

## Task File Format

Each per-file task file (e.g., `.writing-tasks/aa/bb/c.txt`) is a plain Markdown list. Three states:

| Marker | State      | Meaning                                            |
| ------ | ---------- | -------------------------------------------------- |
| `[ ]`  | Unfinished | Task has been recorded but work has not started.   |
| `[~]`  | Partial    | Work is in progress but paused. Remind the user.   |
| `[x]`  | Finished   | Work is done. Kept in the file as a record.        |

Example `.writing-tasks/chapters/methods.md`:

```markdown
- [ ] Rewrite the sampling paragraph for clarity
- [~] Add the new citation from Smith 2024
- [x] Fix typo in the section heading
```

The agent (or user) chooses the initial marker when adding a task. The skill changes markers in response to user commands — it never decides them on its own.

## Index File Format

`writing-task-manager.md` lists **only files that still have unfinished work**. One line per file, sorted by path ascending (case-insensitive). When a file's task file no longer contains any `[ ]` or `[~]` lines, its line is removed from the index.

On Linux/macOS:

```markdown
# Writing tasks

- [ ] ./aa/bb/c.txt
- [ ] ./chapters/methods.md
- [ ] ./intro.md
```

On Windows:

```markdown
# Writing tasks

- [ ] .\aa\bb\c.txt
- [ ] .\chapters\methods.md
- [ ] .\intro.md
```

Notes:
- The `- [ ]` checkbox on the index line is part of the format — it is *not* a task to be checked off, just a visual marker.
- Use the OS-native path separator throughout (`/` on Linux/macOS, `\` on Windows). The leading `./` or `.\` prefix is part of the format.
- Sorting: ascending, lexicographic, case-insensitive. The agent must keep the index sorted on every change.

## Path Resolution

The "project root" is the directory the agent was invoked from. The skill does not search upward for a `.writing-tasks/` folder — it always uses the invocation root. The user is expected to always launch the agent from the project root, not from a subfolder.

Path separators follow the host OS:

- **Windows**: use `\` (e.g., `chapters\methods.md`, `.\aa\bb\c.txt`).
- **Linux / macOS**: use `/` (e.g., `chapters/methods.md`, `./aa/bb/c.txt`).

The agent should use the runtime's native path-handling tools (`os.path.join`, `pathlib.Path`, etc.) so the skill works the same on all three platforms. The storage folder itself is always named `.writing-tasks` (the leading dot is part of the name, not a separator) and is the same string on every OS.

- If the user names a file with a relative path, use it as-is.
- If the user names an absolute path, convert to a path relative to the project root before mirroring.

## Workflow

The skill runs in two modes:

- **Mode 1 — Check**: the user wants to see unfinished or in-progress work.
- **Mode 2 — Record**: the user wants to add new tasks to the persistent store.

A single activation may combine a mode-1 read with a mode-2 write. Marking a task in progress or finished is a small update that can run alongside either mode.

These operations are idempotent.

### Step 0 — Identify the mode

Read the user's request. Decide which mode(s) apply:

- Phrases like "what's still open?", "show my todo list", "what's left?", "show pending" → **Mode 1: Check**.
- Phrases like "save these tasks", "track these TODOs", "add a task to ...", "record these", "log this" → **Mode 2: Record**.
- Phrases like "mark X as done", "mark X as in progress", "I finished X" → an **Update** that can accompany either mode.

If the request is ambiguous, ask the user. Default to **Mode 1** if the user's intent is unclear and the index is non-empty; default to **Mode 2** if the index is empty.

### Step 1 — Always-on partial reminder

At the **start** of every activation, scan all task files under `.writing-tasks/` for any `- [~]` line. If any are found, surface them to the user and **wait for a decision before continuing**:

> You have partial work on the following tasks. The only way to dismiss a partial is to mark it as finished. For each one: continue (keep `[~]`), or mark it `[x]`?
>
> - `<source_path>`: <description>
> - ...

The user must respond to each partial before the rest of the activation proceeds. The reminder cannot be skipped — it runs on every activation without exception.

If there are no partials, this step is silent.

### Step 2 — Initialize (Mode 2 only, lazy)

Check for the storage layout. If anything is missing, create it:

1. Create `.writing-tasks/` in the project root if it does not exist.
2. Create `.writing-tasks/writing-task-manager.md` with the header `# Writing tasks` and an empty body if it does not exist.

This step is a no-op when the structure already exists.

### Step 3 — Pre-check for tasks in context (Mode 2 only)

Mode 2 assumes the task list is already in the conversation context — produced by upstream analysis done by the agent, or supplied directly by the user.

Look at the conversation context. Is there a TODO list (or a list of writing tasks) present?

- **Yes** → continue to Step 4.
- **No** → ask the user:
  > I don't see a task list in context. Do you have detailed tasks I should record, or should I start the analysis first?
  - **User has detailed tasks** → take them as input, continue to Step 4.
  - **User wants analysis first** → exit the skill. The agent runs the analysis, and the next activation of this skill will find the resulting list in context.
  - **User has neither** → exit cleanly. Do not write any files (Step 2 is also rolled back if it was just created for this request — see "No tasks in context" in Edge Cases).

### Step 4 — Add tasks (Mode 2 only)

Input shape: a list of `{ source_path, description }` pairs, where `source_path` is the project-relative path of the file the task applies to, and `description` is the task text.

For each item:

1. Compute the mirrored task file path: `.writing-tasks/<source_path>`.
2. Read the task file if it exists.
3. **Check for duplicates.** If the task file already contains a line whose description (text after the marker and one space) matches `description` exactly, **skip this item** — do not append. Duplicate detection covers all three states (`[ ]`, `[~]`, `[x]`); the goal is to never record the same task twice.
4. If no duplicate and the file does not exist, create it (and any missing parent directories).
5. Append a new line: `- [ ] <description>` (use the user's exact wording for the description).
6. After processing all items, ensure the index has a line `- [ ] .<sep><source_path>` (where `<sep>` is the OS-native separator) for every distinct `source_path` that now contains at least one `[ ]` or `[~]` line.
7. Re-sort the index ascending by path (case-insensitive, lexicographic).

Do not edit existing task lines during an add — append only, after the dedup check.

### Step 5 — Show open work (Mode 1 only)

Used when the user asks "what's still open?" or similar.

1. Read `writing-task-manager.md`.
2. If empty, report: "No open writing tasks."
3. Otherwise, display the file contents as-is.

### Step 6 — Mark task in progress (Update)

Used when the user wants to indicate they have started working on a task.

Input: `source_path` and a way to identify the specific task — either the exact description text or its 1-based line number in the task file.

1. Find the matching `- [ ]` line in `.writing-tasks/<source_path>`.
2. Change the marker to `- [~]`.
3. Confirm the change back to the user.

If the line is already `[~]` or `[x]`, report the current state — do not change it.

### Step 7 — Mark task finished (Update)

Used when the user wants to mark a task as done.

Input: `source_path` and either the exact description text or its 1-based line number.

1. Find the matching `- [ ]` or `- [~]` line in `.writing-tasks/<source_path>`.
2. Change the marker to `- [x]`. The line stays in the task file as a record.
3. Re-read the task file. If it now contains no `[ ]` or `[~]` lines, remove the corresponding line from `writing-task-manager.md`.
4. Re-sort the index if any change was made.
5. Confirm the change back to the user.

If the line is already `[x]`, report the current state — do not change it.

## Edge Cases

- **No `.writing-tasks/` folder**: Step 2 (Initialize) creates it lazily when needed.
- **Source path contains a directory that does not exist on disk**: still create the mirrored path under `.writing-tasks/`. The skill does not require the source file to exist.
- **Adding a duplicate description**: Step 4 checks for exact-text matches in the target task file and skips duplicates across all three states (`[ ]`, `[~]`, `[x]`). The user will not see the same task recorded twice.
- **Index sort drift**: always re-sort the index after any add or finish. Use a stable, case-insensitive ascending sort.
- **The user provides a task with no source path**: ask. Every task must belong to a file.
- **No tasks in context at activation (Mode 2)**: Step 3 takes over. Do not write any files. If Step 2 ran first and the user then has no tasks to record, leave the freshly-created `.writing-tasks/` folder and `writing-task-manager.md` empty rather than removing them — they are harmless and may be used by a future activation. Do not assume an empty task list is a valid input.
- **Multiple skills touching `.writing-tasks/`**: this skill owns that directory. Other skills should not write to it.
