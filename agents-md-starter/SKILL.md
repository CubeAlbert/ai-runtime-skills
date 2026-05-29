---
name: agents-md-starter
description: Initialize or generate an AGENTS.md file for a project that doesn't have one. Use this skill whenever the user wants to create, initialize, or generate an AGENTS.md for their project, when they mention AGENTS.md setup, when they want to document their project for AI agents, or when you notice the project has no AGENTS.md and the user asks about project documentation. Also trigger when the user asks to "set up AGENTS.md", "add AGENTS.md to the project", or similar phrases in any language.
---

# AGENTS.md Starter

Generate a project-specific `AGENTS.md` by analyzing the codebase and filling in the bundled template. The goal is to produce an AGENTS.md that accurately describes the project so both humans and AI agents can onboard quickly.

## Bundled Resources

- `assets/AGENTS.md` — English template with all standard sections
- `assets/AGENTS.zh-CN.md` — Chinese template (mirrors the English structure)

Load the appropriate template at the start of each invocation. Never hardcode the template content — always read it from `assets/`.

## Prerequisites

This skill requires the following CLI tools to be installed in the execution environment:

| Tool | Used in | Purpose |
|------|---------|---------|
| `git` | 3a, 3b, 3g | `git remote -v` for repo name, `git ls-files` for generated files, `git log` / `git branch` for branch and commit conventions |

All file-reading operations (config files, build manifests, directory listings) are handled by the agent runtime's built-in tools and do not require additional CLI dependencies.

---

## Workflow

### Step 1: Check for existing AGENTS.md

Check if `AGENTS.md` exists in the project root. If it does:
- Show the user the first 10-15 lines so they can assess it.
- Ask: "AGENTS.md already exists. Overwrite it or skip?" Do not proceed until the user answers. If running in a non-interactive environment, default to **skip** (preserve the existing file).

### Step 2: Detect language

Determine the document language with the following priority:

1. **README signal** (most reliable): Read the first 20-30 lines of the project README to detect its primary language. This reflects the project's target audience.
2. **Conversation signal** (fallback): If no README exists, use the user's natural language from the conversation, filtering out technical terms.

- **Chinese (中文)** → use `assets/AGENTS.zh-CN.md`
- **Other / English** → use `assets/AGENTS.md`

If still ambiguous in an interactive environment, ask the user.

**Non-interactive mode**: Use the same README-based detection. If the README cannot be read or its language is ambiguous, default to **English** (`assets/AGENTS.md`).

### Step 3: Analyze the project

Systematically gather information. Run independent checks concurrently if the runtime supports it; otherwise sequential execution is acceptable. Limit file reads to what's necessary: structured config manifests (e.g., `package.json`, `go.mod`, `Cargo.toml`) may be read in full; for source code analysis (3h), read at most 3-5 representative files.

Collect the following:

If a git command fails (e.g., git is not installed, the project is not a git repository, or there are no commits yet), skip that specific check gracefully and use the next-best information source or leave the corresponding AGENTS.md section commented out.

#### 3a. Identity & Purpose
- **Project name**: Check `git remote -v` for the repo name, then `package.json` → `name`, `Cargo.toml` → `[package] name`, `go.mod` → module path, `pyproject.toml` → `[project] name`, `pom.xml` → `<artifactId>`, or the root directory name as fallback.
- **Description**: Check README (first 50 lines), `package.json` → `description`, `Cargo.toml` → `[package] description`, `pyproject.toml` → `[project] description`.

#### 3b. Tech Stack & Dependencies
Look for these files and extract version constraints:
| File | Extracted info |
|------|---------------|
| `go.mod` | Go version (`go 1.22`), module path |
| `package.json` | Node/npm version (`engines`), type (`module`/`commonjs`) |
| `pyproject.toml` | Python version (`requires-python`), build system |
| `Cargo.toml` | Rust edition |
| `pom.xml` / `build.gradle` | Java version |
| `Gemfile` | Ruby version |
| `*.csproj` | .NET version |
| `Dockerfile` | Runtime & system deps |

Also check for multiple languages (monorepo with `frontend/` + `backend/` etc.).

Identify the package manager and lock file(s): `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `go.sum`, `Cargo.lock`, `poetry.lock`, `Gemfile.lock`. Note any vendored or in-tree dependencies.

Check for code generation setup and generated files: protobuf, GraphQL, OpenAPI, gRPC. Run `git ls-files` to detect generated file patterns (e.g., `.pb.go`, `_generated.ts`).

#### 3c. Build & Run
- Look for build/run scripts in `package.json` → `scripts`, `Makefile`, `Justfile`, `Taskfile`.
- Check for common build tool configs: `webpack.config.*`, `vite.config.*`, `tsconfig.json`, `Makefile`.
- Identify the build artifact path if obvious (e.g., `dist/`, `target/`, `build/`).

#### 3d. Test
- Look for test scripts: `package.json` → `scripts.test`, `Makefile` test targets, pytest config, `jest.config.*`, `vitest.config.*`.
- Identify the testing framework from dependencies (`jest`, `mocha`, `pytest`, `JUnit`, `testing` package in Go).
- Check for test directories: `tests/`, `__tests__/`, `spec/`, `*.test.*` file patterns.

#### 3e. Lint & Format
- Check for config files: `.eslintrc.*`, `.prettierrc*`, `.golangci.yml`, `.rubocop.yml`, `pylintrc`, `clippy.toml`, `.editorconfig`.
- Find format/lint commands in `package.json` scripts or `Makefile`.

#### 3f. Project Layout
- List the top-level directory tree (2 levels deep max).
- Identify key directories: source code, tests, docs, config, scripts, deployment.
- For monorepos, note which directory handles which language/responsibility.

#### 3g. CI/CD & Branching Conventions
- Check for CI config files: `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `azure-pipelines.yml`, `circleci/`. Note CI dashboard URL if discoverable.
- Check git branching and commit conventions: run `git log --oneline -20` and `git branch -a` to infer patterns (e.g., `feature/*`, `fix/*`, conventional commits).

#### 3h. Error Handling & Logging
- Read 3-5 representative source files (e.g., entry points or core modules) to detect error handling patterns (custom error types, error wrapping, panic vs. return).
- Check for logging libraries and patterns.

### Step 4: Fill the template

Read the chosen template file from `assets/`. Then fill each section:

1. **Replace placeholders** like `[PROJECT_NAME]`, `[command to build]`, `[all-test command]` with concrete values found during analysis.
2. **Delete the template note**: Remove the `**Note**: This is a template — delete any section...` line early.
3. **Delete inapplicable sub-sections**: If a subsection is entirely irrelevant (e.g., "Cross-Platform Compliance" for a web app that only targets one platform), delete it cleanly.
4. **Comment out unknown sections**: If you cannot determine what to put in a section and the user hasn't clarified, wrap it in HTML comments `<!-- ... -->` rather than deleting. This preserves the template structure for the user to fill in later.

#### Section-specific guidance

- **Getting Started / Prerequisites**: List the actual runtime version detected (e.g., `Go 1.22+`), and any system libraries that are obvious from the codebase. Omit "Local Infrastructure" if no Docker/database is detected.
- **Build & Run**: Provide the exact commands, not placeholders. If there are multiple build variants (dev/prod), list both.
- **Test**: Provide the exact test commands. If no test framework is detected, comment out the test section.
- **Project Layout**: Draw the actual directory tree from your analysis, with brief annotations for each top-level directory.
- **Code Style & Quality**: Fill in the actual linter/formatter commands found. Keep the "Core Principle" about matching surrounding code.
- **Error Handling & Logging**: Describe the actual patterns observed in the codebase — don't guess.
- **Review & Landing Pipeline**: Fill in branching conventions from git log patterns. Comment out CI dashboard links unless found.
- **CI**: Fill in the actual CI config file location and common troubleshooting commands. Comment out if no CI is set up.
- **Key Rules**: NEVER delete or modify this section. These four rules are universal and should appear verbatim from the template.

### Step 5: Interactive clarification

Before writing the final file, present a summary of findings and ask about the remaining uncertain items. **If running in a non-interactive environment, skip this step** — proceed to Step 6 with any low-confidence sections wrapped in HTML comments.

1. **Show what you found**: Brief bullet list of detected tech stack, build commands, test framework, etc.
2. **Ask about gaps**: For each major section where you have low confidence, ask the user. Group questions efficiently — don't ask one at a time.
   - Example: "I couldn't find the test command for the `backend/` module. What command runs those tests?"
   - Example: "Is there a CI dashboard URL you'd like me to include?"
3. **Respect the user's answers**: If they say "I don't know" or "skip", comment out that section.

### Step 6: Write the file

Write `AGENTS.md` to the project root. After writing, show the user a brief summary of what was filled in and what remains commented out for their later attention.

---

## Critical Rules

1. **Never delete Section 6 (Key Rules / 核心原则).** These four rules must appear in every generated AGENTS.md, verbatim from the template.
2. **Comment out, don't delete.** When a section or sub-section cannot be filled with confidence, wrap it in `<!-- ... -->` so the user can find and complete it later. Only delete a section if it is truly inapplicable (e.g., "Cross-Platform Compliance" for a single-platform app).
3. **Read the templates at invocation time.** Do not hardcode template content into this skill — always read from `assets/` so the latest template is used.
4. **Be honest about confidence.** Distinguish clearly between "detected from the codebase" and "guessed based on convention." When presenting findings to the user, flag low-confidence items explicitly.

---

## Example: Interactive clarification

After analysis, present findings like this:

```
Here's what I found:

  - Project: "my-api" (Go 1.22, gin framework)
  - Build: `go build -o bin/server ./cmd/server`
  - Test: `go test ./...`
  - Lint: golangci-lint (config: .golangci.yml)
  - CI: GitHub Actions (.github/workflows/ci.yml)

A few things I'm unsure about:

  1. Are there system libraries required beyond what's in go.mod? (e.g., openssl, libgit2)
  2. What's your PR naming convention? (feature/*, fix/*, etc.)
  3. Do you have a CI dashboard URL you want included?
```

Then wait for the user's answers before writing the final file.

---

## Post-generation

After writing AGENTS.md, remind the user:
- Review the commented-out sections and fill them in when ready.
- The file should evolve with the project — update it when the build/test commands change.
- Delete the template note line if it still appears anywhere.
