<!--
READING GUIDE: This file may be large. Read the Table of Contents first, then jump to the
relevant section. Read 100 lines at a time until the section is complete. Do not load the
entire file at once unless it is short.
-->

# Design

## Table of Contents

- [1. Project Description](#1-project-description)
- [2. Architecture Design](#2-architecture-design)
- [3. Project Structure](#3-project-structure)
- [4. Module Design](#4-module-design)
  - [4.1 Module Name](#41-module-name)
- [5. Document References & Conventions](#5-document-references--conventions)

---

## 1. Project Description

[What this project does, who it's for, and the problem it solves. Keep this concise — 1-2 paragraphs.]

## 2. Architecture Design

[High-level architecture. Include: tech stack choices and rationale, system boundaries, data flow between components, external dependencies/services. Use diagrams in ASCII or Mermaid where helpful.]

## 3. Project Structure

[Directory tree with annotated purpose for each top-level directory and key subdirectories. Example:]

```
project-root/
├── src/             # Source code
│   ├── core/        # Core business logic
│   ├── api/         # API layer
│   └── utils/       # Shared utilities
├── tests/           # Test suite
├── config/          # Configuration files
├── docs/            # Project documentation
└── scripts/         # Build and utility scripts
```

## 4. Module Design

[Detailed design for each module. Add subsections as the project grows. Each module section should be self-contained enough that an LLM reading it alone understands the module's responsibility, public interface, and internal structure.]

### 4.1 [Module Name]

**Purpose:** [What this module does]

**Responsibilities:**
- [Responsibility 1]
- [Responsibility 2]

**Key Interfaces / Public API:**
- `[function/class/endpoint signature]` — [what it does]

**Internal Structure:**
- [Key internal components and how they relate]

**Design Decisions:**
- [Why this module is structured this way, tradeoffs considered]

### 4.2 [Module Name]

[Add more module sections as needed, following the same format as 4.1.]

## 5. Document References & Conventions

[Pointers to external docs, specs, or conventions the project follows.]

**References:**
- [Link or path to relevant document] — [what it covers]

**Conventions:**
- [Coding convention, naming rule, or pattern adopted by this project]
- [Any team-level agreement that affects design]
