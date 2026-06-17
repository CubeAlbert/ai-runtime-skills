---
name: resume-optimizer
description: Optimize bilingual (Chinese/English) LaTeX resumes for a specific job application by tailoring content to the JD and company. Use this skill when the user wants to tailor their resume, apply for a job, optimize their CV for a position, customize their resume, mention a company folder with job descriptions, or say things like "帮我优化XX的简历", "tailor my resume for XX", "customize my CV". This skill must be explicitly invoked — do not trigger automatically.
---

# Resume Optimizer

Tailor bilingual LaTeX resumes (`CV_CHN.tex` + `CV_EN.tex`) for a specific job application. The master templates contain **all** of the candidate's experience and skills. This skill copies them into a company-specific subfolder, then cuts irrelevant content, adjusts priority, and tweaks wording — without ever fabricating anything. The result is two compiled PDFs merged into a single file.

## Prerequisites

| Tool | Purpose |
|------|---------|
| `pdflatex` | Compile `.tex` → `.pdf` (must support CJK via `\usepackage{CJK}` or similar) |
| Python 3 | Run `scripts/merge_pdfs.py` |

All file operations (read, copy, write) are handled by the agent runtime's built-in tools.

## Bundled Resources

- `scripts/merge_pdfs.py` — Merge two PDF files into one. Run with `--help` for usage.

---

## Workflow

### Step 1: Validate inputs

The user provides a **subfolder name** (e.g., "HSBC", "Google"). Look for it in the current working directory.

**If the subfolder does not exist**, report to the user and stop. Do not proceed.

Verify that both master templates exist in the working directory:

- `CV_CHN.tex`
- `CV_EN.tex`

**If either is missing**, report which one and stop. Do not proceed without both.

Verify the subfolder contains a JD file:

- `jd.txt`, `jd.pdf`, or `jd.docx` (checked in that order)

**If no JD file is found**, report to the user and stop.

Also check for an optional company info file:

- `company.txt`, `company.pdf`, or `company.docx` (checked in that order)

If none exists, proceed with JD only — that's fine.

### Step 2: Read all inputs

Read all of the following into context before making any changes:

1. **`CV_CHN.tex`** — Master Chinese resume (all experience + skills)
2. **`CV_EN.tex`** — Master English resume (all experience + skills)
3. **JD file** (`jd.txt`/`jd.pdf`/`jd.docx`) — The job description
4. **Company file** (`company.txt`/`company.pdf`/`company.docx`) — Company background (if it exists)

From the JD, identify:
- **Target role / position** (e.g., "Senior Software Engineer", "后端开发工程师"). This will be used in the output filename — extract the most specific title. If the JD is ambiguous or contains multiple roles, ask the user: "我找到了以下几个可能的职位名称，用哪个？"
- **Key required skills** (languages, frameworks, domains)
- **Preferred/nice-to-have qualifications**
- **Years of experience expected**
- **Domain/industry context** (finance, e-commerce, gaming, etc.)

From the company file (if present), note:
- **Industry** — helps decide what experience to emphasize or de-emphasize
- **Tech stack hints** — any technology mentioned on the company page
- **Culture/values** — anything that might inform which projects to highlight

### Step 3: Copy templates to subfolder

Copy `CV_CHN.tex` and `CV_EN.tex` into the subfolder. These copies are what you will edit. **Never modify the master templates in the working directory root.**

```
working_directory/
├── CV_CHN.tex          ← READ ONLY, never touch
├── CV_EN.tex           ← READ ONLY, never touch
├── HSBC/
│   ├── jd.txt
│   ├── CV_CHN.tex      ← COPY, safe to edit
│   └── CV_EN.tex       ← COPY, safe to edit
```

### Step 4: Analyze and plan

Read through both CV copies and build a mental map:

- What work experiences are listed (company, role, dates, projects)?
- What skills are claimed?
- What's the structure: sections, ordering, emphasis?

Cross-reference with the JD requirements. For each section/entry in the CV, decide:

| Action | When to apply |
|--------|--------------|
| **Keep as-is** | Directly relevant to the JD |
| **Boost priority** | JD emphasizes this — move earlier in the section |
| **Tone down** | Partially relevant but not core — reduce detail or combine into a shorter mention |
| **Cut** | Irrelevant technology/platform/domain that doesn't transfer (e.g., ".NET project" for a pure Java role). **Before cutting, verify the timeline below** — if removing this project would leave a work period with zero project coverage, do NOT cut it. Instead, use **Tone down** or **Rephrase**. |
| **Rephrase** | Keep the fact but adjust framing to align with JD/company context (e.g., "金融系统开发" → "系统开发" if applying to a non-finance company) |

**Critical rules for editing:**

1. **Never fabricate.** Do not add skills the candidate doesn't have (no matter how much the JD asks for them). Do not invent projects, metrics, or achievements. The master templates are the source of truth.
2. **Never change the LaTeX format.** Don't touch `\usepackage`, `\newcommand`, formatting commands, font settings, margins, section styling — nothing structural. Only edit the **content text** within sections.
3. **Keep the same document structure.** Don't add or remove sections — work with what's already there.
4. **Both CVs should be consistent.** The Chinese and English versions should reflect the same set of changes (same cuts, same priority adjustments, same rephrasings).
5. **No timeline gaps in project experience.** Every work experience period must have at least one corresponding project covering that timeframe. Before cutting a project, map its dates against the work experience entries:
   - If the project is the **only one** under a given work experience entry → do NOT cut it. Use **Tone down** (shorten description) or **Rephrase** (remove domain-specific language) instead.
   - If the project's time range extends beyond its parent work experience → check both sides independently.
   - Build a quick coverage table before making cuts:

   ```
   Work Period          | Projects covering it
   ---------------------|---------------------------
   Feb 2026 - May 2026  | AI Agent, Finance Terminal
   Feb 2020 - Sep 2025  | Asset Pricing, Test Framework, Trade Booking, .NET Pipeline, OTC Upload, Recon Platform
   Sep 2018 - Jan 2020  | Bright Dairy CRM
   ```

   In this example, the Citi period (Feb 2020 - Sep 2025) has 6 projects — cutting 2-3 is safe. But the HAND period (Sep 2018 - Jan 2020) has only 1 project — cutting it would create a gap, so keep it.

6. **Ensure project dates align with work experience dates.** Each project's date range must fall within (or closely align with) the date range of the work experience entry it belongs to. After cutting projects, re-verify that the earliest and latest project dates still cover the full span of each work experience period.

**Rephrasing guidelines:**

- When toning down domain-specific language: replace with a more general description, don't just delete.
  - Bad: "负责金融交易系统的开发与维护" → (deleted)
  - Good: "负责交易系统的开发与维护" (remove "金融" if irrelevant)
- When boosting: expand slightly within what's true, or move the item higher in its section.
- Preserve all dates, job titles, company names — those are factual and untouchable.

### Step 5: Edit CV_CHN.tex

Open the copied `{subfolder}/CV_CHN.tex` and apply the plan from Step 4. Work section by section.

**⚠️ LaTeX 编辑的编码陷阱：** LaTeX 源码包含大量反斜杠和花括号，在搜索、匹配、替换时容易与工具/脚本的转义规则冲突。注意以下四个高频问题：

1. **反斜杠转义冲突** — `\h`、`\s`、`\\` 在不同上下文中含义不同：
   - 在 regex 中 `\s` 是空白字符类，`\h` 是水平空白；但 LaTeX 中 `\section`、`\hspace` 是命令。搜索 LaTeX 命令时使用 **普通字符串匹配** 而非 regex，或在 regex 中将反斜杠双写：`\\section`。
   - LaTeX 换行符 `\\` 是一个命令（两个字符），但在 Python/ruby 字符串中 `\\` 表示一个字面反斜杠。匹配时需写 `\\\\`（四个反斜杠）才能命中源码中的 `\\`。
   - **建议**：优先使用 Edit 工具的 `old_string` 精确匹配，避免 regex 搜索 LaTeX 命令。

2. **花括号与 f-string/template 冲突** — LaTeX 大量使用 `{}`（命令参数、环境边界）：
   - 在 Python f-string 中 `{` 和 `}` 是占位符，需双写 `{{` / `}}` 才能输出字面花括号。
   - 在 JavaScript template literal 中 `${` 是插值语法，需转义。
   - **建议**：不要用 f-string/template literal 拼接 LaTeX 代码段；改用普通字符串拼接或直接使用 Edit 工具逐段替换。

3. **Tab 与空格的不可见差异** — `.tex` 文件中可能混用 tab 和空格做缩进：
   - Edit 工具的 `old_string` 必须 **逐字符完全匹配**（包括不可见字符）。源码中是 tab，你粘贴空格就匹配不上。
   - **建议**：从文件中原样复制要替换的文本（Read → Copy → Paste 到 `old_string`），不要手打。

4. **短字符串搜索假阳性** — 搜索太短的 LaTeX 命令可能命中大量无关位置：
   - 例如搜索 `\item` 会命中所有列表项；搜索 `\begin` 会命中所有环境。
   - **建议**：搜索时带上足够的上下文（如 `\item \textbf{Java}` 而非仅 `Java`），或使用 Grep 的 `-C` 查看上下文确认后再替换。

**Always verify** by re-reading the edited region after each change — a single stray backslash or unmatched brace breaks compilation.

1. **Summary/Profile section**: Rewrite to align with this specific role and company. Mention the target role by name if it fits naturally.
2. **Skills section**: Reorder so JD-matching skills appear first. Cut skills that are irrelevant to this role. Add **only** skills that are present elsewhere in the master CV but were moved.
3. **Experience section**: For each entry, apply the keep/boost/tone-down/cut decision. When cutting an entire project or role, remove it cleanly without leaving broken references.
4. **Other sections** (education, certifications, etc.): Generally keep these. Only cut certifications that are completely irrelevant (e.g., a legacy cert for a modern role).

After editing, verify:
- [ ] All LaTeX commands and environments are properly closed
- [ ] No stray text fragments from cut content
- [ ] The document compiles in your head — no broken `\section{}`, `\begin{}`/`\end{}` pairs

### Step 6: Edit CV_EN.tex

Apply the **same set of changes** to `{subfolder}/CV_EN.tex`. The English version should mirror the Chinese version exactly — same cuts, same reorderings, same rephrasings.

If a rephrasing is language-specific (e.g., removing "金融" from Chinese text), make the equivalent adjustment in English (e.g., "financial trading system" → "trading system").

### Step 7: Cross-validate Chinese and English CVs

Before compiling, verify that both CVs have the **exact same item counts** across every section. The two versions must be structurally identical — same cuts, same entries, same detail level. If any count differs, there is a discrepancy that must be found and fixed.

#### 7a: Count items in both CVs

For **each** of the following categories, count the items in `CV_CHN.tex` and `CV_EN.tex` independently, then compare:

| # | Category | What to count | How to count |
|---|----------|---------------|--------------|
| 1 | **个人简介** (Summary/Profile) | Number of discrete statements or bullet points in the profile section | Count each sentence or `\item` in the profile/summary block |
| 2 | **技术栈** (Skills / Tech Stack) | Each skill category and the number of skills in each category | Count each skill group (e.g., "Languages", "Frameworks", "Tools") and the individual items under each group. Record as: `Languages: 8, Frameworks: 6, Tools: 5` |
| 3 | **教育经历** (Education) | Number of education entries | Count each school/degree entry. Each entry is typically one `\item` or one block with institution + degree + date |
| 4 | **工作经历** (Work Experience) | Number of work entries, and for each entry: the number of responsibility/achievement bullet points | Count each company/role as one entry. Within each entry, count the bullet points (`\item` or `\bullet`) describing responsibilities. Record as: `Entry 1 (Company A): 5 bullets, Entry 2 (Company B): 4 bullets, Total entries: 2, Total bullets: 9` |
| 5 | **项目经历** (Projects) | Number of projects, and for each project: (a) number of tech stack items, (b) number of responsibility descriptions, (c) number of achievements/outcomes | Count each project as one entry. Within each project: count tech stack items, responsibility bullets, and achievement/result bullets separately. Record as: `Project 1 (Name): 4 tech, 3 responsibilities, 2 achievements` |
| 6 | **额外信息** (Additional Information) | Number of extra/additional items | Count items in sections like "Certifications", "Languages", "Awards", "Volunteering", or any catch-all "Additional" section. Record as total count. |

#### 7b: Compare and report

Produce a comparison table:

```
| Category            | CV_CHN | CV_EN | Match? |
|---------------------|--------|-------|--------|
| 个人简介条数          | 3      | 3     | ✓      |
| 技术栈               |        |       |        |
|   - Languages       | 8      | 8     | ✓      |
|   - Frameworks      | 6      | 5     | ✗      |
| 教育经历条数          | 2      | 2     | ✓      |
| 工作经历             |        |       |        |
|   - 条目数           | 3      | 3     | ✓      |
|   - 职责总数          | 15     | 15    | ✓      |
| 项目经历             |        |       |        |
|   - 项目数           | 4      | 4     | ✓      |
|   - 技术栈总数        | 16     | 16    | ✓      |
|   - 职责总数          | 12     | 11    | ✗      |
|   - 成果总数          | 5      | 5     | ✓      |
| 额外信息总数          | 3      | 3     | ✓      |
```

#### 7c: Fix discrepancies

If **any** count differs between CN and EN:

1. **Locate the mismatched section.** The comparison table tells you which category and sub-category is off.
2. **Find the specific missing/extra item.** Read both CVs' corresponding sections line-by-line. One version has an entry the other doesn't, or a bullet was accidentally deleted/duplicated during editing.
3. **Fix the file that is wrong.** Which one is correct? Refer back to the editing plan from Step 4:
   - If an item was deliberately **cut**, remove it from the version that still has it.
   - If an item should have been **kept**, add it back to the version missing it.
   - If an item was accidentally **duplicated**, remove the duplicate.
4. **Re-count** the affected categories after fixing. Do not proceed until every count matches.

This is a hard gate — **do not proceed to compilation until all counts match perfectly**.

### Step 8: Compile both PDFs

Compile each `.tex` file using `pdflatex`. Run **twice** for each file to resolve cross-references:

```bash
# Compile Chinese CV
cd {subfolder}
pdflatex CV_CHN.tex
pdflatex CV_CHN.tex

# Compile English CV
pdflatex CV_EN.tex
pdflatex CV_EN.tex
```

**If compilation fails**, read the error output carefully:
- Common issues: unclosed braces, stray characters from editing, encoding problems with CJK characters.
- Fix the `.tex` file and retry. Do not ask the user unless you cannot resolve the error after two attempts.

After successful compilation, verify that `CV_CHN.pdf` and `CV_EN.pdf` exist in the subfolder.

### Step 9: Extract candidate name

Open `{subfolder}/CV_EN.tex` and locate `\begin{document}`. Scan the **first 50 lines** after `\begin{document}` — this is where personal information (name, email, phone, LinkedIn) typically appears in a resume header.

From these 50 lines, try to identify the candidate's name by looking at:

- Explicit LaTeX name commands (e.g., `\name{Albert Li}`, `\author{Li Ming}`)
- Large/bold text near the top (e.g., `\Large{Albert Li}`, `\textbf{Li Ming}`)
- Text adjacent to an email address (e.g., `Albert Li \\ albert@example.com`)
- Any other personal information context in the header

If the name is **confidently identified**, record it for use in the output filename. Strip spaces for the filename: `Albert Li` → `AlbertLi`.

If the name **cannot be confidently identified** within the first 50 lines, **do not block the workflow**. Set the name aside as `TBD` and continue to Step 10 — the merge step will prompt the user.

### Step 10: Merge PDFs

**If the name was successfully extracted in Step 9**, construct the output filename as:

```
{EnglishName}_CV_{Position}_{Company}.pdf
```

- `{EnglishName}` — from Step 9, with spaces removed or joined (e.g., `LiMing`, `AlbertLi`)
- `{Position}` — from Step 2, cleaned up: remove spaces, keep only alphanumeric chars (e.g., `SeniorDeveloper`, `BackendEngineer`)
- `{Company}` — the subfolder name as-is

Example: `LiMing_CV_SeniorDeveloper_HSBC.pdf`

Then run the merge script:

```bash
python {skill_path}/scripts/merge_pdfs.py \
  {subfolder}/CV_CHN.pdf \
  {subfolder}/CV_EN.pdf \
  --output {subfolder}/{EnglishName}_CV_{Position}_{Company}.pdf
```

**If the name could not be extracted (TBD)**, ask the user:

> 我无法自动从简历中提取英文姓名。请提供候选人的英文名（如 AlbertLi、LiMing），我将继续合并 PDF。

Do **not** block the workflow earlier — compile both PDFs first, then ask for the name only when you reach this step. Once the user provides the name, proceed with the merge command above.

Use `python {skill_path}/scripts/merge_pdfs.py --help` if you need to see all options.

### Step 11: Generate summary and report

Write a `summary.md` file into the subfolder (`{subfolder}/summary.md`) with the following structure:

```markdown
# 简历优化摘要 — {Company}

**职位**: {Position}  
**输出**: {merged_pdf_filename}  
**优化日期**: {YYYY-MM-DD}

---

## 变更明细

### 裁剪（Cuts）
- （列出每个被移除的项目/技能，说明原因）

### 优先级调整（Priority Boosts）
- （列出每个被提前的项目/技能，说明与 JD 的匹配点）

### 措辞调整（Rephrases）
- （列出每个措辞变更：原表述 → 新表述，说明调整原因）

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `CV_CHN.tex` | 优化后的中文简历（只读副本） |
| `CV_EN.tex` | 优化后的英文简历（只读副本） |
| `CV_CHN.pdf` | 编译后的中文 PDF |
| `CV_EN.pdf` | 编译后的英文 PDF |
| `{merged_filename}` | **最终合并版**（中文在前，英文在后） |
| `summary.md` | 本文件 |

---

> 母版文件 `CV_CHN.tex` 和 `CV_EN.tex`（工作目录根）未被修改。
```

After writing the file, tell the user briefly where the output is:

```
已完成 {Company} 的简历优化，输出 {subfolder}/{merged_filename}
详细变更见 {subfolder}/summary.md
```

---

## What NOT to do

1. **Never modify the master templates** (`CV_CHN.tex`, `CV_EN.tex` in the working directory root). Only edit the copies in the subfolder.
2. **Never fabricate experience or skills.** The candidate's real experience is in the master templates — you can only select, reorder, and rephrase.
3. **Never change LaTeX formatting.** `\usepackage`, `\newcommand`, margin settings, font choices, section styles — all untouchable.
4. **Never proceed if validation fails.** Missing subfolder, missing JD file, missing master templates — stop and tell the user.
5. **Never skip the cross-validation step.** All six category counts must match between CN and EN before compilation. If they don't match, find and fix the discrepancy.
6. **Never discard the Chinese or English version.** Both must be compiled and merged into the final output.
7. **Never create timeline gaps.** Every work experience period must have project coverage. Do not cut the only project under a work experience entry — use tone-down or rephrase instead.

---

## Example

**User says:** "帮我优化 HSBC 的简历"

**Skill does:**

1. Checks `./HSBC/` exists → yes
2. Checks `./CV_CHN.tex` and `./CV_EN.tex` exist → yes
3. Finds `./HSBC/jd.txt` → reads it
4. No `./HSBC/company.txt` → proceeds with JD only
5. Copies `CV_CHN.tex` and `CV_EN.tex` into `./HSBC/`
6. Analyzes: JD is for "Senior Java Developer" at HSBC. Key skills: Java, Spring, microservices, financial systems. Nice-to-have: Kubernetes, AI/ML.
7. Plans cuts: candidate has a 2-year .NET project → cut. Candidate has a brief Python scripting mention → keep but don't boost.
8. Plans boosts: candidate has deep Java/Spring experience → move to first position. Candidate did an AI side project → move from "Other" to "Skills" section.
9. Plans rephrases: several mentions of "电商平台" → make generic ("大型交易平台") since HSBC is finance, not e-commerce.
10. Edits both `.tex` files accordingly.
11. Cross-validates: counts all 6 categories, finds 技术栈-Frameworks mismatch → fixes the missing item in CV_EN.tex. Re-counts → all match.
12. Compiles both with `pdflatex`.
13. Merges → `./HSBC/LiMing_CV_SeniorJavaDeveloper_HSBC.pdf`
14. Writes `summary.md` to `./HSBC/` and reports the output path to user.
