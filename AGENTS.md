# ai-runtime-skills

Personal skill templates for AI agents. Compliant with the [AgentSkills.io specification](https://agentskills.io/specification).

## 1. Getting Started

### Prerequisites
- **Runtime / Toolchain**: None required. Skills are Markdown + YAML frontmatter files consumed by AI agent runtimes.
- **System Libraries**: None.
- **Local Infrastructure**: None.

<!--
### Environment Setup
No configuration or initialization steps required.
-->

### Build & Run
There is no build step. Skills are consumed directly by AI agents at runtime — no compilation or packaging needed.

### Test
```bash
# Validate a skill's frontmatter and naming conventions
skills-ref validate ./<skill-directory>
```
Manual validation only. No automated test suite.

---

## 2. Project Layout

```text
ai-runtime-skills/
├── agents-md-starter/       — Skill: generate AGENTS.md files for projects
│   ├── assets/              — Bundled AGENTS.md templates (EN, ZH-CN)
│   └── SKILL.md             — Skill definition (YAML frontmatter + workflow)
├── LICENSE                  — MIT license
├── README.md                — Project overview
└── AGENTS.md                — This file
```

Each skill is a top-level directory following the AgentSkills.io structure:

```text
skill-name/
├── SKILL.md          # Required: YAML frontmatter + Markdown instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: additional documentation
├── assets/           # Optional: templates, images, data files
└── ...               # Any additional files or directories
```

### Dependencies & Codegen
- **Package Manager**: None. This is not a software package — skills are self-contained directories.
- **In-tree / Vendored Deps**: None.
- **Generated Code**: None.

---

## 3. Architecture & Code Conventions

### Skill Format
- **Spec**: All skills follow the [AgentSkills.io specification](https://agentskills.io/specification).
- **Required frontmatter**: `name` (lowercase, hyphens, max 64 chars, must match directory name) and `description` (max 1024 chars, describes what the skill does and when to use it).
- **Optional frontmatter**: `license`, `compatibility`, `metadata`, `allowed-tools`.
- **Body**: Free-form Markdown. Recommended sections: step-by-step instructions, examples, common edge cases.
- **Progressive disclosure**: Keep `SKILL.md` under 500 lines. Move detailed reference material to `references/`.

### Scripting
- **Default language**: Python. Use it for skill scripts unless there is a platform-specific reason to use something else.
- **Platform-specific**: Bash or PowerShell when the target platform dictates it.
- Scripts in `scripts/` should be self-contained and handle edge cases gracefully.

### Compatibility
- Skills should be **agent-agnostic**. Do not write skills that only work with a specific product — they should be usable by any agent runtime that supports the AgentSkills.io spec.

### Code Style & Quality
- **Core Principle**: Match the surrounding code. When a file does something one way and you're about to do it differently, understand *why* before deviating — the choice is usually load-bearing, not cosmetic.
<!--
- **Linting & Formatting**: No automated linting configured. Validate skills manually with `skills-ref validate ./<skill-directory>`.
-->

### Testing Conventions
- Manual validation only: `skills-ref validate ./<skill-directory>` checks frontmatter validity and naming conventions.
<!--
- **Framework & Assertions**: No test framework configured.
-->

### Error Handling & Logging
Not applicable — this is a content repository, not an application.

### Resource Lifecycle & Ownership
Not applicable.

<!--
### Cross-Platform Compliance (Optional)
Not applicable.
-->

---

## 4. Review & Landing Pipeline

### Before Submitting a PR
1. Run `skills-ref validate ./<skill-directory>` on any changed or new skill.
2. Verify the `name` field matches the skill's directory name.
3. Verify the `description` field describes both what the skill does and when to use it.

<!--
### Branching & PR Naming
No established conventions yet. Only one commit on main.
-->

<!--
### Code Review Workflow (Optional)
No automated review tooling configured.
-->

---

## 5. Continuous Integration (CI)

No CI/CD configured. Validation is manual:
```bash
skills-ref validate ./<skill-directory>
```

<!--
- **CI Dashboard**: None.
- **Local CI Emulation**: None.
-->

---

## 6. Key Rules

1. **Don't commit untested code.** If you didn't run the tests, it doesn't work.
2. **Don't overstate.** Be honest about what was done and what actually works. Document limitations.
3. **Read before you write.** Understand why the existing code made the choices it did before changing them.
4. **Fix the root cause, not the symptom.** Don't take a bug report's or AI's suggested quick-fix at face value — verify it addresses the right architectural layer.
