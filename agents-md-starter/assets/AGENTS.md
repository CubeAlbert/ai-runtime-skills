# [PROJECT_NAME]

[One-line summary of what this project does and its core objective].

**Note**: This is a template — delete any section or sub-section that does not apply to this project, then delete this line. Leaving inapplicable sections in place will confuse both human contributors and AI agents.

## 1. Getting Started

### Prerequisites
- **Runtime / Toolchain**: `[e.g., Go 1.22+, Node 20+, JDK 21]`
- **System Libraries**: `[e.g., openssl, build-essential, libgit2 / None]`
- **Local Infrastructure (Optional)**: `[e.g., Docker Desktop, LocalStack, MinIO — delete if purely stateless]`

### Environment Setup
1. **Configuration**: Copy `[.env.example / config.yaml.template]` to `[.env / config.yaml]` and adjust local variables.
2. **Initialization (Optional)**: `[Command to seed local DB, run initial setup scripts, or pull local certificates]`.
3. **Database / Schema Migrations (Optional)**: `[Command to bring local database/search index schema up to date]`.

### Build & Run
```bash
# Build a working binary or production artifact
[command to build]

# Run the application locally
[command to run]
```
- **Build Artifact Path**: `[path/to/output]`
- **Profiles / Variants**: `[e.g., --release, -Pprod, or environment flags if applicable]`

### Test
```bash
# Run all tests
[all-test command]

# Run a single test file / suite
[single-test command]

# Run tests matching a specific pattern/filter
[pattern-test command]
```
**Note**: [Specify if any mandatory wrapper, container environment, or flag is needed to pick up local changes during test runs].

---

## 2. Project Layout

```text
[root]/
├── [path]/             — [Purpose of this top-level directory]
├── [path]/             — [Purpose of this top-level directory]
└── [path]/             — [Purpose of this top-level directory]
```
*[Brief 1-2 sentence paragraph explaining the high-level organization of the repository to orient newcomers or AI tools].*

### Source Tree Structure
```text
[core_module]/          — [What lives here and why it is the core]
[domain_module]/        — [What domain logic or subsystem lives here]
```
- **Multi-language / Multi-subsystem Note**: [If applicable, explain which directory handles which language/responsibility, e.g., "frontend/ handles React UI, backend/ handles Go API"].

### Dependencies & Codegen
- **Package Manager**: `[e.g., go.mod / package.json / pom.xml]` located at `[path]`.
- **In-tree / Vendored Deps**: [List any vendored or private dependencies checked into source control, and why].
- **Generated Code**: [List auto-generated files (e.g., Protobuf, GraphQL clients), the command/script to regenerate them, and when it should be run].

---

## 3. Architecture & Code Conventions

### Code Style & Quality
- **Core Principle**: Match the surrounding code. When a file does something one way and you're about to do it differently, understand *why* before deviating — the choice is usually load-bearing, not cosmetic.
- **Linting & Formatting**: `[Command to format, e.g., cargo fmt / npm run lint]`. Run this before committing.

### Testing Conventions
- **Discoverability**: Place tests where they are most discoverable — alongside related tests or close to the code they exercise. Use new files when a feature is self-contained; prefer existing files when extending coverage for an already-covered area.
- **Framework & Assertions**: `[e.g., JUnit5 with AssertJ, pytest, Go standard testing library]`.
- **Anti-Patterns to Avoid**: `[e.g., Avoid hardcoded ports, don't use arbitrary time.Sleep() instead of awaiting conditions, avoid global state pollution]`.

### Error Handling & Logging
- **Error Policy**: [When to panic/crash vs. when to return errors; custom error types to use].
- **Logging Policy**: [Telemetry standards, when to use DEBUG/INFO/WARN/ERROR, and strict rules against logging sensitive data like PII, secrets, or tokens].

### Resource Lifecycle & Ownership
- **Lifecycle Management**: [How resources are acquired and released, e.g., RAII, defer, try-with-resources, explicit close() methods].
- **Ownership Rules**: [Who is responsible for freeing/closing a resource — the allocator (caller) or the consumer (callee)?]
- **Common Pitfalls**: [Project-specific risks, e.g., leaking DB connections in error paths, double-freeing handles, unbuffered channel blocks].

### Cross-Platform Compliance (Optional)
- **Cross-Check Command**: `[Command to type-check or compile for all target operating systems/architectures]`.
- **Note**: Platform-gated code is **not** checked unless the matching target is built. Run the cross-check before landing changes.

---

## 4. Review & Landing Pipeline

### Before Submitting a PR
1. All automated tests pass locally.
2. Code passes local formatting, linting, and type-checking gates.
3. **Verification**: [e.g., Verify your test actually fails if you revert your core logic fix].

### Branching & PR Naming
- **Convention**: `[e.g., feature/issue-num-short-description, bugfix/*, or conventional commit prefixes]`.

### Code Review Workflow (Optional)
- **Tooling**: [If utilizing specialized CLI tools like gh, glab, or custom review wrappers, document standard review commands here].
- `[command A]` only shows conversation comments. Use `[command B]` to pull the full picture chronologically including inline diff feedback.

---

## 5. Continuous Integration (CI)

- **CI Dashboard**: [Link to GitHub Actions / GitLab CI / Jenkins]
- **Local CI Emulation (Optional)**: `[Command to run CI pipeline locally, if using tools like act or local runners]`.
- **Common CI Troubleshooting Recipes**:
```bash
# View current pipeline status for this branch
[command]

# Pull failure logs for the latest run
[command]

# Watch / stream a running build until it finishes
[command]
```
**Rule**: If the CI helper scripts produce confusing output, fix the scripts directly rather than working around them — they are thin presenters over the CI API.

---

## 6. Key Rules

1. **Don't commit untested code.** If you didn't run the tests, it doesn't work.
2. **Don't overstate.** Be honest about what was done and what actually works. Document limitations.
3. **Read before you write.** Understand why the existing code made the choices it did before changing them.
4. **Fix the root cause, not the symptom.** Don't take a bug report's or AI's suggested quick-fix at face value — verify it addresses the right architectural layer.